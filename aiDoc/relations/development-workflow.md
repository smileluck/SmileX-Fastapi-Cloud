<!-- last-updated: 2026-06-03 -->
# 开发流程

## 推荐开发顺序

1. **需求分析**：明确功能范围和接口契约
2. **模型设计**：在 `database/models/` 定义 ORM 模型
3. **Schema 定义**：在 `modules/<name>/schemas/` 定义请求/响应 Schema
4. **Service 实现**：在 `modules/<name>/services/` 实现业务逻辑
5. **Endpoint 实现**：在 `modules/<name>/endpoints/` 创建 API 端点，在 `router.py` 注册路由
6. **数据库迁移**：`uv run alembic revision --autogenerate -m "描述"` → `uv run alembic upgrade head`
7. **前端实现**：定义类型 → API 函数 → 页面组件
8. **集成测试**：前后端联调验证

## 前后端协作

- 后端先提供稳定的接口设计和 Swagger 文档
- 前端可并行开发，使用 Swagger UI 或 Mock 数据
- 接口变更必须同步更新 Swagger 注释
- 联调时使用真实后端接口验证

## 分支策略

- `main`: 生产分支，保持稳定可发布状态
- `develop`: 开发分支，日常开发合并目标
- `feature/*`: 功能分支，从 `develop` 创建，完成后合回
- `hotfix/*`: 紧急修复分支，从 `main` 创建，修复后合回 `main` 和 `develop`

## 提交规范

### 格式

```
type(scope): description
```

### 类型

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复缺陷 |
| `docs` | 文档变更 |
| `style` | 代码格式（不影响逻辑） |
| `refactor` | 重构（既不是新功能也不是修复） |
| `test` | 测试相关 |
| `chore` | 构建或辅助工具变更 |

### 前端提交流程

1. 确保 `pnpm typecheck` 通过
2. 确保 `pnpm lint` 通过
3. 使用 `pnpm commit:zh` 交互式提交，或手动按规范格式编写

### 后端提交流程

1. 确保代码无语法错误
2. 确保数据库迁移文件正确生成（如有模型变更）
3. 手动按规范格式编写提交信息

## 环境与依赖

### 后端

```bash
# 激活虚拟环境（Windows）
.\venv\Scripts\activate.bat

# 安装依赖
uv install

# 启动开发服务器
uvicorn main:app --reload
# 或
python main.py
```

### 前端

```bash
# 安装依赖
pnpm install

# 开发模式（测试环境）
pnpm dev

# 开发模式（生产环境）
pnpm dev:prod

# 构建生产版本
pnpm build

# 类型检查
pnpm typecheck

# 代码检查与修复
pnpm lint

# 生成路由
pnpm gen-route
```

### API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 数据库迁移

```bash
# 创建迁移
uv run alembic revision --autogenerate -m "描述信息"

# 应用迁移
uv run alembic upgrade head

# 回退迁移
uv run alembic downgrade -1
```
