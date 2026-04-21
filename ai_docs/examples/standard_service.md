# 标准 Service 模式

在生成 `app/business/<domain>/nodes/<unit>/service.py` 时，使用这份模式。

## 目的
`service.py` 负责节点级业务用例编排。
它应该用业务语言协调业务对象、规则和 port 调用。

## 职责
- 接收节点级 command 或 DTO 输入。
- 在需要时通过 `rules.py` 进行校验或规范化。
- 协调业务实体与 port 调用。
- 返回节点级结果 DTO 或领域结果对象。
- 保持用例流程在阅读上仍然是业务流程。

## 必须做到
- 只依赖 `ports.py` 中定义的业务抽象。
- 使用业务语言，而不是 vendor 语言。
- 让编排过程显式、清晰、易读。
- 只能通过 ports 调用 adapters。

## 必须避免
- import 供应商 SDK。
- 直接 import HTTP client、RPC client 或存储驱动。
- 直接 import SQLAlchemy model 或 ORM session。
- 承担 transport 相关映射。
- 把 provider 切换逻辑藏在 service 内部。
- 把业务决策下沉到 `infrastructure/`。

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
在完成生成前，检查：
- 如果把每个 port 都替换成 fake，这个 service 还能方便测试吗？
- 如果 provider 从 local 切换成 HTTP，这个文件还能保持不变吗？
- 这个文件读起来像业务编排，而不是集成代码吗？

## 相邻文件关系
- `node.py` 负责把 workflow state 适配为 service 输入。
- `ports.py` 定义这个 service 需要什么依赖。
- `infrastructure/` 实现这些依赖。
- `rules.py` 存放可复用的业务校验和判定逻辑。
