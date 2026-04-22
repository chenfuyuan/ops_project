## Why

当前仓库已经定义了平台中立的 CI/CD 主基线与应用代码最小 CI 基线，但仍缺少 GitHub Actions 形式的可执行落地资产，导致主分支与 Pull Request 的代码变更无法在 GitHub 协作流程中自动执行默认门禁。现在补齐这一层，可以把既有基线从文档约束转化为实际可阻断的最小 CI 能力，同时保持现有边界与命令语义不被改写。

## What Changes

- 新增一个面向 GitHub Actions 的最小代码侧 CI capability，用于把现有三层最小流水线模型映射为单个 workflow 内的多 job 编排。
- 规定该 workflow 以 `push` 与 `pull_request` 为触发入口，服务于主分支与 Pull Request 的默认代码准入。
- 规定 workflow 继续复用现有基线中的命令语义与 `uv` 执行基线，而不是在平台配置中重新定义新的检查规则。
- 明确平台映射只覆盖最小代码侧 CI，不扩展到文档一致性门禁、CD、镜像构建、制品上传、缓存、矩阵或其他增强项。

## Capabilities

### New Capabilities
- `github-actions-minimal-ci`: 定义如何使用单个 GitHub Actions workflow 与多个 jobs 落地现有应用代码最小 CI 基线。

### Modified Capabilities
- `application-minimal-ci`: 补充该 capability 可被映射到 GitHub Actions 的实现要求，但不改变其平台中立边界与三层最小流水线语义。

## Impact

- 受影响目录主要包括 `.github/workflows/` 以及与 CI 命令入口相关的仓库工程资产。
- 受影响系统为 GitHub 仓库内的 `push` / `pull_request` 协作流程与默认代码准入门禁。
- 继续以 `pyproject.toml`、`uv`、现有测试目录与架构检查资产作为执行基础，不新增 CD 或企业平台依赖。
