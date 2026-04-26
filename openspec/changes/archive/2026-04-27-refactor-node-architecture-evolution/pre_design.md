# Pre-design: 渐进式 node 架构演进规范与 outline 重构

## Problem framing

当前大纲生成已经完成 MVP，但暴露出一个更通用的架构问题：复杂业务 node 的职责边界没有足够显式，也缺少可被 AI 持续遵守的渐进式演进规则。

`outline` 节点现在虽然遵循了 `service.py / entities.py / rules.py / ports.py / infrastructure/` 的基础结构，但随着功能增长，`OutlineNodeService` 已经同时承担多个独立业务行为：

- 创建 seed
- 获取 seed
- 生成 skeleton
- 确认 skeleton
- 展开 volume
- 编辑 volume
- 编辑 chapter
- 聚合 outline

这些行为属于同一个 node，但不是同一个业务行为。继续把它们放在一个 service 中，会导致后续复杂 node 都倾向于把业务编排堆进单文件。

真正要解决的问题不是“某个文件太长”，而是：为所有 business node 建立一套可渐进演化的轻量 DDD 架构规则，并将这套演进规则沉淀进 `ai_docs`，让后续 AI 生成和重构代码时能持续遵守。

## Goals

本 change 必须达成：

1. 建立 business node 的渐进式轻量 DDD 演进规则
   - 简单 node 不强制完整 DDD 目录。
   - 复杂 node 按 `facade + application/use_cases + domain + infrastructure` 演进。
   - 演进触发依据是业务/领域复杂度，而不是单纯文件长度。
   - 数字阈值只作为辅助提醒。

2. 将渐进式演进规则沉淀到 AI 规则
   - 更新 `ai_docs/rules/architecture_rules.md`。
   - 必要时新增或更新 `ai_docs/examples/standard_node_evolution.md`。
   - 后续 AI 在生成或重构 node 时，应能判断：什么时候保持轻量结构；什么时候升级到轻量 DDD；什么时候评估 domain-level bounded context；什么时候不能继续往 `service.py` 或单文件中堆逻辑。

3. 定义复杂业务 node 的目标结构
   - 采用渐进式轻量 DDD / Clean Architecture。
   - 复杂 node 采用 `facade + application/use_cases + domain + infrastructure`。
   - `facade.py` 是 node 对外稳定入口。
   - `application/use_cases/` 一个业务行为一个 use case。
   - `domain/` 承载领域模型、规则、领域服务和 repository 抽象。
   - `infrastructure/` 承载具体技术适配实现。
   - `node.py` 仅作为 workflow adapter。

4. 将“pre_design / OpenSpec 流程必须显式考虑架构设计”沉淀到 AI 规则
   - 后续任何需求进入 pre_design 或 OpenSpec 流程时，不能只描述功能需求、接口和任务清单。
   - 必须显式评估架构影响、分层职责、演进路径，以及是否需要同步 AI 规范。

5. 以后续 outline 重构为首个应用对象
   - outline 是本规则的首个明确命中案例。
   - 后续实现时应将 outline 从当前 service-heavy 结构迁移到目标架构。
   - 但本 pre-design 阶段不直接编写实现代码。

## Non-goals

本 change 不做：

1. 不立即生成实现代码
   - 当前阶段只生成 `pre_design.md`。
   - 后续是否执行 outline 重构由用户决定。

2. 不把整个 `novel_generate` 立即提升为 domain-level bounded context
   - 现在只确认 node-level 轻量 DDD。
   - 只有多个 node 共享稳定领域模型、repository 或领域服务时，才评估 domain-level 演进。

3. 不按技术细节主导拆分 repository
   - repository 的核心职责是领域模型/聚合的获取与保存边界。
   - 不因为存在 ORM record、mapper、事务逻辑，就机械拆 repository。
   - 技术实现可以辅助组织，但不能反向决定领域边界。

4. 不让 AI gateway 吸收业务语义
   - 大纲、章节蓝图、章节生成等业务语义仍属于 `business`。
   - `capabilities/ai_gateway` 继续保持中性能力边界。

5. 不以数字阈值替代架构判断
   - 行数、方法数、类数量是辅助信号。
   - 真正的拆分依据是业务行为、领域模型、聚合边界、状态流转和复用边界。

6. 不把 OpenSpec 流程降级为功能清单生成器
   - 后续流程必须保留架构判断和边界设计。

## Requirement understanding

这次需求的本质是建立一套可持续约束 AI 编码行为的架构演进机制，而不是一次性的 outline 文件整理。

需要解决三类问题：

1. 复杂 node 如何组织
   - 简单 node 可以保持轻量结构。
   - 当 node 出现多业务行为、领域状态、聚合、多个 adapter 或复用压力时，应升级到轻量 DDD 结构。
   - 升级后的 node 以业务/领域职责为拆分依据，而不是按技术细节机械拆文件。

2. AI 以后如何判断是否该演进
   - 不能继续把新方法塞进 `service.py` 或任意单文件。
   - 需要显式判断：这是新的业务行为，还是已有行为的一部分；是否出现新的领域概念、聚合或状态流转；是否出现新的领域资源获取边界；是否多个 node 开始共享同一领域模型或规则。
   - 数字阈值只能作为提醒，不是最终判断依据。

3. OpenSpec / pre_design 如何纳入架构设计
   - 后续任何需求进入 pre_design 或 OpenSpec 时，不能只写功能变化。
   - 必须评估架构影响、分层职责、演进路径和是否需要同步 AI 规范。
   - proposal/design/tasks 不能绕过 pre_design 中已确认的架构边界。

## Constraints

后续设计与实现必须遵守：

1. 业务/领域职责优先
   - 拆分文件、目录和抽象时，先看业务行为、领域模型、聚合边界、状态流转和复用边界。
   - 技术复杂度只作为次级信号，不能主导领域边界。

2. repository 语义必须保持领域化
   - repository 是领域模型/聚合的获取与保存边界。
   - repository 抽象应按领域资源或聚合命名。
   - 不因 ORM record、mapper、事务等技术细节自动拆成多个 repository。
   - 技术实现可以在 `infrastructure` 内部辅助组织，但不能反向改变 repository 的领域语义。

3. facade 不得重新变成 service 大泥球
   - `facade.py` 是 node 对外稳定入口。
   - 允许做转发、依赖聚合、日志上下文、统一异常转换、事务/幂等等横切协调。
   - 不承载具体业务规则。
   - 不承载单个业务行为的完整编排逻辑。

4. use case 承载应用层业务行为
   - 一个独立业务行为对应一个 use case。
   - use case 负责应用层编排：调用领域模型、规则、repository、port。
   - use case 不直接调用 SDK、HTTP client、ORM session 或 provider。
   - use case 不做 capability provider 选择。

5. domain 保持纯业务语义
   - `domain/` 承载模型、值对象、领域规则、领域服务和 repository 抽象。
   - `domain/` 不依赖 `infrastructure/`、`capabilities/`、HTTP、ORM 或 SDK。
   - 领域服务只用于无法自然归属单个实体/聚合的领域逻辑，不作为新 service 大泥球。

6. infrastructure 只做适配
   - `infrastructure/` 实现 repository、AI port、外部系统 port 等具体适配。
   - 可以包含持久化、AI prompt/schema、协议映射、错误转换、provider 映射。
   - 不承载业务决策。
   - 不把业务语义下沉到 capability。

7. AI gateway 保持中性能力
   - outline、chapter blueprint、chapter generation 等业务语义保留在 `business`。
   - `capabilities/ai_gateway` 不吸收业务任务语义。
   - AI 相关 adapter 在业务 node 的 `infrastructure/ai/` 中把业务意图翻译成中性 AI gateway 请求。

8. OpenSpec 流程必须保留架构判断
   - pre_design 必须包含架构影响分析。
   - proposal/design/tasks 必须承接 pre_design 中的架构边界。
   - 当需求影响稳定 AI 规则时，任务中必须包含 `ai_docs` 更新。
   - 不允许只生成功能任务而跳过架构设计。

## Invariants

这些是不应被后续 OpenSpec 文档推翻的硬边界：

1. 拆分依据不以技术细节为主
   - 不以“ORM mapper 多了”“schema 多了”“函数长了”作为主导拆分理由。
   - 必须先判断背后的业务/领域职责是否已经分化。

2. 复杂 node 的目标形态是轻量 DDD
   - `facade + application/use_cases + domain + infrastructure` 是复杂 node 的默认演进目标。
   - 简单 node 可以裁剪，但复杂 node 不应继续堆单文件。

3. repository 是领域边界，不是技术 DAO 集合
   - repository 命名和拆分必须反映领域资源/聚合。
   - 具体持久化技术不出现在 domain repository 抽象中。

4. facade 是入口，不是业务规则层
   - facade 可以协调横切关注点。
   - 业务行为编排进入 use case。
   - 领域规则进入 domain。

5. OpenSpec 必须包含架构维度
   - 后续 OpenSpec 文档不能只描述功能。
   - 如果 design/tasks 没有体现架构边界和演进规则，就不满足本 change 的意图。

6. AI 规范更新是本 change 的必交付
   - 后续 tasks 必须包含更新 `ai_docs/rules/architecture_rules.md`。
   - 必须新增或更新 node 架构演进相关 example。
   - 必须明确 pre_design / OpenSpec 流程中的架构设计检查规则。

## Architecture direction

采用渐进式轻量 DDD node 架构。

核心方向：

```text
简单 node 保持轻量；
复杂 node 按业务/领域复杂度升级为轻量 DDD；
多个 node 共享稳定领域模型时，再评估 domain-level bounded context。
```

复杂 node 的目标结构：

```text
app/business/<domain>/nodes/<unit>/
├─ facade.py
├─ node.py
├─ application/
│  ├─ dto.py
│  └─ use_cases/
│     ├─ create_seed.py
│     ├─ generate_skeleton.py
│     ├─ confirm_skeleton.py
│     ├─ expand_volume.py
│     └─ get_outline.py
├─ domain/
│  ├─ models.py
│  ├─ rules.py
│  ├─ services.py
│  └─ repositories.py
└─ infrastructure/
   ├─ persistence/
   │  └─ outline_repository.py
   └─ ai/
      ├─ outline_generation_adapter.py
      ├─ prompts.py
      └─ schemas.py
```

以 outline 为例：

- `facade.py`
  - 对外暴露 `create_seed()`、`generate_skeleton()`、`confirm_skeleton()`、`expand_volume()`、`update_volume()`、`update_chapter()`、`get_outline()`。
  - 负责稳定入口、日志上下文、异常协调、横切逻辑。
  - 不写具体业务规则。

- `application/use_cases/`
  - 每个业务行为一个 use case。
  - `create_seed.py` 处理 seed 创建编排。
  - `generate_skeleton.py` 处理 seed → skeleton。
  - `confirm_skeleton.py` 处理 skeleton 确认。
  - `expand_volume.py` 处理 confirmed skeleton → chapter summaries。
  - `update_volume.py`、`update_chapter.py` 处理编辑行为。
  - `get_outline.py` 处理 outline 聚合读取。

- `domain/`
  - `models.py` 放 `Seed`、`Skeleton`、`SkeletonVolume`、`ChapterSummary`、`Outline`、状态枚举和值对象。
  - `rules.py` 放 seed 完整性、skeleton 状态转换、outline 完整性判断等领域规则。
  - `repositories.py` 放 `OutlineRepository` 等按领域资源/聚合定义的 repository 抽象。
  - `services.py` 只放无法自然归属单个实体/聚合的领域服务。

- `infrastructure/`
  - `persistence/outline_repository.py` 实现 `OutlineRepository`。
  - `ai/` 实现 AI 生成 port，包含 prompt、schema、响应映射等适配逻辑。
  - 技术实现可以内部拆文件，但拆分服从业务/领域表达，不改变 domain 抽象。

## Key decisions

### 决策 1：采用 node-level 轻量 DDD，而不是立即升级整个 domain

当前只有 outline 明确复杂化，章节蓝图、章节生成等后续 node 尚未稳定。因此不应过早把整个 `novel_generate` 提升为 domain-level bounded context。

现在的规则是：复杂度先在 node 内消化；当多个 node 共享稳定领域模型或 repository 时，再上移到 domain-level。

这样可以避免提前抽象出不稳定的“创作计划”等大领域模型。

### 决策 2：`facade.py` 取代 `service.py` 作为 node 对外入口

`service.py` 容易被 AI 理解为“所有业务逻辑都写这里”。改成 `facade.py` 可以更明确地表达：它是入口，不是全部业务承载层；它允许横切协调；它把具体行为委托给 use case；它对 HTTP / workflow / bootstrap 提供稳定依赖面。

### 决策 3：一个业务行为一个 use case

业务行为是拆分 use case 的主依据，而不是代码行数。

例如 outline 当前应至少拆成：create seed、get seed、generate skeleton、confirm skeleton、expand volume、update volume、update chapter、get outline。

每个 use case 负责应用层编排，但不承载底层适配细节，也不直接依赖 SDK/ORM/provider。

### 决策 4：repository 抽象放在 domain，按领域资源/聚合定义

repository 是领域模型获取和保存边界，因此它属于领域语言的一部分。

例如 `OutlineRepository` 表达的是“我需要获取/保存 outline 相关聚合”，而不是“我需要访问某几张 SQL 表”。

所以 repository 不按 ORM record、mapper、事务细节拆分。技术实现如何组织，留在 `infrastructure/persistence/` 内部。

### 决策 5：渐进演化规则必须进入 ai_docs

这不是一次性讨论结论，而是后续 AI 工作的长期规则。必须更新：

- `ai_docs/rules/architecture_rules.md`
- 相关 examples，例如：
  - `ai_docs/examples/standard_node_evolution.md`
  - 可能需要更新 `standard_service.md`，或将其替换/改名为 `standard_facade_and_use_cases.md`
  - 更新 `standard_ports.md` 中 repository/port 与 domain repository 的关系说明
  - 更新 `standard_workflow_node.md` 中 node adapter 与 facade 的关系

### 决策 6：OpenSpec / pre_design 必须显式包含架构设计

后续所有需求在 pre_design 和 OpenSpec 流程中必须显式评估架构影响。

这应成为 AI 规范的一部分，而不是只依赖临时对话记忆。

后续文档生成时必须回答：

- 这个需求影响哪些架构边界？
- 是否会让某个 node 膨胀？
- 是否命中 node 演化规则？
- 是否需要更新 ai_docs？
- proposal/design/tasks 如何承接这些架构决策？

## Trade-offs

### 取舍 1：轻量 DDD vs 当前平铺结构

选择轻量 DDD 的代价是目录和概念更多；收益是复杂 node 的职责边界更稳定。

当前平铺结构适合初期快速开发，但 outline 已经证明：当业务行为增加时，`service.py` 容易变成堆积点。

### 取舍 2：node-level 演进 vs domain-level 抽象

选择 node-level 演进的好处是克制，避免过早抽象。代价是未来多个 node 共享领域模型时，可能需要二次上移。

这个代价是可接受的，因为共享模型必须在多个 node 实际出现后才能稳定判断。

### 取舍 3：领域信号优先 vs 数字阈值优先

选择领域信号优先，能避免机械拆分。代价是需要 AI 在 pre_design / OpenSpec 中做更明确的架构判断。

因此必须把判断流程写入 `ai_docs`，否则 AI 容易退回“看行数拆文件”的低质量规则。

### 取舍 4：repository 领域化 vs 技术 DAO 化

选择 repository 领域化，能保持业务语言清晰。代价是 infrastructure 内部可能仍需要组织 ORM records/mappers，但这些只是实现细节，不进入领域抽象。

这符合当前项目边界：业务核心不直接依赖 ORM 或 SQLAlchemy。

### 取舍 5：facade 横切协调 vs 纯转发

允许 facade 承载轻量横切协调，可以避免日志、异常、事务边界散落到每个 use case。代价是需要明确禁止 facade 写具体业务规则，否则会重新变成大 service。

因此规范中必须写清：facade 可做横切，不可做业务行为实现。

## OpenSpec mapping

后续 OpenSpec 文档应按以下方式承接本 pre_design。

### `proposal.md` 应表达

`proposal.md` 应聚焦“为什么要做”和“做什么”，包括：

1. 动机
   - outline MVP 暴露出复杂 node 缺少渐进式架构演进规则的问题。
   - 需要把 node 架构演进规则和 OpenSpec 架构设计要求沉淀进 `ai_docs`。
   - outline 是首个应用对象，但主目标是长期 AI 规范与 node 架构演进机制。

2. 变更范围
   - 新增或更新 AI 架构规则。
   - 定义 business node 渐进式轻量 DDD 结构。
   - 定义 pre_design / OpenSpec 流程中的架构设计检查要求。
   - 后续重构 outline，使其符合新 node 架构。

3. 影响
   - 影响 `ai_docs/rules/architecture_rules.md`。
   - 影响 `ai_docs/examples/` 中 node/facade/use case/repository 样例。
   - 影响 `app/business/novel_generate/nodes/outline/` 的后续结构。
   - 可能影响测试组织和架构测试。

### `design.md` 应展开

`design.md` 应详细展开架构规则和迁移设计，包括：

1. 渐进式 node 架构层级
   - 轻量 node 结构。
   - 复杂 node 轻量 DDD 结构。
   - 多 node 共享领域时的 domain-level bounded context 评估条件。

2. 复杂 node 标准结构
   - `facade.py`
   - `application/use_cases/`
   - `domain/models.py`
   - `domain/rules.py`
   - `domain/services.py`
   - `domain/repositories.py`
   - `infrastructure/`
   - `node.py`

3. 职责边界
   - facade、use case、domain model、domain rule、domain service、repository、adapter、workflow node 的职责。
   - 明确哪些逻辑不能放进 facade、use case、domain、infrastructure。

4. 演化触发规则
   - 业务行为数量。
   - 新领域概念/聚合/状态流转。
   - 多 adapter 或外部协作复杂度。
   - 多 node 复用压力。
   - 数字阈值作为辅助信号，但不是主导规则。

5. outline 迁移方向
   - 当前 `OutlineNodeService` 中每个公开方法对应哪些 use case。
   - 当前 `entities.py/rules.py/ports.py` 如何迁移到 `domain/`。
   - 当前 `infrastructure/ai_adapter.py` 如何迁移到 `infrastructure/ai/`。
   - 当前 repository 抽象如何保持领域化。
   - 当前 HTTP 和 bootstrap 如何依赖新的 facade。

6. AI 规范更新设计
   - `architecture_rules.md` 增补内容。
   - 新增或更新 examples。
   - 后续 pre_design / OpenSpec 架构设计检查规则。

### `tasks.md` 应拆解

`tasks.md` 应至少包含以下任务组：

1. AI 规则更新
   - 更新 `ai_docs/rules/architecture_rules.md`。
   - 新增或更新 node 演进样例。
   - 更新 facade/use case/repository/workflow node 相关 examples。
   - 补充 OpenSpec 流程必须考虑架构设计的规则。

2. outline 结构迁移
   - 新建 `facade.py`。
   - 新建 `application/use_cases/`。
   - 迁移 DTO。
   - 新建 `domain/` 并迁移模型、规则、repository 抽象。
   - 迁移 infrastructure 适配实现。
   - 更新 bootstrap、HTTP、测试 import。

3. 测试与守护
   - 调整现有 outline 单元测试到 use case / facade 边界。
   - 保留 HTTP integration 测试。
   - 保留 repository integration 测试。
   - 必要时新增架构测试，防止复杂 node 继续新增单一 `service.py` 大泥球。
   - 运行项目 CI 等价验证。

4. 清理旧结构
   - 删除或迁移旧 `service.py`。
   - 避免保留无意义 re-export 或兼容壳，除非确有稳定外部依赖需要。
   - 更新文档和样例中的旧命名。

## Generation guardrails

后续生成 OpenSpec 或实现代码时必须遵守以下护栏。

### 必须遵守

1. 主目标不能被缩小成 outline service 拆分
   - 本 change 的主目标是 node 架构演进规则 + AI 规范沉淀 + OpenSpec 架构设计规则。
   - outline 是首个应用对象，不是唯一目标。

2. 必须更新 ai_docs
   - 不能只改应用代码。
   - 必须把渐进式 node 架构和 OpenSpec 架构设计检查规则沉淀到 AI 文档。

3. 必须采用方案 A
   - 采用渐进式轻量 DDD node 架构。
   - 不采用当前平铺增强版作为最终目标。
   - 不立即升级整个 `novel_generate` 为 domain-level bounded context。

4. 拆分必须以业务/领域职责为主
   - use case 按业务行为拆。
   - repository 按领域资源/聚合定义。
   - domain 按领域模型、规则、不变量组织。
   - 技术细节只作为 infrastructure 内部实现组织依据。

5. facade 不得承载业务规则
   - facade 可做入口、转发、横切协调。
   - 具体业务行为进入 use case。
   - 领域不变量进入 domain。

6. OpenSpec 必须承接架构判断
   - proposal/design/tasks 中必须出现架构影响、职责边界、演化规则和 ai_docs 更新项。
   - 不允许只生成 CRUD 式任务清单。

### 允许补全

后续 OpenSpec 文档可以补全：

- 具体目录命名细节。
- 具体 use case 类名或函数名。
- 测试文件迁移计划。
- 架构测试的具体实现方式。
- outline 迁移的详细步骤。
- ai_docs examples 的具体文件命名。

但这些补全不能改变本 pre_design 已确认的架构方向。

### 禁止补全

后续 OpenSpec 文档不得擅自：

- 把 repository 改成按 ORM/mapper/事务技术细节主导拆分。
- 把业务语义下沉到 `capabilities/ai_gateway`。
- 让 `facade.py` 重新承载全部业务行为。
- 跳过 `ai_docs` 更新。
- 跳过 OpenSpec 架构设计规则。
- 直接把整个 `novel_generate` 升级成 domain-level bounded context。
- 把数字阈值写成唯一硬性拆分依据。
- 保留旧 `service.py` 作为兼容壳并继续堆逻辑，除非设计中明确说明短期迁移原因和移除条件。

### 遇到未决事项时

如果后续文档或实现遇到未决问题，应按以下顺序处理：

1. 先检查是否已有 `ai_docs` 规则能回答。
2. 再检查本 pre_design 的硬边界。
3. 如果仍不明确，回到用户确认，不要自行扩大范围。
4. 对架构边界不清的问题，不应直接进入实现。
