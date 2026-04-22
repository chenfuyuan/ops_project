## 1. 审核当前容器化资产

- [x] 1.1 核对 `Dockerfile` 与 `docker-compose.yml` 的实际服务范围
- [x] 1.2 确认当前最小容器化闭环仅覆盖 `api`、`worker`、`redis`

## 2. 更新 OpenSpec delta spec

- [x] 2.1 在 `project-bootstrap-baseline` 中补充当前最小 Docker 基线的规范表述
- [x] 2.2 明确未进入当前 Compose 的 PostgreSQL、对象存储/MinIO、migration execution 不得描述为现成容器服务
- [x] 2.3 保留长期运行时架构目标，不将当前最小 Docker 基线误写成完整拓扑

## 3. 同步主 spec

- [x] 3.1 将 approved delta 同步到 `openspec/specs/project-bootstrap-baseline/spec.md`
- [x] 3.2 校验主 spec 与 change spec 的 wording 一致

## 4. 验证

- [x] 4.1 确认 OpenSpec 文本与仓库中的 `Dockerfile`、`docker-compose.yml` 一致
- [x] 4.2 确认 OpenSpec 未夸大 PostgreSQL、MinIO、migration service 的当前容器化状态
