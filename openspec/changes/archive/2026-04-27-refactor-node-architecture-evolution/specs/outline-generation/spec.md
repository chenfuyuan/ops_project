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
