---
title: Phase 6.1 — 基础设施升级
version: 1.0
date: 2026-04-20
parent: Phase 6 — SaaS 化
---

# 基础设施升级

## 概述

将单用户本地架构升级为可水平扩展的多用户服务架构。建立在模块化单体基础上——每个模块的 ORM 模型和仓储已按模块隔离，基础设施升级主要影响 `shared/infra/` 和 `bootstrap/`，各模块的业务代码无需改动。

四个核心变更：数据库升级、对象存储、任务队列、容器化部署。

---

## 1. 数据库升级：PostgreSQL 多租户与连接池

### 1.1 驱动层切换

Phase 1 起即使用 PostgreSQL + SQLAlchemy 2.0。SaaS 阶段的主要变更是增加连接池配置和多租户隔离，驱动层本身无需切换。

| 项目 | Phase 1-5 | Phase 6 升级 |
|------|-----------|-------------|
| 连接池 | 默认配置 | asyncpg 连接池（min=5, max=20） |
| 全文搜索 | 无 | PostgreSQL tsvector（可选） |
| 多租户 | 单用户 | user_id 隔离 |

### 1.2 连接池配置

SaaS 阶段升级 `shared/infra/db.py` 的连接池配置：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| host | localhost | 数据库主机 |
| port | 5432 | 端口 |
| database | novel_ai | 数据库名 |
| user | novel_ai | 用户名 |
| min_connections | 5 | 最小连接数 |
| max_connections | 20 | 最大连接数 |
| command_timeout | 60 | 命令超时（秒） |

提供 connect/disconnect 生命周期方法，以及 execute/fetch/fetchrow 查询方法。

### 1.3 多租户隔离

所有业务表新增 user_id 外键（关联 users 表），所有查询强制按 user_id scope。

user_id 过滤在两层实施：
1. 模块 facade 层：接收 user_id 参数并传递给内部服务
2. 仓储层：各模块 `infrastructure/repositories.py` 的所有查询方法强制包含 user_id 条件

需要添加 user_id 的表：novels、chapters、characters、blueprints、foreshadowings。每个表的 user_id 字段创建索引。

### 1.4 数据迁移策略

对于从 Phase 1-5 单用户模式升级到 SaaS 多用户模式：

1. 运行 Alembic 迁移，为所有业务表添加 user_id 字段
2. 将现有数据的 user_id 统一设为 default_user_id
3. 部署新版本，启用多租户隔离

---

## 2. 文件存储：本地文件系统 → 对象存储

### 2.1 StorageAdapter 协议

定义统一的文件存储抽象接口：

| 方法 | 说明 |
|------|------|
| save(key, content, content_type) | 保存文件，返回访问 URL 或 key |
| read(key) | 读取文件内容 |
| delete(key) | 删除文件 |
| exists(key) | 检查文件是否存在 |
| list_keys(prefix) | 列出指定前缀下的所有 key |
| get_url(key) | 获取文件的访问 URL |

### 2.2 实现类

三个实现：

- LocalStorage：本地文件存储（Phase 1-5 兼容，开发环境使用），基于 aiofiles，文件存储在 base_dir 下
- S3Storage：AWS S3 对象存储，基于 aiobotocore，支持配置 bucket、region、access_key、secret_key
- MinIOStorage：MinIO 自托管对象存储（S3 兼容），继承 S3Storage，仅 endpoint_url 不同

### 2.3 存储路径规范

```
{user_id}/{novel_id}/chapters/chapter_{num:03d}.md
{user_id}/{novel_id}/exports/novel_export_{timestamp}.epub
{user_id}/{novel_id}/assets/{filename}
{user_id}/avatars/{filename}
```

### 2.4 存储工厂

根据 settings.storage_backend 配置（local / s3 / minio）创建对应的 StorageAdapter 实例。

---

## 3. 任务队列：ARQ

### 3.1 为什么选 ARQ

| 方案 | 优点 | 缺点 |
|------|------|------|
| Celery | 功能全面，生态成熟 | 重，配置复杂，不原生 async |
| ARQ | 轻量，原生 asyncio，Redis-based | 功能较少，社区较小 |
| Dramatiq | 中等复杂度 | 不原生 async |

本项目已使用 asyncio 全栈，ARQ 是最自然的选择。

### 3.2 Worker 定义

三个异步任务：

- generate_chapter_task(novel_id, chapter_num, user_id)：异步章节生成，先检查配额再执行生成，完成后记录用量
- generate_outline_task(novel_id, user_id)：异步大纲生成
- batch_generate_task(novel_id, chapter_range, user_id)：批量章节生成，逐章调用 generate_chapter_task

Worker 配置：max_jobs=5，job_timeout=600（单任务最长 10 分钟），Redis 连接。

### 3.3 TaskQueue 接口

TaskQueue 封装 ARQ 的任务入队操作：

| 方法 | 说明 |
|------|------|
| enqueue_chapter_generation(novel_id, chapter_num, user_id) | 入队章节生成任务 |
| enqueue_outline_generation(novel_id, user_id) | 入队大纲生成任务 |
| enqueue_batch_generation(novel_id, chapter_range, user_id) | 入队批量生成任务 |
| get_job_status(job_id) | 查询任务状态 |

### 3.4 任务状态 API

`GET /api/tasks/{job_id}` — 查询异步任务执行状态。前端轮询此端点获取进度，或后续升级为 WebSocket 推送。

---

## 4. 部署架构

### 4.1 架构图

```
                    ┌─────────────────┐
                    │     Nginx       │
                    │   (反向代理/TLS) │
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
          ┌─────┴─────┐ ┌───┴───┐ ┌─────┴─────┐
          │  FastAPI   │ │ React │ │ ARQ Worker │
          │  (API x2)  │ │ (SPA) │ │  (x1-N)   │
          └─────┬──────┘ └───────┘ └─────┬──────┘
                │                        │
      ┌─────────┼────────────────────────┤
      │         │         │              │
  ┌───┴────┐ ┌──┴───┐ ┌──┴────┐ ┌──────┴──┐
  │Postgres│ │Redis │ │Chroma │ │S3/MinIO │
  │  SQL   │ │      │ │  DB   │ │         │
  └────────┘ └──────┘ └───────┘ └─────────┘
```

### 4.2 Docker Compose 服务

| 服务 | 镜像 | 说明 |
|------|------|------|
| nginx | nginx:alpine | 反向代理/TLS，静态文件服务，SSE/WebSocket 支持 |
| api | 自定义 | FastAPI 应用，2 副本，uvicorn 运行 |
| worker | 自定义 | ARQ Worker，可水平扩展 |
| frontend | 自定义 | React SPA 构建 |
| postgres | postgres:16-alpine | PostgreSQL 数据库，带健康检查 |
| redis | redis:7-alpine | Redis 缓存/队列，带健康检查 |
| chromadb | chromadb/chroma | 向量数据库 |
| minio | minio/minio | 对象存储，Console 端口 9001（仅开发环境暴露） |

### 4.3 Nginx 配置要点

- / 路径：React SPA，try_files 回退到 index.html
- /api/ 路径：代理到 api_backend upstream，禁用缓冲（支持 SSE/流式响应），read_timeout 600s
- /ws/ 路径：WebSocket 代理（未来实时协作）

### 4.4 环境配置

Settings 使用 pydantic-settings，从 .env 文件加载。主要配置分组：

| 分组 | 配置项 |
|------|--------|
| 数据库 | database_url |
| Redis | redis_url |
| 存储 | storage_backend, storage_local_dir, s3_*, minio_* |
| 认证 | jwt_secret, jwt_algorithm, access_token_expire_minutes, refresh_token_expire_days |
| OAuth | google_client_id/secret, github_client_id/secret |
| ChromaDB | chroma_host, chroma_port |
| 环境 | environment (development/staging/production), debug |

---

## 5. 新增依赖

| 包 | 用途 |
|----|------|
| asyncpg | PostgreSQL 异步驱动 |
| arq | 异步任务队列 |
| aiobotocore | S3/MinIO 客户端 |
| pyjwt | JWT 生成与验证 |
| passlib[bcrypt] | 密码哈希 |
| httpx | OAuth2 回调 HTTP 客户端 |
| python-multipart | 文件上传 |
| pydantic-settings | 环境配置管理 |
