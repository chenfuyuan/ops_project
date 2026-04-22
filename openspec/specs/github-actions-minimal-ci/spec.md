## github-actions-minimal-ci

### Purpose
为应用代码最小 CI 提供 GitHub Actions 平台映射入口，保持与平台中立基线一致的最小职责边界。

### Requirement: GitHub Actions 必须提供最小代码侧 CI workflow 入口
系统 MUST 在仓库中提供一个 GitHub Actions workflow 文件，作为最小代码侧 CI 的唯一平台入口。该 workflow MUST 面向 `push` 与 `pull_request` 触发，并用于主分支与 Pull Request 的默认代码准入。该入口 MUST 只承接最小代码侧 CI，不得扩展为部署、发布、回滚或其他 CD 流程。

#### Scenario: 代码变更触发最小 CI workflow
- **WHEN** 开发者向主分支推送代码，或对仓库发起 Pull Request
- **THEN** GitHub Actions 会自动触发唯一的最小代码侧 CI workflow
- **AND** 该 workflow 的职责仅限于代码准入校验，而不包含部署或发布动作

### Requirement: GitHub Actions workflow 必须以多 job 映射三层最小流水线模型
系统 MUST 在单个 GitHub Actions workflow 中使用多个 jobs 映射现有应用代码最小 CI 的三层模型：静态与结构校验层、测试校验层、可运行性与构建确认层。各 job MUST 按职责拆分，并通过显式依赖保持“前层失败不继续后层”的阻断顺序。系统 MUST NOT 退化为单 job 串行脚本，也 MUST NOT 拆分为多个 workflow 共同承载本次最小 CI。

#### Scenario: 三层模型被映射为单 workflow 多 job
- **WHEN** 团队查阅 GitHub Actions 的最小 CI 配置
- **THEN** 可以看到单个 workflow 内至少存在静态/结构、测试、可运行性确认三个职责明确的 jobs
- **AND** 后一层 job 依赖前一层 job 成功完成后才会执行

#### Scenario: 前层失败会阻断后层执行
- **WHEN** 静态与结构校验层或测试校验层中的任一阻断检查失败
- **THEN** 后续依赖该层的 job 不会继续执行
- **AND** 整个 workflow 会以失败状态结束

### Requirement: GitHub Actions jobs 必须复用现有最小 CI 命令语义与 uv 基线
系统 MUST 在 GitHub Actions workflow 中继续使用 `uv` 作为依赖与命令执行基线，并复用现有应用代码最小 CI 基线中的命令语义。各 job MUST 以仓库已存在的 `app/`、`tests/unit/`、`tests/architecture/`、`tests/integration/` 等资产为执行对象，而不是在 workflow 中重新定义一套脱离基线文档的新规则。

#### Scenario: workflow 复用现有命令语义
- **WHEN** 维护者查看 GitHub Actions job 中执行的命令
- **THEN** 可以看到这些命令与现有最小 CI 基线中的 `uv` 命令语义一致
- **AND** 不会看到平台配置自行定义的另一套检查边界

#### Scenario: workflow 以仓库真实测试资产为执行对象
- **WHEN** GitHub Actions 运行最小 CI jobs
- **THEN** 各 job 调用的检查与测试入口对应仓库当前真实存在的代码和测试目录
- **AND** 不会依赖仓库中并不存在的脚本、制品或平台资产

### Requirement: GitHub Actions 平台映射不得扩展到本次 change 之外的增强能力
系统 MUST 将 GitHub Actions 落地范围限制在最小代码侧 CI 所需的常规实现细节内，例如代码检出、Python 环境准备、`uv` 安装与最小依赖同步。系统 MUST NOT 在本次 capability 中加入文档一致性门禁、缓存、矩阵、多 Python 版本、多操作系统、镜像构建、制品上传、签名、扫描、审批链或其他增强型平台能力。

#### Scenario: workflow 保持最小实现边界
- **WHEN** 团队审查本次 GitHub Actions 最小 CI 方案
- **THEN** 只能看到让现有三层最小 CI 可执行所必需的常规平台准备与 job 编排
- **AND** 不会把增强型平台能力写成当前 change 的既定目标或已落地事实
