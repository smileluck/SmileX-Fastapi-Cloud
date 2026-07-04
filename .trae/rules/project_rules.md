---
tool: trae
role: compatibility-adapter
canonical_source: /AGENTS.MD
structured_context: /aiDoc
---

# Trae 规则适配层

本文件只用于兼容 Trae 现有的自动加载路径。

## 真实规则入口

请按下面顺序读取：

1. `/AGENTS.MD`
2. `/aiDoc/README.md`：查"任务→必读文档"路由表，确定本次任务必读哪些子文档
3. 路由表指向的 `/aiDoc/` 子文档

## 适配层约束

- 不要在这里扩写项目级规则
- 项目级规则变更时，先更新 `/AGENTS.MD` 与 `/aiDoc/`
- 工具目录只保留薄适配层职责，不再保存独立 project rule 副本
