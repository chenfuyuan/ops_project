# 分层上下文管理

## Goal

建立适合长篇写作的分层上下文边界，让系统在不同创作任务里知道哪些信息必须长期保留、哪些可以阶段性压缩。

## User Value

作者能够在章节持续增加时仍保持关键上下文可用，不至于因为信息膨胀而让生成质量明显下滑。

## Success Criteria

- 上下文分层被表达成独立需求，而不是隐含在记忆系统内部。
- 该需求能自然连接蓝图增强和后续叙事能力。
- 卡片不提前定义层级算法、存储实现或预算策略细节。

## Scope

- 长篇创作中的上下文层次划分需求
- 不同层级信息在不同任务中的使用边界
- 与蓝图增强、知识沉淀和章节生成的关系

## Non-goals

- Token 预算算法
- 检索实现
- 数据结构设计

## Dependencies / Prerequisites

- Phase 2 质量治理基线

## Notes

- 这张卡片是叙事增强能力的关键底座。
- 历史参考：[`phase3-narrative/04-onion-model-t1.md`](../../../../archive/project_plan-pre-phase-first/phase3-narrative/04-onion-model-t1.md)
