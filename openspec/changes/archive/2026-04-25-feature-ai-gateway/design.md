## 背景

MVP 创作链路中的大纲生成、章节蓝图和章节生成都需要访问模型能力。AI 网关作为共享前置能力，应为这些业务流程提供统一、可替换、可治理的模型访问入口，而不是让各业务流程分别处理供应商协议、模型选择、凭据、失败语义和响应映射。

当前 change 的上游约束来自 `pre_design.md` 与 `proposal.md`：AI 网关必须保持 capability-neutral，业务层负责把“大纲”“蓝图”“章节”等任务语义映射为中性能力诉求；AI 网关只接收 `capability_profile`、输入内容、输出模式和通用约束，再完成配置解析、provider 选择、协议调用、失败治理和统一响应。

该设计落位在 `app/capabilities/ai_gateway/`。它影响运行时装配和配置读取，但不改变大纲生成、章节蓝图或章节生成的业务需求，也不引入业务 prompt、业务 schema 或业务 workflow 集成。

## 目标 / 非目标

**目标：**

- 建立 `app/capabilities/ai_gateway` 的标准 capability 骨架。
- 提供稳定 facade 与公开 contracts，作为调用方访问模型能力的唯一推荐入口。
- 支持通过中性 `capability_profile` 选择模型能力来源。
- 支持文本生成与中性 JSON / 结构化输出。
- 接入一个 OpenAI-compatible HTTP provider，验证真实外部模型调用链。
- 使用结构化配置文件声明 profile、provider、model、能力标签、上下文限制、成本等级、timeout 和 retry 等配置。
- 使用环境变量承载 API key 等敏感凭据。
- 通过配置读取抽象隔离配置来源，避免后续切换文件、数据库或配置中心时改动核心网关逻辑。
- 提供最小 timeout、少量 retry、稳定错误类型和日志脱敏边界。
- 提供覆盖 contract、配置解析、provider 映射、错误归一化和架构依赖方向的测试策略。

**非目标：**

- 不把大纲、蓝图、章节等业务任务语义写入 AI 网关。
- 不设计或存储业务 prompt 模板。
- 不定义任何大纲、蓝图、章节等业务 schema。
- 不在本 change 内集成业务 workflow 或业务 port。
- 不提供限流、缓存、熔断或高级 fallback 策略。
- 不提供流式输出。
- 不提供配置管理 UI、数据库配置治理、运行时 profile 编辑或配置审计。
- 不把 provider、model、base_url、api_key 暴露给业务核心。
- 不以供应商 SDK 作为首个 provider 接入方式。

## 决策

### 决策 1：采用标准 capability 结构承载 AI 网关

AI 网关应放在 `app/capabilities/ai_gateway/`，采用稳定根包导出、facade 对外入口、contracts 对外契约、service 内部编排、providers 实现外部协议、config 隔离配置读取的结构。

建议结构：

```text
app/capabilities/ai_gateway/
├─ __init__.py
├─ facade.py
├─ service.py
├─ errors.py
├─ contracts/
│  ├─ __init__.py
│  ├─ request.py
│  ├─ response.py
│  └─ models.py
├─ providers/
│  ├─ __init__.py
│  ├─ base.py
│  └─ openai_compatible.py
└─ config/
   ├─ __init__.py
   ├─ models.py
   ├─ repository.py
   └─ file_repository.py
```

选择该结构的原因是它符合仓库既有架构规则：`capabilities/` 承载跨业务复用的中性能力，不依赖 `business/`，并通过 facade 与 contracts 保持对外依赖面稳定。

替代方案是仅实现一个轻量 provider wrapper。该方案实现更快，但会让配置解析、profile、错误归一化和结构化输出能力后补时分散在调用方或业务层，增加返工风险。

### 决策 2：facade 与 contracts 作为稳定公开边界

外部调用方应优先从 capability 根包导入 facade 和公开 contract 类型，而不是直接依赖 `service.py`、`providers/*` 或 `config/*`。

公开 contract 应覆盖以下中性概念：

- `capability_profile`：中性 profile 名称。
- 消息或文本输入：不包含业务任务语义。
- 输出模式：文本或结构化输出。
- 结构化输出约束：通用 JSON/schema/response format 表达。
- 统一响应：文本或结构化结果、使用量摘要、provider-neutral metadata。

选择该边界的原因是后续 provider、配置来源和内部编排都可能演进，而 facade 与 contracts 应尽量保持稳定。

替代方案是让业务代码直接依赖 provider 或配置模型。该方案短期简单，但会泄露 provider/model 细节并破坏 AI 网关作为统一能力入口的价值。

### 决策 3：使用 `capability_profile`，不让调用方指定 provider/model

调用方只传中性 `capability_profile`。AI 网关通过配置 repository 将 profile 解析为 provider、model、能力标签、上下文限制、成本等级、timeout 和 retry 等配置。

profile 名称必须表达中性能力诉求，例如 `balanced_text`、`long_context_json`。不得使用 `outline_generation_model`、`chapter_writer` 等业务语义名称。

选择该方案的原因是业务任务与模型来源需要解耦。业务层可以决定当前任务需要哪类中性能力，但不应该把具体 provider/model 固化进业务核心。

替代方案是调用方直接指定 provider/model。该方案简单直接，但会让业务层绑定模型实现，后续替换供应商或模型时需要修改业务代码。

### 决策 4：结构化配置文件 + 环境变量密钥 + 配置 repository 抽象

AI 网关配置分为两类：

- 非敏感结构化配置：profiles、providers、models、能力标签、上下文限制、成本等级、timeout、retry。
- 敏感凭据：API key 等，通过环境变量提供。

配置文件可以保存环境变量引用，例如 provider 配置中的 `api_key_env`。`file_repository.py` 负责读取配置文件、解析环境变量引用并校验必要字段。`service.py` 只依赖 `config/repository.py` 中定义的抽象接口，不读取文件或环境变量。

选择该方案的原因是 profile/provider 映射需要结构化表达，密钥又不能进入配置文件；同时 repository 抽象能避免后续切换到数据库、配置中心或其他配置来源时改动 facade/service 主逻辑。

替代方案包括纯环境变量和数据库配置治理。纯环境变量适合极小配置，但难以维护多 profile 映射；数据库治理扩展性更强，但会引入运行时管理、权限、审计、缓存刷新和一致性问题，不适合 MVP。

### 决策 5：首个 provider 使用 OpenAI-compatible HTTP

首个真实外部调用路径使用 OpenAI-compatible HTTP provider。provider 内部负责将 AI 网关中性 request 映射为外部 HTTP 请求，并将响应映射回统一 response。

OpenAI-compatible provider 可以处理协议字段、HTTP 状态、provider 错误体、timeout、retry 和响应结构异常，但这些细节不得泄露到公开 contract。

选择该方案的原因是 OpenAI-compatible HTTP 兼容多个供应商和代理服务，不需要把首个实现绑定到单一供应商 SDK。它能验证真实调用链，同时保持 provider-neutral contract。

替代方案是供应商 SDK。SDK 接入可能更贴近某个供应商能力，但更容易把供应商类型、错误模型和参数命名带入核心契约，增加后续替换成本。

### 决策 6：结构化输出保持中性，不承载业务 schema

AI 网关支持结构化输出，但只表达通用 JSON/schema 或 response format 能力。调用方可以传入中性结构化约束；AI 网关负责协议映射和最小解析失败转换，但不理解 schema 的业务含义。

选择该方案的原因是大纲、蓝图和章节等业务可能都需要结构化结果，但各自 schema 应由业务 change 定义。AI 网关只提供“请求并返回结构化输出”的通用能力。

替代方案是在 AI 网关内预置大纲/蓝图/章节 schema。该方案看似便捷，但会把业务语义下沉到 `capabilities/`，违反架构边界。

### 决策 7：纳入最小失败治理，不做完整韧性平台

MVP 应支持：

- provider 调用 timeout。
- 少量 retry，主要覆盖短暂网络失败或可恢复外部错误。
- 稳定错误类型，例如配置错误、provider 调用错误、timeout 错误、provider 响应映射错误、结构化输出错误。
- 关键节点日志，但不得记录 API key、完整 prompt、完整响应或其他敏感内容。

选择该方案的原因是外部模型调用失败是常态，如果不在 AI 网关统一处理，业务方会重复处理 provider 差异。

替代方案是把 timeout/retry/error 都推迟。该方案初始实现更小，但会让业务调用方过早承担 provider 失败细节。另一个替代方案是同时实现限流、缓存、熔断和 fallback，但这会显著扩大 scope，应作为后续独立 change。

## 关键流程

### 文本生成流程

1. 业务层根据自身任务语义选择中性 `capability_profile`。
2. 调用 AI 网关 facade，传入 profile、输入消息或文本，并声明输出模式为文本。
3. service 通过 config repository 查询 profile 配置。
4. profile 解析为 provider、model、上下文限制、成本等级、timeout 和 retry 等信息。
5. service 根据 provider 名称选择 provider abstraction 的具体实现。
6. OpenAI-compatible provider 将中性请求映射为 HTTP 请求。
7. provider 执行外部调用、timeout、少量 retry 和响应解析。
8. facade 返回统一文本响应、使用量摘要和 provider-neutral metadata。

### 结构化输出流程

1. 调用方选择中性 `capability_profile`，并声明输出模式为结构化输出。
2. 请求携带通用结构化约束，例如 JSON schema 或 provider-neutral response format。
3. service 保持约束的中性表达，并交给 provider 做协议映射。
4. provider 请求模型返回结构化结果。
5. AI 网关执行最小结果解析与错误转换。
6. facade 返回统一 structured response，不解释业务 schema 的语义。

### 配置加载流程

1. file repository 读取结构化配置文件。
2. 配置文件声明 profiles、providers、models 和能力标签。
3. 配置中的密钥字段使用环境变量引用，而不是明文密钥。
4. repository 解析环境变量并校验必要字段。
5. service 只通过 repository 查询 profile/provider，不读取文件或环境变量。

### 错误转换流程

- profile 不存在：转换为稳定配置错误。
- profile 指向未知 provider：转换为稳定配置错误。
- provider 配置缺少 base_url、model 或密钥引用：转换为稳定配置错误。
- provider 网络失败或超时：按最小 retry 策略处理；最终失败时转换为稳定 provider 调用错误或 timeout 错误。
- provider 返回非预期结构：转换为稳定 provider response error。
- 结构化输出解析失败：转换为稳定 structured output error，不归咎于具体业务 schema。

## 风险 / 权衡

- [风险] capability contract 过早绑定 OpenAI-compatible 协议字段 → [缓解] 公开 contract 只使用中性字段，协议字段只存在于 `providers/openai_compatible.py` 内部映射中。
- [风险] profile 命名滑向业务任务语义 → [缓解] 在 spec 和测试中明确 profile 名称必须表达中性能力诉求，不得使用大纲、蓝图、章节等业务名称。
- [风险] 配置文件格式后续需要调整 → [缓解] service 只依赖配置 repository 抽象，文件格式变化限制在 file repository 和 config models 内。
- [风险] 结构化输出被误认为业务 schema 托管能力 → [缓解] 明确 AI 网关只处理通用 JSON/schema 约束与解析错误，不定义或解释业务 schema。
- [风险] retry 导致外部调用成本或延迟增加 → [缓解] MVP 只做少量可配置 retry，并让 profile/provider 配置承载 timeout 和 retry 上限。
- [风险] 日志泄露敏感 prompt、响应或凭据 → [缓解] 日志只记录 profile、provider 名称、动作、结果摘要、耗时和错误分类，不记录 API key、完整请求体或完整模型输出。
- [风险] 首个 provider 不覆盖所有供应商差异 → [缓解] MVP 只承诺 OpenAI-compatible HTTP 路径；多 provider、高级 fallback 和供应商特性作为后续独立 change。

## 迁移计划

本 change 是新增 capability，不需要数据迁移，也不改变现有业务流程契约。

实施顺序应为：

1. 新增 AI 网关 capability 目录、公开 contracts 和错误类型。
2. 定义配置模型与 repository 抽象。
3. 实现结构化配置文件读取和环境变量密钥解析。
4. 定义 provider abstraction。
5. 实现 OpenAI-compatible HTTP provider。
6. 实现 service 与 facade。
7. 在 bootstrap 中完成最小运行时装配和配置接线。
8. 补充单元、集成和架构边界测试。

回退策略是移除或停止装配该新增 capability。由于本 change 不修改现有业务流程，回退不应影响当前已存在的业务入口。

## 测试策略

- contract 单元测试：验证请求、响应、输出模式、profile、结构化约束和使用量摘要等公开模型行为。
- 配置解析测试：验证结构化配置文件读取、环境变量密钥解析、缺失字段、未知 provider、未知 profile 等失败路径。
- service 单元测试：使用 fake repository 和 fake provider 验证 profile 解析、provider 选择、文本生成、结构化输出和错误转换。
- provider 集成测试：使用本地 HTTP mock 或等价测试边界验证 OpenAI-compatible 请求映射、响应映射、HTTP 错误、timeout 和 retry。
- 架构测试：验证 `capabilities/ai_gateway` 不依赖 `business/`，业务核心不直接依赖 provider 内部文件，公开导入面优先来自 capability 根包/facade。
- 日志与敏感信息测试：至少覆盖 API key 不进入异常消息或日志上下文的关键路径。

## 开放问题

- 结构化配置文件的具体路径和文件格式需要在实现阶段结合现有配置加载方式确定，但不得改变“配置文件 + 环境变量密钥 + repository 抽象”的决策。
- HTTP client 采用仓库已有封装还是补充最小封装，需要在实现阶段根据现有依赖确认；无论选择哪种方式，都不得引入供应商 SDK 作为主路径。
- 默认 profile 名称和示例配置需要保持中性，后续业务 change 可以选择使用哪些 profile，但不能要求 AI 网关理解业务任务语义。
