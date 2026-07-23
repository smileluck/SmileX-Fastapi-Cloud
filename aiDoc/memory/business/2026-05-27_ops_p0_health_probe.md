# 运维 P0 修复：健康探针 + 启动硬终止

## 需求描述

针对系统扫描发现的三个 P0 级运维缺陷进行修复：

1. **生产部署健康检查必然 404**：`deploy/deploy.env` 的 `HEALTH_CHECK_URL` 指向 `/openapi.json`，但生产环境（`ENVIR=prod` 且 `OPENAPI_ENABLE_IN_PROD=false`）下 `openapi_url=None` 被禁用，导致 `deploy.sh` 健康检查恒 404，可能误判部署失败或触发回滚。
2. **无独立无鉴权健康/就绪探针**：现有 `/admin/sys/monitor/metrics` 需 `require_permission`，K8s/nginx/部署脚本无法用轻量探针判断服务状态。
3. **关键启动失败被静默吞掉**：`main.py` lifespan 中调度器同步、IP 黑名单预热、种子数据失败仅 `logger.error` 后继续启动，安全/调度功能可能静默失效。

## 状态

已完成

## 修复方案

### 缺陷 1 + 2：新增健康探针端点（B 方案：顶级路由）

新增 `backend/modules/admin/endpoints/sys/health.py`，采用**顶级路由**方案（不挂 `/admin` 或 `/open` 任何业务前缀），在 `main.py` 顶层 `app.include_router(health_router)` 注册。提供两个无鉴权端点（不使用 `ResponseModel` 包装，与业务响应结构解耦）：

- `GET /health`（liveness）：固定返回 200 `{"status":"up"}`，仅判断进程存活
- `GET /ready`（readiness）：检查 DB（`SELECT 1`）+ Redis（`PING`），任一失败返回 503，全部成功返回 200；不暴露错误详情，仅给 `ok`/`fail` 状态

`deploy/deploy.env` 的 `HEALTH_CHECK_URL` 从 `/openapi.json` 改为 `/ready`，并补充注释说明原 bug 原因与顶级路径优势。

#### 为什么选顶级路由（B 方案）而非 /admin/sys/* 或 /open/*

| 方案 | 路径 | 鉴权 | 日志中间件 | 评价 |
|------|------|------|-----------|------|
| A（挂 /admin/sys/*） | `/admin/sys/health` + `/ready` | 无 | 受 `OperationLogMiddleware` 约束，需额外维护白名单 | 可行但耦合多 |
| B（顶级路由）✓ | `/health` + `/ready` | 无 | 天然不受任何业务中间件约束 | **最干净** |
| C（挂 /open/*） | `/open/health` + `/ready` | **HMAC 签名** | 强制写 `sys_openapi_log` 商户审计表 | **不可行**（探针无法携带签名头，恒 401） |

关键澄清：项目里的 `/open/*`（开放接口）**不是无鉴权接口**，而是面向第三方商户的 HMAC 签名鉴权接口（`OpenapiLogMiddleware` + `current_merchant` 依赖）。把探针放 `/open` 会导致健康检查恒 401。`/admin/*` 则受 `OperationLogMiddleware` 约束（该中间件第 240 行 `if not path.startswith("/admin/")` 才放行），高频探针会污染审计日志。顶级路径最干净。

### 缺陷 3：启动步骤按致命性分级

`backend/main.py` lifespan 三类启动步骤重新分级：

| 步骤 | 致命性 | 失败行为 |
|------|--------|----------|
| IP 黑名单预热 | 非致命（会从 DB 回源，限流仍可用） | 保留 try/except + ERROR 日志 + 结构化字段 `extra={event: startup_degraded, component: ip_blacklist}` |
| 调度器同步 | **致命**（核心业务：异步导出/限流配置/内置任务） | **移除 try/except，异常自然抛出阻止启动** |
| 种子数据 | 非致命（只影响菜单可见性） | 保留 try/except，日志级别从 ERROR 降为 WARNING（避免污染 5xx 错误率统计） |

shutdown 阶段（yield 之后）的 try/except 保留不变，避免停止失败影响其他资源清理。

### 配套：无需操作日志白名单（B 方案优势）

采用顶级路由后，探针路径 `/health` `/ready` **不以 `/admin/` 开头**，天然不受 `OperationLogMiddleware` 约束。也不以 `/open/` 开头，不受 `OpenapiLogMiddleware` 约束。**无需在 `WHITELIST_PREFIXES` 中维护任何条目**——这是 B 方案相比挂到 `/admin/sys/` 下的核心优势，少一处需要维护的耦合点。

## 涉及范围

### 后端

- `backend/modules/admin/endpoints/sys/health.py`：新增，liveness + readiness 探针（顶级路由）
- `backend/main.py`：顶层注册 `health_router` + lifespan 启动步骤按致命性分级

### 前端

无。

### 部署

- `deploy/deploy.env`：`HEALTH_CHECK_URL` 从 `/openapi.json` 改为 `/ready`

## 约束与备注

- 探针端点是项目内**首个不使用 `ResponseModel` 包装**的端点，属于基础设施语义的合理例外。在端点 docstring 中显式标注例外原因，避免后续被「统一化」误改。
- 探针响应不暴露错误详情（避免泄漏内部拓扑），详细错误记录到日志。
- 选择 `/ready` 而非 `/health` 作为部署脚本的健康检查目标：部署语义是「能否接入流量」，属 readiness 职责。
- 不引入 `/healthz` `/readyz` K8s 惯用别名（当前部署基于 systemd，YAGNI）。
- 探针如需 IP 白名单（仅允许负载均衡器探测），应在 nginx/网关层实现，不在应用层处理。

## 相关文件

- `backend/modules/admin/endpoints/sys/health.py`（新增）
- `backend/main.py`
- `deploy/deploy.env`
- `docs/superpowers/specs/2026-05-27-ops-p0-fix-design.md`（设计规范）
- `docs/superpowers/plans/2026-05-27-ops-p0-fix-plan.md`（实现计划，B 方案）

## 记录日期

2026-05-27
