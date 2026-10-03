<!-- last-updated: 2026-05-30 -->
# Web 安全防护现状与约束

## 已实现的防护

| 防护项 | 方案 | 关键文件 |
|--------|------|----------|
| SQL 注入 | SQLAlchemy ORM + 参数化查询；`execute_raw_sql` 有 DDL 黑名单 | `core/security/sanitize.py` |
| XSS | CSP 安全头 + `bleach` 富文本清洗 | `core/security/sanitize.py`, `core/middleware/security_middleware.py` |
| 安全响应头 | X-Content-Type-Options / Referrer-Policy / Permissions-Policy / CSP | `core/middleware/security_middleware.py` |
| 限流 | IP / 用户 / 路径多维限流 + IP 黑名单 | `core/security/rate_limit.py` |
| 文件上传 | 扩展名白名单 + 大小限制 + UUID 重命名 | 上传相关 service |
| 输入校验 | Pydantic schema 全覆盖 | 各模块 `schemas/` |
| 认证授权 | JWT + Redis session + RBAC | `modules/app/deps/auth/` |
| 错误处理 | 不暴露堆栈 / SQL 细节，统一响应结构 | 异常处理中间件 |

## 需注意的约束

### CSRF 策略
- **当前方案**: JWT 存 localStorage，通过 `Authorization` header 传递，不依赖 cookie，浏览器不会自动附带 → CSRF 风险低
- **重要约束**: 如果未来改用 cookie 传递 token，**必须**同步实现 CSRF token 防护（Double Submit Cookie 或 Synchronizer Token）
- CORS 已限制允许的 origin，提供额外防护层

### Token 存储
- **当前方案**: JWT 存 localStorage（通过 `localStg` 封装）
- **已知风险**: localStorage 可被 XSS 窃取；当前 XSS 防护到位（无 v-html、CSP 严格、bleach 清洗），实际风险可控
- **待办**: 迁移到 httpOnly cookie 可进一步降低风险，但改动面大（前后端认证架构），作为专项任务处理

### 富文本清洗
- `sanitize_rich_text` 基于 `bleach` 白名单清洗，已在通知模块接入
- **新增富文本字段时**: 必须在 schema 的 `field_validator` 中调用 `sanitize_rich_text`
- 允许的标签: `b, strong, i, em, u, p, br, ul, ol, li, a`（定义在 `core/security/sanitize.py`）

### 前端安全
- 不使用 `v-html`（已确认全项目无此用法）
- 开发环境 token 通过 `.env` 环境变量管理，不硬编码
