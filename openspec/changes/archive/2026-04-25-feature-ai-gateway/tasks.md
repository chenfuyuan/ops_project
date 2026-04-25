## 1. Capability 骨架与公开契约

- [x] 1.1 创建 `app/capabilities/ai_gateway/` 标准目录结构，并通过根包导出稳定 facade、公开 request/response/model 类型和错误类型。
- [x] 1.2 定义公开 request contracts，覆盖中性 `capability_profile`、消息或文本输入、文本输出模式、结构化输出模式和通用结构化约束。
- [x] 1.3 定义公开 response contracts，覆盖统一文本响应、统一结构化响应、使用量摘要和 provider-neutral metadata。
- [x] 1.4 定义公开模型类型，覆盖 profile 名称、输出模式、消息角色、能力标签、结构化输出约束和通用 metadata。
- [x] 1.5 定义 AI 网关稳定错误类型，覆盖配置错误、provider 调用错误、timeout 错误、provider 响应映射错误和结构化输出错误。

## 2. 配置模型与配置读取抽象

- [x] 2.1 定义 AI 网关配置模型，覆盖 profiles、providers、models、能力标签、上下文限制、成本等级、timeout 和 retry 配置。
- [x] 2.2 定义配置 repository 抽象，使 service 只通过抽象读取 profile 和 provider 配置。
- [x] 2.3 实现结构化配置文件 repository，支持读取 profile/provider/model 映射并校验必要字段。
- [x] 2.4 实现环境变量密钥解析，支持通过环境变量引用 API key，并拒绝缺失或空密钥。
- [x] 2.5 增加明文密钥防护，确保结构化配置文件不承载 API key 明文。

## 3. Provider 抽象与 OpenAI-compatible provider

- [x] 3.1 定义 provider base abstraction，使 AI 网关 service 不依赖具体 provider 实现细节。
- [x] 3.2 实现 OpenAI-compatible HTTP provider 的请求映射，将中性文本生成请求映射为外部 HTTP 请求。
- [x] 3.3 实现 OpenAI-compatible HTTP provider 的结构化输出映射，将通用 JSON/schema 约束映射为外部协议参数。
- [x] 3.4 实现 OpenAI-compatible HTTP provider 的响应映射，返回统一文本响应、统一结构化响应、使用量摘要和 provider-neutral metadata。
- [x] 3.5 实现 provider HTTP 错误、网络失败、timeout 和非预期响应结构到稳定 AI 网关错误类型的转换。
- [x] 3.6 实现 provider 最小 retry 策略，并确保 retry 次数和 timeout 来自 profile/provider 配置。

## 4. Service、Facade 与运行时装配

- [x] 4.1 实现 AI 网关 service，根据 `capability_profile` 查询配置、选择 provider 并执行文本生成或结构化输出请求。
- [x] 4.2 实现 AI 网关 facade，作为调用方访问模型能力的稳定入口，并屏蔽 service、config 和 provider 细节。
- [x] 4.3 增加 provider registry 或等价装配机制，使 provider 选择集中在 service 组合边界或 bootstrap，而不是散落到调用方。
- [x] 4.4 在 bootstrap 中完成最小运行时装配和配置接线，不在 bootstrap 中承载业务逻辑。
- [x] 4.5 增加安全日志，覆盖配置解析、provider 调用开始和结束、失败转换等关键节点，并避免记录 API key、完整请求体、完整 prompt 或完整模型输出。

## 5. 测试覆盖

- [x] 5.1 编写 contract 单元测试，验证 request、response、输出模式、profile、结构化约束和使用量摘要等公开模型行为。
- [x] 5.2 编写配置解析测试，覆盖有效配置、未知 profile、未知 provider、缺失字段、环境变量密钥缺失和明文密钥拒绝。
- [x] 5.3 编写 service 单元测试，使用 fake repository 和 fake provider 验证 profile 解析、provider 选择、文本生成、结构化输出和错误转换。
- [x] 5.4 编写 OpenAI-compatible provider 集成测试，覆盖请求映射、响应映射、HTTP 错误、timeout、retry 和非预期响应结构。
- [x] 5.5 编写结构化输出测试，覆盖成功解析和解析失败转换为稳定 structured output error。
- [x] 5.6 编写日志与敏感信息测试，验证 API key、完整请求体、完整 prompt 和完整模型输出不会进入日志或对外错误。
- [x] 5.7 编写或更新架构测试，验证 `app/capabilities/ai_gateway` 不依赖 `app/business`，公开调用面不要求调用方依赖 provider 内部文件。

## 6. 验证与收尾

- [x] 6.1 运行 AI 网关相关单元测试和集成测试，确认新增能力满足 specs 场景。
- [x] 6.2 运行架构边界测试，确认 capability 中性边界未被破坏。
- [x] 6.3 运行项目既有测试基线，确认新增 AI 网关能力未破坏现有脚手架、bootstrap 和接口测试。
- [x] 6.4 自检实现未引入业务 prompt、业务 schema、业务 workflow 集成、限流、缓存、熔断、流式输出或配置管理 UI。
