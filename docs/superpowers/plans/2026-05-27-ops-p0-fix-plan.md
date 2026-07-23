# 运维 P0 修复 — 实现计划（B 方案：顶级路由）

> 关联 spec：[2026-05-27-ops-p0-fix-design.md](../specs/2026-05-27-ops-p0-fix-design.md)
> 创建日期：2026-05-27
> 修订：2026-05-27，从初版（挂 `/admin/sys/*`）改为 B 方案（顶级路由），减少 `sys/__init__.py` 与 `operation_log_middleware.py` 两处耦合。

---

## 任务总览

| # | 任务 | 依赖 | 验收 |
|---|------|------|------|
| 1 | 新建 `health.py` 端点（顶级路由，无 prefix） | 无 | `health_router` 含 `/health`、`/ready` 两个路由 |
| 2 | `main.py` 顶层注册 `health_router` | #1 | `/health`、`/ready` 路由可访问 |
| 3 | `main.py` lifespan 启动分级 | 无 | 调度器同步失败阻止启动；IP 黑名单失败加结构化日志；种子数据降级 WARNING |
| 4 | 修改 `deploy.env` HEALTH_CHECK_URL | #1, #2 | 健康检查指向 `/ready` |
| 5 | 补 aiDoc 业务记忆 | #1-#4 | 新增业务记忆文件 + 更新索引 |
| 6 | 手工验证清单 | #1-#4 | 8 项验证全部通过 |

**执行顺序**：1 → 2 → 3 → 4 → 5 → 6。

> 与初版（7 任务）相比，B 方案省去了「sys/__init__.py 注册」与「操作日志白名单」两个任务，因为顶级路径天然不受这两个机制约束。

---

## 任务 1：新建 `health.py` 端点

**文件**：`backend/modules/admin/endpoints/sys/health.py`（新增）

**要点**：
- 顶级路由（`APIRouter(tags=[...])`，无 prefix）
- 无 `Depends(current_user)`、无 `require_permission`
- 不声明 `response_model`（探针例外，docstring 注明原因）
- DB 检查用 `SELECT 1`，Redis 检查用 `client.ping()`
- `/ready` 任一失败返回 HTTP 503，全部成功返回 HTTP 200
- 不暴露错误详情，详情记日志

**路径设计**（与 spec 3.2 节完全对齐）：

`health_router` 不带 prefix，在 `main.py` 顶层 `app.include_router(health_router)` 注册，最终对外路径：

- `GET /health` — liveness
- `GET /ready` — readiness

顶级路径天然不受 `OperationLogMiddleware`（仅作用 `/admin/*`）和 `OpenapiLogMiddleware`（仅作用 `/open/*`）约束，无需维护任何白名单。

**实现代码骨架**：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
健康检查与就绪探针端点（顶级路由）。

设计说明：
    本端点刻意不使用 ResponseModel 包装、不挂鉴权依赖，并挂在顶级路径（非 /admin、非 /open）。
    原因：
      1. 探针是基础设施语义（供 K8s/nginx/部署脚本探测），需绕过鉴权与业务中间件链路。
      2. 顶级路径天然不受 OperationLogMiddleware（仅作用 /admin/*）与 OpenapiLogMiddleware
         （仅作用 /open/*，强制 HMAC 签名）约束，无需在白名单中维护，最干净。
      3. 与业务响应结构解耦。
"""
import logging

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.redis import get_redis_client

logger = logging.getLogger(__name__)

# 顶级路由：不挂到 sys_router，直接在 main.py 顶层注册
# 最终对外路径为 /health 与 /ready（脱离 /admin /open 业务前缀）
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


@health_router.get("/health", summary="存活探针 (liveness)", status_code=status.HTTP_200_OK)
async def health():
    """存活探针：仅判断进程是否存活，不检查外部依赖。"""
    return {"status": "up"}


@health_router.get("/ready", summary="就绪探针 (readiness)")
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
- `GET /health` → 200 `{"status":"up"}`
- `GET /ready` → 200 或 503
- 无需 Authorization header

---

## 任务 2：`main.py` 顶层注册 `health_router`

**文件**：`backend/main.py`（修改）

**改动 2a** — import 区（与现有 router import 同区）：

```python
from modules.admin.endpoints.sys.health import health_router
```

**改动 2b** — 顶层注册区（在 `app.include_router(open_router)` 后）：

```python
# 健康/就绪探针：顶级路由，无鉴权，不受任何业务中间件约束
app.include_router(health_router)
```

**验收**：启动应用后 `/health` 与 `/ready` 可访问（200/503 任一非 404 即说明路由已注册）。

---

## 任务 3：`main.py` lifespan 启动分级

**文件**：`backend/main.py`（修改）

**改动 3a — IP 黑名单预热加结构化日志**（保留 try/except，加 `extra` 字段）：

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

**改动 3b — 调度器同步改为硬阻止启动**（移除 try/except）：

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

**改动 3c — 种子数据降级 WARNING**（保留 try/except，降级日志）：

```python
try:
    from modules.scheduler.seed import seed_scheduler
    async for db_seed in get_session():
        await seed_scheduler(db_seed)
except Exception as exc:
    logger.warning("定时任务种子数据加载失败，部分预置任务可能缺失: %s", exc)
```

**改动 3d — shutdown 阶段 try/except 保留不变**（yield 之后，避免停止失败影响资源清理）。

**验收**：
- 正常启动：日志显示「定时任务同步完成」
- 模拟 `sync_jobs_from_db` 抛异常：应用启动失败，uvicorn 退出非零
- 模拟 IP 黑名单预热失败：应用仍启动，日志含 `event=startup_degraded`

---

## 任务 4：修改 `deploy.env` HEALTH_CHECK_URL

**文件**：`deploy/deploy.env`（修改）

**改动**：

```diff
- HEALTH_CHECK_URL="http://127.0.0.1:${GUNICORN_PORT}/openapi.json"
+ HEALTH_CHECK_URL="http://127.0.0.1:${GUNICORN_PORT}/ready"
```

并补充注释说明顶级路径优势。

**验收**：检查文件内容，确认 URL 指向 `/ready`。

---

## 任务 5：补 aiDoc 业务记忆

按 AGENTS.MD 规则，用户提出业务需求时必须新增 `memory/business/` 记录。

**文件 5a**：`aiDoc/memory/business/2026-05-27_ops_p0_health_probe.md`（新增）

记录：
- 需求描述：修复生产部署健康检查假性失败 + 新增无鉴权探针 + 启动失败分级处理
- 路径方案：**B 方案 — 顶级路由 `/health` `/ready`**（不挂 `/admin` 或 `/open`，原因：`/open` 强制 HMAC 签名会导致探针恒 401；`/admin` 需额外维护操作日志白名单；顶级路径最干净）
- 涉及范围：后端 health.py、main.py、deploy.env
- 相关文件：列出本次改动文件
- 记录日期：2026-05-27

**文件 5b**：`aiDoc/memory/business/README.md`（修改）

在需求索引末尾加入：

```markdown
- [2026-05-27 运维 P0 修复：健康探针 + 启动硬终止](./2026-05-27_ops_p0_health_probe.md) — 新增无鉴权顶级探针 `/health`（liveness）与 `/ready`（readiness，检查 DB+Redis）；`deploy.env` 健康检查从 `/openapi.json` 改为 `/ready`（修复生产环境 openapi 被禁用导致健康检查恒 404）；`main.py` lifespan 调度器同步失败改为硬阻止启动，IP 黑名单预热失败加结构化降级日志，种子数据降 WARNING；采用顶级路由方案，无需维护操作日志白名单
```

**文件 5c**：`aiDoc/memory/project-memory.md`（修改）

在近期条目顶部加入本次条目。

**验收**：三个文件均更新，无占位符。

---

## 任务 6：手工验证清单

完成 #1-#4 后，启动应用并逐项验证：

| # | 验证项 | 预期结果 |
|---|--------|----------|
| 1 | `curl http://localhost:8000/health` | 200 `{"status":"up"}` |
| 2 | `curl http://localhost:8000/ready` | 200 `{"status":"ready","checks":{"db":"ok","redis":"ok"}}` |
| 3 | 停 Redis 后访问 `/ready` | 503，`checks.redis="fail"` |
| 4 | 停 DB 后访问 `/ready` | 503，`checks.db="fail"` |
| 5 | `/health` 与 `/ready` 无 Authorization header | 不返回 401 |
| 6 | 临时让 `sync_jobs_from_db` 抛异常，启动应用 | 启动失败，uvicorn 退出非零 |
| 7 | 临时让 IP 黑名单 `warmup_blacklist` 抛异常，启动应用 | 应用启动，日志含 `event=startup_degraded` |
| 8 | 连续访问 `/health` 与 `/ready` 各 10 次后查 `sys_operation_log` 与 `sys_openapi_log` | 两表均无对应记录（顶级路径天然豁免，无需白名单） |

**prod 配置额外验证**：
- 设 `ENVIR=prod`，运行 `deploy/deploy.sh deploy` 的健康检查步骤，确认指向 `/ready` 且通过。

---

## 完成定义（Definition of Done）

- [ ] 任务 1-5 全部代码改动完成
- [ ] 任务 6 全部 8 项验证通过
- [ ] 所有改动提交 git
- [ ] aiDoc 业务记忆已补全（遵循 AGENTS.MD）

---

## 风险与回滚

- **回滚**：所有改动均为增量或局部修改，回滚直接 `git revert` 对应 commit。
- **最大风险**：任务 3 调度器同步硬阻止启动，若 DB 中存在脏任务数据可能导致无法启动。缓解：异常会记录完整堆栈，运维可据日志定位修复。
- **B 方案特性**：顶级路由 `/health` `/ready` 不暴露任何内部信息，但如需对探针做 IP 白名单（仅允许负载均衡器探测），应在 nginx/网关层实现，不在应用层处理。
