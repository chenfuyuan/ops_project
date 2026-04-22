## ADDED Requirements

### Requirement: project_plan 必须作为唯一前期规划入口
系统必须将 `novel_docs/project_plan/` 定义为当前唯一的前期规划主入口，并要求旧规划资产整体退出主路径，只作为独立 archive 中的历史参考存在。

#### Scenario: 旧规划资产归档后建立唯一入口
- **WHEN** 团队查看 `novel_docs/project_plan/` 的当前结构
- **THEN** 只能看到新的路线图与需求卡片结构，而不会看到仍作为主入口使用的旧规划文档

### Requirement: 顶层结构必须采用 phase-first 路线图组织
系统必须使用 phase-first 结构组织 `novel_docs/project_plan/`，其中顶层 overview 负责项目目标、路线图与阅读路径导航，phase 目录负责阶段分组，而不是承载实现设计。

#### Scenario: 顶层 overview 仅承担导航职责
- **WHEN** 读者打开 `novel_docs/project_plan/00-overview.md`
- **THEN** 文档必须聚焦项目目标、phase 路线图、阅读路径与当前不做什么，而不能扩展为架构、数据模型或模块设计总纲

#### Scenario: phase 仅作为路线图分组
- **WHEN** 读者浏览 `novel_docs/project_plan/phases/` 下的 phase 目录
- **THEN** 每个 phase 必须被表达为路线图阶段分组，而不是执行单元或设计容器
