# 一致性审计

## Goal

在章节产出后识别与既有状态相冲突的关键问题，尽早暴露会破坏长篇可信度的矛盾。

## User Value

作者不用靠手工回忆所有前文细节，就能及时发现角色、时间线、物品和事实层面的风险。

## Success Criteria

- 系统具备针对章节一致性问题的独立审查需求边界。
- 审计结果能够支撑后续人工处理或自动修订决策。
- 该卡片本身足以作为未来单个 change 的上游输入。

## Scope

- 章节完成后的质量检查需求
- 对关键一致性风险的发现和呈现
- 审计结果与后续处理环节的衔接关系

## Non-goals

- 具体审计维度实现
- 修订策略细节
- 张力或风格层面的判断

## Dependencies / Prerequisites

- Phase 1 MVP 闭环已明确

## Notes

- 这是 Phase 2 的核心起点之一。
- 历史参考：[`phase2-consistency/01-auditor.md`](../../../../archive/project_plan-pre-phase-first/phase2-consistency/01-auditor.md)
