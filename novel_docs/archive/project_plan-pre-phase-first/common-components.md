---
title: 通用组件清单
version: 1.0
date: 2026-04-20
description: 从 AI 小说生成系统设计中提取的与业务无关的通用组件，可独立复用
---

# 通用组件清单

## 文档角色

本文档属于**横切 topic 专题**，用于承载跨多个 phase 复用、且不属于总纲入口职责的通用组件设计。

默认使用方式：
- 从总纲入口页按需进入
- 在相关 phase overview 中作为补充专题被引用
- 不作为某个单独 phase 的子项被打散维护

## 概述

本文档从 6 个阶段的设计中识别出与小说业务无关的通用组件。这些组件可以独立开发、独立测试，在其他 AI 应用中直接复用。

按通用程度分为三类：
- **完全通用** — 与业务零耦合，任何 AI 应用或 Web 服务都能直接用
- **半通用** — 轻度业务耦合，稍作抽象即可通用
- **SaaS 通用** — Phase 6 的基础设施组件，任何 SaaS 产品都需要

## 模块化单体中的放置位置

| 组件 | 放置位置 | 理由 |
|------|---------|------|
| LLM 网关 | `modules/llm/` | 有自己的领域（profiles、路由规则），通过 facade 对外服务 |
| 熔断器 | `shared/infra/circuit_breaker.py` | 通用基础设施，无业务逻辑 |
| SSE 事件总线 | `shared/events/` | 跨模块事件机制 |
| Webhook 通知器 | `shared/infra/webhook.py` | 通用基础设施 |
| Token 计数器 | `shared/infra/token_estimator.py` | 工具函数，无领域 |
| 向量检索封装 | `modules/memory/infrastructure/` | 仅 memory 模块直接使用 |
| 流水线编排器 | `modules/chapter/application/` | chapter 模块的核心编排 |
| 上下文预算管理器 | `modules/memory/application/` | memory 模块内部逻辑 |
| Schema 校验状态机 | `shared/kernel/state_machine.py` | 多模块可能复用 |
| DB 驱动任务调度器 | `modules/autopilot/`（Phase 5） | 有自己的生命周期和领域 |
| AI 文本检测器 | `modules/style/`（Phase 4） | style 模块内部工具 |

SaaS 基础设施组件（Phase 6）各自成为独立模块：`modules/user/`、`modules/billing/`、`modules/collaboration/`、`modules/marketplace/`。对象存储适配器放在 `shared/infra/storage.py`，任务队列封装放在 `shared/infra/queue.py`。

---

## 一、完全通用组件

### 1.1 LLM 网关 (LLM Gateway)

**来源：** Phase 1 `02-llm-adapter.md`、Phase 5 `02-circuit-breaker.md`

**职责：** 统一接口封装多家 LLM 提供商，按任务类型路由到不同模型，内置重试、熔断、流式输出。

**核心能力：**

| 能力 | 说明 |
|------|------|
| 统一接口 | `invoke(messages) → response` 和 `stream(messages) → AsyncIterator`，上层不关心具体提供商 |
| 多提供商适配 | OpenAI 兼容协议（覆盖 GPT/DeepSeek/Qwen/Ollama 等）、Anthropic 原生 SDK |
| 任务路由 | 通过配置表将不同任务类型（draft/audit/summarize 等）路由到不同模型 |
| 流式输出 | SSE 格式流式返回，支持前端实时显示 |
| 重试机制 | 指数退避重试（可配置次数和延迟） |
| 熔断保护 | 单实体熔断（连续 N 次失败暂停）+ 全局熔断（防 API 雪崩） |
| 结构化输出 | JSON mode + 容错解析（json-repair）+ Pydantic 校验 + 自动修复重试 |
| Token 追踪 | 记录每次调用的 prompt/completion tokens，用于成本统计 |

**接口设计：**

LLMAdapter 协议提供两个核心方法：`invoke`（同步调用，返回 LLMResponse）和 `stream`（流式调用，返回异步字符串迭代器）。

LLMRouter 在此基础上增加任务路由能力：根据 task_type 获取对应的 adapter，并提供带路由的 invoke/stream 方法。

此外提供 `extract_json` 辅助函数：接收 LLMRouter、消息列表和 Pydantic schema，自动调用 LLM 并解析为结构化对象，支持配置最大重试次数（默认 2 次）。

**配置存储：**

**llm_profiles 表：** LLM 模型配置

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| name | TEXT | 配置名称（必填） |
| provider | TEXT | 提供商（必填）：openai_compatible / anthropic |
| base_url | TEXT | API 地址 |
| api_key | TEXT | API 密钥（加密存储） |
| model | TEXT | 模型名称（必填） |
| task_type | TEXT | 任务类型标识（必填） |
| params | JSON | 参数配置（temperature, max_tokens 等） |
| is_default | INTEGER | 是否默认，默认 0 |
| created_at | TIMESTAMP | 创建时间 |

**可替代方案：** [LiteLLM](https://github.com/BerriAI/litellm) 提供了类似的多提供商统一接口，可以考虑直接使用或在其基础上封装任务路由和熔断。

---

### 1.2 熔断器 (Circuit Breaker)

**来源：** Phase 5 `02-circuit-breaker.md`

**职责：** 保护外部 API 调用，防止级联故障和雪崩。

**核心能力：**

| 能力 | 说明 |
|------|------|
| 单实体熔断 | 某个实体（如某本小说）连续 N 次失败 → 暂停该实体的调用 |
| 全局熔断 | 所有调用累计 M 次失败 → 全局暂停，冷却后半开探测 |
| 状态机 | closed → open → half-open → closed |
| 错误分类 | 区分可熔断错误（网络超时、API 限流）和不可熔断错误（参数错误、鉴权失败） |

**接口设计：**

CircuitBreaker 提供三个核心方法：
- `before_call`：检查是否允许调用，open 状态时抛出异常
- `on_success`：调用成功后重置计数
- `on_failure`：调用失败后累计失败次数

初始化时配置 failure_threshold（失败阈值）和 cooldown_seconds（冷却时间）。

CircuitBreakerLLMAdapter 包装 LLMAdapter，自动集成熔断逻辑。

---

### 1.3 SSE 事件总线 (Event Bus)

**来源：** Phase 5 `03-realtime-notifications.md`

**职责：** 服务端向前端实时推送事件，支持按实体 ID 分频道订阅。

**核心能力：**

| 能力 | 说明 |
|------|------|
| 发布-订阅 | 按实体 ID（如 novel_id）分频道，多个客户端可订阅同一频道 |
| SSE 端点 | FastAPI SSE 端点，自动心跳保活 |
| 事件类型 | 支持自定义事件类型和数据格式 |
| 客户端管理 | 自动清理断开的连接 |

**接口设计：**

EventBus 提供发布-订阅模式：
- `subscribe(channel_id)`：订阅频道，返回异步队列
- `unsubscribe(channel_id, queue)`：取消订阅
- `emit(channel_id, event_type, data)`：向频道发布事件

配合 FastAPI SSE 端点使用：客户端通过 GET 请求订阅指定频道，服务端以 SSE 格式推送事件，内置 30 秒心跳保活机制。

---

### 1.4 Webhook 通知器 (Webhook Notifier)

**来源：** Phase 5 `03-realtime-notifications.md`

**职责：** 向外部系统发送事件通知，带 HMAC 签名验证。

**核心能力：**

| 能力 | 说明 |
|------|------|
| HMAC-SHA256 签名 | 请求体签名，接收方可验证来源 |
| 可配置触发条件 | 按事件类型和频率配置通知策略 |
| 失败重试 | 发送失败自动重试，超过阈值标记为不可达 |
| 异步发送 | 不阻塞主流程 |

**接口设计：**

WebhookNotifier 提供 `notify` 方法：接收 webhook_url、webhook_secret、event_type 和 payload，使用 HMAC-SHA256 签名后异步发送 HTTP 请求，返回是否成功。

---

### 1.5 Token 计数器 (Token Estimator)

**来源：** Phase 1 `06-memory-system.md`

**职责：** 快速估算中英文混合文本的 token 数量，用于上下文预算管理。

估算规则：中文约 1.5 字/token，英文约 0.75 词/token。提供 `estimate_tokens(text)` 函数返回估算的 token 数。

**可替代方案：** [tiktoken](https://github.com/openai/tiktoken) 提供精确计数，但速度较慢。估算器适合预算管理场景（不需要精确值）。

---

### 1.6 向量检索封装 (Vector Store Wrapper)

**来源：** Phase 1 `06-memory-system.md`

**职责：** 封装 ChromaDB 的分段、索引、查询、过滤操作。

**核心能力：**

| 能力 | 说明 |
|------|------|
| 文本分段 | 按段落或固定 token 数切分文本 |
| 批量索引 | 带元数据的批量向量写入 |
| 语义查询 | 按相似度检索 + 元数据过滤 |
| 集合管理 | 创建/删除集合，按实体隔离 |

**接口设计：**

VectorStore 协议提供三个核心方法：
- `add(collection, documents, metadatas, ids)`：带元数据的批量向量写入
- `query(collection, query_texts, n_results, where)`：按相似度检索 + 元数据过滤
- `delete(collection, ids)`：删除指定向量

TextSegmenter 提供 `segment(text, max_tokens)` 方法，按段落或固定 token 数（默认 500）切分文本。

---

## 二、半通用组件（轻度抽象后可通用）

### 2.1 流水线编排器 (Pipeline Orchestrator)

**来源：** Phase 1 `05-chapter-pipeline.md`、Phase 2 `05-pipeline-upgrade.md`

**业务耦合点：** 当前绑定了 Plan/Compose/Draft/Audit/Revise/Commit 这些具体阶段。

**抽象方向：** 提取为通用的 Stage Pipeline 框架。

**通用接口：**

PipelineStage 协议定义每个阶段：包含 name 属性和 `execute(context)` 异步方法。

PipelineOrchestrator 接收阶段列表，提供：
- `run(initial_context, resume_from)`：顺序执行各阶段，每步持久化中间产物，支持断点续跑
- `get_artifacts(run_id)`：获取某次运行的所有中间产物

**通用能力：**
- 阶段顺序执行，上下文在阶段间传递
- 每步输入输出持久化为中间产物
- 检查点恢复：任意步骤失败后可从该步重跑
- 循环支持：某些阶段可配置为循环执行（如 Audit→Revise 循环）
- 耗时和资源追踪

**适用场景：** 任何多步骤 AI 处理流水线（文档处理、数据分析、内容生成等）。

---

### 2.2 上下文预算管理器 (Context Budget Allocator)

**来源：** Phase 1 `06-memory-system.md`、Phase 3 `04-onion-model-t1.md`

**业务耦合点：** 当前的 T0/T1/T2/T3 层内容是小说特定的（角色状态、伏笔等）。

**抽象方向：** 提取为通用的多层优先级上下文裁剪框架。

**通用接口：**

ContextLayer 描述每一层上下文：包含 name、priority（数字越小优先级越高，0=永不裁剪）、content、tokens 和 trim_strategy（none / truncate / compress / remove）。

ContextBudgetAllocator 接收总预算，提供 `allocate(layers)` 方法：
1. 永不裁剪的层先占位
2. 剩余预算按比例分配给其他层
3. 超出的层按 trim_strategy 处理

**通用能力：**
- 多层优先级定义（永不裁剪 / 可压缩 / 动态水位线 / 优先牺牲）
- Token 预算分配和动态调整
- 可插拔的裁剪策略（截断、LLM 压缩、按相关度移除）
- 预算使用报告（每层实际占用多少 token）

**适用场景：** 任何需要在有限上下文窗口中组装多来源信息的 AI 应用（RAG、Agent、长对话等）。

---

### 2.3 Schema 校验状态机 (Schema-Validated State Machine)

**来源：** Phase 2 `03-fact-locks.md`

**业务耦合点：** 当前的 Delta 格式是角色状态、伏笔等小说特定的。

**抽象方向：** 提取为通用的增量状态更新框架。

**通用接口：**

StateDelta 是增量变更描述的基类，子类定义具体字段。

StateManager 接收 Pydantic schema，提供：
- `apply_delta(entity_id, delta)`：校验 delta 合法性 → 合并到当前状态 → 持久化新快照
- `get_current(entity_id)`：获取最新状态快照
- `get_history(entity_id)`：获取状态变更历史

**通用能力：**
- 增量更新而非全量替换
- Pydantic schema 校验，非法变更被拒绝
- 状态快照历史（每次变更保留快照，可回溯）
- 变更日志

**适用场景：** 任何需要追踪实体状态变化的系统（游戏状态、工作流状态、文档版本等）。

---

### 2.4 数据库驱动任务调度器 (DB-Driven Job Scheduler)

**来源：** Phase 5 `01-autopilot.md`

**业务耦合点：** 当前绑定了小说的自动驾驶阶段（MACRO_PLANNING/WRITING 等）。

**抽象方向：** 提取为通用的后台任务调度框架。

**通用接口：**

JobDefinition 描述任务：包含 id、status（idle / running / paused / error / completed）、current_stage、current_step、error_count 和 config。

JobScheduler 提供：
- `register_stage(name, handler)`：注册阶段处理器
- `start/pause/resume/stop(job_id)`：任务生命周期控制
- `run_loop()`：后台轮询，执行 running 状态的任务

**通用能力：**
- 数据库驱动（进程重启无缝恢复）
- 步骤级幂等恢复
- 与熔断器集成
- 状态流转管理
- 并发控制

**适用场景：** 任何需要后台自动执行多步骤任务的系统。

---

### 2.5 AI 文本检测器 (AI Text Detector)

**来源：** Phase 4 `03-anti-ai-rules.md`

**业务耦合点：** 当前的疲劳词表和句式模式是小说写作特定的。

**抽象方向：** 提取为通用的 AI 生成文本检测框架，规则库可配置。

**通用接口：**

DetectionRuleSet 定义检测规则集：包含 language、fatigue_words（按严重度分组的疲劳词表）和 banned_patterns（正则表达式列表）。

AITextDetector 接收规则集，提供 `score(text)` 方法返回 DetectionResult，包含：
- score：0-1 的 AI 检测分数（越低越好）
- fatigue_word_hits：命中的疲劳词及位置
- pattern_violations：命中的禁用句式及位置
- suggestions：改进建议

**适用场景：** 任何需要检测和降低 AI 痕迹的内容生成系统（文章、营销文案、报告等）。

---

## 三、SaaS 基础设施组件（Phase 6）

这些是标准 SaaS 基础设施，与 AI 小说业务完全无关：

| 组件 | 说明 | 复杂度 |
|------|------|--------|
| **用户认证系统** | 邮箱密码 + OAuth2 (Google/GitHub) + JWT (access+refresh) + 角色权限 | 中 |
| **用量追踪与配额管理** | usage_records 表 + 套餐定义 + 超额拦截 + 月度统计 | 中 |
| **模型代理** | 平台 Key vs 用户自有 Key 路由 + 按用量计费 | 低 |
| **协作权限框架** | owner/editor/viewer 矩阵 + 邀请机制 + 分享链接 | 中 |
| **模板市场框架** | 发布/浏览/下载/评分/评论 + 内容审核 | 高 |
| **对象存储适配器** | LocalStorage / S3Storage / MinIOStorage 统一接口 | 低 |
| **任务队列封装** | ARQ (Redis) 异步任务执行 + 状态查询 | 低 |

---

## 组件依赖关系

```
LLM 网关
  ├── 熔断器（集成到 LLM 调用链）
  ├── Token 计数器（用于预算管理）
  └── 结构化输出提取器（依赖 LLM 网关）

上下文预算管理器
  └── Token 计数器

流水线编排器
  ├── LLM 网关（各阶段调用 LLM）
  └── SSE 事件总线（推送阶段进度）

DB 驱动任务调度器
  ├── 流水线编排器（调度器驱动流水线执行）
  ├── 熔断器（集成保护）
  ├── SSE 事件总线（推送任务状态）
  └── Webhook 通知器（外部通知）
```

## 建议的开发顺序

如果要先独立开发通用组件：

```
第一批（Phase 1 前置）:
  1. LLM 网关（含结构化输出、重试）
  2. Token 计数器
  3. 向量检索封装

第二批（Phase 1 同步）:
  4. 流水线编排器
  5. 上下文预算管理器
  6. SSE 事件总线

第三批（Phase 2-5 同步）:
  7. 熔断器（集成到 LLM 网关）
  8. Schema 校验状态机
  9. Webhook 通知器
  10. DB 驱动任务调度器
  11. AI 文本检测器

第四批（Phase 6）:
  12-18. SaaS 基础设施组件
```
