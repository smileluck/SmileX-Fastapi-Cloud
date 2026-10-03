<!-- last-updated: 2026-05-18 -->
# Router 层示例

## 用途

展示如何组织模块路由并注册到应用。

## 核心原则

- 每个模块一个 `router.py`
- 使用 `APIRouter` 创建主路由和子路由
- 在 `main.py` 中通过 `include_router()` 注册

## 示例

### 模块路由 `modules/admin/router.py`

```python
from fastapi import APIRouter
from modules.admin.endpoints.sys import user, role, menu, permission, dict, config
from modules.admin.endpoints import auth, mcp

router = APIRouter()

# 认证相关（无需鉴权）
router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 系统管理（需鉴权）
router.include_router(user.router, prefix="/sys/user", tags=["用户管理"])
router.include_router(role.router, prefix="/sys/role", tags=["角色管理"])
router.include_router(menu.router, prefix="/sys/menu", tags=["菜单管理"])
router.include_router(permission.router, prefix="/sys/permission", tags=["权限管理"])
router.include_router(dict.router, prefix="/sys/dict", tags=["字典管理"])
router.include_router(config.router, prefix="/sys/config", tags=["配置管理"])
router.include_router(mcp.router, prefix="/mcp", tags=["MCP工具"])
```

### 应用注册 `main.py`

```python
from modules.admin.router import router as admin_router
from modules.app.router import router as app_router

app.include_router(admin_router, prefix="/admin")
app.include_router(app_router, prefix="/app")
```

## 关键点

- 子路由前缀避免重复，如 `prefix="/sys/user"` 而非在子路由中再加 `/user`
- `tags` 用于 Swagger 文档分组
- 认证路由和业务路由可以有不同的中间件配置
- 新增模块只需创建新的 router.py 并在 main.py 中注册

## 真实参考文件

- `backend/modules/admin/router.py`
- `backend/main.py`
