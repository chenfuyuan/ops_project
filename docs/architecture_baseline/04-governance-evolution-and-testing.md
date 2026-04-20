# 治理、演进、命名与测试

- 来源文档：`docs/new_project_architecture_baseline_clean.md`
- 关联文档：`00-overview.md`、`01-top-level-modules.md`、`03-anti-corruption-and-dependencies.md`

---

## 1. 本文件回答的问题

本文件用于回答以下问题：

- 这套架构需要重点防止哪些腐化趋势；
- 应该用哪些治理手段长期守住边界；
- 项目未来如何从单体内部模块化演进到独立服务；
- 命名规范和测试策略应该如何统一；
- 哪些反模式需要明确禁止。

---

## 2. 架构治理目标

该基线不是一次性目录模板，而是一组需要长期守护的规则。重点要防止以下趋势：

- `shared` 逐步演化为杂物间；
- `capabilities` 逐步演化为伪共享业务层；
- `service.py` 逐步绕过 `ports` 直接调用实现；
- `workflow state` 逐步演化为无边界全局上下文；
- 运行时实现选择逐步回流到业务代码内部。

---

## 3. 推荐守护手段

- 通过 import 规则限制模块依赖方向；
- 通过架构测试校验 `service.py` 不得直接依赖 SDK / ORM / HTTP client；
- 通过代码审查检查新增代码是否误入 `shared` 或 `capabilities`；
- 通过模块 owner 或责任人机制守护共享层与能力层边界；
- 通过统一装配与测试替身校验接口隔离是否仍然有效。

---

## 4. 高敏感评审区域

新增模块或新代码进入以下区域时，应提高评审标准：

- `shared/`
- `capabilities/`
- `workflow/state.py`
- `business/**/ports.py`
- `business/**/infrastructure/*`

这些区域与边界定义、架构演进和依赖约束强相关，进入门槛应高于普通业务实现文件。

---

## 5. 微服务演进策略

本架构默认支持以下演进路径：

### 阶段 1：单体内部模块化

- `capabilities` 以本地模块形态存在；
- 业务通过 `ports + infrastructure` 调用本地能力。

### 阶段 2：能力独立部署

- 将某个 `capability` 拆分为独立服务；
- 业务侧仅替换 `infrastructure` 实现；
- `ports` 与 `service.py` 不变。

### 阶段 3：跨进程通信增强

- 从本地方法调用演进为 HTTP / RPC / MQ；
- 由 `infrastructure` 处理序列化、鉴权、重试、超时等问题。

### 阶段 4：按业务边界继续拆分

- 如果业务域进一步膨胀，可继续按业务域拆分服务；
- 当前节点结构与端口边界仍可保留。

### 关键前提

只有当业务侧已经完成依赖抽象隔离时，这种演进才会保持较低成本。

---

## 6. 命名规范

### 6.1 目录命名

- 业务目录采用业务能力或业务单元命名；
- 通用能力目录采用中性能力命名；
- 避免使用 `utils`、`common2`、`misc`、`temp` 之类模糊名称。

### 6.2 端口命名

端口命名必须表达**业务所需能力**，而不是技术手段。

推荐：

- `ContextReader`
- `ContentWriter`
- `ArtifactRepository`

不推荐：

- `HttpPort`
- `OpenAIAdapterPort`
- `SDKGateway`

### 6.3 基础设施实现命名

实现类名应表达“如何接入某类依赖”，例如：

- `LocalCapabilityContextReader`
- `HttpCapabilityContextReader`
- `SqlArtifactRepository`
- `ExternalValidationClient`

---

## 7. 测试策略

### 7.1 单元测试

重点测试：

- `service.py`
- `rules.py`
- `entities.py`

测试方式：

- 通过 `ports` 替身注入 fake / stub / mock；
- 不依赖真实三方服务；
- 不依赖真实网络。

### 7.2 集成测试

重点测试：

- `infrastructure/`
- `capabilities/infrastructure/`
- `interfaces/`

验证内容：

- 协议映射正确性；
- 外部依赖连接稳定性；
- 数据映射与异常转换是否符合预期；
- 重试、超时、鉴权、错误翻译等横切策略是否符合预期。

### 7.3 端到端测试

从 `interfaces` 入口验证完整调用链。

### 7.4 架构测试

建议补充面向结构约束的自动化测试，例如：

- 禁止 `service.py` 直接 import 供应商 SDK；
- 禁止 `interfaces` 直接依赖业务侧 `infrastructure`；
- 禁止 `capabilities` 依赖 `business`；
- 禁止 `shared` 引入业务语义模块；
- 检查业务调用是否遵循 `service -> ports -> infrastructure` 链路。

---

## 8. 反模式与禁止事项

### 8.1 禁止把 `capabilities` 做成“伪共享业务层”

凡是带明显业务语义、只服务单一业务、没有复用价值的代码，不得提前进入 `capabilities`。

### 8.2 禁止业务逻辑下沉到 `infrastructure`

`infrastructure` 只做适配，不做业务决策。

### 8.3 禁止 `service.py` 直接调用 SDK / HTTP / ORM

这会破坏业务边界，导致后期替换成本陡增。

### 8.4 禁止通过 `shared` 传播业务耦合

`shared` 不能成为跨模块偷懒依赖的通道。

### 8.5 禁止工作流层承载业务实现

工作流只负责编排，不负责业务规则和外部依赖细节。

### 8.6 禁止为所有模块强制重型分层

保持轻量结构，按复杂度演进，而不是按理想模型预先堆叠层次。

### 8.7 禁止把工作流状态当成隐式万能上下文

不能用不断扩张的全局状态替代清晰的节点边界与输入输出契约。

### 8.8 禁止在业务代码中分散做实现选择

本地 / 远端 / mock / provider 切换应集中在 `bootstrap` 或边界适配区，不应渗透到业务用例。

---

## 9. 推荐初始化骨架

```text
project_scaffold/
├─ app/
│  ├─ business/
│  │  └─ domain_a/
│  │     ├─ workflow/
│  │     │  ├─ graph.py
│  │     │  ├─ state.py
│  │     │  ├─ registry.py
│  │     │  └─ edges.py
│  │     ├─ domain_services/
│  │     └─ nodes/
│  │        └─ unit_x/
│  │           ├─ node.py
│  │           ├─ service.py
│  │           ├─ dto.py
│  │           ├─ entities.py
│  │           ├─ rules.py
│  │           ├─ ports.py
│  │           └─ infrastructure/
│  │              ├─ capability_adapter.py
│  │              ├─ external_service.py
│  │              └─ repository.py
│  ├─ capabilities/
│  │  └─ capability_x/
│  │     ├─ contracts.py
│  │     ├─ dto.py
│  │     ├─ service.py
│  │     └─ infrastructure/
│  │        └─ provider_a.py
│  ├─ interfaces/
│  │  └─ http/
│  ├─ shared/
│  │  ├─ kernel/
│  │  ├─ infra/
│  │  └─ events/
│  └─ bootstrap/
```

该骨架具备以下特征：

- 顶层边界清晰；
- 节点内部轻量但有明确防腐能力；
- 能力组件可复用且可独立部署；
- 支持工作流编排；
- 支持后续演进为微服务；
- 为领域内共享逻辑预留自然落点；
- 能通过架构治理手段持续守护边界。

---

## 10. 架构决策摘要

1. 节点内部不强制四层架构，采用轻量平铺结构；
2. 业务依赖通过 `ports + infrastructure` 隔离；
3. `capabilities` 只承载通用能力；
4. 业务专属外部依赖允许留在业务侧，但必须通过节点内 `infrastructure` 适配；
5. 工作流负责编排，节点负责实现；
6. `bootstrap` 统一装配实现；
7. 领域内共享逻辑优先留在业务域内部；
8. 共享层与能力层采用准入治理，避免长期腐化。

---

## 11. 一句话边界定义

- `business`：承载业务语义与业务流程实现；
- `workflow`：承载业务流程拓扑与状态流转；
- `node.py`：节点入口适配器；
- `service.py`：节点业务用例编排；
- `ports.py`：业务定义的能力接口；
- `infrastructure/`：端口实现与防腐适配区；
- `domain_services/`：业务域内部共享、但不跨业务复用的领域级逻辑区；
- `capabilities`：无业务语义的通用能力组件；
- `interfaces`：外部协议入口；
- `shared`：稳定低语义共享基础模块；
- `bootstrap`：运行时装配与实现选择中心。
