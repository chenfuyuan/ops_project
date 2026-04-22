# 用量与配额

## Goal

为多用户服务建立可理解的用量边界和资源分配规则，支持平台管理不同用户对创作能力的使用。

## User Value

用户能够知道自己可以使用多少资源，平台也能基于清晰边界控制成本和服务体验。

## Success Criteria

- 用量记录和配额边界被定义为独立需求。
- 该需求与账户能力和平台基础之间的关系清晰。
- 卡片不提前展开计费模型、支付网关或数据库实现。

## Scope

- 用量统计与额度限制的产品需求
- 平台对模型和创作资源的分配边界
- 与账户和模板市场之间的协同关系

## Non-goals

- 支付集成
- 详细计费规则
- 财务对账流程

## Dependencies / Prerequisites

- [account-access](account-access.md)

## Notes

- 这张卡片聚焦“边界管理”，不是商业化方案总纲。
- 历史参考：[`phase6-saas/03-billing-quota.md`](../../../../archive/project_plan-pre-phase-first/phase6-saas/03-billing-quota.md)
