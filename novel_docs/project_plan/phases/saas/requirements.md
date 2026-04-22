# SaaS Requirements Index

本页只维护 SaaS 阶段的需求索引、状态和依赖，详细边界请查看单需求卡片。

| Requirement | Summary | Status | Priority | Dependencies | Card |
| --- | --- | --- | --- | --- | --- |
| Platform foundation | 建立多用户服务所需的平台基础能力 | 待前置完成 | P0 | Phase 5 | [platform-foundation](requirements/platform-foundation.md) |
| Account access | 支持用户注册、登录和身份边界 | 待前置完成 | P0 | platform-foundation | [account-access](requirements/account-access.md) |
| Usage quotas | 管理用量、额度和模型访问策略 | 待前置完成 | P1 | account-access | [usage-quotas](requirements/usage-quotas.md) |
| Collaboration | 让多位参与者围绕同一小说协作 | 待前置完成 | P1 | account-access | [collaboration](requirements/collaboration.md) |
| Template marketplace | 支持模板分发、发现和复用场景 | 待前置完成 | P2 | account-access, usage-quotas | [template-marketplace](requirements/template-marketplace.md) |
