# 自动推进执行

## Goal

让系统能够在既定边界内自动推进从规划到写作的关键流程，减少人工逐步触发的操作负担。

## User Value

作者可以把更多精力放在策略判断和关键节点审核上，而不是重复执行机械流程。

## Success Criteria

- 自动推进被定义为独立需求，而不是零散附着在多个功能之上。
- 用户可以理解系统何时自动继续、何时需要停下等待。
- 卡片不提前展开状态机、守护进程或数据库细节。

## Scope

- 自动推进主流程的产品目标
- 自动执行中的暂停、继续和完成边界
- 与通知、熔断和控制入口的关系

## Non-goals

- 具体状态图设计
- 后台任务调度实现
- 多租户运行策略

## Dependencies / Prerequisites

- Phase 2, Phase 3, Phase 4 的基础能力方向已清晰

## Notes

- 这是 Phase 5 的主轴卡片。
- 历史参考：[`phase5-automation/01-autopilot.md`](../../../../archive/project_plan-pre-phase-first/phase5-automation/01-autopilot.md)
