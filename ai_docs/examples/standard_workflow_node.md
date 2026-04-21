# 标准 Workflow Node 模式

在生成 `app/business/<domain>/nodes/<unit>/node.py` 时，使用这份模式。

## 目的
`node.py` 是面向 workflow 的业务步骤 adapter。
它负责把 workflow state 转换为 service command，调用 service，再把结果映射回 workflow state。

## 职责
- 接收 workflow state 或上游 node 输出。
- 只提取当前步骤真正需要的数据。
- 构造节点级 command 或 DTO。
- 调用 `service.py`。
- 只写回下游 workflow 步骤真正需要的最小结果。

## 必须做到
- 把 workflow state 当作边界输入，而不是无限可变的大包对象。
- 保持 node 逻辑轻薄，聚焦于适配。
- 向 service 传递显式 DTO 或 command 对象。
- 返回边界清晰的 state 更新或结果映射。

## 必须避免
- 在这里放业务规则。
- 直接调用 SDK、repository 或外部服务。
- 重新实现本应属于 `service.py` 的编排逻辑。
- 往 workflow state 中加入无关的中间细节。

## 推荐结构
```python
from app.business.<domain>.nodes.<unit>.dto import <Command>
from app.business.<domain>.nodes.<unit>.service import <Unit>Service
from app.business.<domain>.workflow.state import WorkflowState


class <Unit>Node:
    def __init__(self, service: <Unit>Service) -> None:
        self._service = service

    def run(self, state: WorkflowState) -> WorkflowState:
        command = <Command>(
            request_id=state.request_id,
            topic=state.topic,
        )

        result = self._service.execute(command)

        return state.model_copy(update={
            "artifact_id": result.artifact_id,
        })
```

## State 约束
生成 node 时，优先遵循以下原则：
- 只读取当前 node 需要的字段
- 只写回真正需要跨 node 传递的字段
- 临时计算结果尽量保留在 node 或 service 内，而不是回灌到全局 workflow state

`workflow/state.py` 是高敏感边界，必须保持最小化。

## Node 质量自检
在完成生成前，检查：
- 如果 workflow state 的形状略有变化，是否只需要调整这个 adapter？
- 这个文件是否只包含输入映射、service 调用和输出映射？
- 我是否不小心把业务校验或集成逻辑放进来了？
- 我是否往 workflow state 写回了过多的临时数据？

## 与相邻文件的关系
- `workflow/state.py` 定义跨 node 共享的 state。
- `node.py` 负责把该 state 适配到某个步骤。
- `service.py` 负责业务编排。
- `ports.py` 和 `infrastructure/` 负责依赖边界。
