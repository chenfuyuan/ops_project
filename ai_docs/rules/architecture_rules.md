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
- 默认采用“根包稳定导出 + facade 对外入口 + contracts 对外契约 + 内部 service + providers 实现”的结构。

不要：
- 依赖 `business/`。
- 以“共享能力”为名隐藏业务规则。
- 将 provider 特有字段泄漏到面向业务的契约中。
- 让外部调用方直接依赖 capability 内部实现文件路径。

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

## `capabilities/` 标准结构
所有 capability 默认采用以下结构：

```text
capabilities/<capability>/
├─ __init__.py
├─ facade.py
├─ service.py
├─ errors.py
├─ contracts/
│  ├─ __init__.py
│  ├─ request.py
│  ├─ response.py
│  └─ models.py
└─ providers/
   ├─ __init__.py
   ├─ base.py
   └─ <provider>_provider.py
```

职责约定：
- `__init__.py`：统一对外导出稳定入口；外部优先从根包 import
- `facade.py`：capability 对外访问入口，负责暴露稳定方法与屏蔽内部实现细节
- `service.py`：capability 内部编排层，不作为外部稳定依赖面
- `errors.py`：对外稳定错误类型
- `contracts/request.py`：公开输入类型
- `contracts/response.py`：公开输出类型
- `contracts/models.py`：request / response 共用的公开模型、枚举和值对象
- `providers/base.py`：provider 抽象约束
- `providers/*_provider.py`：各 provider 的具体实现

外部依赖约束：
- 推荐外部调用方只依赖 capability 根包导出，例如 `from app.capabilities.<capability> import XxxFacade, XxxRequest, XxxResponse`
- 不要让外部调用方直接依赖 `service.py`、`contracts/request.py`、`providers/*` 等内部文件路径
- capability 内部允许继续拆分文件，但应优先通过 `__init__.py` 保持外部导入面稳定

命名约束：
- 对外入口优先使用 `facade.py`，避免使用语义模糊且易与 `interfaces/` 混淆的 `api/`
- 对外公开类型优先使用 `contracts/`，避免将 facade、request、response、provider 混放在同一概念目录中
- `models.py` 仅用于公开契约中的公共组成件；如果不存在共享公开模型，可以保留为空壳或在确有必要时再补充内容

裁剪约束：
- 允许在单个 capability 极小且尚未用到某类对象时，暂时保留空文件或占位文件，以维持统一结构
- 如果团队后续明确决定允许小型 capability 缩减目录，再单独更新本规则；在此之前，不建议按 capability 大小使用不同目录模板

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

## `domain_services/` 的适用边界
`domain_services/` 是可选目录，只用于承载同一业务域内多个节点共享、但不具备跨业务复用价值的领域级逻辑。

适合放入：
- 同一业务域内多个节点共用的领域策略与组装逻辑
- 领域级工厂、策略集合、校验器组合
- 仅在当前业务域内有意义、不适合进入 `shared` 或 `capabilities` 的组件

不适合放入：
- 纯通用能力，应进入 `capabilities`
- 全局基础设施，应进入 `shared`
- 单个节点私有逻辑，应保留在节点内部
- 对外部系统的直接适配，应优先放在节点内 `infrastructure/`

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
