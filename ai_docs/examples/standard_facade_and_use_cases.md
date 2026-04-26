# 标准 Facade 与 Use Case 模式

在复杂 business node 中，使用 `facade.py` 作为对外稳定入口，并将独立业务行为拆到 `application/use_cases/`。

## Facade 目的

`facade.py` 面向 HTTP、workflow、bootstrap 或其他业务入口暴露稳定方法。它负责依赖聚合、转发和必要横切协调，但不承载具体业务规则。

## Facade 可以做

- 持有 use case 实例。
- 暴露 node 对外稳定方法。
- 添加安全的日志上下文。
- 做统一异常转换或横切协调。
- 协调事务、幂等或调用顺序边界，前提是不写具体业务规则。

## Facade 不要做

- 不实现完整业务行为。
- 不写领域规则或状态转换判断。
- 不直接调用 SDK、HTTP client、ORM session 或 provider。
- 不绕过 use case 直接调用 infrastructure adapter。

## Use Case 目的

use case 承载一个独立业务行为的应用层编排。它用业务语言协调 command/query、domain model、domain rule、repository 抽象和外部 port。

## 推荐结构

```python
class CreateDraftUseCase:
    def __init__(self, repository: DraftRepository) -> None:
        self._repository = repository

    def execute(self, command: CreateDraftCommand) -> Draft:
        validate_draft_command(command)
        draft = Draft.from_command(command)
        return self._repository.save(draft)


class DraftFacade:
    def __init__(self, create_draft: CreateDraftUseCase) -> None:
        self._create_draft = create_draft

    def create_draft(self, command: CreateDraftCommand) -> Draft:
        return self._create_draft.execute(command)
```

## 与相邻文件关系

- `application/dto.py` 定义 command、query、result。
- `application/use_cases/*.py` 定义业务行为编排。
- `domain/models.py` 定义领域模型和值对象。
- `domain/rules.py` 定义领域规则和不变量。
- `domain/repositories.py` 定义 repository 抽象。
- `infrastructure/` 实现 repository 和外部 port。
- `node.py` 将 workflow state 映射为 facade 输入。

## 自检问题

- 这个 facade 方法是否只是入口和协调，而不是业务规则实现？
- 这个 use case 是否对应一个清晰业务行为？
- use case 是否只依赖抽象，而没有直接依赖具体 adapter？
- 领域不变量是否放在 domain，而不是 facade 或 infrastructure？
