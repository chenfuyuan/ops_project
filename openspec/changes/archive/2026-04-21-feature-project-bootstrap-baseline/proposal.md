## Why

当前仓库已经具备架构基线文档与技术基线文档，但缺少一个可驱动后续实现的正式 OpenSpec 变更集。如果没有这一步，项目初始化很容易退化为“只搭目录”或“直接写骨架代码”，从而丢失边界治理、运行拓扑、工作流组织方式与基础设施基线这些真正需要先被固定的内容。

现在推进这个 change，是为了把文档中的架构共识转化为可执行的初始化方案，确保后续设计、规格和任务拆解都在同一组边界与约束下展开。

## What Changes

- 新增“项目初始化骨架”变更，用于定义新项目默认的模块化单体骨架与初始化范围。
- 明确项目的顶层边界：`business / capabilities / interfaces / shared / bootstrap`。
- 明确项目作为工作流编排型后端的默认业务组织方式，包括 `workflow/`、`nodes/` 及节点内部 `node.py / service.py / dto.py / entities.py / rules.py / ports.py / infrastructure/` 的承接结构。
- 沿用既有技术基线文档中的默认运行时与技术选型：`API 进程 + Worker 进程`、PostgreSQL、Redis、S3-compatible Object Storage、FastAPI、Pydantic v2、SQLAlchemy 2.x、Alembic、Celery、`Python 3.13`，并使用 `uv + pyproject.toml + uv.lock` 作为统一依赖与环境管理基线。
- 新增项目初始化阶段必须同时建立的治理要求，包括依赖方向、准入规则、架构测试、高敏感评审区域与测试分层，并要求这些约束可执行而不只是文档说明。
- 约束后续实现只覆盖项目骨架与基础接入点，不扩展到具体业务实现、CI/CD 或生产级平台建设。

## Capabilities

### New Capabilities
- `project-bootstrap-baseline`: 定义新项目初始化所需的骨架结构、工作流组织方式、运行时基线、基础设施接入边界与治理护栏。

### Modified Capabilities
- 无

## Impact

- 影响 `openspec/changes/feature-project-bootstrap-baseline/` 下的后续设计、规格与任务产物。
- 影响后续项目初始化实现时的目录结构、工作流与节点模板、应用入口、配置体系、数据库迁移基座、异步任务接线与对象存储接入方式。
- 影响后续架构治理方式，包括 import 约束、准入规则、架构测试与高敏感区域评审标准。
- 不影响现有业务能力、外部 API 合约或已上线系统行为。
