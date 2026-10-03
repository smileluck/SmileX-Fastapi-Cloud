<!-- last-updated: 2026-06-03 -->
# 示例层

`aiDoc/examples/` 是讲解型示例层，告诉 AI 每一层应该按什么标准组织和书写。

## 用途

- 示例不是要求逐字复制，而是展示项目标准的代码组织方式
- 当 AI 需要新增某一层文件时，应先阅读对应示例，再开始实现
- 优先参考仓库中的真实文件，示例作为补充参考

## 后端开发阅读顺序

1. `backend/model-example.md` — 如何定义 ORM 模型
2. `backend/schema-example.md` — 如何定义 Pydantic Schema
3. `backend/service-example.md` — 如何实现 Service 层
4. `backend/endpoint-example.md` — 如何实现 Endpoint 层
5. `backend/router-example.md` — 如何注册路由

## 前端开发阅读顺序

1. `frontend/api-example.md` — 如何封装 API 调用
2. `frontend/view-example.md` — 如何组织页面组件
3. `frontend/utils-usage-example.md` — 如何使用工具函数
4. `frontend/dict-component-example.md` — 如何使用字典通用组件（DictSelect / DictTag / DictText）

## 原则

- 如果仓库中真实代码与示例不一致，以真实代码为准，并更新示例
- 新增模块时，先参考 `aiDoc/modules/module-development.md` 的步骤，再按示例格式实现
