## ADDED Requirements

### Requirement: phase 必须提供轻量标准文档集
每个 `phases/<phase>/` 目录必须只包含轻量标准文档集：`00-overview.md`、`requirements.md` 与 `requirements/<slug>.md`，用于表达 phase 目标、需求索引和单需求边界，而不得在 phase 范围内提前承载设计方案。

#### Scenario: phase 文档集结构固定
- **WHEN** 新建或重组任一 phase 目录
- **THEN** 该目录必须围绕 phase 概览、需求索引和单需求卡片组织，而不能继续平铺架构设计、数据模型或任务拆解文档

### Requirement: 单需求卡片必须定义清晰边界且禁止提前设计
每张 `requirements/<slug>.md` 卡片必须至少表达 Title、Goal、User Value、Success Criteria、Scope、Non-goals、Dependencies / Prerequisites 与 Notes，用于清晰界定需求边界，并且不得包含接口方案、数据模型、模块拆分、实现步骤或详细技术选型。

#### Scenario: 需求卡片可作为未来 change 的上游输入
- **WHEN** 团队准备从某张需求卡片启动后续实施
- **THEN** 卡片内容必须足以帮助判断是否值得做、要做什么和不做什么，并可自然映射为未来单个 OpenSpec change 的上游输入

#### Scenario: 需求卡片不提前展开设计
- **WHEN** 团队审阅某张需求卡片
- **THEN** 文档必须停留在目标、价值、边界和成功标准层面，而不能包含接口定义、数据结构设计或实现任务拆解

### Requirement: requirements.md 必须作为 phase 内需求索引
每个 phase 的 `requirements.md` 必须提供 phase 内需求索引与状态视图，至少能表达 Requirement、Summary、Status、Priority、Dependencies 与 Card，帮助维护需求顺序与关系，而不能替代单需求卡片或演变为任务清单。

#### Scenario: phase 需求索引聚焦索引和关系
- **WHEN** 读者查看某个 phase 的 `requirements.md`
- **THEN** 文档必须展示需求列表、优先级和依赖关系，并将细节边界指向对应卡片，而不是直接展开实现步骤
