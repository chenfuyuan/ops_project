# 质量治理流程接入

## Goal

把审计、修订和状态治理能力接入章节产出后的稳定流程，让质量保障成为主线工作流的一部分。

## User Value

团队不需要临时决定每章写完之后要执行哪些补救动作，质量治理会成为默认流程的一环。

## Success Criteria

- 质量治理需求与主创作流程的衔接关系清晰。
- 用户能够理解章节完成后会发生哪些质量相关动作。
- 卡片不提前定义完整流水线实现或前端交互细节。

## Scope

- 章节产出后的质量处理链路需求
- 审计结果、修订动作和状态回写之间的关系
- 对工作流可追踪性的基本要求

## Non-goals

- 守护进程设计
- 自动审批规则全集
- 前端页面细节

## Dependencies / Prerequisites

- [revision-loop](revision-loop.md)
- [fact-lock-governance](fact-lock-governance.md)

## Notes

- 未来 change 可围绕“章节后质量治理流程”独立展开。
- 历史参考：[`phase2-consistency/05-pipeline-upgrade.md`](../../../../archive/project_plan-pre-phase-first/phase2-consistency/05-pipeline-upgrade.md)
