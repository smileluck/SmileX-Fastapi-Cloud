# 后端响应消息 i18n（中英 + 可扩展）

## 需求描述

后端所有用户可见的响应消息（统一返回 `msg`、异常消息、Pydantic 校验消息）实现国际化，当前支持中文与英文，要求后续易扩展新语言，并支持动态字段插入。前端按 `Accept-Language` 头告知后端返回哪种语言。

## 状态

已完成

## 涉及范围

### 后端

- 新增 `backend/core/i18n/` 包：`context.py`（语言 ContextVar，镜像 `tenant_id_ctx`）、`catalog.py`（加载 `locales/*.yaml` 为扁平 dotted-key 字典）、`translate.py`（`t(key, **kwargs)` + `_SafeDict` 占位符 + 三级回退 locale→fallback→default→raw key）、`accept_language.py`（RFC 质量值 + 前缀匹配纯函数）。
- 新增 `backend/core/i18n/locales/zh-CN.yaml` 与 `en-US.yaml`（331 key，1:1 对齐）。
- 配置 `I18nModel`（`DEFAULT_LANGUAGE` / `SUPPORTED_LANGUAGES` / `FALLBACK_LANGUAGE`）注册进 `GlobalSetting`，`setup_app` 预加载 catalog。
- `RequestContextMiddleware`（最外层纯 ASGI）解析 `Accept-Language` 并 set/reset 语言 ContextVar。
- `CustomCodeBase`：`.msg` 改为按 key 懒翻译，新增 `.key`；`CustomResponseCode`/`CustomErrorCode` 成员第二位由中文改为 i18n key。
- 异常类（`errors.py`）：新增 `default_msg_key` 类属性，`msg` 默认改 `None`，构造期按当前请求语言翻译。
- `errors_handler.py`：所有硬编码中文兜底改为 `t(...)`；`PYDANTIC_ERROR_MSG_MAP` 改为 key 映射。
- `ResponseModel.msg` Field 默认改 `""`，规避 import 期 `t()`。
- 全量迁移约 350 条 inline 中文：`modules/**`、`plugins/multi_tenant/**`、`core/storage/**`、`core/security/oauth/jwt.py`、`core/security/rate_limit.py`、`core/middleware/{security_middleware,rate_limit_middleware}.py` 的 `msg=`/`ValueError`/`detail=`/`"msg":`。

### 前端

- `src/service/request/index.ts` 的 `onRequest` 拦截器注入 `Accept-Language: getLocale()`（取 vue-i18n 当前 locale）。后端 `msg` 原样展示，不再前端翻译。

## 约束与备注

- 语言来源仅 `Accept-Language` 头（不做 query 参数、不加用户表 language 字段）。
- 明确不翻译：`logger` 日志串、Pydantic `Field(description=)`、FastAPI `summary=`、启动/基础设施层错误（DB 池、URL 构建器、雪花 ID、config loader 等 RuntimeError/启动期 ValueError）。
- 新增语言 = 加 `locales/<locale>.yaml` + 追加 `I18N.SUPPORTED_LANGUAGES`，无需改代码。
- 命名空间约定：`response.*`（CustomResponseCode）/ `error.*`（CustomErrorCode + 处理器兜底）/ `pydantic.*` / `common.*`（通用与批量模板）/ `validation.*`（校验器）/ `<模块>.*`。
- 动态字段用 `{name}` 命名占位符；`_SafeDict` 保证缺占位符/格式错误永不抛异常。

## 相关文件

- `backend/core/i18n/`（整个包）
- `backend/core/i18n/locales/{zh-CN,en-US}.yaml`
- `backend/core/config/settings_model.py`、`settings.py`
- `backend/core/middleware/share_middleware.py`
- `backend/core/response/{response_code.py,response_schema.py}`
- `backend/core/exception/{errors.py,errors_handler.py}`
- `backend/core/registry/setup_registry.py`
- `frontend/src/service/request/index.ts`
- `aiDoc/frontend-backend/boundary.md`（i18n 契约）

## 记录日期

2026-07-29
