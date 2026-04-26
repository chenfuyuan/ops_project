# Pre-design: 大纲生成

## Problem Framing

项目需要从"模糊想法"到"可执行的章节级创作计划"建立通路。大纲生成是这条通路的第一步——把作者的结构化种子转化为可编辑、可向下游传递的大纲。当前这个能力完全缺失，阻塞了整个 MVP 创作闭环。

### 背景

- MVP 阶段目标是"跑通人工主导的最小创作闭环"
- 基础设施（项目脚手架、CI/CD）和 AI 网关均已实现
- 大纲生成是第一个真正的业务功能需求，后续章节蓝图、章节生成流水线都依赖它
- PostgreSQL 切换作为独立前置 change，本 change 假设已完成

## Goals

- 接受结构化种子输入（题材、主角、核心冲突、大致走向等固定字段）
- 分两阶段生成大纲：先产出粗粒度骨架（卷/幕），用户确认后展开为章节级摘要
- 大纲结果结构化存储到 PostgreSQL，支持局部编辑
- 通过 AI 网关 STRUCTURED 模式生成，确保输出可直接入库
- 为后续"章节蓝图"需求提供稳定的上游输入

## Non-goals

- 不设计节点间编排引擎或通用工作流状态机
- 不做提示词调优（prompt 内容是实现细节，不在本设计范围）
- 不做章节级详细拆分（属于章节蓝图需求）
- 不做前端 UI（属于 MVP 创作工作台需求）
- 不做 PostgreSQL 基础设施切换（独立前置 change）

## Requirement Understanding

大纲生成是一个两阶段、人工主导的生成流程：

1. **种子 → 骨架**：用户提交结构化种子，系统生成 3-5 个卷/幕的粗粒度骨架，每个卷只有标题 + 核心转折描述
2. **骨架 → 章节摘要**：用户确认（可编辑）骨架后，系统逐卷展开为章节级摘要（标题 + 简短摘要）

用户在两个阶段之间有完整的审阅和编辑权。

### 成功标准

- 从结构化种子出发可生成可编辑的大纲结果
- 用户可在骨架阶段审阅、编辑后再决定是否展开
- 大纲结果可作为后续章节蓝图的稳定输入
- 骨架和章节摘要均支持局部编辑

## Constraints / Invariants

### 约束

- 业务层不直接依赖 AI 网关 capability，通过 port 抽象注入
- 大纲生成作为 `business/novel_generate/nodes/outline/` 子模块，不是独立顶层模块
- 数据库为 PostgreSQL（假设前置 change 已完成切换）
- AI 调用统一走 AI 网关 Facade 的 STRUCTURED 模式

### 不变量

- 骨架未经用户确认，不可触发章节展开
- 种子字段必须完整才能触发骨架生成
- 大纲的每一层（骨架、章节摘要）都必须支持局部编辑后重新展开
- 大纲结果必须是结构化数据（而非自由文本），保证下游可消费

## Architecture Direction

### 模块结构

```
app/business/novel_generate/
  __init__.py
  nodes/
    outline/
      entities.py      — Seed, Skeleton, SkeletonVolume, Outline, ChapterSummary
      service.py        — OutlineNodeService
      ports.py          — OutlineRepository(Protocol), OutlineAiPort(Protocol)
      rules.py          — 种子完整性校验、骨架确认前置检查等
      dto.py            — 输入输出 DTO

app/business/novel_generate/infrastructure/
  outline_repository.py — SQLAlchemy 实现 OutlineRepository

app/interfaces/http/
  outline.py            — HTTP 端点，薄层调 OutlineNodeService

app/bootstrap/
  novel_generate.py     — 装配 service + repository + AI port
```

### 核心职责

- `OutlineNodeService`：编排两阶段流程 — create_seed / generate_skeleton / confirm_skeleton / expand_chapters / update_*
- `OutlineRepository(Protocol)`：大纲领域模型的持久化抽象
- `OutlineAiPort(Protocol)`：AI 生成能力的抽象，business 层通过此 port 请求骨架生成和章节展开
- `rules.py`：业务规则校验（种子完整性、骨架确认前置检查）
- HTTP 端点：薄层转发，不含业务逻辑

### 数据模型关系

```
Seed (1) ──→ Skeleton (1) ──→ [SkeletonVolume (N)]
                                      │
                                      ▼
                              [ChapterSummary (M per volume)]
                                      │
                                      ▼
                                 Outline (1) ── 聚合最终结果
```

### node 的定位

node 当前只是代码组织概念（子模块），不是运行时工作流节点。不引入节点注册、调度、编排机制。未来 change 在 `novel_generate/nodes/` 下添加 blueprint、chapter_pipeline 等节点时，再考虑是否需要统一抽象。

## Key Decisions / Trade-offs

| 决策 | 选择 | 理由 | 放弃的替代 |
|------|------|------|-----------|
| 输入格式 | 结构化种子（固定字段） | MVP 人工主导，可控性 > 低门槛；向上兼容自由文本 | 自由文本种子 — 需额外提取步骤 |
| 生成流程 | 分两阶段（骨架 → 章节摘要） | 平衡控制力和流畅度，长篇必需 | 一步生成 — 长篇质量不可控；逐层交互 — MVP 过重 |
| 持久化 | PostgreSQL | 结构化数据天然适合关系型存储，状态管理方便 | 文件存储 — 状态管理需自行实现 |
| AI 输出模式 | STRUCTURED | 省掉解析步骤，直接入库 | TEXT — 需额外解析，出错概率高 |
| 顶层模块 | `novel_generate` | 大纲只是创作流水线的一个节点，避免后续每步骤一个顶层模块 | `outline` 独立顶层 — 模块碎片化 |
| AI 集成方式 | 通过 OutlineAiPort 抽象注入 | business 层不依赖 capability 细节 | 直接调 AiGatewayFacade — 违反架构边界 |
| 骨架展开粒度 | 逐卷展开 | 控制单次 AI 调用输出规模，质量更稳定 | 全量展开 — 长篇时 JSON 输出过大 |

## Critical Flows

### 流程 1：创建种子并生成骨架

```
用户提交结构化种子
  → rules 校验种子字段完整性
  → 持久化 Seed
  → 通过 OutlineAiPort 请求骨架生成（STRUCTURED 模式）
  → 持久化 Skeleton + SkeletonVolume[]
  → 返回骨架供用户审阅
```

### 流程 2：确认骨架并展开章节

```
用户编辑骨架（可选）
  → 用户确认骨架
  → rules 检查骨架已确认
  → 逐卷通过 OutlineAiPort 请求章节展开（STRUCTURED 模式）
  → 持久化 ChapterSummary[]
  → 聚合为 Outline
  → 返回完整大纲
```

### 流程 3：编辑已有内容

```
用户修改骨架某个卷的标题/描述
  → 更新对应 SkeletonVolume
  → 该卷的已展开章节标记为过期（如有）

用户修改某章摘要
  → 更新对应 ChapterSummary
```

## OpenSpec Mapping

| 文档 | 应承接的内容 |
|------|------------|
| `proposal.md` | 问题陈述、目标/非目标、用户价值、成功标准、与后续需求（章节蓝图）的衔接关系 |
| `design.md` | 模块结构详细展开、领域模型字段定义、端点契约、数据库表结构、AI 网关调用的 JSON Schema 设计、两阶段流程的详细交互序列 |
| `tasks.md` | 按实现顺序拆分：entities → ports → rules → repository → service → HTTP 端点 → bootstrap 装配 → 集成测试 |

## Generation Guardrails

### 必须遵守

- 问题定义、Goals、Non-goals 如本文所述
- 模块位于 `business/novel_generate/nodes/outline/` 下
- business 层通过 OutlineAiPort 抽象访问 AI 能力，不直接依赖 capability
- 两阶段流程：骨架 → 确认 → 章节展开
- 骨架未确认不可展开的不变量
- 逐卷展开策略

### 允许补全

- 领域模型的具体字段名称和类型
- HTTP 端点的具体路径和请求/响应 schema
- AI 生成的 JSON Schema 具体结构
- 数据库表的列定义和索引策略
- 测试用例的具体场景
- OutlineAiPort 的方法签名细节

### 禁止

- 不得扩大范围引入工作流编排、节点注册机制
- 不得让 business 层直接依赖 AiGatewayFacade 或任何 capability 模块
- 不得将大纲生成作为独立顶层模块
- 不得跳过骨架确认直接展开章节
- 不得把编辑能力降级为"只能整体重新生成"
- 遇到未决事项时，应标注为待澄清并保持最小实现，不得自行脑补新目标
