---
name: project-pre-push-checks
description: 推送前的最小可信出口检查——运行文档漂移检测、按影响面跑项目自身验证、确认 aiDoc 与决策记录同步。
whenToUse: 当用户准备 push、合并分支、或要求"提交前检查 / pre-push"时使用。
---

# 推送前检查（pre-push）

推送前执行最小可信的出口检查。目标是拦住"文档漂移、验证缺失、记录不全"三类问题，而不是替代 CI。

## 检查流程

按顺序执行，任一阻断项失败则停止并报告，禁止跳过。

### 1. 确认变更范围

- 确认 git 根、分支、与远端的差异（待推送的 commit 列表）
- 列出本次推送涉及的全部改动文件

### 2. 文档漂移检测（sync）

在项目根目录运行 harness 的漂移检测脚本：

```bash
python3 /Users/smilex/.agents/skills/project-harness/scripts/check_sync.py .
```

> 说明：命令中的工具包路径在 init 时会渲染为本仓库可执行的真实路径；若仍为占位形式，需手动替换为 Project-Harness 的 checkout 位置。该脚本检查 `AGENTS.md` / `aiDoc/` 的索引、路径引用与代码是否漂移。

- 脚本报出的漂移必须修复或在报告中明确说明理由
- 若目标项目尚未生成 aiDoc 体系（脚本提示缺失），跳过本步并在报告中标注 not-run

### 3. 项目自身验证（按影响面选择）

本仓库实际工具链（`frontend/` 用 pnpm；`backend/` 与 `mcp-platform/` 未配置 lint 与测试框架）：

| 检查 | 命令 | 何时必跑 |
|---|---|---|
| 前端类型检查 | `cd frontend && pnpm typecheck` | TS 类型 / 接口 / 前端改动 |
| 前端 Lint / 格式 | `cd frontend && pnpm lint` | 前端代码改动 |
| 前端构建 | `cd frontend && pnpm build:test` | 构建配置 / 依赖 / 生成物改动 |
| 后端机械验证 | 未配置（`backend/` 无 tests 目录，pyproject 无 pytest/ruff） | — |

- 后端改动的证据以接口冒烟（启动服务 + Swagger 实测）与 `aiDoc/frontend-backend/boundary.md` 契约比对为准，报告中如实标注 not-run / unavailable
- 后端新增验证工具时，同步更新本表

- 禁止反射式全量测试；按 `aiDoc/README.md` 路由与根 `AGENTS.md` 操作不变量选择
- 禁止为变绿放宽过滤或阈值

### 4. 记录完整性

对照改动内容确认：

- [ ] 涉及行为/架构/契约/流程/测试策略变更 → `aiDoc/notes/` 已有对应决策记录
- [ ] 多步骤变更 → `aiDoc/plans/active/` 计划已更新到当前状态
- [ ] 新增/删除 aiDoc 子文档 → `aiDoc/README.md` 索引与路由表已同步
- [ ] 用户新提出的业务需求 → `aiDoc/memory/business/` 已记录并更新索引

### 5. 出口报告

```
## Pre-push 检查结果

### 漂移检测
[check_sync.py 结果：passed / failed（附输出）/ not-run（原因）]

### 项目验证
| 命令 | 结果 |
|---|---|
| `...` | passed/failed/skipped/unavailable/not-run |

### 记录完整性
[逐项 passed / failed / 不适用]

### 结论
[可以推送 / 存在阻断项：列出]
```

- push 本身不属于本 skill 的成功标准；push 是否成功以推送后的可观察结果为准
