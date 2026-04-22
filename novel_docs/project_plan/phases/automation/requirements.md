# Automation Requirements Index

本页只维护自动化阶段的需求索引、状态和依赖，详细边界在卡片中表达。

| Requirement | Summary | Status | Priority | Dependencies | Card |
| --- | --- | --- | --- | --- | --- |
| Autopilot execution | 让系统能按既定规则自动推进创作流程 | 待前置完成 | P0 | Phase 2, 3, 4 | [autopilot-execution](requirements/autopilot-execution.md) |
| Failure guardrails | 在自动推进时提供熔断和恢复边界 | 待前置完成 | P0 | autopilot-execution | [failure-guardrails](requirements/failure-guardrails.md) |
| Realtime notifications | 在关键事件上及时反馈自动化状态 | 待前置完成 | P1 | autopilot-execution | [realtime-notifications](requirements/realtime-notifications.md) |
| Automation console | 提供启动、暂停、观察和批量操作入口 | 待前置完成 | P1 | autopilot-execution, failure-guardrails, realtime-notifications | [automation-console](requirements/automation-console.md) |
