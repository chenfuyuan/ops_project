# 评审清单

在认为生成代码完成之前，应先使用这份清单自检。

## 边界检查

- 新代码是否放在了正确的顶层区域？
- 是否有业务核心文件直接依赖 SDK、HTTP client 或 ORM 实现？
- 轻量 node 的 `service.py` 是否只依赖业务定义的 ports / repositories？
- 复杂 node 是否通过 `facade.py` 暴露稳定入口，而不是让外部调用方深入 use case 或 infrastructure？
- 复杂 node 的独立业务行为是否拆到 `application/use_cases/`？
- 复杂 node 的 `domain/` 是否保持不依赖 infrastructure、capabilities、HTTP、ORM、SDK 或 provider？
- repository 是否按领域资源/聚合定义，而不是按 ORM record、mapper、事务等技术细节拆分？
- `interfaces/` 是否避免直接深入到 `business/**/infrastructure/*`？
- `capabilities/` 是否保持不依赖业务？
- `capabilities/` 是否避免吸收大纲、章节蓝图、章节生成等业务任务语义？
- `shared/` 是否保持不承载业务语义？
- `workflow/` 是否保持不包含外部实现细节？

## node 演进检查

- 当前 node 是否仍适合轻量结构，还是已经命中复杂 node 演进信号？
- 是否出现了多个独立业务行为、明确领域模型、聚合边界、状态流转、多 adapter 协作或跨 node 复用压力？
- 如果命中演进信号，是否优先评估 `facade + application/use_cases + domain + infrastructure` 结构？
- 行数、方法数、类数量是否只作为辅助信号使用，而不是机械拆分依据？
- 如果多个 node 共享稳定领域模型或 repository，是否评估 domain-level bounded context，而不是继续重复定义？

## 命名检查

- 目录和模块是否按领域或职责命名？
- 是否出现了 `misc`、`utils`、`common2`、`temp` 这类模糊名称？
- port 是否按业务能力命名，而不是按 vendor 或 transport 命名？
- repository 是否按领域资源或聚合命名？
- adapter 是否按职责与 provider 或 transport 角色命名？

## Workflow 与 state 检查

- `workflow/state.py` 是否仍然保持最小且边界清晰？
- node 的输入输出是否清晰，而不是传递一个不断膨胀的全局 state 对象？
- `node.py` 是否仍然是 workflow adapter，而不是业务逻辑承载层？
- 复杂 node 的 `node.py` 是否调用 facade，而不是直接调用 use case、repository 或 infrastructure？

## Facade / use case / domain 检查

- `facade.py` 是否只做入口、转发、依赖聚合和必要横切协调？
- `facade.py` 是否避免承载具体业务规则或完整业务行为实现？
- 每个 use case 是否对应一个清晰业务行为？
- use case 是否只做应用层编排，而不直接依赖 SDK、HTTP client、ORM session、provider 或 concrete adapter？
- 领域规则、不变量和状态转换是否位于 domain 边界内？
- 领域服务是否只承载无法自然归属单个实体/聚合的领域逻辑，而不是新的大 service？

## Infrastructure 检查

- `infrastructure/` 是否仍然是 adapter 层，而不是业务逻辑层？
- timeout、retry、auth、serialization 和 provider 细节是否都留在业务核心文件之外？
- 实现切换是否仍然集中在 `bootstrap`，而不是散落到业务代码中？
- 技术实现拆分是否没有反向改变 repository 或 domain 的领域边界？

## OpenSpec / pre_design 检查

- pre_design 是否显式评估架构影响，而不只是描述功能需求？
- proposal / design / tasks 是否承接 pre_design 中确认的架构边界？
- 如果需求影响稳定 AI 规则或样例，tasks 是否包含 `ai_docs` 更新？
- 是否评估了需求对顶层边界、node 内部结构、领域职责拆分和适配边界的影响？

## 测试检查

- 业务规则和 use case / service 是否能通过 port 或 repository 抽象上的 fake、stub 或 mock 来做单元测试？
- `infrastructure` 和 `interfaces` 是否在映射和边界行为重要的地方有集成测试覆盖？
- 每个新增或修改的 `capabilities` 对外方法是否都有对应的 test HTTP 接口和 `tests/http/` 手动请求示例？
- 架构约束是否能通过架构测试或等价机制进行检查？
- 复杂 node 的 domain 依赖方向是否有测试或 review checklist 守护？

## 变更完成检查

- 每次完成一个 change 后，是否已运行项目 CI 等价检查并确认通过？
- 如具备明确授权、目标环境和命令，是否已执行 CD / Docker 部署验证并确认无报错？
- 如果 CD / Docker 部署会影响共享环境、远端服务或需要凭证，是否已先向用户确认目标和命令？

## 编码表达与可观测性检查

- 新增或显著改造的核心模块是否具备模块级说明，能解释职责、输入输出边界和不负责的事项？
- 对外类、公开函数、业务服务方法、facade 方法、use case、repository 协议和 adapter 实现是否具备必要 docstring？
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
- `business/**/domain/repositories.py`
- `business/**/ports.py`
- `business/**/infrastructure/*`
- `business/**/facade.py`

## 常见反模式提醒

- 不要把 `capabilities` 做成伪共享业务层。
- 不要让业务逻辑下沉到 `infrastructure/`。
- 不要让 facade 或 service 直接调用 SDK、HTTP client、RPC client 或 ORM。
- 不要让复杂 node 的 facade 重新变成大 service。
- 不要把 use case 按技术步骤机械拆碎。
- 不要把 repository 做成按技术表或 mapper 拆分的 DAO 集合。
- 不要通过 `shared/` 传播业务耦合。
- 不要让 workflow 层承载业务实现。
- 不要把 workflow state 变成隐式万能上下文。
- 不要在业务代码中分散做实现选择，local / remote / mock / provider 切换应集中在 `bootstrap` 或边界适配区。
