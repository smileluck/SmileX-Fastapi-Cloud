# 运维 P0 修复 — 实现计划

> 关联 spec：[2026-05-27-ops-p0-fix-design.md](../specs/2026-05-27-ops-p0-fix-design.md)
> 创建日期：2026-05-27
> 状态：待实现

---

## 任务总览

| # | 任务 | 依赖 | 验收 |
|---|------|------|------|
| 1 | 新建 `health.py` 端点 | 无 | `/admin/sys/health` 返回 200；`/admin/sys/ready` 检查 DB+Redis |
| 2 | 注册 `health_router` | #1 | `/admin/sys/health`、`/admin/sys/ready` 路由可访问 |
| 3 | 操作日志白名单加探针路径 | 无 | 探针请求不产生操作日志记录 |
| 4 | `main.py` lifespan 启动分级 | 无 | 调度器同步失败阻止启动；IP 黑名单失败加结构化日志；种子数据降级 WARNING |
| 5 | 修改 `deploy.env` HEALTH_CHECK_URL | #1, #2 | 健康检查指向 `/admin/sys/ready` |
| 6 | 补 aiDoc 业务记忆 | #1-#5 | 新增业务记忆文件 + 更新索引 |
| 7 | 手工验证清单 | #1-#5 | 8 项验证全部通过 |

**执行顺序**：1 → 2 → 3 → 4 → 5 → 6 → 7。任务 1、3、4、5 之间无强依赖，但建议按此顺序以便逐步验证。

---

## 任务 1：新建 `health.py` 端点

**文件**：`backend/modules/admin/endpoints/sys/health.py`（新增）

**要点**：
- 无 `Depends(current_user)`、无 `require_permission`
- 不声明 `response_model`（探针例外，docstring 注明原因）
- DB 检查用 `SELECT 1`，Redis 检查用 `client.ping()`
- `/ready` 任一失败返回 HTTP 503，全部成功返回 HTTP 200
- 不暴露错误详情，详情记日志

**路径设计**（与 spec 3.2 节完全对齐）：

spec 定义两个平级路径 `/admin/sys/health` 和 `/admin/sys/ready`。实现采用不带 prefix 的 router + 两个独立端点路径，注册到 `sys_router`（prefix=/sys）下，最终路径精确匹配 spec：

- `GET /admin/sys/health` — liveness
- `GET /admin/sys/ready` — readiness

操作日志白名单需同时覆盖两个路径，但二者共享 `/admin/sys/` 前缀且 `/admin/sys/health` 不是其他接口的前缀，故单独列两个条目更清晰（见任务 3）。

**实现代码骨架**：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
健康检查与就绪探针端点。

注意：本端点刻意不使用 ResponseModel 包装、不挂鉴权依赖。
原因：探针是基础设施语义（供 K8s/nginx/部署脚本探测），
需绕过鉴权与业务中间件链路，与业务响应结构解耦。
详见 docs/superpowers/specs/2026-05-27-ops-p0-fix-design.md 第 3.3 节。
"""
import logging

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.redis import get_redis_client

logger = logging.getLogger(__name__)

# 不使用 prefix，两个端点各自声明完整相对路径，注册到 sys_router 后为
# /admin/sys/health 与 /admin/sys/ready，与 spec 3.2 节接口契约对齐
health_router = APIRouter(tags=["基础设施/健康探针"])


async def _check_db(db: AsyncSession) -> bool:
    """检查数据库连接是否可用（执行 SELECT 1）"""
    try:
        result = await db.execute(text("SELECT 1"))
        return result.scalar() == 1
    except Exception as exc:
        logger.warning("就绪检查 DB 失败: %s", exc)
        return False


async def _check_redis(redis_client) -> bool:
    """检查 Redis 连接是否可用（执行 PING）"""
    try:
        pong = await redis_client.ping()
        return bool(pong)
    except Exception as exc:
        logger.warning("就绪检查 Redis 失败: %s", exc)
        return False


@health_router.get(
    "/health",
    summary="存活探针 (liveness)",
    status_code=status.HTTP_200_OK,
)
async def health():
    """存活探针：仅判断进程是否存活，不检查外部依赖。"""
    return {"status": "up"}


@health_router.get(
    "/ready",
    summary="就绪探针 (readiness)",
)
async def ready(
    db: AsyncSession = Depends(get_session),
    redis_client=Depends(get_redis_client),
):
    """就绪探针：检查 DB 与 Redis 是否就绪。任一失败返回 503。"""
    db_ok = await _check_db(db)
    redis_ok = await _check_redis(redis_client)
    checks = {"db": "ok" if db_ok else "fail", "redis": "ok" if redis_ok else "fail"}
    ready_ok = db_ok and redis_ok
    return JSONResponse(
        status_code=status.HTTP_200_OK if ready_ok else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "ready" if ready_ok else "not_ready", "checks": checks},
    )
```

**验收**：
- `GET /admin/sys/health` → 200 `{"status":"up"}`
- `GET /admin/sys/ready` → 200 或 503
- 无需 Authorization header

---

## 任务 2：注册 `health_router`

**文件**：`backend/modules/admin/endpoints/sys/__init__.py`（修改）

**改动**：
1. 在 import 区加入 `from .health import health_router`
2. 在 `sys_router.include_router(...)` 区块加入 `sys_router.include_router(health_router)`

**改动位置**：参考现有 [sys/__init__.py](../../../backend/modules/admin/endpoints/sys/__init__.py)，在 `from .monitor import monitor_router` 附近加入 health 的 import 与注册。

**验收**：启动应用后 `/admin/sys/health` 与 `/admin/sys/health/ready` 可访问（401/200/503 任一非 404 即说明路由已注册）。

---

## 任务 3：操作日志白名单加健康探针路径

**文件**：`backend/core/middleware/operation_log_middleware.py`（修改）

**改动**：在 `WHITELIST_PREFIXES`（第 29 行附近）的 `/admin/sys/monitor` 后加入两个条目（覆盖 `/health` 和 `/ready` 两个端点）：

```python
"/admin/sys/health",   # 存活探针，高频探测，基础设施语义
"/admin/sys/ready",    # 就绪探针，高频探测，基础设施语义
```

> 注：不能用单一 `/admin/sys/health` 前缀覆盖 `/ready`，因为两者是平级路径（见任务 1 路径设计）。需分别列出。

**验收**：访问 `/admin/sys/health` 与 `/admin/sys/ready` 各 10 次后，`sys_operation_log` 表不产生对应记录。

---

## 任务 4：`main.py` lifespan 启动分级

**文件**：`backend/main.py`（修改）

**改动 4a — IP 黑名单预热加结构化日志**（第 44-50 行）：

保留 try/except，但 `logger.error` 调用增加 `extra` 字段：

```python
try:
    from modules.admin.services.sys.rate_limit_service import RateLimitService
    count = await RateLimitService.warmup_blacklist()
    logger.info("IP 黑名单预热数量: %s", count)
except Exception as exc:
    logger.error(
        "IP 黑名单预热异常，限流功能降级运行: %s",
        exc,
        extra={"event": "startup_degraded", "component": "ip_blacklist"},
    )
```

**改动 4b — 调度器同步改为硬阻止启动**（第 51-66 行）：

移除 try/except，让异常自然抛出：

```python
# 启动定时任务调度器（核心业务，失败必须阻止启动）
from modules.scheduler.core.scheduler import SchedulerManager
import modules.scheduler.tasks.builtin  # noqa: F401
import modules.scheduler.tasks.rate_limit_config  # noqa: F401
import modules.scheduler.tasks.generic  # noqa: F401
import modules.scheduler.tasks.export_task  # noqa: F401

manager = SchedulerManager.get_instance()
manager.start()
app.state.scheduler_manager = manager
async for db_sync in get_session():
    await manager.sync_jobs_from_db(db_sync)
logger.info("定时任务同步完成")
```

**改动 4c — 种子数据降级 WARNING**（第 67-73 行）：

```python
try:
    from modules.scheduler.seed import seed_scheduler
    async for db_seed in get_session():
        await seed_scheduler(db_seed)
except Exception as exc:
    logger.warning("定时任务种子数据加载失败，部分预置任务可能缺失: %s", exc)
```

**改动 4d — 保留 shutdown 阶段的 try/except**（第 75-80 行不变）：
调度器停止仍用 try/except，避免 shutdown 失败影响其他资源清理。

**验收**：
- 正常启动：日志显示「定时任务同步完成」
- 模拟 `sync_jobs_from_db` 抛异常：应用启动失败，uvicorn 退出非零
- 模拟 IP 黑名单预热失败：应用仍启动，日志含 `event=startup_degraded`

---

## 任务 5：修改 `deploy.env` HEALTH_CHECK_URL

**文件**：`deploy/deploy.env`（修改）

**改动**（第 38 行）：

```diff
- HEALTH_CHECK_URL="http://127.0.0.1:${GUNICORN_PORT}/openapi.json"
+ HEALTH_CHECK_URL="http://127.0.0.1:${GUNICORN_PORT}/admin/sys/ready"
```

**验收**：检查文件内容，确认 URL 指向 `/admin/sys/ready`。

---

## 任务 6：补 aiDoc 业务记忆

按 AGENTS.MD 规则，用户提出业务需求时必须新增 `memory/business/` 记录。

**文件 6a**：`aiDoc/memory/business/2026-05-27_ops_p0_health_probe.md`（新增）

按 [TEMPLATE.md](../../../aiDoc/memory/business/TEMPLATE.md) 格式，记录：
- 需求描述：修复生产部署健康检查假性失败 + 新增无鉴权探针 + 启动失败分级处理
- 涉及范围：后端 health.py、main.py、operation_log_middleware.py、deploy.env
- 相关文件：列出本次改动文件
- 记录日期：2026-05-27

**文件 6b**：`aiDoc/memory/business/README.md`（修改）

在需求索引末尾加入：

```markdown
- [2026-05-27 运维 P0 修复：健康探针 + 启动硬终止](./2026-05-27_ops_p0_health_probe.md) — 新增无鉴权 /admin/sys/health 与 /ready 探针；deploy.env 健康检查从 /openapi.json 改为 /ready（修复生产假性失败）；main.py lifespan 调度器同步失败改为硬阻止启动；IP 黑名单预热失败加结构化降级日志；探针路径加入操作日志白名单
```

**文件 6c**：`aiDoc/memory/project-memory.md`（修改）

在「业务需求记忆 / 详细索引见 business/README.md。近期：」列表顶部加入本次条目（保持倒序或按 README 一致风格）。

**验收**：三个文件均更新，无占位符。

---

## 任务 7：手工验证清单

完成 #1-#5 后，启动应用并逐项验证：

| # | 验证项 | 预期结果 |
|---|--------|----------|
| 1 | `curl http://localhost:8000/admin/sys/health` | 200 `{"status":"up"}` |
| 2 | `curl http://localhost:8000/admin/sys/ready` | 200 `{"status":"ready","checks":{"db":"ok","redis":"ok"}}` |
| 3 | 停 Redis 后访问 `/admin/sys/ready` | 503，`checks.redis="fail"` |
| 4 | 停 DB 后访问 `/admin/sys/ready` | 503，`checks.db="fail"` |
| 5 | `/health` 与 `/ready` 无 Authorization header | 不返回 401 |
| 6 | 临时让 `sync_jobs_from_db` 抛异常，启动应用 | 启动失败，uvicorn 退出非零 |
| 7 | 临时让 IP 黑名单 `warmup_blacklist` 抛异常，启动应用 | 应用启动，日志含 `event=startup_degraded` |
| 8 | 连续访问 `/admin/sys/health` 与 `/admin/sys/ready` 各 10 次后查 `sys_operation_log` | 无对应记录（白名单生效） |

**prod 配置额外验证**：
- 设 `ENVIR=prod`，运行 `deploy/deploy.sh deploy` 的健康检查步骤，确认指向 `/admin/sys/ready` 且通过。

---

## 完成定义（Definition of Done）

- [ ] 任务 1-6 全部代码改动完成
- [ ] 任务 7 全部 8 项验证通过
- [ ] 所有改动提交 git（建议拆为 1-2 个 commit：业务代码 + 文档）
- [ ] aiDoc 业务记忆已补全（遵循 AGENTS.MD）

---

## 风险与回滚

- **回滚**：本计划所有改动均为增量或局部修改，回滚直接 `git revert` 对应 commit。
- **最大风险**：任务 4 调度器同步硬阻止启动，若 DB 中存在脏任务数据可能导致无法启动。缓解：异常会记录完整堆栈，运维可据日志定位修复。
