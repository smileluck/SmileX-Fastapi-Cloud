<!-- last-updated: 2026-06-03 -->
# 字典通用组件

## 需求描述

项目已有完整的字典管理模块（后端 CRUD + 前端管理页面），但其他业务模块消费字典数据时没有可复用的通用组件。需要新增前端通用组件，让任何页面都能一行代码使用字典数据。

## 状态

已完成

## 涉及范围

### 后端

无需改动。使用已有的接口：
- `GET /admin/sys/dict/item/all/{dict_code}` — 按 code 获取启用的字典项
- 新增种子数据迁移：gender 字典（男=1, 女=2, 未知=0）

### 前端

新增 4 个文件：
- `hooks/business/dict.ts` — useDict composable（模块级 Map 缓存）
- `components/custom/dict-select.vue` — DictSelect 下拉选择
- `components/custom/dict-tag.vue` — DictTag 标签展示
- `components/custom/dict-text.vue` — DictText 文本展示

新增演示页面：
- `views/demo/dict/index.vue` — 演示全部三个组件 + 表格中使用
- 路由 `/demo/dict`，i18n 已配置

## 约束与备注

- 组件放在 `components/custom/` 下自动注册，无需手动 import
- useDict 缓存为模块级 Map，同一 code 跨组件共享，不设自动过期
- refresh() 方法可手动清除缓存重新请求
- 后端接口仅返回启用的字典项，前端无需过滤

## 相关文件

- `frontend/src/hooks/business/dict.ts`
- `frontend/src/components/custom/dict-select.vue`
- `frontend/src/components/custom/dict-tag.vue`
- `frontend/src/components/custom/dict-text.vue`
- `frontend/src/views/demo/dict/index.vue`
- `backend/alembic/versions/j3k4l5m6n7o8_seed_gender_dict.py`
- `aiDoc/examples/frontend/dict-component-example.md`

## 记录日期

2026-06-03
