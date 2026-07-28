# 后端 Web 安全加固

## 需求描述

针对安全自查发现的 5 个疑点逐项整改：文件上传内容校验、预览 token 暴露面、登出闭环、JWT 精细吊销、HSTS 部署。

## 状态

已完成

## 涉及范围

### 后端

- **文件上传**：`core/storage/validator.py` 新增 `detect_file_type`/`validate_file_content`（引入 `filetype` 库做 magic number 检测，与扩展名 + 声明 MIME 三方交叉校验，挡 `.exe` 伪装 `.jpg`）；`file_service.py` 接入并入库可信 MIME；`settings_model.py` 加 `MAGIC_CHECK_ENABLED`/`MIME_STRICT`；`.env.prod`/`.env.test` 补 `ALLOWED_EXTENSIONS` 白名单（原回退 `None` = 任意文件可传），`.env`/`.env.dev` 移除 `exe/msi/apk`。
- **预览 token**：`jwt.py` 新增 `create_preview_token`/`decode_preview_token`（短期 5min、`scope=preview`、绑定 `file_id`）；`file.py` 新增 `POST /{id}/preview-token` 端点，`preview_file` 改为校验 preview token + file_id 绑定，**不再接受 access token**。
- **登出**：`admin/endpoints/auth.py`、`app/endpoints/auth.py` 各新增 `POST /logout`，复用 `OnlineUserService.kick_user` / `UserManager.logout`。
- **App session key Bug 修复**：`app/deps/auth/user_manager.py` 的 `verify_token_session` 与 `logout` 原用错误 key `SESSION_PREFIX+role+uid`（`JWT_SESSION:app123`），与写入侧 `build_session_key`（`JWT_SESSION:APP:123`）不一致 → 登出静默失效、verify 查不到 session；两处统一改为 `build_session_key`。
- **JWT jti 黑名单**：`jwt.py` access/refresh token 注入 `jti`（uuid4）；`core/security/oauth/user_manager.py` 新增 `revoke_token_by_jti`/`is_token_revoked`（Redis key `JWT_JTI_BLACKLIST:{jti}`，TTL=token 剩余寿命）；admin/app 两端 `verify_token_session` 加黑名单校验（每次直查 Redis，不进内存缓存）。批量吊销仍用 `kick_all_sessions`。
- **HSTS**：不改代码，新建 `deploy/SECURITY_HSTS_CHECKLIST.md`（生产当前仅 HTTP，HSTS 关闭正确，HTTPS 就绪后开启）。

### 前端

- `service/api/file.ts`：新增 `fetchGetPreviewToken`，`getFilePreviewUrl` 改为接收 preview token（不再自取 access token）。
- `views/manage/file/modules/file-preview-modal.vue`：打开时异步换 preview token 再拼 URL。

## 约束与备注

- **破坏性变更**：预览接口鉴权方式改变（access token → preview token），前端必须配套，否则预览 401。
- jti 黑名单用于单 token 精细吊销；密码修改等批量吊销继续走 `kick_all_sessions`（删 session Hash）。
- 限流 fail-open、HSTS 保持现状（合理取舍 / 当前无 HTTPS）。
- 预览 token 有效期内登出仍可用（短 exp 缓解；强一致需 preview_file 内查 session，留作后续）。

## 相关文件

- `backend/core/storage/validator.py`、`backend/modules/admin/services/sys/file_service.py`
- `backend/core/security/oauth/jwt.py`、`backend/core/security/oauth/user_manager.py`
- `backend/modules/admin/deps/auth/user_manager.py`、`backend/modules/app/deps/auth/user_manager.py`
- `backend/modules/admin/endpoints/sys/file.py`、`backend/modules/admin/endpoints/auth.py`、`backend/modules/app/endpoints/auth.py`
- `frontend/src/service/api/file.ts`、`frontend/src/views/manage/file/modules/file-preview-modal.vue`
- `deploy/SECURITY_HSTS_CHECKLIST.md`、`aiDoc/frontend-backend/boundary.md`

## 记录日期

2026-07-28
