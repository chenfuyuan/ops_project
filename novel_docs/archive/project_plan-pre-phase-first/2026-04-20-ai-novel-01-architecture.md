---
title: AI 长篇小说生成系统 — 系统架构与核心流水线
version: 1.0
date: 2026-04-20
parent: 2026-04-20-ai-novel-00-overview.md
---

# 系统架构与核心流水线

## 文档角色

本文档属于**总纲专题**，承载跨多个 phase 共享的系统架构主线与核心流水线设计。

使用方式：
- 从总纲入口页按需进入
- 为 phase overview 和专题文档提供架构背景
- 不替代任何单一 phase 的目标、范围或完成标准说明

## 整体架构

采用模块化单体架构，按业务领域纵向划分模块，模块间通过 facade 通信。

```
┌──────────────────────────────────────────────────────────┐
│                    TS Web Frontend                        │
│          (项目管理 / 编辑器 / 可视化面板)                   │
└───────────────────────┬──────────────────────────────────┘
                        │ REST API + SSE
┌───────────────────────┴──────────────────────────────────┐
│            app/interfaces/http/ (FastAPI)                 │
│          路由委托模块 facade，不直接调用内部服务              │
├──────────────────────────────────────────────────────────┤
│                     app/modules/                          │
│                                                          │
│  ┌────────┐ ┌─────────┐ ┌────────┐ ┌─────────┐         │
│  │ novel  │ │character│ │outline │ │blueprint│         │
│  │ 小说管理│ │ 角色状态 │ │ 大纲生成│ │蓝图+伏笔 │         │
│  └────────┘ └─────────┘ └────────┘ └─────────┘         │
│  ┌─────────────┐ ┌────────┐ ┌────────────┐                  │
│  │   chapter   │ │ memory │ │ ai_gateway │                  │
│  │流水线+章后管线│ │记忆引擎 │ │ AI网关路由 │                  │
│  └─────────────┘ └────────┘ └───────┘                   │
│                                                          │
│  每个模块内部：api/ | application/ | domain/ | infra/     │
│  模块间通信：仅通过 api/contracts.py 和 api/facade.py     │
├──────────────────────────────────────────────────────────┤
│          app/shared/ + app/bootstrap/                     │
│  kernel (IDs, types, exceptions)                         │
│  infra (DB, logger, settings, cache)                     │
│  events (事件总线)                                        │
│  bootstrap (容器, 模块注册, 装配, 启动)                    │
└──────────────────────────────────────────────────────────┘
```

后续 Phase 新增模块：audit（P2）、narrative（P3）、style（P4）、autopilot（P5）、user / billing / collaboration / marketplace（P6）。

## 各层职责

### TS Web Frontend

单页应用，提供：
- 项目管理：创建/配置小说项目，选择类型和模型
- 大纲编辑器：可视化编辑雪花法产物和章节蓝图
- 写作工作台：章节编辑、触发生成、查看 diff
- 状态面板：角色状态、伏笔台账、剧情线进度
- 分析面板：张力曲线、风格评分、审计问题列表
- 自动驾驶控制台：启停、进度监控、暂停审核

与后端通过 REST API 通信，实时更新通过 SSE 推送。

### Python API Layer

FastAPI 应用，职责：
- RESTful 路由（`interfaces/http/routes/`），委托模块 facade 处理业务逻辑
- 请求校验（Pydantic models）
- SSE 端点用于流式生成和进度推送
- `bootstrap/` 统一装配模块依赖图
- 后续 SaaS 阶段加入认证鉴权中间件

### Pipeline Orchestrator

核心编排器，管理单章生成的完整生命周期。职责：
- 按顺序调度各 Agent（Plan → Compose → Draft → Audit → Revise → Commit）
- 每步的输入输出持久化为中间产物（pipeline_artifacts 表）
- 检查点恢复：任意步骤失败后可从该步重跑
- 人工模式下在每步之间暂停等待确认
- 自动模式下连续执行，仅在审计发现关键问题时暂停

### Agent 层

6 个核心 Agent，各自职责明确：

**Planner（规划器）**
- 输入：大纲、章节蓝图、作者意图、记忆检索结果
- 输出：章节意图文档（must-keep / must-avoid / 冲突处理指导）
- LLM 调用：1 次

**Composer（上下文编译器）**
- 输入：章节意图、DB 中的全部状态
- 输出：上下文包（context payload）+ 规则栈（rule stack）+ 输入追踪（trace）
- LLM 调用：0 次（纯本地编译）
- 核心逻辑：调用 MemoryEngine.build_context() 执行洋葱模型分层裁剪，再叠加主题代理规则编译规则栈

**Writer（写作器）**
- 输入：编译后的上下文包 + 规则栈 + 主题代理指令
- 输出：章节草稿
- LLM 调用：1 次（流式输出）
- 内置：字数治理、去 AI 化规则、风格指纹注入

**Auditor（审计器）**
- 输入：章节草稿 + DB 中的状态
- 输出：问题清单（每项含维度、严重度、描述）
- LLM 调用：1 次
- 审计维度：角色记忆、状态连续性、伏笔追踪、时间线、资源连续性、大纲偏离、叙事节奏等

**Reviser（修订器）**
- 输入：章节草稿 + 审计问题清单（仅 critical 项）+ DB 中的相关状态
- 输出：修订后的章节文本
- LLM 调用：1 次
- 工作模式：接收具体的 critical 问题描述和原文，针对性修改而非重写全章
- 循环约束：最多 3 轮 Audit→Revise，3 轮后仍有 critical 则暂停等人工

**Reflector（状态反射器）**
- 输入：最终章节文本 + 当前 DB 状态
- 输出：JSON Delta（角色状态变更、新伏笔、伏笔推进、摘要、三元组、张力评分）
- LLM 调用：1 次
- 关键约束：输出经 Pydantic schema 校验，非法变更被拒绝

### Core Services

分布在各业务模块中，详见 [03-core-services.md](2026-04-20-ai-novel-03-core-services.md)（含模块归属表）。

### AI 网关层

位于 `modules/ai_gateway/`，通过 facade 对外提供统一接口。

AIGatewayAdapter 提供两个核心方法——同步调用（invoke）返回完整响应，流式调用（stream）返回异步迭代器。上层代码不关心具体模型提供商。

多模型路由：
- 每个任务类型（plan / draft / audit / reflect / summarize 等）可配置不同的模型
- 通过 `ai_gateway_profiles` 表存储配置，运行时按任务类型查找
- 初期支持 OpenAI 兼容协议（覆盖 GPT、Claude 兼容端点、DeepSeek、Qwen、Ollama 等）
- 后续按需加入 Anthropic 原生 SDK、其他厂商 SDK

路由策略示例：
| 任务 | 推荐模型 | 理由 |
|------|---------|------|
| draft（写作） | Claude / GPT-4o | 创意能力强 |
| audit（审计） | GPT-4o-mini / DeepSeek | 成本低，逻辑推理够用 |
| reflect（状态提取） | GPT-4o-mini | 结构化输出稳定 |
| plan（规划） | Claude / GPT-4o | 需要全局理解 |
| summarize（摘要） | GPT-4o-mini | 简单任务，成本优先 |

### Persistence Layer

三种存储各司其职，由 `shared/infra/` 提供连接管理：
- **PostgreSQL (SQLAlchemy 2.0)：** 所有结构化状态（角色、伏笔、剧情线、摘要、审计问题、配置等）。每个模块在自己的 `infrastructure/orm_models.py` 中定义模型。
- **ChromaDB：** 章节文本向量和外部知识向量，用于语义检索。由 `memory` 模块封装。
- **文件系统：** 章节全文 markdown、流水线中间产物的大文本内容。DB 中存引用路径。

## 核心写作流水线

### 单章生成完整流程

```
┌──────────┐
│  Plan    │ Planner 读取大纲/蓝图 + 作者意图 + 记忆检索
│          │ → 输出：章节意图文档 (chapter_intent)
└────┬─────┘
     ▼
┌──────────┐
│ Compose  │ Composer 查询 DB 状态，洋葱模型分层裁剪（无 LLM）
│          │ → 输出：上下文包 (context) + 规则栈 (rules) + 追踪 (trace)
└────┬─────┘
     ▼
┌──────────┐
│  Draft   │ Writer 接收治理后上下文 + 主题代理规则
│          │ → 输出：章节草稿 (draft)
└────┬─────┘
     ▼
┌──────────┐     ┌──────────┐
│  Audit   │────▶│  Revise  │ 关键问题自动修订
│          │◀────│          │ 非关键标记人工审核
└────┬─────┘     └──────────┘
     │ 关键问题清零
     ▼
┌──────────┐
│  Commit  │ Reflector 提取事实 → JSON Delta + schema 校验 → 更新 DB
│          │ 章后统一管线：摘要、三元组、伏笔、张力、风格评分
└──────────┘
```

### 大纲生成流程（雪花写作法）

```
Step 1: 核心种子
  "当[主角]遭遇[事件]，必须[行动]，否则[灾难]；同时[隐藏危机]酝酿"
  → 保存到 novel_architecture.core_seed

Step 2: 角色动力三角
  每个角色：表层追求 / 深层欲望 / 灵魂需求
  弧线设计：初始状态 → 触发 → 认知失调 → 转变 → 终态
  关系冲突网
  → 保存到 characters 表

Step 3: 角色初始状态
  结构化角色表：物品、能力、身体/心理状态、关系网、触发事件
  → 保存到 character_states 表（chapter_num=0）

Step 4: 世界观构建
  三维世界：物理维度 / 社会维度 / 隐喻维度
  动态元素与角色决策的交互
  → 保存到 novel_architecture.world_building

Step 5: 三幕结构
  触发 / 对抗 / 解决
  嵌套反转、伏笔回收计划、悬念因子
  → 保存到 novel_architecture.three_act_structure
```

每步之间写入 `checkpoint` 字段，失败后可从断点续跑。

### 章节蓝图生成

输入：大纲（三幕结构）
输出：每章的结构化蓝图

每章蓝图包含：
- `title` — 章节标题
- `positioning` — 角色/事件/主题定位
- `core_function` — 推进/转折/揭示
- `suspense_density` — 悬念密度（1-5）
- `foreshadow_ops` — 伏笔操作列表（植入/强化/收获 + 目标伏笔 ID）
- `disruption_level` — 认知颠覆度（1-5 星）
- `summary` — 一句话概要

长篇按批次生成（每批 20 章），支持从已有蓝图续写。
章节按 3-5 章为一个"悬念单元"分组，遵循 2 紧 → 1 缓的节奏曲线。
