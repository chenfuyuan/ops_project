## Why

仓库现在已经落地了最小 Docker 容器化基线：存在 `Dockerfile` 与 `docker-compose.yml`，并且当前可验证的本地最小闭环是 `api + worker + redis`。但现有 `project-bootstrap-baseline` OpenSpec 仍主要停留在运行时拓扑的抽象层，没有明确区分“已提交到仓库的最小容器化资产”和“仍属于长期架构目标但尚未进入 Docker 编排的基础设施组件”。

如果不补这一层规范，后续在阅读 OpenSpec 时容易把 PostgreSQL、S3-compatible Object Storage/MinIO、migration execution 误解为已经进入当前 Docker 基线的现成能力。

## What Changes

- 为 `project-bootstrap-baseline` 增加关于当前最小容器化基线的规范说明
- 明确当前已提交 Docker 资产覆盖 `api`、`worker`、`redis`
- 明确 PostgreSQL、对象存储/MinIO、数据库迁移执行链路仍是架构目标与承接位，而不是当前已提交的 Docker 服务
- 保持长期运行时架构基线不变，只补当前仓库事实边界

## Impact

- 影响 OpenSpec 文本表达与事实一致性
- 不新增运行时组件
- 不扩展为 CI/CD、Kubernetes、生产部署平台或完整本地基础设施编排设计
