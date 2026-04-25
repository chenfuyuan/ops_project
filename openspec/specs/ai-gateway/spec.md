## ADDED Requirements

### Requirement: 统一 AI 网关入口
系统 SHALL 提供一个位于 `app/capabilities/ai_gateway` 的中性 AI capability，调用方 SHALL 通过稳定 facade 和公开 contracts 请求模型能力，而不是直接依赖 provider、配置读取实现或外部协议细节。

#### Scenario: 调用方通过 facade 请求模型能力
- **WHEN** 调用方使用 AI 网关公开 facade 发起文本生成或结构化输出请求
- **THEN** 系统 SHALL 通过统一入口处理请求并返回统一响应

#### Scenario: 调用方绕过公开入口依赖 provider 内部实现
- **WHEN** 调用方试图直接依赖 AI 网关 provider 内部文件作为稳定调用面
- **THEN** 系统 SHALL 将该依赖视为违反 capability 边界的用法

### Requirement: 中性 capability profile 选择
系统 SHALL 要求调用方使用中性 `capability_profile` 表达模型能力诉求，并 SHALL 通过配置将 profile 解析为具体 provider、model 和能力参数。AI 网关 MUST NOT 要求调用方直接传入 provider、model、base_url 或 api_key。

#### Scenario: 使用中性 profile 请求模型能力
- **WHEN** 调用方提交包含 `capability_profile` 的 AI 网关请求
- **THEN** 系统 SHALL 根据该 profile 查询配置并选择对应模型来源

#### Scenario: profile 名称包含业务任务语义
- **WHEN** profile 名称表达大纲、蓝图、章节等业务任务语义
- **THEN** 系统 SHALL 将该命名视为不符合 AI 网关中性边界的配置

#### Scenario: 调用方直接指定 provider 或 model
- **WHEN** 调用方试图在公开请求契约中直接指定 provider 或 model
- **THEN** 系统 SHALL 拒绝把 provider 或 model 作为业务调用方的稳定选择接口

### Requirement: 文本生成能力
系统 SHALL 支持通过 AI 网关生成文本结果。请求 SHALL 使用中性输入和输出模式表达文本生成诉求，响应 SHALL 返回生成文本、使用量摘要和 provider-neutral metadata。

#### Scenario: 文本生成成功
- **WHEN** 调用方使用有效 `capability_profile` 发起文本生成请求且 provider 返回成功响应
- **THEN** 系统 SHALL 返回统一文本响应、使用量摘要和 provider-neutral metadata

#### Scenario: 文本生成响应包含 provider 私有字段
- **WHEN** provider 返回包含供应商私有字段的成功响应
- **THEN** 系统 SHALL 只将允许的中性结果和 metadata 暴露给调用方

### Requirement: 中性结构化输出能力
系统 SHALL 支持 JSON / 结构化输出请求，并 SHALL 只处理通用 JSON、schema 或 response format 约束。AI 网关 MUST NOT 内置或解释大纲、蓝图、章节等业务 schema。

#### Scenario: 结构化输出成功
- **WHEN** 调用方使用有效 `capability_profile` 和通用结构化约束发起结构化输出请求
- **THEN** 系统 SHALL 返回统一结构化响应并保留 provider-neutral metadata

#### Scenario: 请求包含业务 schema 语义
- **WHEN** 结构化输出约束被命名或实现为大纲、蓝图、章节等业务 schema 托管能力
- **THEN** 系统 SHALL 将该设计视为超出 AI 网关能力边界

#### Scenario: 结构化输出解析失败
- **WHEN** provider 返回的内容无法按通用结构化输出约束解析
- **THEN** 系统 SHALL 返回稳定的结构化输出错误

### Requirement: OpenAI-compatible HTTP provider 接入
系统 SHALL 提供一个 OpenAI-compatible HTTP provider 作为 MVP 首个真实外部模型调用路径。provider SHALL 负责外部协议映射、HTTP 调用、响应映射和 provider 错误翻译，但 MUST NOT 将 OpenAI-compatible 协议字段泄露到公开 contracts。

#### Scenario: OpenAI-compatible 调用成功
- **WHEN** AI 网关选择 OpenAI-compatible provider 且外部服务返回成功响应
- **THEN** 系统 SHALL 将外部响应映射为 AI 网关统一响应

#### Scenario: provider 返回 HTTP 错误
- **WHEN** OpenAI-compatible provider 收到外部 HTTP 错误响应
- **THEN** 系统 SHALL 将该错误转换为稳定的 provider 调用错误

#### Scenario: provider 返回非预期响应结构
- **WHEN** OpenAI-compatible provider 收到无法映射的响应结构
- **THEN** 系统 SHALL 返回稳定的 provider response error

### Requirement: 结构化配置文件与环境变量密钥
系统 SHALL 使用结构化配置文件声明 profile、provider、model、能力标签、上下文限制、成本等级、timeout 和 retry 等非敏感配置，并 SHALL 使用环境变量提供 API key 等敏感凭据。配置文件 MUST NOT 存储明文 API key。

#### Scenario: 配置文件引用环境变量密钥
- **WHEN** 配置文件中的 provider 配置通过环境变量名称引用 API key
- **THEN** 系统 SHALL 从环境变量读取密钥并用于 provider 调用

#### Scenario: 配置文件包含明文密钥
- **WHEN** AI 网关配置文件包含明文 API key
- **THEN** 系统 SHALL 将该配置视为不符合安全要求

#### Scenario: 环境变量密钥缺失
- **WHEN** provider 配置引用的环境变量不存在或为空
- **THEN** 系统 SHALL 返回稳定配置错误

### Requirement: 配置读取抽象
系统 SHALL 定义配置读取抽象，使 service 和 facade 只依赖配置 repository contract，而不依赖具体配置文件路径、文件格式、环境变量读取逻辑、数据库或配置中心实现。

#### Scenario: service 查询 profile 配置
- **WHEN** service 需要根据 `capability_profile` 解析模型能力来源
- **THEN** 系统 SHALL 通过配置 repository 抽象获取 profile 和 provider 配置

#### Scenario: 更换配置来源
- **WHEN** 后续将配置来源从文件切换为数据库或配置中心
- **THEN** 系统 SHALL 允许通过替换 repository 实现完成切换，而不改变 facade 主调用契约

### Requirement: 最小失败治理
系统 SHALL 为外部模型调用提供最小 timeout、少量 retry 和稳定错误归一化。系统 MUST NOT 在本能力中实现限流、缓存、熔断或高级 fallback。

#### Scenario: provider 调用超时
- **WHEN** 外部 provider 调用超过配置的 timeout
- **THEN** 系统 SHALL 按最小 retry 策略处理，并在最终失败时返回稳定 timeout 错误

#### Scenario: provider 发生可恢复网络失败
- **WHEN** 外部 provider 调用出现可恢复网络失败
- **THEN** 系统 SHALL 按配置的少量 retry 策略重试

#### Scenario: provider 调用最终失败
- **WHEN** 外部 provider 调用在 retry 后仍失败
- **THEN** 系统 SHALL 返回稳定 provider 调用错误，而不是泄露供应商私有错误类型

### Requirement: 日志与敏感信息保护
系统 SHALL 在 AI 网关关键节点记录必要日志，包括配置解析、provider 调用开始和结束、失败转换等结果摘要。系统 MUST NOT 在日志、错误消息或 metadata 中记录 API key、完整 prompt、完整请求体、完整模型输出或其他敏感内容。

#### Scenario: provider 调用被记录
- **WHEN** AI 网关调用外部 provider
- **THEN** 系统 SHALL 记录 profile、provider 名称、动作、结果摘要、耗时和错误分类等安全上下文

#### Scenario: 错误路径包含敏感信息
- **WHEN** provider 调用失败且异常包含敏感请求信息或凭据
- **THEN** 系统 SHALL 在对外错误和日志中移除敏感内容

### Requirement: capability 架构边界
系统 SHALL 保持 AI 网关为中性 capability。`app/capabilities/ai_gateway` MUST NOT 依赖 `app/business`，也 MUST NOT 包含大纲、蓝图、章节等创作业务规则。

#### Scenario: AI 网关依赖 business 模块
- **WHEN** AI 网关代码引入 `app/business` 下的模块
- **THEN** 系统 SHALL 将该依赖视为架构边界违规

#### Scenario: AI 网关包含业务任务规则
- **WHEN** AI 网关实现包含大纲、蓝图、章节等业务规则或 prompt 模板
- **THEN** 系统 SHALL 将该实现视为超出 capability 边界
