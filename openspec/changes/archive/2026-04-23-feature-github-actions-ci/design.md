## Context

当前仓库已经通过 `docs/cicd_baseline.md` 与 `docs/application_minimal_ci_baseline.md` 定义了平台中立的 CI/CD 主基线与应用代码最小 CI 基线，但 GitHub 仓库内仍缺少 `.github/workflows/ci.yml` 这一执行入口。现有 `pyproject.toml` 已确认以 Python 3.13 与 `uv` 作为依赖与命令执行基线，`tests/architecture/`、`tests/unit/` 与 `tests/integration/` 也已经提供了可直接映射到三层最小流水线模型的测试资产。

本次设计的核心不是重新定义 CI 规则，而是把既有基线稳定映射到 GitHub Actions。根据 `pre_design.md` 的硬约束，落地方案必须保持“单 workflow、多 job”的结构，保留“静态/结构 -> 测试 -> 可运行性确认”的三层阻断语义，并且只覆盖最小代码侧 CI，不扩展到文档一致性、部署、发布、缓存、矩阵或其他增强型平台能力。

## Goals / Non-Goals

**Goals:**
- 新增一个 `.github/workflows/ci.yml` 作为 GitHub Actions 中的唯一最小 CI 入口。
- 让 workflow 面向 `push` 与 `pull_request` 触发，以服务主分支和 Pull Request 的默认代码准入。
- 通过多个 jobs 映射现有三层最小流水线模型，并使用 `needs` 明确阻断顺序。
- 在各 job 中继续使用 `uv` 与现有基线文档中的命令语义，避免在 workflow 内重新发明规则。
- 让 GitHub Actions 配置只承接平台映射职责，而不侵入 `docs/` 中的平台中立基线边界。

**Non-Goals:**
- 不在本次设计中引入部署、发布、回滚或任何 CD 流程。
- 不把文档一致性校验并入本次默认阻断门禁。
- 不引入缓存、矩阵、多 Python 版本、多操作系统、制品上传、镜像构建、签名、扫描或审批链。
- 不重写 `docs/cicd_baseline.md` 或 `docs/application_minimal_ci_baseline.md` 的平台中立表达。

## Decisions

### 决策一：采用单个 `.github/workflows/ci.yml` 作为唯一入口
- 选择：使用一个 workflow 文件承接本次 GitHub Actions 落地。
- 原因：这与 `pre_design.md` 中“单 workflow、多 job”的既定方向一致，也能让主分支与 Pull Request 的默认代码准入入口保持简单、稳定、可预测。
- 备选方案：拆分为多个 workflow。该方案会增加触发关系与协作心智复杂度，不符合“最小可用 CI”的边界，因此不采用。

### 决策二：用三个 jobs 映射三层最小流水线模型
- 选择：按 `static-and-structure`、`test-suite`、`runtime-validation` 三个 job 进行职责拆分。
- 原因：这种划分直接对应 `docs/application_minimal_ci_baseline.md` 中的三层模型，便于在 GitHub Actions 中清晰表达阶段职责与默认阻断关系。
- 备选方案：使用单 job 串行执行全部命令。该方案虽然更短，但会弱化阶段边界与阻断语义表达，因此不采用。

### 决策三：通过 `needs` 保持串行阻断语义
- 选择：`test-suite` 依赖 `static-and-structure`，`runtime-validation` 依赖 `test-suite`。
- 原因：这样可以确保前一层失败时后一层不会继续执行，保持平台中立三层模型在 GitHub Actions 中的等价语义。
- 备选方案：让 jobs 并行执行并依赖最终聚合结果。该方案不利于表达阶段顺序，也会削弱“前层失败不继续后层”的要求，因此不采用。

### 决策四：各 job 复用现有命令入口与 `uv` 执行基线
- 选择：workflow 中统一准备 Python 3.13 与 `uv`，然后在各 job 内执行与现有文档一致的命令入口，例如 `uv run ruff check app tests`、`uv run python -m unittest discover -s tests/architecture`、`uv run python -m unittest discover -s tests/unit` 与 `uv run python -m unittest discover -s tests/integration`。
- 原因：本次 change 的目标是平台映射，而不是重写规则；继续复用已有命令语义可以避免平台配置与文档基线出现双轨定义。
- 备选方案：在 workflow 中按文件变化、脚本拼装或平台表达式重新组织检查逻辑。该方案会把规则漂移到平台层，不符合本次边界，因此不采用。

### 决策五：最小环境准备只包含 GitHub Actions 常规依赖
- 选择：每个 job 使用 `actions/checkout`、安装 Python 3.13、安装 `uv`、执行 `uv sync --group dev --group test` 或等价最小依赖准备，再运行对应命令。
- 原因：这些是让 workflow 可执行的常规平台细节，属于 `pre_design.md` 明确允许补全的范围。
- 备选方案：引入缓存、矩阵、复合 action 或共享脚本。它们都属于未来增强项，不是本次最小实现所必需，因此不采用。

## Risks / Trade-offs

- [风险：现有命令入口与仓库真实测试资产不完全一致] → 通过在实现阶段优先校准 `docs/application_minimal_ci_baseline.md` 中的命令与当前 `tests/` 目录实际内容，确保 workflow 只调用已存在且可稳定执行的命令。
- [风险：job 拆分后 `needs` 配置错误导致三层语义失真] → 在设计中固定三段式依赖链，并在实现完成后通过一次完整本地执行或等价校验确认阶段顺序与失败阻断表现正确。
- [权衡：不引入缓存会让执行时间更长] → 这是为了保持当前方案最小、稳定、易理解；缓存优化保留给后续独立 change，而不是在本次预支复杂度。
- [权衡：不纳入文档一致性与安全增强项会让 GitHub Actions 落地范围小于主基线全部门禁] → 这是由 `pre_design.md` 明确限定的范围收敛，当前目标是先落地最小代码侧 CI，而不是一次性覆盖所有治理要求。

## Migration Plan

1. 在仓库新增 `.github/workflows/ci.yml`，作为 GitHub Actions 的唯一最小 CI 入口。
2. 在 workflow 中配置 `push` 与 `pull_request` 触发，并定义三个串行 jobs。
3. 为每个 job 补齐最小环境准备：检出代码、安装 Python 3.13、安装 `uv`、同步运行测试所需依赖。
4. 将静态/结构检查、默认测试集合与最小运行性确认命令分别映射到对应 job。
5. 在本地或等价环境验证命令可执行、失败可阻断、三层顺序正确。
6. 若 workflow 无法稳定执行，回滚方式为移除新增的 `.github/workflows/ci.yml`，因为本次 change 不涉及共享数据迁移或运行时状态变更。

## Open Questions

- `uv` 在 GitHub Actions 中采用何种安装方式最贴近当前仓库约束，需要在实现时基于可用 action 或官方安装方式做最小选择。
- `docs/application_minimal_ci_baseline.md` 中默认测试集合是否需要在实现时做轻微校准，以完全反映当前 `tests/unit/`、`tests/architecture/` 与 `tests/integration/` 的真实入口。
- 是否需要补充一小段说明文档，帮助维护者理解 GitHub Actions workflow 与平台中立基线之间的职责关系；若补充，也必须保持为最小说明而非新增治理基线。
