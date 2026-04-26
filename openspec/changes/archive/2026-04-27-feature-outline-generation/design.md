## Context

项目已完成基础设施和 AI 网关建设。当前需要实现第一个业务功能——大纲生成，作为 `novel_generate` 业务域下的 outline 节点。

现有基础设施：
- AI 网关（`app/capabilities/ai_gateway/`）：提供 `AiGatewayFacade`，支持 TEXT 和 STRUCTURED 两种输出模式
- 数据库基础设施（`app/shared/infra/database.py`）：SQLAlchemy engine 和 session 工厂
- HTTP 框架（`app/interfaces/http/`）：FastAPI 应用，已有路由注册机制
- Bootstrap 装配（`app/bootstrap/`）：已有 AI 网关和 API 的装配模块

前置条件：PostgreSQL 基础设施切换作为独立 change 先行完成。

## Goals / Non-Goals

**Goals:**

- 在 `app/business/novel_generate/nodes/outline/` 下建立大纲生成节点，遵循标准业务结构
- 实现两阶段生成流程：结构化种子 → 骨架 → 确认 → 逐卷展开为章节摘要
- 通过 `OutlineAiPort` 抽象注入 AI 能力，business 层不直接依赖 capability
- 使用 PostgreSQL 持久化全部领域模型
- 暴露 HTTP 端点支持创建、生成、确认、展开、编辑操作

**Non-Goals:**

- 不设计节点间编排引擎或通用工作流状态机（node 仅为代码组织概念）
- 不做提示词调优
- 不做章节级详细拆分（属于章节蓝图需求）
- 不做前端 UI

## Decisions

### 决策 1：模块位置 — `business/novel_generate/nodes/outline/`

遵循 `architecture_rules.md` 标准业务结构，将 outline 作为 `novel_generate` 域下的一个 node。`infrastructure/` 放在 node 内部（`nodes/outline/infrastructure/`），而非 domain 级别。

```
app/business/novel_generate/
  __init__.py
  nodes/
    __init__.py
    outline/
      __init__.py
      entities.py
      service.py
      ports.py
      rules.py
      dto.py
      infrastructure/
        __init__.py
        repository.py         — SQLAlchemy 实现 OutlineRepository
        ai_adapter.py         — OutlineAiPort 的实现，桥接 AiGatewayFacade
```

**为什么不放 domain 级 infrastructure/**：架构规则明确 infrastructure 应在 node 内部（`nodes/<unit>/infrastructure/`），保持适配器与节点紧耦合，避免跨节点共享实现细节。

**备选方案**：将 outline 作为独立顶层 `business/outline/` — 放弃，因为大纲只是创作流水线的一个节点，独立顶层会导致后续每步骤一个域。

### 决策 2：领域模型设计

```python
# entities.py 核心模型

class Seed:
    """结构化种子 — 用户提交的小说创作起点"""
    id: UUID
    title: str                    # 小说暂定标题
    genre: str                    # 题材（如"科幻"、"悬疑"）
    protagonist: str              # 主角设定
    core_conflict: str            # 核心冲突
    story_direction: str          # 大致走向
    additional_notes: str | None  # 补充说明（可选）
    created_at: datetime
    updated_at: datetime

class SkeletonVolume:
    """骨架卷 — 粗粒度结构单元"""
    id: UUID
    skeleton_id: UUID
    sequence: int                 # 卷序号
    title: str                    # 卷标题
    turning_point: str            # 核心转折描述
    created_at: datetime
    updated_at: datetime

class Skeleton:
    """骨架 — 种子生成的粗粒度大纲结构"""
    id: UUID
    seed_id: UUID
    status: SkeletonStatus        # DRAFT / CONFIRMED
    volumes: list[SkeletonVolume]
    created_at: datetime
    updated_at: datetime
    confirmed_at: datetime | None

class ChapterSummary:
    """章节摘要 — 由骨架卷展开的细粒度单元"""
    id: UUID
    volume_id: UUID
    sequence: int                 # 章节在卷内的序号
    title: str                    # 章节标题
    summary: str                  # 章节摘要
    is_stale: bool                # 父卷编辑后标记为过期
    created_at: datetime
    updated_at: datetime

class Outline:
    """大纲 — 聚合最终结果"""
    id: UUID
    seed_id: UUID
    skeleton_id: UUID
    status: OutlineStatus         # IN_PROGRESS / COMPLETE
    created_at: datetime
    updated_at: datetime
```

**`SkeletonStatus` 和 `OutlineStatus` 为枚举**：
- `SkeletonStatus`: `DRAFT` → `CONFIRMED`
- `OutlineStatus`: `IN_PROGRESS` → `COMPLETE`

**为什么 Seed 独立存在而不是 Skeleton 的字段**：种子是用户主动提交的输入，骨架是系统生成的输出，生命周期不同。种子创建后可以不生成骨架（保存草稿），也可以基于同一种子重新生成骨架。

### 决策 3：ports 抽象设计

```python
# ports.py

class OutlineRepository(Protocol):
    """大纲领域模型的持久化抽象"""
    def save_seed(self, seed: Seed) -> Seed: ...
    def get_seed(self, seed_id: UUID) -> Seed | None: ...
    def save_skeleton(self, skeleton: Skeleton) -> Skeleton: ...
    def get_skeleton(self, skeleton_id: UUID) -> Skeleton | None: ...
    def get_skeleton_by_seed(self, seed_id: UUID) -> Skeleton | None: ...
    def save_chapter_summaries(self, summaries: list[ChapterSummary]) -> list[ChapterSummary]: ...
    def get_chapters_by_volume(self, volume_id: UUID) -> list[ChapterSummary]: ...
    def mark_chapters_stale(self, volume_id: UUID) -> None: ...
    def save_outline(self, outline: Outline) -> Outline: ...
    def get_outline_by_seed(self, seed_id: UUID) -> Outline | None: ...
    def update_skeleton_volume(self, volume: SkeletonVolume) -> SkeletonVolume: ...
    def update_chapter_summary(self, chapter: ChapterSummary) -> ChapterSummary: ...

class OutlineAiPort(Protocol):
    """AI 生成能力的业务抽象"""
    def generate_skeleton(self, seed: Seed) -> list[SkeletonVolume]: ...
    def expand_volume(self, seed: Seed, skeleton: Skeleton, volume: SkeletonVolume) -> list[ChapterSummary]: ...
```

**为什么 OutlineAiPort 的方法接收领域模型而不是原始字段**：保持 port 的业务语义——调用方不需要知道怎么把种子翻译成 AI 请求，那是 infrastructure adapter 的职责。

**为什么 `expand_volume` 接收 seed 和 skeleton**：展开章节时 AI 需要整体上下文（种子设定 + 骨架全貌），不仅仅是当前卷的信息。

### 决策 4：AI 适配器实现策略

`infrastructure/ai_adapter.py` 实现 `OutlineAiPort`，内部：

1. 将领域模型翻译为 `AiGatewayRequest`（STRUCTURED 模式）
2. 定义 JSON Schema 约束骨架和章节的输出结构
3. 调用 `AiGatewayFacade.generate()`
4. 将 `structured_content` 映射回领域模型

```
OutlineNodeService
  → OutlineAiPort.generate_skeleton(seed)
    → [ai_adapter] 构建 AiGatewayRequest(
        capability_profile="outline-skeleton",
        output_mode=STRUCTURED,
        structured_output=StructuredOutputConstraint(schema=SKELETON_SCHEMA),
        messages=[system_prompt, user_prompt(seed)]
      )
    → AiGatewayFacade.generate(request)
    → 解析 structured_content → list[SkeletonVolume]
```

**capability_profile 命名**：使用 `"outline-skeleton"` 和 `"outline-chapter-expansion"` 两个 profile，由 AI 网关配置映射到具体 provider/model。

### 决策 5：逐卷展开策略

骨架确认后，按卷序号依次展开。每次调用 `OutlineAiPort.expand_volume()` 处理一个卷，返回该卷下的全部章节摘要。

**为什么不批量展开**：长篇小说可能有 5+ 卷、50+ 章。一次性生成所有章节的 JSON 输出过大，结构化输出质量不稳定。逐卷展开控制每次输出规模在 10-15 章以内。

**展开顺序**：按 `SkeletonVolume.sequence` 升序。前面卷的展开结果可作为后续卷的上下文（但 MVP 阶段暂不实现跨卷上下文传递，避免复杂度膨胀）。

### 决策 6：编辑与过期标记

- 骨架卷可编辑（标题、转折描述），编辑后该卷下已展开的章节摘要标记 `is_stale = True`
- 章节摘要可编辑（标题、摘要），直接更新
- 过期的章节可以选择重新展开（再次调用 `expand_volume`），也可以保留手动编辑的版本
- 骨架确认后仍可编辑卷内容，但不会自动回退确认状态（编辑的是内容，不是结构）

### 决策 7：数据库表设计

```sql
-- 种子表
CREATE TABLE outline_seeds (
    id UUID PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    genre VARCHAR(50) NOT NULL,
    protagonist TEXT NOT NULL,
    core_conflict TEXT NOT NULL,
    story_direction TEXT NOT NULL,
    additional_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 骨架表
CREATE TABLE outline_skeletons (
    id UUID PRIMARY KEY,
    seed_id UUID NOT NULL REFERENCES outline_seeds(id),
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ,
    UNIQUE(seed_id)
);

-- 骨架卷表
CREATE TABLE outline_skeleton_volumes (
    id UUID PRIMARY KEY,
    skeleton_id UUID NOT NULL REFERENCES outline_skeletons(id) ON DELETE CASCADE,
    sequence INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    turning_point TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(skeleton_id, sequence)
);

-- 章节摘要表
CREATE TABLE outline_chapter_summaries (
    id UUID PRIMARY KEY,
    volume_id UUID NOT NULL REFERENCES outline_skeleton_volumes(id) ON DELETE CASCADE,
    sequence INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    summary TEXT NOT NULL,
    is_stale BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(volume_id, sequence)
);

-- 大纲聚合表
CREATE TABLE outlines (
    id UUID PRIMARY KEY,
    seed_id UUID NOT NULL REFERENCES outline_seeds(id),
    skeleton_id UUID NOT NULL REFERENCES outline_skeletons(id),
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(seed_id)
);
```

**外键 ON DELETE CASCADE**：骨架删除时级联清理卷和章节。种子删除时不级联（需要显式处理）。

### 决策 8：HTTP 端点设计

```
POST   /api/outlines/seeds                     — 创建种子
GET    /api/outlines/seeds/{seed_id}            — 获取种子
POST   /api/outlines/seeds/{seed_id}/skeleton   — 生成骨架
GET    /api/outlines/skeletons/{skeleton_id}     — 获取骨架（含卷列表）
PATCH  /api/outlines/skeletons/volumes/{volume_id}  — 编辑骨架卷
POST   /api/outlines/skeletons/{skeleton_id}/confirm — 确认骨架
POST   /api/outlines/skeletons/{skeleton_id}/expand/{volume_id} — 展开指定卷的章节
PATCH  /api/outlines/chapters/{chapter_id}      — 编辑章节摘要
GET    /api/outlines/seeds/{seed_id}/outline     — 获取完整大纲
```

**路径前缀 `/api/outlines/`**：将大纲相关端点归入统一命名空间。

**为什么不用 `/api/novel-generate/outline/`**：`novel_generate` 是内部业务域组织概念，不应暴露在 API 路径中。用户关心的是"大纲"，不是"创作生成流水线的大纲节点"。

### 决策 9：Bootstrap 装配

在 `app/bootstrap/novel_generate.py` 中完成装配：

1. 创建 `OutlineRepositoryImpl`（注入 SQLAlchemy session factory）
2. 创建 `OutlineAiAdapter`（注入 `AiGatewayFacade`）
3. 创建 `OutlineNodeService`（注入 repository + AI port）
4. 将 service 注册到 HTTP 路由

遵循现有 `bootstrap/ai_gateway.py` 的装配模式。

## Risks / Trade-offs

**[逐卷展开增加调用次数]** → 5 个卷需要 5 次 AI 调用，延迟和成本高于一次性全量展开。缓解：MVP 阶段卷数通常 3-5 个，调用次数可接受；后续可引入并发展开。

**[骨架编辑后不自动重新展开]** → 用户编辑卷内容后只标记章节过期，不自动触发重新生成。缓解：通过 `is_stale` 字段提醒用户，由用户主动决定是否重新展开。降低系统复杂度和意外的 AI 调用开销。

**[前置依赖 PostgreSQL change]** → 大纲生成 change 无法独立验证，需等待数据库切换完成。缓解：PostgreSQL change 范围小，可快速完成。

**[Seed 与 Skeleton 1:1 限制]** → 当前设计一个种子只能有一个骨架（UNIQUE 约束）。如果用户想对同一种子尝试多个骨架方向，需要重新生成覆盖旧骨架。缓解：MVP 阶段简化模型，后续如有需求可放开为 1:N。
