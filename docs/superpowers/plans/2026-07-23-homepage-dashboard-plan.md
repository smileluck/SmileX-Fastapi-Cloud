# 首页仪表盘 — 实现计划

> 关联 spec：[2026-07-23-homepage-dashboard-design.md](../specs/2026-07-23-homepage-dashboard-design.md)
> 创建日期：2026-07-23

---

## 任务总览

| # | 任务 | 依赖 | 验收 |
|---|------|------|------|
| 1 | 后端 Schema：`schemas/sys/dashboard.py` | 无 | Pydantic 模型可导入 |
| 2 | 后端 Service：`services/sys/dashboard_service.py` | #1 | 聚合查询返回正确结构 |
| 3 | 后端 Endpoint：`endpoints/sys/dashboard.py` | #1, #2 | `GET /admin/sys/dashboard/summary` 返回数据 |
| 4 | 后端路由注册：`endpoints/sys/__init__.py` | #3 | 接口可访问 |
| 5 | 前端类型：`typings/api/dashboard.d.ts` | 无 | TypeScript 类型可引用 |
| 6 | 前端 API：`service/api/dashboard.ts` | #5 | `fetchDashboardSummary()` 可调用 |
| 7 | 前端组件改造：`card-data.vue` 改为 props | 无 | 接收真实数据渲染 |
| 8 | 前端新组件：`recent-login.vue` | 无 | 时间线正确渲染 |
| 9 | 前端新组件：`latest-notice.vue` | 无 | 公告列表正确渲染 |
| 10 | 前端重写：`home/index.vue` | #6-#9 | 首页展示完整内容 |
| 11 | 前端清理：删除无关组件 | #10 | 无遗留模板组件 |
| 12 | 前端 i18n：补充首页文案 | #10 | 中英文文案就绪 |
| 13 | aiDoc 业务记忆 | #1-#12 | 遵循 AGENTS.MD 记忆规则 |
| 14 | 手工验证 | #1-#12 | 全部验证通过 |

**执行顺序**：1 → 2 → 3 → 4（后端先行）→ 5 → 6 → 7-9（可并行）→ 10 → 11 → 12 → 13 → 14。

---

## 任务 1：后端 Schema

**文件**：`backend/modules/admin/schemas/sys/dashboard.py`（新增）

**要点**：
- 定义 `DashboardStats`、`DashboardRecentLogin`、`DashboardLatestNotice`、`DashboardSummary` 四个模型
- 继承 `BaseEntity`（项目现有 Pydantic 基类）
- 参考 `schemas/sys/monitor.py` 的写法

**代码骨架**：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
首页仪表盘 Schema
"""

from datetime import datetime
from pydantic import Field

from app.models.common.base import BaseEntity


class DashboardStats(BaseEntity):
    """仪表盘统计数据"""
    user_count: int = Field(default=0, description="用户总数")
    role_count: int = Field(default=0, description="角色总数")
    online_count: int = Field(default=0, description="在线用户数")
    today_login_count: int = Field(default=0, description="今日登录次数")


class DashboardRecentLogin(BaseEntity):
    """最近登录记录"""
    username: str = Field(..., description="登录用户名")
    ip: str = Field(default="", description="客户端IP")
    status: bool = Field(..., description="登录状态：True-成功")
    login_time: datetime = Field(..., description="登录时间")


class DashboardLatestNotice(BaseEntity):
    """最新公告"""
    id: str = Field(..., description="公告ID")
    title: str = Field(..., description="公告标题")
    type: str = Field(..., description="公告类型")
    created_at: datetime = Field(..., description="创建时间")


class DashboardSummary(BaseEntity):
    """仪表盘汇总数据"""
    stats: DashboardStats = Field(..., description="统计数据")
    recent_logins: list[DashboardRecentLogin] = Field(default_factory=list, description="最近登录")
    latest_notices: list[DashboardLatestNotice] = Field(default_factory=list, description="最新公告")
```

**验收**：`from modules.admin.schemas.sys.dashboard import DashboardSummary` 无报错。

---

## 任务 2：后端 Service

**文件**：`backend/modules/admin/services/sys/dashboard_service.py`（新增）

**要点**：
- 复用现有 `OnlineUserService.get_online_count()` 获取在线用户数
- 直接查 `SysUser`、`SysRole`、`SysLoginLog`、`SysNotice` 表做 count/limit
- 每个子查询独立 try-except，失败返回 0 或 []
- Redis 缓存 60 秒（key: `dashboard:summary`）

**关键复用点**：
- `OnlineUserService.get_online_count(role="admin")` — 已有方法，扫描 Redis session key 计数
- `SysLoginLog` 模型字段：`username`、`ip`、`status`、`login_time`
- `SysNotice` 模型字段：`status`（True=已发布）、`title`、`type`、`created_at`
- `SysUser`/`SysRole` 继承 `LogicMixin`，软删除通过 `deleted_at IS NULL` 过滤

**代码骨架**：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
首页仪表盘聚合服务
"""

import json
import logging

from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.redis import get_redis_util
from database.models.sys.user import SysUser
from database.models.sys.role import SysRole
from database.models.sys.login_log import SysLoginLog
from database.models.sys.notice import SysNotice
from database.utils.timezone import timezone
from modules.admin.services.sys.online_user_service import OnlineUserService
from modules.admin.schemas.sys.dashboard import (
    DashboardStats,
    DashboardRecentLogin,
    DashboardLatestNotice,
    DashboardSummary,
)

logger = logging.getLogger(__name__)

_CACHE_KEY = "dashboard:summary"
_CACHE_TTL = 60  # 秒


class DashboardService:
    """首页仪表盘聚合服务"""

    @staticmethod
    async def get_summary(db: AsyncSession) -> DashboardSummary:
        """获取仪表盘汇总数据（带 60 秒 Redis 缓存）"""
        redis_util = get_redis_util()

        # 尝试读缓存
        try:
            cached = await redis_util.get(_CACHE_KEY)
            if cached:
                return DashboardSummary.model_validate_json(cached)
        except Exception as exc:
            logger.warning("读取仪表盘缓存失败: %s", exc)

        # 缓存 miss，执行聚合查询
        stats = await DashboardService._get_stats(db)
        recent_logins = await DashboardService._get_recent_logins(db)
        latest_notices = await DashboardService._get_latest_notices(db)

        summary = DashboardSummary(
            stats=stats,
            recent_logins=recent_logins,
            latest_notices=latest_notices,
        )

        # 写缓存
        try:
            await redis_util.set(_CACHE_KEY, summary.model_dump_json(), ex=_CACHE_TTL)
        except Exception as exc:
            logger.warning("写入仪表盘缓存失败: %s", exc)

        return summary

    @staticmethod
    async def _get_stats(db: AsyncSession) -> DashboardStats:
        """获取统计数据（每个字段独立 try-except 降级）"""
        user_count = 0
        role_count = 0
        online_count = 0
        today_login_count = 0

        try:
            result = await db.execute(
                select(func.count(SysUser.id)).where(SysUser.deleted_at.is_(None))
            )
            user_count = result.scalar() or 0
        except Exception as exc:
            logger.warning("仪表盘查询用户总数失败: %s", exc)

        try:
            result = await db.execute(
                select(func.count(SysRole.id)).where(SysRole.deleted_at.is_(None))
            )
            role_count = result.scalar() or 0
        except Exception as exc:
            logger.warning("仪表盘查询角色总数失败: %s", exc)

        try:
            online_count = await OnlineUserService.get_online_count(role="admin")
        except Exception as exc:
            logger.warning("仪表盘查询在线用户数失败: %s", exc)

        try:
            now = timezone.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            result = await db.execute(
                select(func.count(SysLoginLog.id)).where(SysLoginLog.login_time >= today_start)
            )
            today_login_count = result.scalar() or 0
        except Exception as exc:
            logger.warning("仪表盘查询今日登录数失败: %s", exc)

        return DashboardStats(
            user_count=user_count,
            role_count=role_count,
            online_count=online_count,
            today_login_count=today_login_count,
        )

    @staticmethod
    async def _get_recent_logins(db: AsyncSession) -> list[DashboardRecentLogin]:
        """获取最近 10 条登录记录"""
        try:
            result = await db.execute(
                select(SysLoginLog)
                .order_by(SysLoginLog.login_time.desc())
                .limit(10)
            )
            logs = result.scalars().all()
            return [
                DashboardRecentLogin(
                    username=log.username,
                    ip=log.ip or "",
                    status=log.status,
                    login_time=log.login_time,
                )
                for log in logs
            ]
        except Exception as exc:
            logger.warning("仪表盘查询最近登录失败: %s", exc)
            return []

    @staticmethod
    async def _get_latest_notices(db: AsyncSession) -> list[DashboardLatestNotice]:
        """获取最新 5 条已发布公告"""
        try:
            result = await db.execute(
                select(SysNotice)
                .where(SysNotice.status.is_(True))
                .order_by(SysNotice.created_at.desc())
                .limit(5)
            )
            notices = result.scalars().all()
            return [
                DashboardLatestNotice(
                    id=str(notice.id),
                    title=notice.title,
                    type=notice.type,
                    created_at=notice.created_at,
                )
                for notice in notices
            ]
        except Exception as exc:
            logger.warning("仪表盘查询最新公告失败: %s", exc)
            return []
```

**验收**：`DashboardService.get_summary(db)` 返回 `DashboardSummary` 对象，各字段类型正确。

---

## 任务 3：后端 Endpoint

**文件**：`backend/modules/admin/endpoints/sys/dashboard.py`（新增）

**要点**：
- 参考 `endpoints/sys/monitor.py` 写法
- `dashboard_router` prefix `/dashboard`，挂在 `sys_router` 下最终路径 `/admin/sys/dashboard`
- 需要 JWT 鉴权（`Depends(current_user)`），但不做 `require_permission`（所有已登录用户可访问）
- 操作日志白名单：高频接口，需加入白名单避免刷日志

**代码骨架**：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
首页仪表盘接口
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.response import ResponseModel, response_base
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.services.sys.dashboard_service import DashboardService
from modules.admin.schemas.sys.dashboard import DashboardSummary

logger = logging.getLogger(__name__)

dashboard_router = APIRouter(prefix="/dashboard", tags=["系统管理/首页仪表盘"])


@dashboard_router.get(
    "/summary",
    response_model=ResponseModel[DashboardSummary],
    summary="获取首页仪表盘汇总数据",
)
async def get_dashboard_summary(
    user=Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """获取首页仪表盘汇总数据（统计数据 + 最近登录 + 最新公告）"""
    data = await DashboardService.get_summary(db=db)
    return response_base.success(data=data)
```

**验收**：`GET /admin/sys/dashboard/summary` 带 JWT 返回 200 + 完整数据结构。

---

## 任务 4：后端路由注册 + 操作日志白名单

**文件 4a**：`backend/modules/admin/endpoints/sys/__init__.py`（修改）

在 import 区和 include 区各加一行：

```python
# import 区（与其他 endpoint import 同区）
from .dashboard import dashboard_router

# include 区（在 monitor_router 后面）
sys_router.include_router(dashboard_router)
```

**文件 4b**：操作日志白名单（修改）

检查 `core/middleware/operation_log_middleware.py`（或对应白名单配置位置），将 `/admin/sys/dashboard/summary` 加入白名单，避免每次首页加载写一条操作日志。

> 参考 `aiDoc/memory/business/2026-07-13_operation_log_whitelist_polling.md` 的模式。

**验收**：
- `/admin/sys/dashboard/summary` 路由可访问（非 404）
- 连续访问 3 次后查 `sys_operation_log` 表无对应记录

---

## 任务 5：前端类型声明

**文件**：`frontend/src/typings/api/dashboard.d.ts`（新增）

参考现有 `Api.Monitor.*` 的命名空间模式。检查现有 `app.d.ts` 或 typings 结构，将类型挂到 `Api.Dashboard` 命名空间下。

```typescript
declare namespace Api {
  namespace Dashboard {
    /** 统计数据 */
    interface Stats {
      user_count: number;
      role_count: number;
      online_count: number;
      today_login_count: number;
    }

    /** 最近登录记录 */
    interface RecentLogin {
      username: string;
      ip: string;
      status: boolean;
      login_time: string;
    }

    /** 最新公告 */
    interface LatestNotice {
      id: string;
      title: string;
      type: string;
      created_at: string;
    }

    /** 仪表盘汇总 */
    interface Summary {
      stats: Stats;
      recent_logins: RecentLogin[];
      latest_notices: LatestNotice[];
    }
  }
}
```

> 注意：需确认项目 typings 的 namespace 挂载方式（可能需要在 `app.d.ts` 中扩展 `Api` 命名空间，或独立 `.d.ts` 自动被 TypeScript 包含）。

**验收**：`Api.Dashboard.Summary` 类型在 IDE 中可被识别。

---

## 任务 6：前端 API 封装

**文件**：`frontend/src/service/api/dashboard.ts`（新增）

参考 `service/api/monitor.ts` 的写法：

```typescript
import { request } from '../request';

/** 获取首页仪表盘汇总数据 */
export function fetchDashboardSummary() {
  return request<Api.Dashboard.Summary>({
    url: '/admin/sys/monitor/dashboard/summary',
    method: 'get'
  });
}
```

> 注意：实际 URL 为 `/admin/sys/dashboard/summary`（`monitor` 为误写，需改为正确前缀）。同时确认是否需要在 `service/api/index.ts` 中 re-export。

**验收**：`fetchDashboardSummary()` 返回 `Promise<Api.Dashboard.Summary>`。

---

## 任务 7：改造 `card-data.vue`

**文件**：`frontend/src/views/home/modules/card-data.vue`（修改）

**要点**：
- 移除硬编码 mock 数据和 `$t` 国际化引用
- 定义 `defineProps` 接收 `userCount`、`roleCount`、`onlineCount`、`todayLoginCount`
- 保留 `createReusableTemplate` + `GradientBg` + `CountTo` 动画设计
- 卡片配置改为 computed，从 props 构造

**验收**：传入不同 props 时卡片数字和图标正确变化。

---

## 任务 8：新增 `recent-login.vue`

**文件**：`frontend/src/views/home/modules/recent-login.vue`（新增）

**要点**：
- 使用 NaiveUI `NTimeline` 组件
- 接收 `logins: Api.Dashboard.RecentLogin[]` props
- 每条：用户名 + IP + 时间（格式化为 `YYYY-MM-DD HH:mm`）+ 状态（成功 `type="success"` / 失败 `type="error"`）
- 空数据显示 `NEmpty`
- 标题使用 i18n：`$t('page.home.recentLogin')`

**验收**：传入模拟数据正确渲染时间线；传入空数组显示空态。

---

## 任务 9：新增 `latest-notice.vue`

**文件**：`frontend/src/views/home/modules/latest-notice.vue`（新增）

**要点**：
- 使用 NaiveUI `NList` + `NListItem` 组件
- 接收 `notices: Api.Dashboard.LatestNotice[]` props
- 每条：类型标签（`NTag`，announcement=蓝色/system=灰色/operation=绿色/approval=橙色）+ 标题 + 发布时间
- 空数据显示 `NEmpty`
- 标题使用 i18n：`$t('page.home.latestNotice')`

**验收**：传入模拟数据正确渲染列表；传入空数组显示空态。

---

## 任务 10：重写 `home/index.vue`

**文件**：`frontend/src/views/home/index.vue`（修改）

**要点**：
- 移除所有注释内容和无关 import
- 在 `<script setup>` 中调用 `fetchDashboardSummary()` 获取数据
- 使用 `useAuthStore` 获取当前用户昵称用于欢迎横幅
- 布局：欢迎横幅 → CardData（4 列统计卡片）→ NGrid（左 14/24 RecentLogin + 右 10/24 LatestNotice）
- 加载中状态用 `NSpin`

**代码骨架**：

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/store/modules/auth';
import { fetchDashboardSummary } from '@/service/api/dashboard';
import CardData from './modules/card-data.vue';
import RecentLogin from './modules/recent-login.vue';
import LatestNotice from './modules/latest-notice.vue';

const authStore = useAuthStore();
const loading = ref(true);
const stats = ref<Api.Dashboard.Stats>();
const recentLogins = ref<Api.Dashboard.RecentLogin[]>([]);
const latestNotices = ref<Api.Dashboard.LatestNotice[]>([]);

async function loadData() {
  loading.value = true;
  try {
    const { data } = await fetchDashboardSummary();
    if (data) {
      stats.value = data.stats;
      recentLogins.value = data.recent_logins;
      latestNotices.value = data.latest_notices;
    }
  } finally {
    loading.value = false;
  }
}

onMounted(loadData);
</script>

<template>
  <NSpin :show="loading">
    <NSpace vertical :size="16">
      <!-- 欢迎横幅 -->
      <NCard :bordered="false">
        <div class="text-18px font-500">
          {{ $t('page.home.welcome', { name: authStore.userInfo.nickName }) }}
        </div>
      </NCard>

      <!-- 统计卡片 -->
      <CardData
        v-if="stats"
        :user-count="stats.user_count"
        :role-count="stats.role_count"
        :online-count="stats.online_count"
        :today-login-count="stats.today_login_count"
      />

      <!-- 活动流 -->
      <NGrid :x-gap="16" :y-gap="16" responsive="screen" item-responsive>
        <NGi span="24 s:24 m:14">
          <NCard :bordered="false" class="card-wrapper">
            <RecentLogin :logins="recentLogins" />
          </NCard>
        </NGi>
        <NGi span="24 s:24 m:10">
          <NCard :bordered="false" class="card-wrapper">
            <LatestNotice :notices="latestNotices" />
          </NCard>
        </NGi>
      </NGrid>
    </NSpace>
  </NSpin>
</template>
```

> 注意：`authStore.userInfo` 的字段名需确认实际属性（可能是 `userName`、`nickName` 等）。

**验收**：登录后首页展示欢迎横幅、4 个统计卡片、登录时间线和公告列表。

---

## 任务 11：清理无关组件

**删除以下文件**：

| 文件 | 删除原因 |
|------|----------|
| `frontend/src/views/home/modules/header-banner.vue` | 模板遗留装饰横幅 |
| `frontend/src/views/home/modules/line-chart.vue` | mock 折线图，无真实数据 |
| `frontend/src/views/home/modules/pie-chart.vue` | mock 饼图，无真实数据 |
| `frontend/src/views/home/modules/project-news.vue` | mock 项目新闻 |
| `frontend/src/views/home/modules/creativity-banner.vue` | 模板装饰横幅 |

**验收**：文件已删除，`home/index.vue` 无对已删文件的 import 引用，前端编译无报错。

---

## 任务 12：前端 i18n

**文件**：`frontend/src/locales/langs/zh-cn.ts` 和 `en-us.ts`（修改）

在 `page.home` 下补充：

**中文**：
```typescript
home: {
  welcome: '欢迎回来，{name}',
  userCount: '用户总数',
  roleCount: '角色数量',
  onlineCount: '在线用户',
  todayLoginCount: '今日登录',
  recentLogin: '最近登录',
  latestNotice: '最新公告',
  loginSuccess: '成功',
  loginFailed: '失败',
  noData: '暂无数据'
}
```

**英文**：
```typescript
home: {
  welcome: 'Welcome back, {name}',
  userCount: 'Total Users',
  roleCount: 'Total Roles',
  onlineCount: 'Online Users',
  todayLoginCount: "Today's Logins",
  recentLogin: 'Recent Logins',
  latestNotice: 'Latest Notices',
  loginSuccess: 'Success',
  loginFailed: 'Failed',
  noData: 'No data'
}
```

> 注意：需检查现有 `page.home` 是否已有部分 key（如 `visitCount` 等模板遗留），一并清理。

**验收**：切换中英文，首页文案正确显示。

---

## 任务 13：aiDoc 业务记忆

按 `AGENTS.MD` 规则，用户提出业务需求时必须新增 `memory/business/` 记录。

**文件 13a**：`aiDoc/memory/business/2026-07-23_homepage_dashboard.md`（新增）

记录：
- 需求描述：修复空白首页，用真实业务数据替换 mock，展示统计卡片 + 活动流
- 涉及范围：后端新增聚合接口 + 前端首页重写
- 相关文件：列出本次改动文件
- 记录日期：2026-07-23

**文件 13b**：`aiDoc/memory/business/README.md`（修改）

在需求索引末尾加入条目。

**文件 13c**：`aiDoc/memory/project-memory.md`（修改）

在近期条目顶部加入。

**验收**：三个文件均更新，无占位符。

---

## 任务 14：手工验证

| # | 验证项 | 预期结果 |
|---|--------|----------|
| 1 | `GET /admin/sys/dashboard/summary`（带 JWT） | 200，返回 stats + recent_logins + latest_notices |
| 2 | 无 JWT 访问上述接口 | 401 |
| 3 | 连续访问 3 次 | 第 2 次起走 Redis 缓存（可通过日志或响应速度确认） |
| 4 | 连续访问后查 `sys_operation_log` | 无 dashboard/summary 记录（白名单生效） |
| 5 | 前端登录后首页 | 显示欢迎横幅 + 4 个统计卡片 + 登录时间线 + 公告列表 |
| 6 | 统计卡片数字 | 用户总数/角色数/在线数/今日登录与实际数据一致 |
| 7 | 切换中英文 | 文案正确切换 |
| 8 | 空数据场景（清空 login_log） | 时间线显示空态，不报错 |
| 9 | `pnpm build` | 前端构建无报错 |
| 10 | `cd backend && python -c "from modules.admin.endpoints.sys.dashboard import dashboard_router"` | 无 ImportError |

---

## 完成定义（Definition of Done）

- [ ] 任务 1-12 全部代码改动完成
- [ ] 任务 13 aiDoc 业务记忆已补全
- [ ] 任务 14 全部 10 项验证通过
- [ ] 所有改动提交 git

---

## 风险与回滚

- **回滚**：所有改动均为新增文件或局部修改，回滚直接 `git revert` 对应 commit。
- **最大风险**：前端 `home/index.vue` 重写可能遗漏对 store/router 的依赖。缓解：保留原文件的响应式布局类名和 computed gap 逻辑。
- **缓存一致性**：60 秒缓存意味着数据最多延迟 1 分钟。对于仪表盘概览数据可接受。如需实时，前端可手动刷新页面。
