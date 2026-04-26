## Context

大纲生成 MVP 已经完成，并以 `app/business/novel_generate/nodes/outline/` 作为 `novel_generate` 业务域下的首个业务 node。当前结构遵循了既有 `service.py / entities.py / rules.py / ports.py / infrastructure/` 模式，但 `OutlineNodeService` 已经聚合了创建 seed、生成 skeleton、确认 skeleton、展开 volume、编辑 volume/chapter、聚合 outline 等多个独立业务行为。

这说明问题不只是 outline 的文件体量，而是项目缺少一套对所有 business node 生效的渐进式架构演进规则。后续如果继续让 AI 按旧样例生成代码，复杂 node 会倾向于把行为继续堆进单一 `service.py` 或其他单文件。

本设计受 `pre_design.md` 约束：采用方案 A，即渐进式轻量 DDD node 架构；拆分依据必须以业务/领域职责为主；repository 是领域模型/聚合的获取与保存边界；AI gateway 必须保持中性能力；后续 pre_design / OpenSpec 流程必须显式考虑架构设计。

## Goals / Non-Goals

**Goals:**

- 在 `ai_docs` 中建立 business node 的渐进式轻量 DDD 演进规则。
- 定义简单 node、复杂 node、domain-level bounded context 三个演进层级的判断方式。
- 定义复杂 node 的目标结构：`facade.py`、`application/use_cases/`、`domain/`、`infrastructure/`、`node.py`。
- 明确 facade、use case、domain model/rule/service/repository、infrastructure adapter、workflow node 的职责边界。
- 将“pre_design / OpenSpec 流程必须显式考虑架构设计”沉淀进 AI 规则。
- 将 outline 作为首个应用对象，迁移到复杂 node 目标结构，同时保持现有业务行为、HTTP API 和 AI gateway 契约不变。

**Non-Goals:**

- 不把整个 `novel_generate` 立即升级为 domain-level bounded context。
- 不按 ORM record、mapper、事务等技术细节主导 repository 抽象拆分。
- 不改变现有大纲生成 HTTP API、数据库业务数据模型或 AI gateway capability 契约。
- 不把 outline、章节蓝图、章节生成等业务语义下沉到 `capabilities/ai_gateway`。
- 不把行数、方法数、类数量写成唯一硬性演进规则。
- 不保留旧 `service.py` 作为继续承载业务逻辑的兼容壳。

## Decisions

### 决策 1：采用渐进式轻量 DDD node 架构

业务 node 不一开始强制完整 DDD 目录，而是按复杂度演进：

```text
简单 node -> 复杂 node 轻量 DDD -> domain-level bounded context
```

简单 node 可以保持轻量结构，避免过度工程化。复杂 node 一旦出现多个独立业务行为、明确领域模型、状态流转、聚合边界、多 adapter 协作或跨 node 复用压力，就应优先采用：

```text
nodes/<unit>/
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

只有当多个 node 共享稳定领域模型、repository 或领域服务时，才评估上移到 `business/<domain>/domain/` 这类 domain-level bounded context。

替代方案是继续增强当前平铺结构，或立即抽出整个 `novel_generate` 的领域层。前者只能缓解 `service.py` 膨胀，后者在当前只有 outline 稳定落地时过早。因此选择 node-level 渐进式演进。

### 决策 2：`facade.py` 是 node 对外入口

复杂 node 的对外入口使用 `facade.py`，不再以 `service.py` 表达“所有业务逻辑都在这里”。facade 对 HTTP、workflow、bootstrap 暴露稳定调用面，允许承担依赖聚合、转发、日志上下文、统一异常转换、事务或幂等等横切协调。

facade 不承载具体业务规则，也不实现单个业务行为的完整流程。业务行为进入 use case，领域规则进入 domain。

替代方案是保留 `service.py` 作为入口，但该名称已经在 outline 中表现出“继续堆业务方法”的倾向，不适合作为复杂 node 的长期标准。

### 决策 3：一个业务行为一个 use case

复杂 node 的 `application/use_cases/` 按业务行为拆分。以 outline 为例，应至少包含：

- `create_seed`
- `get_seed`
- `generate_skeleton`
- `confirm_skeleton`
- `expand_volume`
- `update_volume`
- `update_chapter`
- `get_outline`

use case 负责应用层编排：接收 command/query DTO，调用领域模型、领域规则、repository 抽象和外部 port，返回应用层结果。use case 不直接依赖 SDK、HTTP client、ORM session、provider 或 capability 实现。

替代方案是按技术类型拆分 use case 或按文件行数拆分，这会偏离业务行为边界，因此不采用。

### 决策 4：domain 承载领域模型、规则、领域服务和 repository 抽象

复杂 node 的 `domain/` 是纯业务语义边界，不依赖 `infrastructure/`、`capabilities/`、HTTP、ORM、SDK 或 provider。

repository 抽象放在 domain 中，因为 repository 表达的是领域模型/聚合的获取与保存边界。例如 `OutlineRepository` 表达“获取/保存 outline 相关聚合”，不是“访问几张 SQL 表”。因此 repository 的命名和拆分依据是领域资源或聚合，而不是 ORM record、mapper、事务等技术细节。

领域服务只用于无法自然归属单个实体/聚合的领域逻辑，不能变成新的 service 大泥球。

### 决策 5：infrastructure 只做适配

复杂 node 的 `infrastructure/` 实现持久化、AI、外部系统等具体适配。它可以包含 SQLAlchemy record、mapper、prompt、schema、provider 映射、错误转换等实现细节，但这些技术组织不能反向决定 domain 抽象。

outline 的 AI adapter 必须继续把业务语义留在 business 层，并把领域模型翻译为 AI gateway 的中性 STRUCTURED 请求。`capabilities/ai_gateway` 不吸收大纲、章节蓝图或章节生成等业务语义。

### 决策 6：OpenSpec / pre_design 必须包含架构设计评估

本 change 不仅更新代码结构，还要更新 AI 工作流程规则。后续任何需求进入 pre_design 或 OpenSpec 流程时，必须显式评估：

- 是否影响 `business / capabilities / interfaces / shared / bootstrap` 顶层边界。
- 是否影响 business node 内部结构。
- 是否命中 node 演进信号。
- 是否出现新的领域模型、聚合、repository 或领域服务。
- 是否需要同步更新 `ai_docs`。

proposal/design/tasks 必须承接 pre_design 中确认的架构边界，不能只生成 CRUD 式功能任务清单。

## Risks / Trade-offs

- [目录和概念增多] → 通过渐进式规则缓解：简单 node 不强制完整 DDD，只有复杂 node 才升级。
- [facade 重新膨胀] → 在 `ai_docs` 中明确 facade 可做横切协调但不得承载业务规则；业务行为必须进入 use case。
- [use case 过度碎片化] → 拆分依据使用业务行为，不按技术步骤或行数机械拆分。
- [repository 被技术 DAO 化] → 在规则和样例中明确 repository 是领域模型/聚合获取保存边界，技术细节只留在 infrastructure 内部。
- [过早抽出 domain-level bounded context] → 明确只有多个 node 共享稳定领域概念时才评估上移，outline 当前先在 node 内演进。
- [AI 规范更新后与旧样例冲突] → 更新或替换 `standard_service.md` 等旧样例，并新增 node 演进样例，避免后续 AI 继续模仿旧结构。
- [重构影响现有测试] → 保留 HTTP integration 与 repository integration 测试，调整 unit test 到 use case / facade 边界，并用架构测试守护新边界。

## Migration Plan

1. 更新 `ai_docs/rules/architecture_rules.md`，新增渐进式 node 演进规则、复杂 node 目标结构、职责边界和 OpenSpec 架构设计检查要求。
2. 新增或更新 `ai_docs/examples/`：补充 node 演进样例、facade/use case 样例、repository 领域边界说明和 workflow node 调用 facade 的模式。
3. 重构 outline node：创建 `facade.py`、`application/use_cases/`、`domain/`、`infrastructure/persistence/`、`infrastructure/ai/`，迁移现有 service、entities、rules、ports、repository、ai adapter。
4. 更新 HTTP 和 bootstrap，使其依赖新的 outline facade。
5. 调整 outline 单元测试到 use case / facade 边界，保留 HTTP 和 repository 集成测试。
6. 新增或调整架构测试，守护复杂 node 的职责边界和 capability 中性边界。
7. 运行项目 CI 等价验证。

Rollback 策略：本变更主要是本地代码结构和 AI 文档更新，不涉及数据库迁移或外部 API 变更。如实现阶段出现问题，可以按文件级回退 outline 结构迁移，同时保留已确认的 ai_docs 规则或单独修正规则文档。

## Open Questions

- `standard_service.md` 是保留并标注为轻量 node 旧模式，还是重命名/替换为 facade/use case 样例，需要在实现 `ai_docs` 更新时根据实际文档组织决定。
- 是否新增架构测试来禁止复杂 node 继续新增 `service.py`，还是先以 ai_docs 规则和 review checklist 守护，需要在实现阶段评估测试稳定性。
