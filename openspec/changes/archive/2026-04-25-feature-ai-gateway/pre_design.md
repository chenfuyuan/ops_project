# Pre-design: AI Gateway

## 1. Problem framing

MVP 创作链路中的大纲生成、章节蓝图和章节生成都需要访问模型能力。如果每个业务流程直接选择供应商、模型、凭据、调用协议和错误处理方式，后续切换模型来源、统一治理成本与上下文能力、以及维护失败语义都会变得分散且高返工。

AI 网关要解决的问题不是“某个创作任务应该如何提示模型”，而是为所有创作任务提供一个稳定、统一、可替换的模型能力入口。业务层负责把自身任务语义映射为中性的模型能力诉求；AI 网关只接收中性 profile、输入内容、输出模式和通用约束，然后完成配置解析、provider 选择、协议调用、失败治理和统一响应。

本 change 是后续大纲生成、章节蓝图、章节生成等能力的共享前置能力。它应先把 capability 边界、配置抽象和首个外部 provider 路径建立起来，避免后续业务 change 重复定义模型访问方式。

## 2. Goals

- 在 `app/capabilities/ai_gateway` 下提供中性的 AI capability。
- 对外暴露稳定 facade 和 contracts，使调用方通过统一入口请求模型能力。
- 支持调用方通过中性 `capability_profile` 选择模型能力来源。
- 支持文本生成与中性 JSON / 结构化输出能力。
- 接入一个 OpenAI-compatible HTTP provider，作为 MVP 的首个真实外部模型调用路径。
- 使用结构化配置文件声明 profile、provider、model、能力标签、上下文限制和成本等级等映射。
- 使用环境变量承载 API key 等敏感凭据，避免密钥进入配置文件。
- 定义配置读取抽象，使后续从文件切换到数据库、远程配置中心或其他配置来源时，不需要改动 facade、service 或 provider 选择核心逻辑。
- 提供最小 timeout、少量 retry 和稳定错误归一化。
- 为后续 OpenSpec 文档生成提供明确边界，防止 AI 网关吸收业务语义。

## 3. Non-goals

- 不把“大纲生成”“章节蓝图”“章节生成”等业务任务语义写入 AI 网关。
- 不设计或保存业务 prompt 模板。
- 不定义大纲、蓝图、章节等业务 schema。
- 不在本 change 内完成大纲、蓝图或章节业务流程集成。
- 不做限流、缓存、熔断策略设计或实现。
- 不做配置管理 UI、数据库配置治理、运行时 profile 编辑或配置审计。
- 不引入供应商 SDK 作为首个接入方式。
- 不把 provider、model、base_url、api_key 等实现细节暴露给业务核心。
- 不提供流式输出能力；如后续需要，应作为独立扩展评估。

## 4. Requirement understanding

AI 网关应被视为跨业务复用的中性能力，而不是创作业务的一部分。大纲生成、蓝图生成和章节生成会基于自身语义决定需要什么模型能力，例如长上下文、低成本、结构化 JSON 输出或更高质量文本生成。但这些业务语义到能力诉求的映射必须发生在业务层或业务定义的 port 适配层，而不是进入 AI 网关内部。

调用 AI 网关时，调用方应提供中性 `capability_profile`，例如 `long_context_json`、`balanced_text` 这类描述能力诉求的名称。AI 网关通过配置 repository 解析 profile，得到 provider、model、能力标签、上下文限制、成本等级、timeout 和 retry 等配置，再选择对应 provider 完成调用。

结构化输出能力只表示“请求模型返回符合通用 JSON / schema 约束的结果”。AI 网关可以承载通用 JSON schema 或 response format 之类的 provider-neutral contract，但不应该知道该 schema 是用于大纲、章节蓝图还是章节正文。

MVP 既要避免只做空骨架导致后续无法验证真实调用链，也要避免直接把系统做成完整配置治理平台。因此，本 change 采用能力骨架优先，同时接入一个 OpenAI-compatible HTTP provider，并把配置来源通过抽象隔离。

## 5. Constraints and invariants

### Hard constraints

- AI 网关代码落位在 `capabilities/`，不得依赖 `business/`。
- 对外调用面应通过 capability 根包和 facade 暴露；调用方不应依赖 provider 内部文件。
- `service.py` 不能直接依赖具体 provider 实现选择细节；实现选择应通过配置、registry 或组合边界处理。
- provider/model/base_url/api_key 等外部实现细节不得泄露到业务核心。
- API key 等敏感信息只能通过环境变量或等价安全配置来源注入，不得写入结构化配置文件。
- 配置读取必须经过抽象接口；核心网关逻辑不关心配置来自文件、数据库还是配置中心。
- timeout、retry 和 provider 协议错误应转换为 AI 网关稳定错误类型。
- 日志不得记录 API key、完整请求体、完整模型输出或其他敏感内容。

### Invariants for later artifacts

- AI 网关不承担任务语义到模型诉求的映射。
- AI 网关不选择“哪个业务任务应该用哪个模型”；它只根据 profile 解析到具体 provider/model。
- 后续新增 provider、配置来源或 profile 存储方式，不应改变 facade 的主要调用契约。
- 后续 OpenSpec 文档不得把限流、缓存、熔断、运行时配置管理或业务流程集成扩进本 change。
- profile 名称必须保持中性，避免 `outline_generation_model`、`chapter_writer` 等业务语义命名。

## 6. Recommended architecture direction

推荐采用标准 capability 骨架，并在 AI 网关内部拆出 contracts、service、provider abstraction 和 config repository。

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

### Component responsibilities

- `__init__.py`：导出稳定对外入口和公开 contract 类型。
- `facade.py`：AI 网关对外访问入口，屏蔽 service、config 和 provider 细节。
- `contracts/request.py`：定义文本生成和结构化输出的中性请求类型。
- `contracts/response.py`：定义统一响应、使用量摘要和 provider-neutral metadata。
- `contracts/models.py`：定义 `CapabilityProfileName`、输出模式、消息、结构化输出约束、能力标签等共享公开模型。
- `service.py`：根据请求 profile 读取配置、选择 provider、调用 provider 并归一化响应。
- `errors.py`：定义配置错误、provider 调用错误、超时错误、响应映射错误、结构化输出错误等稳定错误类型。
- `providers/base.py`：定义 provider 抽象接口，使 service 不依赖具体 OpenAI-compatible 实现。
- `providers/openai_compatible.py`：实现 OpenAI-compatible HTTP 协议映射、timeout、retry 和错误翻译。
- `config/models.py`：定义 profile/provider 配置模型，不包含业务语义。
- `config/repository.py`：定义配置读取抽象，例如按 profile 名称读取 profile、按 provider 名称读取 provider 配置。
- `config/file_repository.py`：实现结构化配置文件读取，并解析环境变量密钥引用。

实际文件结构可在后续 design 中根据仓库已有模式微调，但必须保持上述职责边界。

## 7. Key decisions and trade-offs

### Decision 1: Use `capability_profile` instead of explicit provider/model

调用方传入中性 profile，AI 网关配置将 profile 映射到 provider/model。这样业务层不需要知道具体模型来源，也便于后续按成本、上下文长度或供应商可用性调整配置。

放弃显式 provider/model 的原因是它会让业务层过早耦合供应商和模型细节，违背统一网关的核心价值。

### Decision 2: Use structured config file + environment variable secrets

profile 和 provider 映射适合结构化表达；API key 等敏感值适合环境变量。这个组合比纯环境变量更适合多 profile、多 provider 的可读配置，也比数据库治理更轻。

为了避免后续返工，核心代码只依赖配置 repository 抽象，不直接依赖文件路径或具体 settings 字段。后续如果需要数据库、远程配置中心或热更新，可以新增 repository adapter。

### Decision 3: Use OpenAI-compatible HTTP as first external provider

OpenAI-compatible HTTP 兼容面更广，不把首个实现绑定到单一供应商 SDK。它能验证真实外部调用链，同时保持 provider-neutral contract。

放弃供应商 SDK 的原因是 SDK 会把供应商对象、错误类型和参数模型更容易带入 capability contract，增加后续替换成本。

### Decision 4: Support text generation and neutral structured output only

文本生成覆盖章节正文等场景，结构化输出覆盖大纲、蓝图等后续业务可能需要的 JSON 结果。MVP 不做流式输出，以避免牵出接口形态、任务生命周期和前端消费方式。

结构化输出只表达通用 JSON/schema 能力，不承载业务 schema。

### Decision 5: Include minimal timeout, retry and error normalization

外部模型调用天然存在网络失败、超时、响应格式异常和 provider 错误。MVP 需要最小治理，否则业务方会重复处理 provider 差异。

本 change 不做限流、缓存、熔断，因为这些属于更完整的运行时韧性治理，应在真实调用和业务链路稳定后单独评估。

## 8. Critical flows

### Text generation flow

1. 业务层根据自身任务语义选择中性 `capability_profile`。
2. 调用 AI 网关 facade，传入 profile、输入消息或文本，以及输出模式 `text`。
3. service 通过 config repository 读取 profile 配置。
4. profile 解析到 provider、model、上下文限制、成本等级、timeout 和 retry 等配置。
5. service 根据 provider 名称选择 provider 实现。
6. OpenAI-compatible provider 将中性请求映射为 HTTP 请求。
7. provider 执行 timeout、少量 retry 和响应解析。
8. service/facade 返回统一文本响应、使用量摘要和 provider-neutral metadata。

### Structured output flow

1. 调用方选择中性 `capability_profile`，并声明输出模式为 JSON / structured。
2. 请求携带通用结构化约束，例如 JSON schema 或 provider-neutral response format。
3. service 保持约束的中性表达，并交给 provider 做协议映射。
4. provider 请求模型返回结构化结果。
5. AI 网关执行最小结果解析与错误转换。
6. facade 返回统一 structured response，不解释业务 schema 的语义。

### Configuration loading flow

1. 启动或首次使用时，file repository 读取结构化配置文件。
2. 配置文件声明 profiles、providers、models 和能力标签。
3. 配置中的密钥字段使用环境变量引用，而不是明文密钥。
4. repository 解析环境变量并校验必要字段。
5. service 只通过 repository 查询 profile/provider，不读取文件或环境变量。

### Error flow

- profile 不存在：转换为稳定配置错误。
- profile 指向未知 provider：转换为稳定配置错误。
- provider 配置缺少 base_url、model 或密钥引用：转换为稳定配置错误。
- provider 网络失败或超时：按最小 retry 策略处理；最终失败时转换为稳定 provider 调用错误或 timeout 错误。
- provider 返回非预期结构：转换为稳定 provider response error。
- 结构化输出解析失败：转换为稳定 structured output error，不归咎于具体业务 schema。

## 9. OpenSpec mapping

### `proposal.md` should cover

- 为什么 MVP 创作链路需要统一 AI 网关。
- 本 change 交付的用户价值：统一入口、可替换模型来源、按中性能力诉求选择 profile。
- 明确 scope：capability contract、profile 配置、OpenAI-compatible provider、最小失败治理。
- 明确 non-goals：业务 prompt、业务 schema、业务流程集成、限流缓存熔断、运行时配置治理。

### `design.md` should cover

- capability 边界与目录结构。
- facade、contracts、service、providers、config repository 的职责。
- `capability_profile` 的中性语义和配置映射方式。
- 结构化配置文件与环境变量密钥的治理边界。
- OpenAI-compatible HTTP provider 的协议映射原则。
- timeout、retry、错误模型和日志脱敏要求。
- 测试策略：contract/unit、config parsing、provider mapping、错误归一化、架构边界。

### `tasks.md` should break down

- 建立 AI 网关 capability 目录和公开导出。
- 定义 contracts：请求、响应、消息、输出模式、profile、使用量和 metadata。
- 定义 errors。
- 定义 config models 与 repository 抽象。
- 实现 file config repository 与环境变量密钥解析。
- 定义 provider base abstraction。
- 实现 OpenAI-compatible HTTP provider。
- 实现 service 与 facade。
- 接入 bootstrap/config wiring，仅做运行时装配，不写业务逻辑。
- 编写单元、集成和架构测试。

### Later artifacts must not invent

- 业务 prompt 模板。
- 大纲、蓝图、章节业务 schema。
- 业务 workflow 集成任务。
- 配置管理 UI、数据库配置表、运行时编辑能力。
- 限流、缓存、熔断。
- 流式输出能力。
- 供应商 SDK 作为主路径。

## 10. Generation guardrails

- 必须保持 capability-neutral；AI 网关不能包含创作任务语义。
- profile 名称必须表达中性能力诉求，不得以业务任务命名。
- 调用方不得直接指定或依赖 provider/model/api key。
- facade 和 contracts 是主要稳定边界；内部 service/provider/config 可演进但不能泄露给业务层。
- 配置来源不得写死在 service 或 facade 中；必须通过 repository 抽象。
- OpenAI-compatible provider 可以包含协议细节，但不得让协议字段污染公开 contract。
- 日志应覆盖配置解析、provider 调用开始/结束、失败转换等关键节点，但必须避免记录密钥、完整 prompt、完整响应或敏感内容。
- 测试必须覆盖成功路径和关键失败路径，尤其是 profile 缺失、provider 配置错误、HTTP 失败、timeout、响应结构异常和结构化输出解析失败。
- 如果后续 OpenSpec 生成时遇到未决事项，应显式标为待确认，不得把未讨论内容伪装成既定决策。

## 11. Fit for a single change

该范围适合单个 `feature-ai-gateway` change，因为它聚焦共享 AI capability 的 MVP 交付：能力契约、配置抽象、一个真实 OpenAI-compatible provider 和最小失败治理。

以下内容应作为后续独立 change：

- 大纲生成业务流程。
- 章节蓝图业务流程。
- 章节生成流水线。
- AI 网关运行时治理增强，例如限流、缓存、熔断。
- 配置数据库化、管理 UI 或审计。
- 流式输出。
- 多 provider 选择策略和高级 fallback。
