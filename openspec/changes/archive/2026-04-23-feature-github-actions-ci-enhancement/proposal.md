## Why

当前仓库已经具备最小可用的 GitHub Actions CI，但它仍主要承担基础校验职责，尚未形成适合日常 Pull Request 协作的平衡型工程化门禁。随着仓库进入“有最小 CI、开始追求稳定协作质量”的阶段，现在需要在不扩大到发布或部署链路的前提下，补齐质量门禁、架构守卫、执行效率与失败诊断能力。

## What Changes

- 在现有 GitHub Actions CI 基础上，引入面向 Pull Request 的轻量质量预检能力，例如标题规范与基础格式校验。
- 将架构守卫从“已有测试入口”提升为显式的 CI 门禁目标，明确其在增强型流水线中的职责与边界。
- 为现有三段最小 CI 增加工程化增强能力，包括缓存、并发取消、轻量路径感知、测试结果可见性与失败产物归档。
- 保持当前 CI 的主入口、`uv` 基线、Python 3.13 基线与三段职责不变，不将范围扩展到发布、部署、镜像、制品或完整 CD。

## Capabilities

### New Capabilities
- `github-actions-enhanced-ci`: 定义 GitHub Actions 在最小代码侧 CI 之上提供平衡型质量门禁、架构守卫、运行治理与失败诊断增强的要求边界。

### Modified Capabilities
- `github-actions-minimal-ci`: 明确最小 GitHub Actions CI 作为增强型 CI 的基础入口与保留边界，允许在不突破最小 CI 核心职责的前提下被增强型 capability 叠加使用。

## Impact

- 受影响系统：`/.github/workflows/ci.yml` 及相关 GitHub Actions 配置。
- 受影响规则：Pull Request 准入规则、架构守卫表达、CI 失败诊断与执行治理策略。
- 受影响依赖：继续使用 Python 3.13、`uv` 与现有 `tests/architecture`、`tests/unit`、`tests/integration` 作为主要执行资产。
- 不影响范围：业务 API、运行时架构、发布部署链路、镜像与制品交付流程。
