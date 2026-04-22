## Why

当前 `novel_docs/project_plan/` 的主入口混合了路线图、需求拆分与大量前置设计内容，已经开始把项目推进到“先定义完整解法，再寻找需求落点”的错误方向。现在需要先重建文档职责边界，把前期规划收敛为“路线图导航 + 需求卡片”，为后续按需进入 OpenSpec change 建立稳定上游输入。

## What Changes

- 将现有 `novel_docs/project_plan/` 中作为主入口使用的旧规划文档整体退出主路径，并统一归档到独立 archive 位置。
- 重建 `novel_docs/project_plan/00-overview.md`，使其只承担项目目标、phase 路线图、阅读路径与当前不做什么的导航职责。
- 按 `phase-first` 结构重组 `novel_docs/project_plan/phases/`，让每个 phase 仅作为路线图分组，而不是设计容器或执行单元。
- 为每个 phase 建立轻量标准文档集，包括 `00-overview.md`、`requirements.md` 与 `requirements/<slug>.md`。
- 将原先散落在 phase 文档、专题设计文档和架构规划文档中的内容，收敛为“一个需求一张卡片”的边界表达，卡片只描述目标、用户价值、成功标准、范围与非目标。
- 建立“单张需求卡片 -> 未来单个 OpenSpec change”的映射关系，但本次不提前创建任何 change、proposal、design 或 tasks 产物。

## Capabilities

### New Capabilities
- `project-plan-roadmap-reorganization`: 定义 `novel_docs/project_plan/` 作为唯一前期规划入口时，路线图导航、phase 组织与旧资产归档的结构要求。
- `phase-requirement-card-structure`: 定义 phase 内 `requirements.md` 与单需求卡片的固定职责、字段边界及禁止事项。

### Modified Capabilities
- 无

## Impact

- 主要影响 `novel_docs/project_plan/` 下的文档结构、目录命名、入口组织方式与历史规划资产的归档位置。
- 不涉及运行时代码、API、数据模型、数据库结构或外部依赖改动。
- 影响后续规划工作流：未来应从单张需求卡片进入 OpenSpec，而不是在 `project_plan` 阶段提前展开设计与任务拆解。
