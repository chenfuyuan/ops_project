## ADDED Requirements

### Requirement: 创建结构化种子

系统 SHALL 接受用户提交的结构化种子输入，包含以下必填字段：小说暂定标题、题材、主角设定、核心冲突、大致走向。可选字段：补充说明。系统 SHALL 持久化种子并返回种子标识。

#### Scenario: 提交完整种子

- **WHEN** 用户提交包含所有必填字段的结构化种子
- **THEN** 系统持久化种子并返回种子 ID 及完整种子内容

#### Scenario: 缺少必填字段

- **WHEN** 用户提交的种子缺少任一必填字段
- **THEN** 系统拒绝请求并返回具体缺失字段的错误信息

#### Scenario: 获取已有种子

- **WHEN** 用户通过种子 ID 查询
- **THEN** 系统返回该种子的完整内容

### Requirement: 生成骨架

系统 SHALL 基于已创建的结构化种子，通过 AI 网关 STRUCTURED 模式生成粗粒度骨架。骨架包含 3-5 个卷/幕，每个卷包含标题和核心转折描述。生成的骨架状态为 DRAFT。

#### Scenario: 成功生成骨架

- **WHEN** 用户对一个已存在的种子请求生成骨架
- **THEN** 系统通过 AI 网关 STRUCTURED 模式生成骨架，返回包含多个卷的骨架结构，骨架状态为 DRAFT

#### Scenario: 种子不存在

- **WHEN** 用户对一个不存在的种子 ID 请求生成骨架
- **THEN** 系统返回种子未找到的错误

#### Scenario: 种子已有骨架

- **WHEN** 用户对一个已有骨架的种子请求重新生成
- **THEN** 系统覆盖旧骨架及其关联的卷和章节摘要，生成新的骨架

### Requirement: 编辑骨架卷

系统 SHALL 允许用户编辑骨架卷的标题和核心转折描述。编辑卷后，该卷下已展开的章节摘要 SHALL 被标记为过期（`is_stale = True`）。

#### Scenario: 编辑卷标题

- **WHEN** 用户修改某个骨架卷的标题
- **THEN** 系统更新该卷标题，并将该卷下所有已展开的章节摘要标记为过期

#### Scenario: 编辑卷转折描述

- **WHEN** 用户修改某个骨架卷的核心转折描述
- **THEN** 系统更新该卷转折描述，并将该卷下所有已展开的章节摘要标记为过期

#### Scenario: 卷无已展开章节

- **WHEN** 用户编辑一个尚未展开章节的卷
- **THEN** 系统正常更新卷内容，无需标记过期

### Requirement: 确认骨架

系统 SHALL 允许用户确认骨架，将骨架状态从 DRAFT 变更为 CONFIRMED。骨架 MUST 处于 DRAFT 状态才能被确认。

#### Scenario: 确认 DRAFT 状态的骨架

- **WHEN** 用户对一个 DRAFT 状态的骨架执行确认操作
- **THEN** 骨架状态变更为 CONFIRMED，记录确认时间

#### Scenario: 确认已 CONFIRMED 的骨架

- **WHEN** 用户对一个已 CONFIRMED 的骨架执行确认操作
- **THEN** 系统返回骨架已确认的提示，不做重复操作

### Requirement: 展开卷章节

系统 SHALL 在骨架已确认后，允许用户逐卷展开为章节摘要。展开通过 AI 网关 STRUCTURED 模式完成，每次展开一个卷，生成该卷下的全部章节摘要（标题 + 摘要文本）。骨架 MUST 处于 CONFIRMED 状态才能触发展开。

#### Scenario: 展开已确认骨架的某一卷

- **WHEN** 用户对已确认骨架中的某一卷请求展开
- **THEN** 系统通过 AI 网关 STRUCTURED 模式生成该卷下的章节摘要列表，每条包含章节标题和摘要

#### Scenario: 骨架未确认时请求展开

- **WHEN** 用户对 DRAFT 状态的骨架请求展开某卷
- **THEN** 系统拒绝并返回"骨架未确认，不可展开"的错误

#### Scenario: 重新展开已有章节的卷

- **WHEN** 用户对已有章节摘要（包括过期的）的卷请求重新展开
- **THEN** 系统覆盖该卷下旧的章节摘要，生成新的章节摘要

### Requirement: 编辑章节摘要

系统 SHALL 允许用户编辑章节摘要的标题和摘要文本，直接更新对应记录。

#### Scenario: 编辑章节标题

- **WHEN** 用户修改某章的标题
- **THEN** 系统更新该章标题

#### Scenario: 编辑章节摘要文本

- **WHEN** 用户修改某章的摘要
- **THEN** 系统更新该章摘要文本

### Requirement: 获取完整大纲

系统 SHALL 提供按种子 ID 获取完整大纲的能力，返回种子、骨架（含全部卷）、以及已展开的全部章节摘要的聚合视图。大纲在骨架确认且所有卷均已展开后状态为 COMPLETE。

#### Scenario: 获取完整已展开大纲

- **WHEN** 用户请求获取某种子的完整大纲，且该种子的骨架已确认、所有卷已展开
- **THEN** 系统返回包含种子信息、骨架结构、全部卷及各卷下章节摘要的聚合大纲，状态为 COMPLETE

#### Scenario: 获取部分展开的大纲

- **WHEN** 用户请求获取某种子的完整大纲，但仅部分卷已展开
- **THEN** 系统返回当前已有内容的聚合大纲，状态为 IN_PROGRESS，已展开的卷包含章节，未展开的卷章节列表为空

#### Scenario: 种子无骨架时获取大纲

- **WHEN** 用户请求获取某种子的大纲，但尚未生成骨架
- **THEN** 系统返回大纲未找到的错误

### Requirement: AI 生成通过 port 抽象

大纲生成的 AI 调用 MUST 通过 `OutlineAiPort` 抽象进行，business 层 SHALL NOT 直接依赖 `AiGatewayFacade` 或任何 capability 模块。`OutlineAiPort` 的实现 adapter 在 infrastructure 层桥接 AI 网关。

#### Scenario: business 层调用 AI 生成

- **WHEN** `OutlineNodeService` 需要调用 AI 生成骨架或展开章节
- **THEN** 通过 `OutlineAiPort` 接口调用，不直接 import 或引用 `app.capabilities` 下的任何模块

### Requirement: 结构化输出格式

所有 AI 生成 MUST 使用 AI 网关的 STRUCTURED 输出模式，通过 JSON Schema 约束输出结构。返回的 `structured_content` MUST 可直接映射为领域模型实例。

#### Scenario: 骨架生成使用 STRUCTURED 模式

- **WHEN** 系统通过 AI 网关生成骨架
- **THEN** 请求使用 `OutputMode.STRUCTURED`，附带骨架结构的 JSON Schema 约束

#### Scenario: 章节展开使用 STRUCTURED 模式

- **WHEN** 系统通过 AI 网关展开某卷章节
- **THEN** 请求使用 `OutputMode.STRUCTURED`，附带章节摘要列表的 JSON Schema 约束

## ADDED Requirements

### Requirement: 大纲生成节点采用复杂 node 架构

大纲生成节点作为首个明确命中复杂度信号的 business node，MUST 采用 `facade + application/use_cases + domain + infrastructure` 的轻量 DDD node 结构进行内部架构重构。该重构 MUST NOT 改变现有 HTTP API、AI gateway 能力契约、数据库业务数据模型或大纲生成业务行为。

#### Scenario: HTTP 入口调用 outline facade

- **WHEN** HTTP outline 接口需要调用大纲生成业务能力
- **THEN** 接口层 SHALL 依赖 outline node 的 `facade.py` 对外入口，而不是直接依赖旧的单一 `service.py`

#### Scenario: outline 业务行为拆分为 use cases

- **WHEN** 大纲生成节点处理创建种子、获取种子、生成骨架、确认骨架、展开卷、编辑卷、编辑章节或获取完整大纲
- **THEN** 每个独立业务行为 SHALL 由 `application/use_cases/` 下对应 use case 承载应用层编排

#### Scenario: outline 领域概念迁移到 domain

- **WHEN** 大纲生成节点表达 `Seed`、`Skeleton`、`SkeletonVolume`、`ChapterSummary`、`Outline`、状态枚举、领域规则或 repository 抽象
- **THEN** 这些领域概念 SHALL 位于 `domain/` 边界内，并保持不依赖 HTTP、ORM、AI gateway capability 或 provider 实现

#### Scenario: outline infrastructure 保持适配职责

- **WHEN** 大纲生成节点访问持久化或 AI gateway
- **THEN** 具体 SQLAlchemy repository 实现和 AI gateway adapter SHALL 位于 `infrastructure/` 下，并通过 domain/application 层定义的抽象被调用

### Requirement: 大纲生成 AI 业务语义保持在 business 层

大纲生成相关 AI prompt、结构化 schema、响应映射和 profile 使用策略 SHALL 保持在 business outline node 的 infrastructure AI adapter 边界内，MUST NOT 下沉到 `capabilities/ai_gateway` 形成业务语义耦合。

#### Scenario: 生成骨架时翻译业务语义

- **WHEN** outline use case 需要生成 skeleton
- **THEN** business outline node 的 AI adapter SHALL 将领域模型翻译为 AI gateway 的中性 STRUCTURED 请求，`capabilities/ai_gateway` 不应出现大纲业务语义

#### Scenario: 展开卷章节时映射结构化响应

- **WHEN** outline AI adapter 收到 AI gateway 的结构化章节展开响应
- **THEN** adapter SHALL 将响应映射回 outline 领域模型或应用层结果，且不得让 provider 特有字段泄漏到 domain 或 use case
