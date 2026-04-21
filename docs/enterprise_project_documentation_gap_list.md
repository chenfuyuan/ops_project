# 企业级项目文档缺口清单

## 文档目标
本文档用于盘点当前仓库在企业级项目治理与交付层面的文档覆盖情况，明确已覆盖内容、缺失领域、优先级和建议补齐路径。

## 适用范围
- 面向项目正式文档体系 `docs/`
- 面向团队协作、运维、发布、安全与治理实践
- 不替代 `ai_docs/` 中的 AI 精简规则

## 本文负责 / 不负责
### 本文负责
- 盘点当前文档覆盖范围
- 识别企业级项目文档缺口
- 给出优先级与补齐建议
- 作为后续专题文档的导航入口

### 本文不负责
- 不展开具体环境、发布、安全或告警细则
- 不重写架构边界、依赖方向和命名规则
- 不替代各专题基线文档

## 当前已覆盖内容
当前仓库已在以下方面具备较清晰的正式文档：

1. 架构总览与模块边界
   - `docs/architecture_baseline/00-overview.md`
   - `docs/architecture_baseline/01-top-level-modules.md`
   - `docs/architecture_baseline/03-anti-corruption-and-dependencies.md`
   - `docs/architecture_baseline/04-governance-evolution-and-testing.md`

2. 技术栈与运行时基线
   - `docs/technical_architecture_baseline.md`

3. 命名与架构评审
   - `docs/naming_conventions.md`
   - `docs/architecture_review_checklist.md`

这些文档已经较好回答了“代码和模块应该如何组织”的问题，但对“系统如何稳定、安全、可审计地运行和交付”覆盖不足。

## 企业级项目文档缺口
### P0：必须优先补齐
1. 环境与部署基线
   - 缺少各环境的目标、差异控制和最小部署要求
   - 缺少 API / Worker / PostgreSQL / Redis / S3-compatible storage 的环境级约束

2. 配置与密钥管理
   - 缺少配置分类、来源优先级、密钥注入与轮换原则
   - 缺少禁止项，例如硬编码、入库、入日志、进仓库

3. 可观测性与告警
   - 缺少日志、指标、健康检查、告警分级的正式基线
   - 缺少发布后观察与故障定位所需的最小闭环定义

4. 安全基线
   - 缺少统一的应用安全、数据安全、依赖安全和例外机制说明
   - 缺少与配置、发布、审计相关的统一安全约束

5. 发布、变更与回滚
   - 缺少发布前检查、数据库迁移控制、发布后验证和回滚原则
   - 缺少变更记录与审批范围说明

### P1：建议后续补齐
1. 数据治理与敏感数据分级
2. 接口治理与错误码规范
3. 异步任务治理与队列规范
4. 运维值班与故障处置 Runbook
5. SLA / SLO 与告警升级路径
6. 权限模型与审计追踪细则

## 推荐新增文档
本次优先新增以下 6 份文档：

1. `docs/enterprise_project_documentation_gap_list.md`
2. `docs/deployment_environment_baseline.md`
3. `docs/configuration_and_secrets_management.md`
4. `docs/observability_and_alerting.md`
5. `docs/security_baseline.md`
6. `docs/release_change_and_rollback.md`

## 文档边界说明
为了避免重复，新增文档遵循以下原则：
- 架构边界与依赖方向，以 `docs/architecture_baseline/*.md` 为准
- 技术栈、运行拓扑和基础组件，以 `docs/technical_architecture_baseline.md` 为准
- 新文档只补运行治理、交付治理和安全治理层内容
- 交叉主题通过引用衔接，不在多篇文档中重复展开

## 建议维护方式
- 当运行环境、基础设施、发布流程或安全要求变化时，同步更新对应专题文档
- 当专题文档新增后，如果形成长期稳定规则，再按需同步到 `ai_docs/`
- 新增专题文档时，应保持单文档单主责，避免重新写成泛化总纲

## 推荐阅读顺序
1. `docs/enterprise_project_documentation_gap_list.md`
2. `docs/deployment_environment_baseline.md`
3. `docs/configuration_and_secrets_management.md`
4. `docs/observability_and_alerting.md`
5. `docs/security_baseline.md`
6. `docs/release_change_and_rollback.md`
