# 标准 Workflow Node 模式

在生成 `app/business/<domain>/nodes/<unit>/node.py` 时，使用这份模式。

## 目的

`node.py` 是面向 workflow 的业务步骤 adapter。它负责把 workflow state 转换为 node facade 或轻量 service 的输入，调用业务入口，再把结果映射回 workflow state。

## 职责

- 接收 workflow state 或上游 node 输出。
- 只提取当前步骤真正需要的数据。
- 构造节点级 command 或 DTO。
- 调用 node 的稳定业务入口：复杂 node 调用 `facade.py`，轻量 node 可调用 `service.py`。
- 只写回下游 workflow 步骤真正需要的最小结果。

## 必须做到

- 把 workflow state 当作边界输入，而不是无限可变的大包对象。
- 保持 node 逻辑轻薄，聚焦于适配。
- 向 facade / service 传递显式 DTO 或 command 对象。
- 返回边界清晰的 state 更新或结果映射。

## 必须避免

- 在这里放业务规则。
- 直接调用 SDK、repository、use case、infrastructure adapter 或外部服务。
- 重新实现本应属于 facade / use case / service 的编排逻辑。
- 往 workflow state 中加入无关的中间细节。

## 复杂 node 推荐结构

```python
from app.business.<domain>.nodes.<unit>.application.dto import <Command>
from app.business.<domain>.nodes.<unit>.facade import <Unit>Facade
from app.business.<domain>.workflow.state import WorkflowState


class <Unit>Node:
    def __init__(self, facade: <Unit>Facade) -> None:
        self._facade = facade

    def run(self, state: WorkflowState) -> WorkflowState:
        command = <Command>(
            request_id=state.request_id,
            topic=state.topic,
        )

        result = self._facade.execute(command)

        return state.model_copy(update={
            "artifact_id": result.artifact_id,
        })
```

## State 约束

生成 node 时，优先遵循以下原则：
- 只读取当前 node 需要的字段
- 只写回真正需要跨 node 传递的字段
- 临时计算结果尽量保留在 node、facade 或 use case 内，而不是回灌到全局 workflow state

`workflow/state.py` 是高敏感边界，必须保持最小化。

## Node 质量自检

- 如果 workflow state 的形状略有变化，是否只需要调整这个 adapter？
- 这个文件是否只包含输入映射、业务入口调用和输出映射？
- 我是否不小心把业务校验或集成逻辑放进来了？
- 我是否往 workflow state 写回了过多的临时数据？
- 复杂 node 是否调用 facade，而不是直接调用 use case 或 infrastructure？

## 与相邻文件的关系

- `workflow/state.py` 定义跨 node 共享的 state。
- `node.py` 负责把该 state 适配到某个步骤。
- `facade.py` 是复杂 node 的稳定业务入口。
- `application/use_cases/` 负责业务行为编排。
- `domain/` 负责领域模型、规则和 repository 抽象。
- `infrastructure/` 负责依赖边界实现。
