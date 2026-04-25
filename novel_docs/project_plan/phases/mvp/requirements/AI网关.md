# AI 网关

## Goal

让系统通过统一 AI 网关承接创作任务的模型访问，为大纲、蓝图和章节生成提供一致的能力入口，并支持调用方按中性能力诉求选择合适的模型来源。

## User Value

创作流程不需要被单一模型绑定，团队可以通过统一网关按能力、成本、上下文长度等中性维度选择更合适的模型来源，同时降低后续接入和切换成本。

## Success Criteria

- MVP 范围内的创作任务都可以通过统一 AI 网关请求模型能力。
- 需求边界明确支持调用方按中性能力诉求选择模型来源，任务语义到模型诉求的映射不进入 AI 网关内部。
- 后续需求能够把 AI 能力访问视为共享前置能力，而不是各自重复定义。

## Scope

- AI 网关作为统一模型访问入口的产品要求
- 多模型来源接入与按能力、成本、上下文等中性维度选型的需求表达
- 模型凭据、配置与切换的规划边界

## Non-goals

- 供应商 SDK 选型
- Prompt 模板细节
- 限流、缓存或熔断策略设计

## Dependencies / Prerequisites

- [project-scaffold](项目脚手架与基础设施.md)

## Notes

- 未来 change 需要决定 AI 网关的接入方式与配置治理实现。
- 历史参考：[`phase1-mvp/02-ai-gateway.md`](../../../../archive/project_plan-pre-phase-first/phase1-mvp/02-ai-gateway.md)
