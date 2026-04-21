# Examples

这个目录用于存放提供给 AI 助手参考的标准实现样例。

## 当前样例
- `standard_service.md`：说明业务节点 `service.py` 应如何组织
- `standard_ports.md`：说明业务侧依赖边界应如何表达
- `standard_infrastructure_adapter.md`：说明业务 adapter 应如何实现 port 并隔离 provider 细节
- `standard_workflow_node.md`：说明 workflow-facing node adapter 应如何把 state 映射为 service 输入再映射回去

## 规则
这里只添加团队希望 AI 反复模仿的模式。宁可保留少量高质量样例，也不要堆积大量不完整样例。
