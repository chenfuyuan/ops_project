## MODIFIED Requirements

### Requirement: GitHub Actions 平台映射不得扩展到本次 change 之外的增强能力
系统 MUST 将 GitHub Actions 最小平台映射范围限制在最小代码侧 CI 所需的常规实现细节内，例如代码检出、Python 环境准备、`uv` 安装与最小依赖同步。系统 MUST 将缓存、并发治理、路径感知、质量预检、失败诊断增强等能力视为独立的增强型 capability，而不是直接并入最小平台映射本身。系统 MUST NOT 在最小 capability 中加入文档一致性门禁、矩阵、多 Python 版本、多操作系统、镜像构建、制品上传、签名、扫描、审批链或其他超出最小 CI 与增强型 CI 既定边界的能力。

#### Scenario: 最小 GitHub Actions CI 保持边界且可被增强型 capability 叠加
- **WHEN** 团队同时查阅最小 GitHub Actions CI 与增强型 GitHub Actions CI 的规格
- **THEN** 可以明确区分哪些能力属于最小平台映射，哪些能力属于增强型 capability
- **AND** 最小 capability 仍保持其作为基础入口与保留边界的定位

#### Scenario: 最小 capability 不会吞并增强型工程化能力
- **WHEN** 后续文档或实现尝试将质量预检、缓存、并发治理或失败归档直接写入最小 GitHub Actions capability
- **THEN** 规格能够明确判定这些能力应由增强型 capability 承接
- **AND** 最小 capability 不会因此失去“最小、稳定、平台映射”的定位
