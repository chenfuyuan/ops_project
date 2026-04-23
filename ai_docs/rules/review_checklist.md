# 评审清单

在认为生成代码完成之前，应先使用这份清单自检。

## 边界检查
- 新代码是否放在了正确的顶层区域？
- 是否有业务核心文件直接依赖 SDK、HTTP client 或 ORM 实现？
- `service.py` 是否只依赖业务定义的 ports？
- `interfaces/` 是否避免直接深入到 `business/**/infrastructure/*`？
- `capabilities/` 是否保持不依赖业务？
- `shared/` 是否保持不承载业务语义？
- `workflow/` 是否保持不包含外部实现细节？

## 命名检查
- 目录和模块是否按领域或职责命名？
- 是否出现了 `misc`、`utils`、`common2`、`temp` 这类模糊名称？
- port 是否按业务能力命名，而不是按 vendor 或 transport 命名？
- adapter 是否按职责与 provider 或 transport 角色命名？

## Workflow 与 state 检查
- `workflow/state.py` 是否仍然保持最小且边界清晰？
- node 的输入输出是否清晰，而不是传递一个不断膨胀的全局 state 对象？
- `node.py` 是否仍然是 adapter，而不是业务逻辑承载层？

## Infrastructure 检查
- `infrastructure/` 是否仍然是 adapter 层，而不是业务逻辑层？
- timeout、retry、auth、serialization 和 provider 细节是否都留在业务核心文件之外？
- 实现切换是否仍然集中在 `bootstrap`，而不是散落到业务代码中？

## 测试检查
- 业务规则和 service 是否能通过 port 边界上的 fake、stub 或 mock 来做单元测试？
- `infrastructure` 和 `interfaces` 是否在映射和边界行为重要的地方有集成测试覆盖？
- 架构约束是否能通过架构测试或等价机制进行检查？

## 编码表达与可观测性检查
- 模块、类、函数和复杂分支是否具备足够注释，能解释职责、约束和关键设计原因？
- 是否避免了只重复代码字面含义的低价值注释？
- 关键流程、状态变化、外部调用和异常路径是否具备适当日志？
- 日志是否包含足够排障上下文，同时避免泄露敏感信息和制造高频噪音？

## 高敏感区域提醒
以下区域的改动需要额外审慎：
- `shared/`
- `capabilities/`
- `workflow/state.py`
- `business/**/ports.py`
- `business/**/infrastructure/*`

## 常见反模式提醒
- 不要把 `capabilities` 做成伪共享业务层。
- 不要让业务逻辑下沉到 `infrastructure/`。
- 不要让 `service.py` 直接调用 SDK、HTTP client 或 ORM。
- 不要通过 `shared/` 传播业务耦合。
- 不要让 workflow 层承载业务实现。
- 不要把 workflow state 变成隐式万能上下文。
- 不要在业务代码中分散做实现选择，local / remote / mock / provider 切换应集中在 `bootstrap` 或边界适配区。
