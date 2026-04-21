# 架构规则

本文件将仓库的架构规则整理为适合 AI 使用的参考说明。

## 顶层边界
`app/` 下的代码必须归入以下区域之一：

- `business/`：唯一允许承载业务语义的顶层区域。
- `capabilities/`：跨业务复用、使用中性语言、且不带业务语义的通用能力。
- `interfaces/`：HTTP 等外部协议入口。
- `shared/`：稳定、低业务语义的内核与基础设施构件。
- `bootstrap/`：运行时装配、依赖组装与实现选择。

决定代码位置时，应优先按语义归属判断，而不是按技术类型判断。

## 各区域可以做什么
### `business/`
- 承载 workflow、node、业务实体、业务规则、用例编排，以及业务自己定义的 ports。
- 通过 `ports + infrastructure` 访问 capabilities、外部系统和存储。
- 将业务语言保留在 `service.py`、`entities.py`、`rules.py` 和 `ports.py` 中。

不要：
- 在业务核心文件中直接放入供应商 SDK、ORM 实现或 HTTP client。
- 让 `service.py` 绕过 `ports` 直接调用具体 adapter。

### `capabilities/`
- 承载可复用、无业务语义的通用能力。
- 统一 provider 差异并暴露稳定契约。

不要：
- 依赖 `business/`。
- 以“共享能力”为名隐藏业务规则。
- 将 provider 特有字段泄漏到面向业务的契约中。

### `interfaces/`
- 负责协议输入解析、边界处理，并调用业务入口。

不要：
- 直接深入到 `business/**/infrastructure/*`。
- 在这里实现业务规则或外部依赖适配。

### `shared/`
- 承载低语义、跨上下文复用的内核类型和基础设施工具。

不要：
- 存放业务 DTO、业务枚举、业务规则，或无处安放的“杂项”代码。
- 把 `shared/` 变成杂物间。

### `bootstrap/`
- 负责装配依赖和选择实现。
- 处理 local / remote / mock / provider 等实现切换。

不要：
- 承载业务逻辑。
- 被其他层反向依赖。

## 标准业务结构
一个业务域通常应采用如下结构：

```text
business/<domain>/
├─ workflow/
├─ domain_services/
└─ nodes/
   └─ <unit>/
      ├─ node.py
      ├─ service.py
      ├─ dto.py
      ├─ entities.py
      ├─ rules.py
      ├─ ports.py
      └─ infrastructure/
```

并不是每个文件都必须存在，但职责边界必须保持一致。

## workflow 与 node 的职责
### `workflow/`
负责流程拓扑、registry、edges 和 state 流转。

不要：
- 实现业务规则。
- 直接调用外部 SDK 或存储实现。
- 让 `state.py` 膨胀成无边界的全局上下文。

### `node.py`
- 将 workflow state 适配为 node 输入。
- 调用 `service.py`。
- 将结果映射回 workflow state。

### `service.py`
- 编排节点级业务用例。
- 组合 entities、rules 和 port 调用。

不要：
- 直接调用 SDK、HTTP client、RPC client 或 ORM 实现。
- 承担 timeout、retry、transport 或 provider 切换等职责。

### `ports.py`
- 用业务语言定义接口。
- 表达业务需要什么，而不是技术怎么做。

### `infrastructure/`
- 实现 adapter、翻译、协议映射和持久化集成。

不要：
- 承载业务决策。

## 必须遵循的调用链
推荐调用链：

```text
interfaces -> business workflow/node -> service.py -> ports.py -> infrastructure/* -> capabilities/external systems/storage
```

业务代码不能绕过 `ports`。
`interfaces` 不能绕过业务边界。
`workflow` 代码不能直接进行基础设施调用。

## 允许的依赖方向
```text
interfaces  -> business
business    -> shared
business core -> ports
business infrastructure -> capabilities / external systems / storage
capabilities -> shared
bootstrap   -> all (composition only)
```

## 禁止的依赖方向
- `capabilities -> business`
- `shared -> business`
- `interfaces -> business/**/infrastructure/*`
- `service.py -> concrete adapter`
- `workflow -> external SDK / remote client / storage implementation`
- 业务核心文件直接依赖供应商 SDK、HTTP client 或 ORM 实现

## 高敏感区域
以下区域的改动需要更严格的审查：
- `shared/`
- `capabilities/`
- `workflow/state.py`
- `business/**/ports.py`
- `business/**/infrastructure/*`

## 快速放置判断
- 带业务语义：`business/`
- 可复用的中性能力：`capabilities/`
- 协议入口：`interfaces/`
- 稳定、低语义的共享构件：`shared/`
- 装配与实现选择：`bootstrap/`
