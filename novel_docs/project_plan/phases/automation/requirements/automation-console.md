# 自动化控制台

## Goal

提供启动、暂停、观察和批量操作自动化流程的统一入口，让用户能够管理自动推进而不是被动接受结果。

## User Value

作者可以在一个控制面上理解自动化状态、手动干预节点和后续行动，而不需要在多个零散入口间跳转。

## Success Criteria

- 自动化关键能力都有统一的操作入口需求。
- 控制台与自动推进、失败保护和通知之间的依赖关系清晰。
- 卡片不提前定义页面布局、组件树或接口细节。

## Scope

- 自动化启动、暂停、恢复和批量操作入口
- 自动化状态查看与人工干预需求
- 与通知、风险保护能力的协同边界

## Non-goals

- 视觉方案
- 权限模型
- 后台任务调度实现

## Dependencies / Prerequisites

- [autopilot-execution](autopilot-execution.md)
- [failure-guardrails](failure-guardrails.md)
- [realtime-notifications](realtime-notifications.md)

## Notes

- 未来 change 可以围绕“自动化控制台”单独推进。
- 历史参考：[`phase5-automation/04-api-frontend.md`](../../../../archive/project_plan-pre-phase-first/phase5-automation/04-api-frontend.md)
