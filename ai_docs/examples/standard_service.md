# 标准 Service 模式（轻量 node）

本模式仅适用于简单 business node。复杂 node 应优先使用 `facade.py + application/use_cases/ + domain/ + infrastructure/`，参考 `standard_node_evolution.md` 和 `standard_facade_and_use_cases.md`。

## 目的

在轻量 node 中，`service.py` 可以负责节点级业务用例编排。它应该用业务语言协调业务对象、规则和 port / repository 调用。

## 适用条件

- 业务行为很少，通常 1–2 个。
- 没有复杂状态流转、聚合边界或多 adapter 协作。
- 文件没有持续吸收多个独立业务行为的趋势。

如果 node 已出现多个独立业务行为、明确领域模型、聚合边界、状态流转或跨 node 复用压力，应演进为复杂 node 结构，而不是继续向 `service.py` 增加方法。

## 职责

- 接收节点级 command 或 DTO 输入。
- 在需要时通过 `rules.py` 进行校验或规范化。
- 协调业务实体与 port / repository 调用。
- 返回节点级结果 DTO 或领域结果对象。
- 保持用例流程在阅读上仍然是业务流程。

## 必须做到

- 只依赖业务定义的抽象。
- 使用业务语言，而不是 vendor 语言。
- 让编排过程显式、清晰、易读。
- 只能通过 ports / repositories 调用 adapters。

## 必须避免

- import 供应商 SDK。
- 直接 import HTTP client、RPC client 或存储驱动。
- 直接 import SQLAlchemy model 或 ORM session。
- 承担 transport 相关映射。
- 把 provider 切换逻辑藏在 service 内部。
- 把业务决策下沉到 `infrastructure/`。
- 在复杂 node 中继续把所有业务行为堆进 `service.py`。

## 推荐结构

```python
from app.business.<domain>.nodes.<unit>.dto import <Command>, <Result>
from app.business.<domain>.nodes.<unit>.entities import <Entity>
from app.business.<domain>.nodes.<unit>.ports import <PortA>, <PortB>
from app.business.<domain>.nodes.<unit>.rules import <rule_or_validator>


class <Unit>Service:
    def __init__(self, port_a: <PortA>, port_b: <PortB>) -> None:
        self._port_a = port_a
        self._port_b = port_b

    def execute(self, command: <Command>) -> <Result>:
        <rule_or_validator>(command)

        entity = <Entity>.from_command(command)
        context = self._port_a.read_context(entity.<field>)
        artifact = self._port_b.save(entity, context)

        return <Result>(artifact_id=artifact.id)
```

## AI 自检问题

- 如果把每个 port 都替换成 fake，这个 service 还能方便测试吗？
- 如果 provider 从 local 切换成 HTTP，这个文件还能保持不变吗？
- 这个文件读起来像业务编排，而不是集成代码吗？
- 当前 node 是否已经命中复杂 node 演进信号？

## 相邻文件关系

- `node.py` 负责把 workflow state 适配为 service 或 facade 输入。
- `ports.py` / `repositories.py` 定义业务需要什么依赖。
- `infrastructure/` 实现这些依赖。
- `rules.py` 存放可复用的业务校验和判定逻辑。
