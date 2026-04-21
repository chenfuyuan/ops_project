# 标准 Infrastructure Adapter 模式

在生成 `app/business/<domain>/nodes/<unit>/infrastructure/*.py` 时，使用这份模式。

## 目的
`infrastructure/` 下的文件负责实现业务定义的 ports，并在业务语言与外部系统、capabilities 或持久化层之间做翻译。

## 职责
- 实现 `ports.py` 中声明的接口。
- 将业务 DTO 或实体翻译成 provider、capability、repository 或协议调用。
- 将外部响应和错误归一化为业务可接受的结果。
- 把 transport、provider、serialization、auth、retry 和 timeout 细节隔离在 `service.py` 之外。

## 必须做到
- 依赖自己所实现的 port 契约。
- 让翻译逻辑尽量贴近边界。
- 仅在这里或更底层的 shared infrastructure 中使用 provider 特定 SDK 或存储驱动。
- 返回值必须符合业务侧 port 契约。

## 必须避免
- 加入本应属于 `service.py` 或 `rules.py` 的业务决策逻辑。
- 将 vendor 特有请求或响应模型泄漏到业务核心文件中。
- 在 adapter 内部动态做实现选择，而这个选择本应属于 `bootstrap`。
- 把一个 adapter 做成承载多个无关集成的大杂烩。

## 推荐结构
```python
from app.business.<domain>.nodes.<unit>.dto import <Query>, <SavedArtifact>
from app.business.<domain>.nodes.<unit>.entities import <Entity>
from app.business.<domain>.nodes.<unit>.ports import ArtifactRepository


class SqlArtifactRepository(ArtifactRepository):
    def __init__(self, session_factory: <SessionFactory>) -> None:
        self._session_factory = session_factory

    def save(self, entity: <Entity>, content: str) -> <SavedArtifact>:
        record = <OrmModel>.from_entity(entity, content)

        with self._session_factory() as session:
            session.add(record)
            session.commit()

        return <SavedArtifact>(artifact_id=record.id)
```

## 另一种常见结构
```python
from app.business.<domain>.nodes.<unit>.dto import <Query>
from app.business.<domain>.nodes.<unit>.ports import ContextReader


class HttpCapabilityContextReader(ContextReader):
    def __init__(self, client: <HttpClient>) -> None:
        self._client = client

    def read_context(self, query: <Query>) -> str:
        response = self._client.post("/context/read", json={"topic": query.topic})
        response.raise_for_status()
        payload = response.json()
        return payload["content"]
```

## Adapter 质量自检
在完成生成前，检查：
- 这个文件是否实现了业务定义的 port，而不是私自发明了另一套契约？
- 如果 provider payload 变了，我是否只需要改这个 adapter，而不用改 `service.py`？
- 所有 vendor 或协议知识是否都被限制在这里？
- 我是否不小心加入了本应放在 rules 或 services 中的业务分支？

## 命名建议
优先使用：
- `SqlArtifactRepository`
- `HttpCapabilityContextReader`
- `S3ArtifactStorage`
- `ExternalValidationClient`

命名时先表达职责，再表达 provider 或 transport。
