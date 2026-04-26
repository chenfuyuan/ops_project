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
