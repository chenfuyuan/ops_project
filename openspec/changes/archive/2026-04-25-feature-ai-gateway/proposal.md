## Why

MVP 创作链路中的大纲生成、章节蓝图和章节生成都需要访问模型能力；如果各业务流程分别处理模型来源、凭据、调用协议和失败语义，后续切换模型与统一治理会产生高返工成本。

本 change 通过中性的 AI 网关建立统一模型访问入口，让后续创作任务可以按能力 profile 请求模型能力，而不是绑定到单一供应商或把模型细节散落在业务代码中。

## What Changes

- 新增 `ai-gateway` capability，作为 MVP 创作任务访问模型能力的统一入口。
- 提供稳定 facade 与公开 contracts，支持调用方通过中性 `capability_profile` 请求模型能力。
- 支持文本生成与中性 JSON / 结构化输出能力，不包含任何大纲、蓝图或章节业务 schema。
- 接入一个 OpenAI-compatible HTTP provider，作为首个真实外部模型调用路径。
- 引入结构化配置文件描述 profile、provider、model、能力标签、上下文限制和成本等级等映射。
- 使用环境变量承载 API key 等敏感凭据，避免密钥进入配置文件。
- 定义配置读取抽象，隔离配置来源，避免后续切换到数据库、配置中心或其他来源时改动网关核心逻辑。
- 提供最小 timeout、少量 retry 和稳定错误归一化。
- 明确 AI 网关不承担业务任务语义到模型诉求的映射；大纲、蓝图、章节等业务语义不得进入该 capability。
- 不做限流、缓存、熔断、流式输出、运行时配置管理、配置 UI 或业务流程集成。

## Capabilities

### New Capabilities

- `ai-gateway`: 定义统一 AI 模型访问能力，覆盖中性 profile 选择、文本生成、结构化输出、OpenAI-compatible provider 接入、配置读取抽象和最小失败治理。

### Modified Capabilities

无。

## Impact

- 影响代码区域：`app/capabilities/ai_gateway/`、运行时装配相关的 `app/bootstrap/` 配置接线，以及必要的配置文件位置。
- 影响测试区域：新增或更新 capability 单元测试、provider/配置解析集成测试，以及架构边界测试。
- 影响配置：需要声明 AI 网关 profile/provider/model 映射的结构化配置文件，并通过环境变量提供外部模型 API key。
- 影响依赖：可能需要使用仓库既有 HTTP client 基线或补充最小 HTTP 调用依赖；不得引入供应商 SDK 作为主路径。
- 不影响业务流程契约：本 change 不修改大纲生成、章节蓝图或章节生成的业务需求，也不暴露 provider/model/api key 给业务核心。
