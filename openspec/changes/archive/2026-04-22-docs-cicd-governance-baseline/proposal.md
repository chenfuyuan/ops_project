## Why

当前仓库虽然已经有 `docs/cicd_baseline.md`、发布、安全、部署等相关文档，但仍缺少一个能够从“CI → 可发布制品 → 受控部署”闭环视角统一组织这些约束的 OpenSpec change。若继续仅依赖分散文档承载 CI/CD 规则，后续评审与落地容易出现门禁口径不一致、可发布制品定义不清、部署准入边界模糊，以及发布后验证与回滚入口分散的问题。

现在推进这个 change，是为了在不绑定任何具体平台的前提下，把现有 CI/CD 治理方向固化为一个稳定的 OpenSpec 输入，确保后续设计、任务拆解和文档补充都在同一组平台中立、严格治理、范围受控的约束下展开。

## What Changes

- 新增一个面向 CI/CD 治理闭环的 OpenSpec change，用于统一定义平台中立的 CI/CD 阶段模型、默认质量门禁、可发布制品抽象、受控部署边界、最小发布后验证与回滚入口。
- 明确本次 change 的交付方式以文档治理为主：新增或强化 CI/CD 主文档，并对发布、安全、部署相关文档建立职责分层与引用关系。
- 强化默认 CI 门禁的治理要求，明确文档一致性、架构/边界检查、依赖/安全最低门禁属于默认阻断项的一部分。
- 约束后续文档与设计必须保持平台中立，不得将 GitHub Actions、GitLab CI、Jenkins、镜像仓库、签名、扫描、审批链等未确认落地的能力写成既成事实。
- 约束 CD 范围仅到受控部署为止，不扩展到多环境晋升、复杂灰度策略、云资源拓扑或运维 SOP。

## Capabilities

### New Capabilities
- 无

### Modified Capabilities
- `cicd-baseline`: 细化并固化 CI/CD 主文档职责、默认质量门禁分层、可发布制品治理抽象，以及与 `docs/release_change_and_rollback.md`、`docs/security_baseline.md`、`docs/deployment_environment_baseline.md` 的职责映射要求。

## Impact

- 影响 `openspec/changes/docs-cicd-governance-baseline/` 下的后续 design、specs、tasks 产物。
- 影响 `openspec/specs/cicd-baseline/spec.md` 对 CI/CD 治理边界的表达与后续 delta 规格定义。
- 影响 `docs/cicd_baseline.md` 与现有发布、安全、部署文档之间的职责分工方式。
- 不影响任何具体 CI/CD 平台实现、YAML/Jenkinsfile 配置、云资源、部署拓扑或运维手册。
