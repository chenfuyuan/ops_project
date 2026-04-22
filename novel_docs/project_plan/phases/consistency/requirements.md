# Consistency Requirements Index

本页只维护 Phase 2 的需求索引和关系图，不替代具体 requirement card。

| Requirement | Summary | Status | Priority | Dependencies | Card |
| --- | --- | --- | --- | --- | --- |
| Consistency auditing | 识别章节与已有状态之间的关键矛盾 | 待前置完成 | P0 | Phase 1 | [consistency-auditing](requirements/consistency-auditing.md) |
| Revision loop | 对审计结果形成可持续修订闭环 | 待前置完成 | P0 | consistency-auditing | [revision-loop](requirements/revision-loop.md) |
| Fact lock governance | 为不可逆事实和状态更新建立治理规则 | 待前置完成 | P0 | consistency-auditing | [fact-lock-governance](requirements/fact-lock-governance.md) |
| Foreshadow tracking | 持续追踪伏笔的推进与回收情况 | 待前置完成 | P1 | fact-lock-governance | [foreshadow-tracking](requirements/foreshadow-tracking.md) |
| Quality pipeline ops | 把一致性检查接入章节产出后的稳定流程 | 待前置完成 | P1 | revision-loop, fact-lock-governance | [quality-pipeline-ops](requirements/quality-pipeline-ops.md) |
