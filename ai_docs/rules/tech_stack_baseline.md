# 技术栈基线

本文件定义本仓库生成代码时默认采用的技术基线。

## 默认技术栈
- Python 3.13
- 使用 `uv`、`pyproject.toml` 和 `uv.lock`
- HTTP API 使用 FastAPI
- 请求、响应、配置和 DTO 校验使用 Pydantic v2
- 数据访问使用 SQLAlchemy 2.x
- Schema 迁移使用 Alembic
- PostgreSQL 承载核心持久化业务数据
- Redis 承载缓存、轻量协调和 Celery 支撑能力
- Celery 承载异步后台任务
- S3-compatible object storage 承载文件和大对象产物

## 默认运行形态
默认运行时拓扑为：
- API process
- Worker process

本地开发可采用 Docker Compose 作为推荐编排方式，以保持 API、Worker 与基础依赖的拓扑一致。
正式环境默认以容器化部署作为交付方向。
当前仓库若未提供 `Dockerfile`、Compose 文件或部署清单，生成代码、命令或文档时不得假定这些工程产物已经存在。

API process 负责同步请求响应链路和任务投递。
Worker process 负责耗时、可重试、批处理或后台任务。

## 存储落位规则
- 核心业务数据进入 PostgreSQL。
- 短生命周期缓存和轻量协调数据进入 Redis。
- 文件以及大体积二进制或文本产物进入 S3-compatible object storage。
- 需要结构化、可审计的元数据保留在 PostgreSQL。
- 大载荷应通过引用传递，而不是直接塞进队列消息。

## 对编码的影响
- 除非用户明确要求，否则不要自行发散到其他技术栈。
- 不要在 `uv` 之外再引入额外的依赖管理体系。
- 不要把实现选择逻辑放进业务代码，应保留在 `bootstrap`。
- 不要在 `service.py` 中直接写外部 SDK 调用。
- 当仓库中尚未存在 `Dockerfile`、Compose 文件或部署清单时，不要输出“基于现有 Docker 资产”的建议，也不要虚构镜像名、服务名或容器启动命令。

## Worker 选择规则
以下场景默认应进入后台 worker：
- 耗时的外部调用
- 文件解析、导入或导出任务
- 可重试任务
- 不需要阻塞请求生命周期的工作
- 适合通过队列削峰的突发性工作

## Shared 基础设施基线
系统级基础设施通常应放在 `shared/infra` 中。
典型示例包括：
- 配置加载
- 数据库连接管理
- 日志和 tracing 包装
- HTTP client 包装
- 序列化辅助
- 通用 retry 和 timeout 包装

## Bootstrap 规则
`bootstrap` 负责：
- 运行时装配
- 实现选择
- local / remote / mock 的接线
- 进程启动时的组装
