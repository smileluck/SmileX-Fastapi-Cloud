# 登录与菜单三件套修复 + 在线用户去重

## 需求描述

用户报告了 4 个独立问题：

1. **菜单 icon 类型未持久化 + 侧边栏不支持本地 icon 渲染**：菜单管理弹窗可选 iconify / 本地图标，但 iconType 字段从未真正写入数据库（响应硬编码 `"1"`），侧边栏因此始终只能渲染 iconify 图标。
2. **黑名单自动拉黑 IP 来源**：登录失败超限触发自动拉黑时，IP 必须来自客户端请求（不能被前端伪造）。
3. **记住密码不生效**：登录页"记住密码"复选框没有 v-model，也没有 localStorage 读写逻辑。
4. **在线用户存在重复**：同一用户在 Redis 中堆积了大量 session（实测最多一个用户 78 个），在线用户列表把同一 IP/UA 显示成多行。

## 状态

已完成

## 涉及范围

### 问题 1：菜单 icon 类型持久化 + 本地 icon 渲染

**根因：**
- 后端 `SysMenu` 模型无 `meta_icon_type` 字段
- `SysMenuResponseData.iconType` 是硬编码默认值 `"1"`，从未真正从数据库读取
- `fetchCreateMenu/fetchUpdateMenu` 没把 iconType 传后端
- `_menu_to_route` 只设置 `meta.icon`，从未设置 `meta.localIcon`

**改造：**

后端：
- `backend/database/models/sys/menu.py`：`SysMenu` 新增 `meta_icon_type: Mapped[int]`（SmallInteger，default=1）
- `backend/alembic/versions/0005_menu_icon_type.py`（新增）：`add_column sys_menu.meta_icon_type`（server_default='1'，nullable=False）
- `backend/modules/admin/schemas/sys/menu.py`：
  - 新增模块级 `_int_icon_type_to_str` BeforeValidator（int/str → "1"/"2"）
  - `SysMenuCreate` 加 `meta_icon_type: int = Field(1, ...)`
  - `SysMenuUpdate` 加 `meta_icon_type: Optional[int]`
  - `SysMenuResponseData.iconType` 改为 `Annotated[str, BeforeValidator(_int_icon_type_to_str)] = Field(validation_alias=AliasChoices("meta_icon_type", "iconType"))`
- `backend/modules/admin/services/sys/menu_service.py`：`create_menu` 的 `SysMenu(...)` 构造里追加 `meta_icon_type=menu_create.meta_icon_type`；`update_menu` 沿用现有 `model_dump(exclude_unset=True)` + setattr 循环，新字段自动生效
- `backend/modules/admin/schemas/sys/route.py`：`RouteMetaResponse` 加 `localIcon: str | None`
- `backend/modules/admin/services/sys/route_service.py`：`_menu_to_route` 根据 `menu.meta_icon_type` 分流到 `icon` 或 `localIcon`

前端：
- `frontend/src/service/api/system-manage.ts`：`fetchCreateMenu` / `fetchUpdateMenu` 请求体加 `meta_icon_type: Number(menu.iconType) || 1`
- 表格列、菜单弹窗、store/modules/route/shared.ts 均已支持 iconType='2' 本地渲染，无需改动

### 问题 2：黑名单自动拉黑 IP 来源

**核查结论：现有代码已经使用客户端请求 IP，无需改动。**

完整链路（已正确）：
- `backend/modules/admin/endpoints/auth.py:134`：`ip = get_real_client_ip(request)` — 从 Request 中获取
- `backend/modules/admin/endpoints/auth.py:179`：`RateLimitService.record_login_failure(ip, username)` — 透传
- `backend/modules/admin/services/sys/rate_limit_service.py:27-54`：`record_login_failure` → `IpBlacklistService.auto_block(ip=ip, ...)`
- `backend/modules/admin/services/sys/ip_blacklist_service.py:175-234`：`auto_block` 接收的 ip 直接来自上层，从未从任何前端入参读取

`LoginPwdModel` 只有 `username/password/captcha_token`，不接受前端传 IP，无法被伪造。
`get_real_client_ip` 已实现"仅在 trusted_proxies 内才解析 X-Forwarded-For / X-Real-IP"，防伪造。

**部署提示：** 若生产环境看到的 IP 不对（如显示代理 IP），原因是 `settings.SECURITY.TRUSTED_PROXIES` 未配置反向代理 IP，导致走 fallback 取 `request.client.host`（代理 IP）。属配置问题，非代码问题。

### 问题 3：记住密码

**根因：** `pwd-login.vue` 的 `<NCheckbox>` 无 v-model；`model.userName/password` 硬编码。

**改造：**

- `frontend/src/views/_builtin/login/modules/pwd-login.vue`：
  - 引入 `localStg`、`watch`
  - 模块顶部读取 `localStg.get('rememberLogin')` 作为 `savedLogin`，初始化 `rememberMe` 与 `model.userName/password`
  - 默认账号密码从硬编码 `'admin'/'admin123'` 改为空字符串，由 localStorage 决定回填
  - `<NCheckbox v-model:checked="rememberMe">`
  - 登录成功后：勾选写入 `{ userName, password }`；未勾选清除
  - `watch(rememberMe)`：取消勾选立即清除（满足"点掉勾选则清空"）
- `frontend/src/typings/storage.d.ts`：`StorageType.Local` 加 `rememberLogin: { userName: string; password: string }`

**安全说明：** 明文存 localStorage 是用户主动要求的行为，与典型"记住密码"语义一致。

### 问题 4：在线用户存在重复

**根因：** Redis 实测 `JWT_SESSION:ADMIN:0:2250298479026176` 有 78 个 session。`BaseUserManager.create_token` 每次登录都 `hset` 一个新 session_id 进 Redis Hash，但没有任何机制清理同 IP/UA 反复登录堆积的旧 session，直到 `REFRESH_LIFETIME`（默认 7 天）自然过期。在线用户列表把同一用户同一 IP/UA 显示成多行。

**改造：**
- `backend/core/security/oauth/user_manager.py`：`BaseUserManager` 新增静态方法 `_evict_duplicate_sessions(redis_key, ip, user_agent)`，扫描同 redis_key（= 同 user_id+tenant_id）下 IP 与 UA 完全相同的旧 session 并 `hdel`；在 `create_token` 写入新 session_meta 之前调用
- `backend/scripts/cleanup_duplicate_sessions.py`（新增）：一次性脚本，扫描全部 `JWT_SESSION:*` key，按 `(ip, user_agent)` 分组保留 `login_time` 最新的一条，删除其余

**关键设计决策：**
1. **仅当 ip 和 user_agent 都非空才清理**：app 端登录默认传空字符串，那种情况下保持原有"允许多 session"语义，避免误伤
2. **同 redis_key 内清理，不跨租户**：每个 tenant_id 是独立 key，跨租户会话互不干涉
3. **保留多端语义**：不同 IP/UA（PC + 手机）仍可并存，符合后台系统偶尔多端的需求
4. **登录即清理**：用户下次登录自动顶掉旧 session，无需主动触发；存量数据用一次性脚本处理

**部署提示：** 上线后建议立刻跑一次 `cd backend && python -m scripts.cleanup_duplicate_sessions` 清理存量堆积，避免列表显示需要等用户重新登录才清爽。

## 关键设计决策

1. **后端 iconType 用 int 存储，前端用 string 表达**：与项目现有 `meta_hidden: bool`（后端基础类型）+ 前端字符串的桥接模式一致；通过 `BeforeValidator(_int_icon_type_to_str)` 在 Pydantic 响应序列化时统一转为 `"1"/"2"`
2. **`update_menu` 不需要显式赋值**：现有 `model_dump(exclude_unset=True) + setattr(menu, key, value)` 循环会自动处理新增字段
3. **路由 meta 分流而非新增字段**：保持 `meta.icon` 语义不变（iconify 名），新增 `meta.localIcon`，与 `frontend/src/typings/router.d.ts` 已有的 meta 定义对齐；前端 `getGlobalMenuByBaseRoute` 早已支持双字段渲染，零改动
4. **问题 2 不改代码**：经核查代码已经正确，避免无意义 churn；如用户实际观察到 IP 不对，是 `TRUSTED_PROXIES` 配置问题
5. **记住密码的 STORAGE_KEY 用 'rememberLogin'**：与现有 `lastLoginUserId` 命名风格一致

## 验证方式

### 问题 1
1. `alembic upgrade head`，确认 `sys_menu.meta_icon_type` 列存在
2. 菜单管理 → 编辑目录/菜单 → 切换 iconify / 本地 → 保存 → 再次编辑回弹窗应保持选择
3. 刷新页面后侧边栏应正确显示对应图标
4. SQL：`SELECT name, meta_icon, meta_icon_type FROM sys_menu` 确认持久化

### 问题 2
1. 故意用错误密码连续登录超过 `LOGIN_FAIL_MAX` 次
2. 查 `sys_ip_blacklist` 表，`ip` 字段应等于客户端请求 IP
3. 若反向代理部署，先配置 `SECURITY.TRUSTED_PROXIES` 再测

### 问题 3
1. 输入用户名密码 → 勾选"记住密码" → 登录成功
2. 浏览器 localStorage 应出现 `rememberLogin` 键
3. 退出登录回到登录页 → 用户名密码应自动回填
4. 取消勾选 → localStorage 键应立即消失
5. 再次刷新 → 用户名密码不再回填

## 记录日期

2026-06-27
