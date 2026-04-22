## MODIFIED Requirements

### Requirement: 项目初始化骨架必须定义默认运行时拓扑
系统初始化方案 MUST 定义 `API 进程 + Worker 进程` 的默认运行时形态，并明确 PostgreSQL、Redis 与 S3-compatible Object Storage 的职责分工。初始化阶段 MAY 只建立基础接入点，但 MUST 保留后续实现这些运行时角色的清晰承接位置。

当仓库提交 Docker/Compose 相关资产时，规格 MUST 明确区分当前已经进入仓库的最小容器化基线与尚未进入容器编排的长期架构目标组件。当前仓库若仅提供最小容器化闭环，则该闭环可以只覆盖 `api`、`worker` 与 `redis`，但不得因此把 PostgreSQL、S3-compatible Object Storage / MinIO 或数据库迁移执行链路误写为已完成的现成容器服务。

#### Scenario: 初始化方案包含 API 与 Worker 入口
- **WHEN** 团队按照初始化方案建立应用入口
- **THEN** 方案中同时包含 API 入口与 Worker 入口的承接方式

#### Scenario: 初始化方案明确基础设施职责
- **WHEN** 团队查阅初始化规格以接入基础设施
- **THEN** 可以明确区分 PostgreSQL 用于核心持久化、Redis 用于缓存与轻量协调、S3-compatible Object Storage 用于文件与产物存储

#### Scenario: 当前最小容器化基线反映已提交资产
- **WHEN** 团队查阅仓库中的 `Dockerfile` 与 `docker-compose.yml`
- **THEN** 可以确认当前最小容器化基线覆盖 `api`、`worker` 与 `redis`

#### Scenario: 未落地依赖不得被描述为现成容器资产
- **WHEN** 团队查阅初始化规格与容器化说明
- **THEN** 若 PostgreSQL、S3-compatible Object Storage / MinIO 或 migration execution 尚未进入当前 Docker 编排，它们必须被表述为后续架构目标与承接位，而不是当前已完成的容器服务

#### Scenario: 长期拓扑目标与当前容器化基线分层表达
- **WHEN** 团队同步运行时文档与 OpenSpec
- **THEN** 规格同时保留长期运行时拓扑目标与当前已提交最小 Docker 资产的说明，避免将两者混写为同一层级的已实现能力
