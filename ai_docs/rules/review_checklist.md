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
- 每个新增或修改的 `capabilities` 对外方法是否都有对应的 test HTTP 接口和 `tests/http/` 手动请求示例？
- 架构约束是否能通过架构测试或等价机制进行检查？

## 变更完成检查
- 每次完成一个 change 后，是否已运行项目 CI 等价检查并确认通过？
- 如具备明确授权、目标环境和命令，是否已执行 CD / Docker 部署验证并确认无报错？
- 如果 CD / Docker 部署会影响共享环境、远端服务或需要凭证，是否已先向用户确认目标和命令？

## 编码表达与可观测性检查
- 新增或显著改造的核心模块是否具备模块级说明，能解释职责、输入输出边界和不负责的事项？
- 对外类、公开函数、业务服务方法、port 协议和 adapter 实现是否具备必要 docstring？
- 复杂分支、隐含前提、顺序要求、状态约束、历史兼容和外部协议约束是否有就近注释解释原因？
- 是否避免了只重复代码字面含义的低价值注释？
- 关键流程进入 / 完成、重要状态变化、外部调用前后、重试 / 降级 / 跳过 / 回退、异常转换和失败路径是否具备适当日志？
- 日志是否包含可排障的动作、对象、结果、阶段、资源标识和失败原因？
- 日志是否避免记录密码、token、密钥、authorization header、原始凭证、完整请求 / 响应体和未脱敏个人敏感信息？
- 高频路径是否避免无意义 `info` 噪音，并优先使用摘要日志或 `debug` 日志？

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
