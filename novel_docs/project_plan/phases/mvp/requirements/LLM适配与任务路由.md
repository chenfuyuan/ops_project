# LLM 适配与任务路由

## Goal

让系统能按创作任务接入并切换不同模型来源，为大纲、蓝图和章节生成提供一致的模型访问能力。

## User Value

创作流程不需要被单一模型绑定，团队可以根据任务差异选择更合适的模型能力和成本组合。

## Success Criteria

- MVP 范围内的创作任务都可以通过统一入口请求模型能力。
- 需求边界明确包含“按任务选择模型”，但不强迫绑定具体实现方式。
- 后续需求能够把模型访问视为共享前置能力，而不是各自重复定义。

## Scope

- 多模型来源接入的产品要求
- 不同创作任务使用不同模型能力的需求表达
- 模型凭据、配置与切换的规划边界

## Non-goals

- 供应商 SDK 选型
- Prompt 模板细节
- 限流、缓存或熔断策略设计

## Dependencies / Prerequisites

- [project-scaffold](项目脚手架与基础设施.md)

## Notes

- 未来 change 需要决定模型接入与配置治理的具体实现。
- 历史参考：[`phase1-mvp/02-llm-adapter.md`](../../../../archive/project_plan-pre-phase-first/phase1-mvp/02-llm-adapter.md)
