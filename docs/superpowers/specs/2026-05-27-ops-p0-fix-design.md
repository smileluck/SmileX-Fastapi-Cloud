# 运维 P0 修复设计规范

> 主题：健康检查、就绪探针与启动失败硬终止
> 状态：待实现
> 创建日期：2026-05-27
> 关联：本规范源于「系统不足与遗漏分析」，是四个改进方向中「可观测性与运维」方向的第一个独立子项目。

---

## 1. 背景与问题

在对系统做整体扫描时，发现三个 **P0 级（必须立刻修）** 运维缺陷。三者共同特征是：在开发环境/非生产环境不易被发现，但在生产部署或故障时会导致严重误判。

### 1.1 缺陷 ①：生产部署健康检查必然 404

- **现状**：`deploy/deploy.env` 第 38 行 `HEALTH_CHECK_URL="http://127.0.0.1:${GUNICORN_PORT}/openapi.json"`。
- **冲突**：`backend/main.py` 第 104-106 行，当 `settings.ENVIR == "prod"` 且 `OPENAPI_ENABLE_IN_PROD` 为假时，`openapi_url=None`、`docs_url=None`、`redoc_url=None`。
- **后果**：生产环境部署后，`deploy/deploy.sh` 的 `cmd_deploy` 健康检查步骤（第 196-206 行）对 `/openapi.json` 发起 curl，恒返回 404，健康检查恒失败。
  - 轻则：部署日志显示「健康检查失败」，运维误以为部署失败，实际服务正常。
  - 重则：触发 `rollback` 流程，回退到旧版本。

### 1.2 缺陷 ②：无独立无鉴权健康/就绪探针

- **现状**：现有健康类接口只有 `modules/admin/endpoints/sys/monitor.py` 的 `GET /admin/sys/monitor/metrics`，且依赖 `require_permission("sys:monitor:view")`。
- **后果**：K8s liveness/readiness probe、nginx upstream 健康检查、外部负载均衡器、`deploy.sh` 部署脚本，都无法用一个无鉴权的轻量探针判断服务状态。

### 1.3 缺陷 ③：关键启动失败被静默吞掉

- **现状**：`backend/main.py` 第 44-73 行，`lifespan` 中三个启动步骤（IP 黑名单预热、调度器同步、定时任务种子数据）均用宽松 `try/except Exception as exc: logger.error(...)`，失败后应用仍继续启动。
- **后果**：
  - IP 黑名单预热失败 → 限流/IP 黑名单功能在生产静默失效，安全策略降级而无人知晓。
  - 调度器同步失败 → 定时任务（含异步导出、限流配置同步）静默失效，业务功能不可用但无告警。
  - 种子数据失败 → 部分预置任务缺失，影响调度器可见性。

---

## 2. 目标与非目标

### 2.1 目标

1. 提供 `/health`（liveness）和 `/ready`（readiness）两个无鉴权探针端点。
2. 修复 `deploy.env` 健康检查 URL，指向真实可用的探针。
3. 对 `main.py` `lifespan` 启动步骤按致命性分级，致命失败应阻止启动。
4. 遵循 AGENTS.MD 文档规则，更新 `aiDoc/memory/business/`。

### 2.2 非目标（YAGNI 边界）

- **不**引入 Prometheus `/metrics` 端点（属于「可观测性」专项，单独规划）。
- **不**引入 OpenTelemetry / 分布式 tracing。
- **不**修改 `/admin/sys/monitor/metrics`（保留给前端监控面板）。
- **不**改 JWT 存储方式或引入 CSRF 防护（属于「安全加固」专项）。
- **不**清理 `errors_handler.py` 的异常处理器冗余注册（属于「功能一致性」范围）。
- **不**新增 `/healthz` `/readyz` K8s 惯用别名（保持简单，当前部署基于 systemd 而非 K8s）。
- **不**改动数据库连接池/Redis 池的初始化失败处理（现有逻辑已会让进程启动失败，保留原状）。

---

## 3. 架构设计

### 3.1 新增端点

新建 `backend/modules/admin/endpoints/sys/health.py`，提供两个端点：

| 端点 | 语义 | 检查内容 | 成功 | 失败 |
|------|------|----------|------|------|
| `GET /health` | liveness（存活） | 不检查任何外部依赖 | HTTP 200 | 永远 200（进程能响应即存活） |
| `GET /ready` | readiness（就绪） | DB 连接（`SELECT 1`）+ Redis 连接（`PING`） | HTTP 200 | HTTP 503 |

路由前缀与现有 `monitor.py` 一致，挂在 `/admin/sys/health` 下，但 **不挂任何依赖**：

- 无 `Depends(current_user)`
- 无 `Depends(require_permission(...))`
- **必须加入操作日志中间件白名单**（见 3.7 节）

### 3.2 接口契约

#### `GET /admin/sys/health`

```json
{
  "status": "up"
}
```

固定返回，HTTP 200。无任何依赖检查。用于「进程是否需要重启」判断。

#### `GET /admin/sys/ready`

成功（全部检查通过）：

```json
{
  "status": "ready",
  "checks": {
    "db": "ok",
    "redis": "ok"
  }
}
```

HTTP 200。

失败（任一检查失败）：

```json
{
  "status": "not_ready",
  "checks": {
    "db": "fail",
    "redis": "ok"
  }
}
```

HTTP 503。

> 说明：`checks` 中只给 `ok` / `fail` 状态，**不**暴露错误详情（避免泄漏内部拓扑）。详细错误记录到日志。

### 3.3 响应模型

为保持与项目统一响应结构（`{code, msg, data, request_id, err_code}`）的一致性，探针响应 **不**使用 `ResponseModel` 包装。原因：

- `ResponseModel` 需要走异常处理器、request_id 中间件等链路，**与"无鉴权轻量探针"的目标冲突**。
- K8s/nginx/部署脚本只关心 HTTP 状态码，不需要业务语义。
- 探针的 503 是基础设施语义，不是业务错误。

因此探针直接返回 `{"status": ...}` dict + 显式 HTTP 状态码。这是探针端点的合理例外，与 AGENTS.MD「Endpoint 必须声明 response_model」的规则冲突，**在实现时需要在端点 docstring 中显式标注例外原因**。

### 3.4 deploy.env 修复

`deploy/deploy.env` 第 38 行：

```diff
- HEALTH_CHECK_URL="http://127.0.0.1:${GUNICORN_PORT}/openapi.json"
+ HEALTH_CHECK_URL="http://127.0.0.1:${GUNICORN_PORT}/admin/sys/ready"
```

选择 `/ready` 而非 `/health` 的原因：`deploy.sh` 的健康检查语义是「服务是否能接入流量」，这正是 readiness 的职责。`/health`（liveness）只判断进程存活，无法发现 DB/Redis 故障。

### 3.5 main.py lifespan 加固

对 `backend/main.py` 第 44-73 行的三个 try/except 块按致命性重新分级：

| 步骤 | 当前行为 | 新行为 | 理由 |
|------|----------|--------|------|
| IP 黑名单预热 | try/except + ERROR 日志，继续启动 | 保留 try/except + ERROR 日志 + 结构化字段 `event=startup_degraded`，继续启动 | 预热失败会自动从 DB 回源查询，限流仍可用，只是首次请求稍慢。属降级而非失效。 |
| 调度器同步 | try/except + ERROR 日志，继续启动 | **改为抛异常阻止启动** | 调度器是核心业务（异步导出、限流配置同步、内置任务），同步失败意味着功能静默失效，宁可启动失败让运维介入。 |
| 定时任务种子数据 | try/except + ERROR 日志，继续启动 | 保留 try/except + **提升日志级别为 WARNING**，继续启动 | 种子数据是幂等的预置任务，缺失只影响菜单可见性，不影响核心功能。ERROR 级别过重，会污染 5xx 错误率统计。 |

#### 调度器同步失败的实现细节

原代码：

```python
try:
    from modules.scheduler.core.scheduler import SchedulerManager
    # ...
    manager = SchedulerManager.get_instance()
    manager.start()
    app.state.scheduler_manager = manager
    async for db_sync in get_session():
        await manager.sync_jobs_from_db(db_sync)
    logger.info("定时任务同步完成")
except Exception as exc:
    logger.error("定时任务同步异常: %s", exc)
```

新行为：移除 `try/except`，让异常自然向上抛出。FastAPI 的 `lifespan` 抛异常会阻止应用启动，uvicorn/gunicorn 会因启动失败而退出非零状态码，触发 systemd 重启或部署脚本失败告警。

保留调度器停止的 `try/except`（第 76-80 行，shutdown 阶段），因为 shutdown 阶段的失败不应影响其他资源的清理。

### 3.6 启动顺序与探针可用性

`/ready` 探针在 lifespan 的 `yield` 之前完成所有初始化，路由在 `setup_app` 阶段已注册（早于 lifespan）。这意味着：

- 启动过程中，路由已存在但 DB/Redis 尚未就绪 → `/ready` 返回 503（符合预期）。
- lifespan 完成后，DB/Redis 就绪 → `/ready` 返回 200。
- lifespan 抛异常（调度器同步失败）→ 进程退出，不会有半就绪状态对外服务。

### 3.7 操作日志中间件白名单（必须）

探针路径 `/admin/sys/health` 以 `/admin/` 开头，会被 `OperationLogMiddleware`（`backend/core/middleware/operation_log_middleware.py`）捕获。该中间件**不区分 GET/POST**，对所有未命中白名单的 `/admin/` 请求都会记录操作日志（`user_id=0, username="anonymous"`）。

探针通常被 K8s/nginx/部署脚本高频探测（每秒数次），若不加入白名单会：

- 污染操作日志表，淹没真实用户操作记录
- 每次探测触发一次 DB 写入（`_write_operation_log` 的 BackgroundTask），增加无意义负载

因此必须在 `WHITELIST_PREFIXES`（`operation_log_middleware.py` 第 29 行）中加入 `/admin/sys/health`：

```python
WHITELIST_PREFIXES: Tuple[str, ...] = (
    "/admin/auth",
    # ...
    "/admin/sys/monitor",
    "/admin/sys/health",   # 新增：健康/就绪探针，基础设施语义，不计入操作日志
    # ...
)
```

`/health` 和 `/ready` 共享前缀 `/admin/sys/health`，一条白名单规则即可覆盖两个端点。

---

## 4. 组件清单

| 单元 | 职责 | 依赖 |
|------|------|------|
| `backend/modules/admin/endpoints/sys/health.py`（新增） | 定义 `/health` 和 `/ready` 端点 | DB session（`get_session`）、Redis client（`get_redis_client`） |
| `backend/modules/admin/endpoints/sys/__init__.py`（修改） | 注册 `health_router` | 无 |
| `backend/core/middleware/operation_log_middleware.py`（修改） | `WHITELIST_PREFIXES` 加入 `/admin/sys/health` | 无 |
| `backend/main.py`（修改） | lifespan 启动步骤分级 | 无 |
| `deploy/deploy.env`（修改） | 健康检查 URL | 无 |
| `aiDoc/memory/business/2026-05-27_ops_p0_health_probe.md`（新增） | 业务需求记忆 | 无 |
| `aiDoc/memory/business/README.md`（修改） | 更新业务需求索引 | 无 |
| `aiDoc/memory/project-memory.md`（修改） | 更新顶层索引近期条目 | 无 |

---

## 5. 数据流

### 5.1 健康检查请求流

```
K8s/nginx/deploy.sh
   │
   │  GET /admin/sys/ready
   ▼
[FastAPI 路由层]  ── 无鉴权依赖 ──▶  health.py:ready()
   │
   ├── 并行检查 ──▶ DB: get_session() → conn.execute(text("SELECT 1"))
   │
   └── 并行检查 ──▶ Redis: get_redis_client() → client.ping()
   │
   ▼
[聚合结果]  全部 ok → 200 {"status":"ready",...}
           任一 fail → 503 {"status":"not_ready",...}
```

### 5.2 启动失败流

```
uvicorn 启动
   │
   ▼
[FastAPI lifespan]
   ├── init DB pool（失败 → 抛异常 → 启动失败，现有行为保留）
   ├── init Redis pool（失败 → 抛异常 → 启动失败，现有行为保留）
   ├── init WebSocket manager
   ├── IP 黑名单预热（失败 → ERROR + startup_degraded，继续）
   ├── 调度器同步（失败 → 抛异常 → 启动失败，新行为）
   └── 种子数据（失败 → WARNING，继续）
   │
   ▼  全部成功
[yield]  服务对外可用，/ready 返回 200
```

---

## 6. 错误处理

| 场景 | 处理 |
|------|------|
| `/ready` DB 检查失败 | 记录 WARNING 日志（路径、错误类型），返回 503，`checks.db="fail"` |
| `/ready` Redis 检查失败 | 记录 WARNING 日志，返回 503，`checks.redis="fail"` |
| `/ready` 检查超时 | 每个 DB/Redis 检查设置超时（DB 沿用连接池超时；Redis 设置 `socket_timeout`），超时视为 fail |
| `/health` 端点 | 无错误处理需求，固定返回 200 |
| 调度器同步失败 | 异常自然抛出，FastAPI 阻止启动，uvicorn 退出非零 |
| IP 黑名单预热失败 | ERROR 日志 + `extra={"event": "startup_degraded", "component": "ip_blacklist"}`，继续启动 |
| 种子数据失败 | WARNING 日志，继续启动 |

---

## 7. 测试策略

当前项目无测试基础设施（这是另一个 P0 不足，由「质量保障基线」专项处理）。本规范的测试策略如下：

### 7.1 手工验证清单（实现后必须执行）

1. 启动应用（开发环境），`curl http://localhost:8000/admin/sys/health` → 200 `{"status":"up"}`
2. `curl http://localhost:8000/admin/sys/ready` → 200 `{"status":"ready","checks":{"db":"ok","redis":"ok"}}`
3. 停掉 Redis，`curl http://localhost:8000/admin/sys/ready` → 503 `{"status":"not_ready","checks":{"db":"ok","redis":"fail"}}`
4. 停掉 DB，`curl http://localhost:8000/admin/sys/ready` → 503，`checks.db="fail"`
5. 确认 `/health` 和 `/ready` 不需要 Authorization header
6. 模拟调度器同步失败（临时让 `sync_jobs_from_db` 抛异常），确认应用启动失败、uvicorn 退出非零
7. 模拟 IP 黑名单预热失败，确认应用仍启动、日志含 `event=startup_degraded`
8. 在 prod 配置下（`ENVIR=prod`）运行 `deploy/deploy.sh deploy` 的健康检查步骤，确认指向 `/admin/sys/ready` 且通过

### 7.2 单元测试占位

`health.py` 的 `ready()` 检查逻辑应在「质量保障基线」专项落地测试框架后补充单元测试，覆盖：DB ok/Redis fail、DB fail/Redis ok、全 fail、全 ok 四种组合。本规范不包含测试代码，但在 `health.py` 中预留可测试的内部函数结构（将 DB/Redis 检查拆为独立 helper）。

---

## 8. 实现顺序（供 writing-plans 展开）

1. 新建 `health.py`：定义 `_check_db()`、`_check_redis()` 内部函数 + `health()`、`ready()` 端点
2. 在 `sys/__init__.py` 注册 `health_router`
3. 在 `operation_log_middleware.py` 的 `WHITELIST_PREFIXES` 加入 `/admin/sys/health`
4. 修改 `main.py` lifespan：调度器同步移除 try/except，IP 黑名单加结构化日志，种子数据降级为 WARNING
5. 修改 `deploy/deploy.env` 的 `HEALTH_CHECK_URL`
6. 按 AGENTS.MD 规则新增 `aiDoc/memory/business/2026-05-27_ops_p0_health_probe.md`，更新 `business/README.md` 与 `project-memory.md`
7. 执行第 7.1 节手工验证清单

---

## 9. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 调度器同步硬阻止启动，若 DB 中存在脏任务数据，可能导致应用无法启动 | 高 | 调度器同步失败属于真实故障，硬失败比静默失效更安全；运维可通过 `alembic` 或 DB 修复脏数据后重启。同步失败的异常信息会记录完整堆栈，便于定位。 |
| `/ready` 每次请求都做 DB/Redis 检查，高频探针可能增加负载 | 中 | `SELECT 1` 和 `PING` 极轻量；若后续接入 K8s 高频探针，可加内存级缓存（TTL 1-2s），本规范暂不实现。 |
| 探针不使用 `ResponseModel`，与项目统一响应结构不一致 | 低 | 探针是基础设施语义，非业务响应。在端点 docstring 显式标注例外原因，避免后续被「统一化」误改。 |
| `/health` 和 `/ready` 暴露了应用存活信息 | 低 | 不暴露任何内部拓扑、版本、配置信息，仅返回状态字符串。如需隐藏，可在 nginx 层加 IP 白名单，本规范不强制。 |

---

## 10. 决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 调度器同步失败是否硬阻止启动 | **是** | 调度器是核心业务（异步导出、限流配置同步、内置任务），静默失效比启动失败更危险。用户在澄清中确认。 |
| 是否新增 `/healthz` `/readyz` 别名 | **否** | 当前部署基于 systemd，非 K8s。YAGNI。如未来上 K8s 可再加别名。 |
| 探针是否使用 `ResponseModel` | **否** | 探针是基础设施语义，需绕过鉴权/中间件链路，与业务响应结构解耦。 |
| `deploy.sh` 健康检查用 `/health` 还是 `/ready` | `/ready` | 部署语义是「能否接入流量」，属 readiness 职责，需检测 DB/Redis 就绪。 |
| `/ready` 暴露错误详情 | **否** | 避免泄漏内部拓扑，详情记日志。 |

---

## 11. 落地后的后续工作（不在本规范范围）

完成本规范后，剩余的系统不足（按优先级）：

1. **后端测试基线**（P0）：pytest + conftest + 核心模块单元测试骨架
2. **后端 i18n 体系**（P0）：错误码 + msg 多语言资源包
3. **后端 CI/CD + lint**（P1）：ruff/mypy + GitHub Actions
4. **Prometheus metrics 端点**（P1）
5. **Docker 化**（P2）
6. **JWT 迁移 httpOnly cookie + CSRF**（P1，安全加固专项）

每个后续工作都应有独立的 spec → plan → 实现周期。
