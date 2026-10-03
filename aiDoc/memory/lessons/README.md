<!-- last-updated: 2026-10-02 -->
# 经验记忆（lessons）

存放开发过程中踩过的坑与反复出现的模式。本目录是**经验 staging 区**：经验在此低成本采集，达到晋升条件后写进约束正文（`/AGENTS.md`、`modules/backend-layer-rules.md`、`frontend-backend/boundary.md` 等），本目录只留记录与去向链接。

## 规则

- 工作中踩坑、review 反复发现同类问题、或发现可复用模式时，必须在同一变更内记一条 lesson
- 已有同类 lesson 时**就地累加出现次数**，不重复建档
- 使用 [TEMPLATE.md](TEMPLATE.md) 作为新记录模板（保持轻量，5 行成本）；头部 `lesson-meta` 标记必须与人读小节保持同步
- 记录或累加后在 [../project-memory.md](../project-memory.md) 中更新索引
- 命名约定：`yyyy-mm-dd-主题.md`

## 晋升纪律

- 触发：同一 lesson 第 2 次出现，或用户显式确认——**一次是经历，两次是模式**
- 动作：在同一变更内把规则写进约束正文所在文档，本记录状态改 `promoted` 并填晋升去向链接，同步头部 `lesson-meta` 标记的 `status`/`target`
- 暂缓：`pending` 且次数 ≥2 但确认暂不晋升时，标记改 `deferred` 并在「晋升去向」写暂缓理由；sync 工作流复核理由是否仍成立
- 晋升涉及行为/架构/契约变化时，仍须按 `aiDoc/notes/README.md` 写决策记录
- 确认无通用价值的条目标 `dropped`，必须写理由
- 禁止只攒经验不晋升；`check_sync.py` 检查 5 对未处理的 `pending` 且次数 ≥2 条目直接报失败

## 晋升后复发

- `promoted` 后同类问题再犯，说明已晋升规则无效（写错文档、措辞不约束、粒度不对）：`lesson-meta` 的 `post` +1，同一变更内**修订已晋升的规则正文**（不再记新 lesson），并按 `aiDoc/notes/README.md` 记录第一次为什么没拦住
- `check_sync.py` 检查 6 会把 `post≥1` 的条目列为提示

## 机械扫描

`check_sync.py` 只按头部 `lesson-meta` 标记机械判定（不解析标题文本），递归扫描子目录：

- `pending` 且 `count≥2` 未晋升也未显式 `deferred` → ❌ 失败
- `promoted` 但 `target` 为空 → ❌ 失败
- 缺 `lesson-meta` 标记、`post≥1`、或 `post` 非数字 → ⚠️ 提示级列出，不拦截
