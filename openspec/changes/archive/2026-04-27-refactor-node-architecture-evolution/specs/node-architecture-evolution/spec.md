## ADDED Requirements

### Requirement: 定义渐进式 business node 架构

系统 SHALL 在 AI 架构规则中定义 business node 的渐进式架构演进模型：简单 node 可以保持轻量结构；复杂 node MUST 按 `facade + application/use_cases + domain + infrastructure` 的轻量 DDD 结构演进；多个 node 共享稳定领域模型、repository 或领域服务时，系统 MUST 要求评估是否升级为 domain-level bounded context。

#### Scenario: 简单 node 保持轻量结构

- **WHEN** AI 生成或重构的 business node 只包含少量业务行为，且没有明确聚合、状态流转、多 adapter 协作或跨 node 复用压力
- **THEN** AI 规则允许该 node 保持轻量目录结构，而不强制创建完整 DDD 目录

#### Scenario: 复杂 node 升级为轻量 DDD

- **WHEN** business node 出现多个独立业务行为、明确领域模型、聚合边界、状态流转、多 adapter 协作或领域复用压力
- **THEN** AI 规则 MUST 要求评估并优先采用 `facade + application/use_cases + domain + infrastructure` 的复杂 node 结构

#### Scenario: 多 node 共享领域时评估 domain-level

- **WHEN** 同一业务域内多个 node 开始共享稳定领域模型、repository 或领域服务
- **THEN** AI 规则 MUST 要求评估是否将共享领域概念上移到 domain-level bounded context，而不是在多个 node 内重复定义

### Requirement: 演进判断以业务和领域信号为主

系统 SHALL 要求 node 演进判断优先依据业务/领域职责信号，包括业务行为分化、领域模型形成、聚合边界、状态流转、领域资源获取边界、多 adapter 协作和跨 node 复用压力。行数、方法数、类数量等数字阈值 SHALL 仅作为辅助提醒，MUST NOT 作为唯一或主导拆分依据。

#### Scenario: 命中业务行为分化信号

- **WHEN** AI 准备向同一 node 的单一文件继续添加新的独立业务行为
- **THEN** AI 规则 MUST 要求先判断该行为是否应成为独立 use case，而不是继续堆入既有文件

#### Scenario: 数字阈值只能辅助判断

- **WHEN** 某个文件行数、公开方法数或类数量增加
- **THEN** AI 规则 MUST 将其作为架构评估提醒，并继续根据业务/领域职责判断是否演进，而不是按技术或数字阈值机械拆分

#### Scenario: 技术细节不主导 repository 拆分

- **WHEN** repository 实现中包含 ORM record、mapper、事务或查询实现细节
- **THEN** AI 规则 MUST 先保持 repository 抽象按领域资源或聚合定义，MUST NOT 因技术实现细节自动拆成多个 repository 抽象

### Requirement: 复杂 node 职责边界清晰

系统 SHALL 在 AI 规则中定义复杂 node 内各层职责：`facade.py` 是 node 对外稳定入口，负责转发、依赖聚合和横切协调；`application/use_cases/` 按一个业务行为一个 use case 承载应用层编排；`domain/` 承载领域模型、规则、领域服务和 repository 抽象；`infrastructure/` 承载具体适配实现；`node.py` 仅作为 workflow adapter。

#### Scenario: facade 不承载业务规则

- **WHEN** AI 为复杂 node 生成或修改 `facade.py`
- **THEN** `facade.py` MUST 只承担入口、转发、依赖聚合、日志上下文、异常协调、事务或幂等等横切职责，不得承载具体业务规则或完整业务行为实现

#### Scenario: use case 承载业务行为编排

- **WHEN** AI 为复杂 node 新增独立业务行为
- **THEN** AI MUST 在 `application/use_cases/` 中创建或修改对应 use case，并通过领域模型、领域规则、repository 抽象和 port 完成应用层编排

#### Scenario: domain 保持纯业务语义

- **WHEN** AI 在复杂 node 的 `domain/` 中定义模型、规则、领域服务或 repository 抽象
- **THEN** 这些代码 MUST NOT 依赖 `infrastructure/`、`capabilities/`、HTTP、ORM、SDK 或 provider 具体实现

#### Scenario: infrastructure 只做适配

- **WHEN** AI 在复杂 node 的 `infrastructure/` 中实现 repository、AI adapter 或外部系统 adapter
- **THEN** 实现 MUST 只处理持久化、协议映射、prompt/schema、错误转换和 provider 映射等适配职责，不得承载业务决策

### Requirement: OpenSpec 流程必须包含架构设计评估

系统 SHALL 在 AI 规则中要求后续 pre_design、proposal、design 和 tasks 显式考虑架构设计。OpenSpec 产物 MUST 评估需求对顶层边界、business node 内部结构、领域职责拆分、技术适配边界、演进路径和 `ai_docs` 更新的影响。

#### Scenario: pre_design 阶段评估架构影响

- **WHEN** AI 为新需求生成 pre_design
- **THEN** pre_design MUST 根据需求复杂度显式评估架构边界、分层职责、演进路径，以及是否需要更新 AI 规范

#### Scenario: design 阶段承接架构决策

- **WHEN** AI 根据 pre_design 生成 OpenSpec design
- **THEN** design MUST 承接 pre_design 中确认的架构边界、关键决策和演进规则，MUST NOT 只描述功能实现细节

#### Scenario: tasks 阶段包含 AI 规则更新

- **WHEN** 需求影响稳定 AI 架构规则或样例
- **THEN** tasks MUST 包含更新 `ai_docs` 的任务，且不得只生成应用代码任务
