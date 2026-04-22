# 审计修订闭环

## Goal

让审计发现的问题能够进入清晰的修订闭环，使章节从“发现问题”走向“被处理或被人工接管”。

## User Value

作者不需要手工在多个步骤之间搬运问题，系统可以把“发现问题”和“处理问题”连接起来。

## Success Criteria

- 审计结果有明确去向，而不是停留在只读报告状态。
- 用户能够区分哪些问题可以继续自动处理，哪些需要人工接管。
- 卡片保持在流程需求层，不提前定义修订算法或状态机。

## Scope

- 审计后进入修订的产品流程
- 自动处理与人工接管的边界
- 问题处理结果的反馈需求

## Non-goals

- 文本重写策略
- 重试次数规则细节
- 自动驾驶阶段编排

## Dependencies / Prerequisites

- [consistency-auditing](consistency-auditing.md)

## Notes

- 未来 change 可以单独定义“审计到修订”的闭环规则。
- 历史参考：[`phase2-consistency/02-reviser.md`](../../../../archive/project_plan-pre-phase-first/phase2-consistency/02-reviser.md)
