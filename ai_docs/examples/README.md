# Examples

这个目录用于存放提供给 AI 助手参考的标准实现样例。

## 当前样例

- `standard_node_evolution.md`：说明 business node 何时保持轻量结构、何时演进为复杂 node 轻量 DDD、何时评估 domain-level bounded context
- `standard_facade_and_use_cases.md`：说明复杂 node 的 `facade.py` 与 `application/use_cases/` 应如何组织
- `standard_service.md`：说明轻量业务节点 `service.py` 应如何组织，复杂 node 不应继续使用该模式承载所有业务行为
- `standard_ports.md`：说明业务侧 port / repository 边界应如何表达
- `standard_infrastructure_adapter.md`：说明业务 adapter 应如何实现 port 并隔离 provider 细节
- `standard_workflow_node.md`：说明 workflow-facing node adapter 应如何把 state 映射为 facade / service 输入再映射回去

## 规则

这里只添加团队希望 AI 反复模仿的模式。宁可保留少量高质量样例，也不要堆积大量不完整样例。
