# 章节生成流水线

## Goal

支持基于蓝图逐章产出内容，并保留人工审核、继续生成和恢复写作节奏的能力。

## User Value

作者可以把蓝图转化为实际章节内容，同时保持对写作过程的控制感，而不是被黑盒式生成流程绑住。

## Success Criteria

- 章节生成需求覆盖“开始生成、查看结果、决定是否继续”的最小闭环。
- 该需求和大纲、蓝图、记忆等前置能力之间的关系清晰。
- 卡片不提前定义内部流水线步骤，只表达使用结果和边界。

## Scope

- 逐章生成的主要用户流程
- 人工主导下的生成、查看和继续写作要求
- 与蓝图和上下文输入的协作边界

## Non-goals

- 修订循环
- 自动驾驶编排
- 审计策略细节

## Dependencies / Prerequisites

- [chapter-blueprints](chapter-blueprints.md)
- [llm-routing](llm-routing.md)

## Notes

- 这是 MVP 闭环中最核心的 change 候选之一。
- 历史参考：[`phase1-mvp/05-chapter-pipeline.md`](../../../../archive/project_plan-pre-phase-first/phase1-mvp/05-chapter-pipeline.md)
