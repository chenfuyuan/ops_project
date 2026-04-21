# 命名规则

命名应表达稳定的领域含义和边界职责。

## 目录命名
- 使用面向领域、能力或职责的名称。
- 优先选择在实现细节变化后仍然成立的名字。
- 避免使用 `misc`、`utils`、`common2`、`temp` 这类模糊目录名。

## Port 命名
Port 应按它提供的业务能力命名，而不是按 transport、vendor 或 SDK 命名。

推荐示例：
- `ContextReader`
- `ContentWriter`
- `ArtifactRepository`
- `TextComposer`

避免示例：
- `HttpPort`
- `SearchApiPort`
- `OpenAIAdapterPort`
- `SDKGateway`

## Infrastructure 实现命名
Adapter 应按“边界职责 + provider 或 transport 角色”命名。

推荐示例：
- `LocalCapabilityContextReader`
- `HttpCapabilityContextReader`
- `SqlArtifactRepository`
- `ExternalValidationClient`

## 通用命名规则
生成的名字应该让读者能回答：
- 它负责的业务或系统职责是什么？
- 它处在哪个边界上？
- 它是接口、adapter，还是业务对象？

如果一个名字只描述技术机制，而没有表达职责，通常说明它太弱了。
