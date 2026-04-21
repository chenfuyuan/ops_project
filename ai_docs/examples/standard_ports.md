# 标准 Ports 模式

在生成 `app/business/<domain>/nodes/<unit>/ports.py` 时，使用这份模式。

## 目的
`ports.py` 定义业务侧的依赖边界。
Port 应使用业务语言描述业务从外部世界需要什么。

## 职责
- 定义 repository、reader、writer、validator 或外部协作接口。
- 用业务术语表达依赖需求。
- 对业务代码隐藏 transport、provider、SDK 和部署细节。

## 必须做到
- 按职责或能力给 port 命名。
- 保持方法名与业务意图一致。
- 在边界上使用业务 DTO、实体或中性值类型。
- 让每个 port 都聚焦于一个清晰职责。

## 必须避免
- 按 vendor、SDK 或 transport 给 port 命名。
- 暴露 provider 特有的请求或响应类型。
- 把 `ports.py` 变成无关接口的大杂烩。
- 让接口形状镜像基础设施实现细节。

## 推荐结构
```python
from typing import Protocol

from app.business.<domain>.nodes.<unit>.dto import <Query>, <SavedArtifact>
from app.business.<domain>.nodes.<unit>.entities import <Entity>


class ContextReader(Protocol):
    def read_context(self, query: <Query>) -> str: ...


class ArtifactRepository(Protocol):
    def save(self, entity: <Entity>, content: str) -> <SavedArtifact>: ...
```

## 命名建议
优先使用：
- `ContextReader`
- `ArtifactRepository`
- `ContentWriter`
- `ResultPublisher`

避免使用：
- `HttpClientPort`
- `OpenAIAdapterPort`
- `SearchApiPort`
- `SDKGateway`

## Port 质量自检
在完成生成前，检查：
- 如果实现从 local 切换成 HTTP，这个名字是否仍然成立？
- 这个接口表达的是业务需求，而不是实现机制吗？
- 多个 adapter 能否在不改业务核心代码的前提下实现它？

## 与 infrastructure 的关系
`infrastructure/` 应实现这些接口，并负责：
- 协议翻译
- provider 映射
- 持久化集成
- 错误归一化
- 必要时处理 timeout 和 retry

这些关注点属于 adapter，不属于 port 契约本身。
