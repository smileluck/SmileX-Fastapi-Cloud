# 运维 P0 修复：健康探针 + 启动硬终止

## 需求描述

针对系统扫描发现的三个 P0 级运维缺陷进行修复：

1. **生产部署健康检查必然 404**：`deploy/deploy.env` 的 `HEALTH_CHECK_URL` 指向 `/openapi.json`，但生产环境（`ENVIR=prod` 且 `OPENAPI_ENABLE_IN_PROD=false`）下 `openapi_url=None` 被禁用，导致 `deploy.sh` 健康检查恒 404，可能误判部署失败或触发回滚。
2. **无独立无鉴权健康/就绪探针**：现有 `/admin/sys/monitor/metrics` 需 `require_permission`，K8s/nginx/部署脚本无法用轻量探针判断服务状态。
3. **关键启动失败被静默吞掉**：`main.py` lifespan 中调度器同步、IP 黑名单预热、种子数据失败仅 `logger.error` 后继续启动，安全/调度功能可能静默失效。

## 状态

已完成

## 修复方案

### 缺陷 1 + 2：新增健康探针端点

新增 `backend/modules/admin/endpoints/sys/health.py`，提供两个无鉴权端点（不使用 `ResponseModel` 包装，与业务响应结构解耦）：

- `GET /admin/sys/health`（liveness）：固定返回 200 `{"status":"up"}`，仅判断进程存活
- `GET /admin/sys/ready`（readiness）：检查 DB（`SELECT 1`）+ Redis（`PING`），任一失败返回 503，全部成功返回 200；不暴露错误详情，仅给 `ok`/`fail` 状态

`deploy/deploy.env` 的 `HEALTH_CHECK_URL` 从 `/openapi.json` 改为 `/admin/sys/ready`，并补充注释说明原 bug 原因。

### 缺陷 3：启动步骤按致命性分级

`backend/main.py` lifespan 三类启动步骤重新分级：

| 步骤 | 致命性 | 失败行为 |
|------|--------|----------|
| IP 黑名单预热 | 非致命（会从 DB 回源，限流仍可用） | 保留 try/except + ERROR 日志 + 结构化字段 `extra={event: startup_degraded, component: ip_blacklist}` |
| 调度器同步 | **致命**（核心业务：异步导出/限流配置/内置任务） | **移除 try/except，异常自然抛出阻止启动** |
| 种子数据 | 非致命（只影响菜单可见性） | 保留 try/except，日志级别从 ERROR 降为 WARNING（避免污染 5xx 错误率统计） |

shutdown 阶段（yield 之后）的 try/except 保留不变，避免停止失败影响其他资源清理。

### 配套：操作日志白名单

探针路径 `/admin/sys/health` 与 `/admin/sys/ready` 以 `/admin/` 开头会被 `OperationLogMiddleware` 捕获（该中间件不区分 GET/POST）。高频探测会污染审计日志表并产生无意义 DB 写入，故在 `WHITELIST_PREFIXES` 中加入两条。

## 涉及范围

### 后端

- `backend/modules/admin/endpoints/sys/health.py`：新增，liveness + readiness 探针
- `backend/modules/admin/endpoints/sys/__init__.py`：注册 `health_router`
- `backend/core/middleware/operation_log_middleware.py`：`WHITELIST_PREFIXES` 加 `/admin/sys/health` 与 `/admin/sys/ready`
- `backend/main.py`：lifespan 启动步骤按致命性分级

### 前端

无。

### 部署

- `deploy/deploy.env`：`HEALTH_CHECK_URL` 从 `/openapi.json` 改为 `/admin/sys/ready`

## 约束与备注

- 探针端点是项目内**首个不使用 `ResponseModel` 包装**的端点，属于基础设施语义的合理例外。在端点 docstring 中显式标注例外原因，避免后续被「统一化」误改。
- 探针响应不暴露错误详情（避免泄漏内部拓扑），详细错误记录到日志。
- 选择 `/ready` 而非 `/health` 作为部署脚本的健康检查目标：部署语义是「能否接入流量」，属 readiness 职责。
- 不引入 `/healthz` `/readyz` K8s 惯用别名（当前部署基于 systemd，YAGNI）。

## 相关文件

- `backend/modules/admin/endpoints/sys/health.py`（新增）
- `backend/modules/admin/endpoints/sys/__init__.py`
- `backend/core/middleware/operation_log_middleware.py`
- `backend/main.py`
- `deploy/deploy.env`
- `docs/superpowers/specs/2026-05-27-ops-p0-fix-design.md`（设计规范）
- `docs/superpowers/plans/2026-05-27-ops-p0-fix-plan.md`（实现计划）

## 记录日期

2026-05-27
