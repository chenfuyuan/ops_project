# 标准 Ports / Repository 模式

在生成业务依赖边界时，先判断依赖表达的是领域资源获取与保存，还是外部协作能力。

## Repository 的目的

repository 是领域模型或聚合的获取与保存边界。它应按业务资源或聚合命名，而不是按 ORM 表、mapper、事务或查询技术细节命名。

复杂 node 中，repository 抽象通常放在：

```text
app/business/<domain>/nodes/<unit>/domain/repositories.py
```

## Port 的目的

port 定义业务侧对外部能力的依赖边界，例如 AI 生成、内容写入、上下文读取、外部校验等。Port 应使用业务语言描述业务从外部世界需要什么。

## 必须做到

- 按职责、业务能力、领域资源或聚合给抽象命名。
- 保持方法名与业务意图一致。
- 在边界上使用业务 DTO、实体或中性值类型。
- 让每个 port / repository 都聚焦于一个清晰职责。
- repository 抽象不暴露 ORM、SQLAlchemy、HTTP、SDK 或 provider 类型。

## 必须避免

- 按 vendor、SDK 或 transport 给 port 命名。
- 按 ORM record、mapper、事务或表结构拆分 repository 抽象。
- 暴露 provider 特有的请求或响应类型。
- 把 `ports.py` 或 `domain/repositories.py` 变成无关接口的大杂烩。
- 让接口形状镜像基础设施实现细节。

## 推荐结构

```python
from typing import Protocol
from uuid import UUID

from app.business.<domain>.nodes.<unit>.domain.models import <Aggregate>


class <Aggregate>Repository(Protocol):
    def save(self, aggregate: <Aggregate>) -> <Aggregate>: ...

    def get(self, aggregate_id: UUID) -> <Aggregate> | None: ...
```

外部能力 port 示例：

```python
class ContentComposer(Protocol):
    def compose(self, request: ComposeContentRequest) -> ComposedContent: ...
```

## 命名建议

Repository 优先使用：
- `OutlineRepository`
- `DraftRepository`
- `ArtifactRepository`

Port 优先使用：
- `ContextReader`
- `ContentWriter`
- `TextComposer`
- `ResultPublisher`

避免使用：
- `HttpClientPort`
- `OpenAIAdapterPort`
- `SearchApiPort`
- `SDKGateway`
- `SeedTableRepository`
- `SkeletonMapperRepository`

## 与 infrastructure 的关系

`infrastructure/` 应实现这些接口，并负责：
- 协议翻译
- provider 映射
- 持久化集成
- ORM record / mapper / session / transaction
- 错误归一化
- 必要时处理 timeout 和 retry

这些关注点属于 adapter 实现，不属于 port / repository 契约本身。

## 质量自检

- 如果实现从 local 切换成 HTTP，这个名字是否仍然成立？
- 这个接口表达的是业务需求，而不是实现机制吗？
- 多个 adapter 能否在不改业务核心代码的前提下实现它？
- repository 是否按领域资源/聚合定义，而不是按技术文件拆分？
