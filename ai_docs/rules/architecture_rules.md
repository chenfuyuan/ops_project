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

- 承载 workflow、node、业务实体、业务规则、用例编排，以及业务自己定义的 ports / repository 抽象。
- 通过领域抽象 + infrastructure adapter 访问 capabilities、外部系统和存储。
- 将业务语言保留在 node 的 facade、application、domain、rules、repositories 和 ports 中。

不要：
- 在业务核心文件中直接放入供应商 SDK、ORM 实现或 HTTP client。
- 让 facade、use case、domain model、domain rule 或 repository 抽象绕过业务边界直接调用具体 adapter。

### `capabilities/`

- 承载可复用、无业务语义的通用能力。
- 统一 provider 差异并暴露稳定契约。
- 默认采用“根包稳定导出 + facade 对外入口 + contracts 对外契约 + 内部 service + providers 实现”的结构。

不要：
- 依赖 `business/`。
- 以“共享能力”为名隐藏业务规则。
- 将 provider 特有字段泄漏到面向业务的契约中。
- 让外部调用方直接依赖 capability 内部实现文件路径。
- 吸收大纲、章节蓝图、章节生成等业务任务语义。

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

## business node 渐进式演进模型

business node 不应一开始全部强制使用完整 DDD 目录，也不应在复杂后继续向单一 `service.py` 或任意单文件堆叠逻辑。默认采用三档渐进模型：

```text
轻量 node -> 复杂 node 轻量 DDD -> domain-level bounded context
```

### Level 1：轻量 node

适用于业务行为少、领域状态简单、没有明确聚合边界、没有多 adapter 协作压力的 node。可使用平铺结构：

```text
business/<domain>/nodes/<unit>/
├─ node.py
├─ service.py 或 facade.py
├─ dto.py
├─ entities.py
├─ rules.py
├─ ports.py
└─ infrastructure/
```

轻量 node 可以继续使用 `service.py` 作为简单业务编排入口，但它不应被复杂 node 继续模仿为“所有业务行为都放这里”。

### Level 2：复杂 node 轻量 DDD

当 node 出现多个独立业务行为、明确领域模型、聚合边界、状态流转、多 adapter 协作或领域复用压力时，应优先演进为：

```text
business/<domain>/nodes/<unit>/
├─ facade.py
├─ node.py
├─ application/
│  ├─ dto.py
│  └─ use_cases/
├─ domain/
│  ├─ models.py
│  ├─ rules.py
│  ├─ services.py
│  └─ repositories.py
└─ infrastructure/
```

职责约定：
- `facade.py`：node 对外稳定入口，负责转发、依赖聚合、日志上下文、异常协调、事务或幂等等横切协调；不承载具体业务规则或完整业务行为实现。
- `application/use_cases/`：一个独立业务行为一个 use case，负责应用层编排，调用领域模型、规则、repository 抽象和外部 port。
- `application/dto.py`：应用层 command、query、result DTO；HTTP response model 可以保留在边界层，除非确实是应用层稳定结果。
- `domain/models.py`：聚合、实体、值对象和领域枚举。
- `domain/rules.py`：领域规则、不变量和状态转换校验。
- `domain/services.py`：无法自然归属单个实体或聚合的领域逻辑；不得成为新的大 service。
- `domain/repositories.py`：按领域资源或聚合定义 repository 抽象。
- `infrastructure/`：实现 repository、AI adapter、外部系统 adapter、协议映射、prompt/schema、错误转换和 provider 映射。
- `node.py`：workflow-facing adapter，只负责把 workflow state 映射为 facade 输入，再把结果写回最小 state。

### Level 3：domain-level bounded context

只有当同一业务域内多个 node 共享稳定领域模型、repository 或领域服务时，才评估上移到 domain-level bounded context，例如：

```text
business/<domain>/
├─ domain/
├─ application/
├─ nodes/
├─ infrastructure/
└─ workflow/
```

不要因为预期未来会复用就提前抽出 domain-level；必须等共享领域概念已经在多个 node 中稳定出现。

## 演进判断规则

演进判断必须优先基于业务/领域职责信号，而不是技术细节或数字阈值。

优先信号：
- 出现新的独立业务行为，而不是已有行为内部步骤。
- 出现明确领域模型、聚合根、值对象、领域不变量或状态流转。
- 出现新的领域资源获取 / 保存边界。
- 出现多个 adapter 或外部协作，且业务编排开始复杂化。
- 多个 node 开始共享同一批领域模型、规则、repository 或领域服务。

辅助信号：
- 单文件行数明显增长。
- 公开方法数量增加。
- 主要类数量增加。
- 单个函数或 use case 难以在一次阅读中理解。

辅助信号只触发“评估是否演进”，不得成为唯一拆分依据。命中辅助信号后，应先判断背后是否存在业务/领域职责分化。

## repository 与 port 的领域边界

repository 的核心作用是领域模型或聚合的获取与保存边界。repository 抽象应按业务资源或聚合命名，例如 `OutlineRepository`，而不是按 ORM 表、mapper、事务或查询技术细节拆分。

规则：
- repository 抽象属于业务/领域语言，可以放在复杂 node 的 `domain/repositories.py` 中。
- repository 方法表达领域需要什么数据，不暴露 SQLAlchemy、HTTP、SDK 或 provider 类型。
- ORM record、mapper、session、事务和查询优化属于 `infrastructure/` 实现细节。
- 不因 repository 实现文件里存在 record、mapper 或事务逻辑，就自动拆成多个 repository 抽象。
- 如果技术实现变大，可以在 `infrastructure/` 内部辅助拆分，但不得反向改变 repository 的领域边界。

port 用于表达业务对外部能力的依赖。对于非持久化外部能力，仍应按业务需要命名 port；对于领域资源获取与保存，优先使用 repository 语义。

## workflow 与 node 的职责

### `workflow/`
负责流程拓扑、registry、edges 和 state 流转。

不要：
- 实现业务规则。
- 直接调用外部 SDK 或存储实现。
- 让 `state.py` 膨胀成无边界的全局上下文。

### `node.py`
- 将 workflow state 适配为当前 node facade 的输入。
- 调用 node facade，而不是直接深入 use case、repository 或 infrastructure。
- 将结果映射回 workflow state。

### `facade.py`
- 是复杂 node 对外稳定入口。
- 面向 HTTP、workflow、bootstrap 等外部调用方暴露稳定方法。
- 可做横切协调，不写具体业务规则。

### `application/use_cases/`
- 一个业务行为一个 use case。
- 只依赖领域模型、领域规则、repository 抽象和业务 port。
- 不直接依赖 SDK、HTTP client、ORM session、provider 或 capability 实现。

### `domain/`
- 承载纯业务语义。
- 不依赖 `infrastructure/`、`capabilities/`、HTTP、ORM、SDK 或 provider。

### `infrastructure/`
- 实现 adapter、翻译、协议映射、AI prompt/schema、错误转换和持久化集成。

不要：
- 承载业务决策。
- 把业务语义下沉到 capability。

## 必须遵循的调用链

轻量 node 推荐调用链：

```text
interfaces/workflow -> business node/service -> ports/repositories -> infrastructure/* -> capabilities/external systems/storage
```

复杂 node 推荐调用链：

```text
interfaces/workflow -> business node/facade -> application/use_cases -> domain/repositories or ports -> infrastructure/* -> capabilities/external systems/storage
```

业务代码不能绕过领域抽象直接调用具体 adapter。
`interfaces` 不能绕过业务入口深入业务侧 `infrastructure`。
`workflow` 代码不能直接进行基础设施调用。

## 允许的依赖方向

```text
interfaces  -> business
business application -> business domain
business domain -> shared（仅低语义基础类型）
business infrastructure -> business domain / capabilities / external systems / storage
capabilities -> shared
bootstrap -> all（composition only）
```

## 禁止的依赖方向

- `capabilities -> business`
- `shared -> business`
- `interfaces -> business/**/infrastructure/*`
- `facade.py -> concrete adapter`（除非仅在 composition 边界中由 bootstrap 完成）
- `application/use_cases -> concrete adapter`
- `domain -> infrastructure / capabilities / HTTP / ORM / SDK / provider`
- `workflow -> external SDK / remote client / storage implementation`
- 业务核心文件直接依赖供应商 SDK、HTTP client 或 ORM 实现

## OpenSpec 与 pre_design 架构设计要求

后续任何需求进入 pre_design 或 OpenSpec 流程时，必须显式考虑架构设计，而不是只描述功能、接口或任务清单。

pre_design / proposal / design / tasks 应根据需求复杂度评估：
- 是否影响 `business / capabilities / interfaces / shared / bootstrap` 顶层边界。
- 是否影响 business node 内部结构。
- 是否命中 node 演进信号。
- 是否出现新的领域模型、聚合、repository、领域服务或外部 port。
- 是否需要同步更新 `ai_docs`。

如果需求影响稳定 AI 架构规则或样例，OpenSpec tasks 必须包含对应 `ai_docs` 更新项。

## 高敏感区域

以下区域的改动需要更严格的审查：
- `shared/`
- `capabilities/`
- `workflow/state.py`
- `business/**/domain/repositories.py`
- `business/**/ports.py`
- `business/**/infrastructure/*`
- `business/**/facade.py`

## 快速放置判断

- 带业务语义：`business/`
- 可复用的中性能力：`capabilities/`
- 协议入口：`interfaces/`
- 稳定、低语义的共享构件：`shared/`
- 装配与实现选择：`bootstrap/`
- 复杂 node 独立业务行为：`business/<domain>/nodes/<unit>/application/use_cases/`
- 复杂 node 领域模型与规则：`business/<domain>/nodes/<unit>/domain/`
- 复杂 node 具体适配实现：`business/<domain>/nodes/<unit>/infrastructure/`
