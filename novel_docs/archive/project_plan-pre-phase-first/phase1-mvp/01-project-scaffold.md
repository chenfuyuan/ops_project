---
title: Phase 1 — 项目脚手架与基础设施
version: 2.0
date: 2026-04-20
---

# 项目脚手架与基础设施

## 架构模式

采用模块化单体架构（详见 `docs/新项目脚手架_纯骨架版_模块化单体.md`）。核心原则：

- 按模块纵向组织，每个模块内部独立分层
- 模块间只通过 `api/contracts.py` 和 `api/facade.py` 通信
- 共享层极小，只放无业务语义的基础设施
- 单体运行，边界按未来服务拆分标准设计

## 项目结构

```
novel-ai/
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py                 # FastAPI 入口
│   │   │
│   │   ├── modules/                # 业务模块（纵向隔离）
│   │   │   ├── novel/              # 小说项目管理
│   │   │   ├── character/          # 角色与状态
│   │   │   ├── outline/            # 大纲生成（雪花法）
│   │   │   ├── blueprint/          # 蓝图生成 + 伏笔台账
│   │   │   ├── chapter/            # 章节 CRUD + 生成流水线 + 章后管线
│   │   │   ├── memory/             # 记忆引擎 + 洋葱模型 + 向量检索
│   │   │   └── llm/                # LLM 适配 + 路由 + 配置
│   │   │
│   │   ├── interfaces/             # 输入输出适配层
│   │   │   └── http/
│   │   │       ├── routes/         # 路由（委托模块 facade）
│   │   │       │   ├── novel.py
│   │   │       │   ├── outline.py
│   │   │       │   ├── blueprint.py
│   │   │       │   ├── chapter.py
│   │   │       │   ├── character.py
│   │   │       │   ├── llm.py
│   │   │       │   └── health.py
│   │   │       ├── schemas/        # 请求响应模型
│   │   │       │   └── common.py
│   │   │       └── middleware/
│   │   │           ├── request_context.py
│   │   │           └── error_handler.py
│   │   │
│   │   ├── shared/                 # 共享层（极小，无业务语义）
│   │   │   ├── kernel/             # 基础类型
│   │   │   │   ├── ids.py
│   │   │   │   ├── types.py
│   │   │   │   ├── exceptions.py
│   │   │   │   └── result.py
│   │   │   ├── infra/              # 基础设施
│   │   │   │   ├── settings.py
│   │   │   │   ├── db.py
│   │   │   │   ├── logger.py
│   │   │   │   ├── cache.py
│   │   │   │   └── clock.py
│   │   │   └── events/             # 事件机制
│   │   │       ├── base.py
│   │   │       ├── bus.py
│   │   │       └── handlers.py
│   │   │
│   │   └── bootstrap/              # 系统装配层
│   │       ├── container.py        # 依赖注入容器
│   │       ├── module_registry.py  # 模块注册表
│   │       ├── wiring.py           # 模块间装配
│   │       └── startup.py          # 启动初始化
│   │
│   ├── migrations/                 # Alembic 数据库迁移
│   │   └── versions/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   └── scripts/
│       ├── init_env.py
│       └── dev_start.py
│
├── frontend/                       # TypeScript 前端
│   ├── package.json
│   ├── src/
│   │   ├── api/                    # API 客户端
│   │   ├── components/             # 通用组件
│   │   ├── pages/                  # 页面
│   │   ├── stores/                 # 状态管理
│   │   └── types/                  # 类型定义
│   └── ...
│
├── data/                           # 运行时数据（gitignore）
│   ├── vectorstore/
│   └── novels/
├── .env.example
├── Makefile
└── docs/
```

### 模块内部标准结构

每个模块遵循统一的内部分层（以 chapter 模块为例）：

```
app/modules/chapter/
├── api/
│   ├── contracts.py        # 公开数据结构（DTO、Protocol）
│   └── facade.py           # 对外统一入口
├── application/
│   ├── services.py         # 用例编排
│   └── pipeline.py         # 生成流水线编排
├── domain/
│   ├── entities.py         # 章节实体
│   └── exceptions.py       # 领域异常
├── infrastructure/
│   ├── repositories.py     # 仓储实现
│   └── orm_models.py       # SQLAlchemy 模型
└── module.py               # 模块注册入口
```

- `api/` 是模块的公开面，其他模块只能依赖这里
- `application/` 编排业务用例，调用仓储和领域对象
- `domain/` 实体、值对象、领域规则
- `infrastructure/` 仓储实现、ORM 模型、外部适配
- `module.py` 声明模块名称、facade、生命周期钩子

## 模块间依赖规则

- 模块间只能依赖对方的 `api/contracts.py` 和 `api/facade.py`
- 禁止直接访问其他模块的 application/domain/infrastructure
- 禁止跨模块直连数据库表或共享 ORM 模型
- 共享层不得承载业务逻辑

示例：memory 模块需要角色数据时，调用 `character_facade.get_current_states(novel_id)` 而非直接查询 character_states 表。

## Phase 1 模块职责

| 模块 | 职责 | 核心实体/表 |
|------|------|------------|
| novel | 小说 CRUD、novel_architecture 存储 | novels, novel_architecture |
| character | 角色 CRUD、状态快照管理 | characters, character_states |
| outline | 雪花法五步大纲生成 | 通过 novel facade 读写 architecture |
| blueprint | 蓝图批次生成、伏笔台账 | chapter_blueprints, foreshadowing |
| chapter | 章节 CRUD + 生成流水线 + 章后管线 | chapters, chapter_summaries, pipeline_artifacts |
| memory | 记忆引擎、洋葱模型上下文、向量检索 | 通过多模块 facade 读取，ChromaDB |
| llm | LLM 适配器、任务路由、配置管理 | llm_profiles |

## 后端技术选型

| 组件 | 选择 | 理由 |
|------|------|------|
| Web 框架 | FastAPI | async 原生、自动 OpenAPI 文档、Pydantic 集成 |
| 数据库 | PostgreSQL | 多用户就绪、JSONB 原生、全文搜索、连接池 |
| ORM | SQLAlchemy 2.0 (async) | 类型安全、每模块独立 ORM 模型、Alembic 集成 |
| 迁移工具 | Alembic | 标准 Python 迁移工具，模块感知 |
| 向量存储 | ChromaDB | Python 原生，嵌入式，零运维 |
| 数据校验 | Pydantic v2 | FastAPI 原生集成，性能好 |
| HTTP 客户端 | httpx | async 原生，用于 LLM API 调用 |
| 包管理 | uv | 快速，现代 Python 包管理 |

## 前端技术选型

| 组件 | 选择 | 理由 |
|------|------|------|
| 框架 | React 19 + TypeScript | 生态最大，组件库丰富 |
| 构建 | Vite 6 | 快速 HMR，开箱即用 |
| UI 库 | shadcn/ui + Tailwind CSS 4 | 可定制性强，不引入重依赖 |
| 状态管理 | Zustand | 轻量，API 简洁 |
| HTTP 客户端 | fetch + SSE | 原生 API，SSE 用于流式生成 |
| 路由 | React Router v7 | 标准选择 |

## 数据库初始化

Phase 1 需要创建的表：

- 核心表：novels, novel_architecture, characters, character_states, chapter_blueprints, chapters, chapter_summaries, foreshadowing
- 配置表：llm_profiles
- 流水线表：pipeline_artifacts

每个模块在自己的 `infrastructure/orm_models.py` 中定义 SQLAlchemy 模型。使用 Alembic 管理迁移，每个 Phase 新增的表通过新的迁移版本引入。表结构详见总设计文档 `2026-04-20-ai-novel-02-data-model.md`。

## 配置管理

通过 `.env` 文件 + 环境变量管理配置，由 `shared/infra/settings.py` 统一加载。

| 配置项 | 说明 |
|--------|------|
| DATABASE_URL | PostgreSQL 连接串 |
| CHROMA_PERSIST_DIR | ChromaDB 持久化目录 |
| DATA_DIR | 小说文件存储目录 |
| HOST / PORT | 服务器监听地址 |
| DEFAULT_LLM_PROVIDER | 默认 LLM 提供商（可通过 DB 中的 llm_profiles 覆盖） |
| DEFAULT_LLM_BASE_URL | 默认 LLM API 端点 |
| DEFAULT_LLM_API_KEY | 默认 LLM API Key |
| DEFAULT_LLM_MODEL | 默认模型 ID |

## 系统装配（bootstrap/）

`bootstrap/` 负责将所有模块和基础设施组装起来，替代传统的单一 `deps.py`。

- `container.py` — 依赖注入容器，持有所有模块 facade 实例
- `module_registry.py` — 模块注册表，按顺序注册模块，解析依赖
- `wiring.py` — 模块间装配逻辑，将 facade 实现绑定到接口
- `startup.py` — 启动初始化，协调整个装配流程

装配顺序：

1. 加载 `shared/infra/settings.py` 配置
2. 初始化 PostgreSQL 连接（SQLAlchemy async engine）
3. 初始化 ChromaDB 客户端
4. 按依赖顺序注册模块（llm → novel → character → blueprint → memory → outline → chapter）
5. 每个模块的 `module.py` 注册 facade 到容器
6. 注册 `interfaces/http/routes/` 到 FastAPI，路由通过容器获取 facade

## 启动流程

```
1. 加载 .env 配置（shared/infra/settings.py）
2. 初始化 PostgreSQL 连接，运行 Alembic 迁移
3. 初始化 ChromaDB 客户端
4. 执行 bootstrap/startup.py：注册模块 → 装配依赖 → 绑定 facade
5. 注册 HTTP 路由（interfaces/http/routes/）
6. 启动 Uvicorn 服务器
```

## 错误处理

- 全局异常处理中间件（`interfaces/http/middleware/error_handler.py`），统一返回格式：`{error: string, detail?: any}`
- LLM 调用失败：重试 2 次（指数退避），仍失败则返回错误
- 数据库操作：事务保护，失败回滚
- 文件操作：写入临时文件后原子重命名
