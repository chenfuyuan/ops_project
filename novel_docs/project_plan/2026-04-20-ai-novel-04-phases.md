---
title: AI 长篇小说生成系统 — 分阶段演进路线
version: 2.0
date: 2026-04-20
parent: 2026-04-20-ai-novel-00-overview.md
---

# 分阶段演进路线

## 文档角色

本文档属于**总纲层中的阶段索引页**，用于表达 6 个 phase 的演进顺序、依赖关系和 phase overview 入口。

它的职责是：
- 提供阶段级阅读顺序
- 帮助后续 OpenSpec 先定位目标 phase
- 指向各 phase overview，而不是重复承载各阶段的完整设计细节

阅读顺序默认遵循：**总纲入口 → 本页 → 目标 phase overview → 按需专题文档**。

## 阶段总览

| Phase | 目标 | 前置依赖 | 入口 |
|------|------|----------|------|
| Phase 1 — MVP | 跑通从大纲到章节生成的最小闭环 | 无 | [phase1-mvp/00-overview.md](phase1-mvp/00-overview.md) |
| Phase 2 — 一致性 | 建立审计、修订、事实锁和状态治理能力 | Phase 1 | [phase2-consistency/00-overview.md](phase2-consistency/00-overview.md) |
| Phase 3 — 叙事 | 提升张力、类型化写作、知识图谱与完整上下文管理 | Phase 2 | [phase3-narrative/00-overview.md](phase3-narrative/00-overview.md) |
| Phase 4 — 风格 | 建立风格指纹、语音漂移检测与去 AI 化规则 | Phase 2 | [phase4-style/00-overview.md](phase4-style/00-overview.md) |
| Phase 5 — 自动化 | 从人工主导升级到自动驾驶与规模化执行 | Phase 2、3、4 | [phase5-automation/00-overview.md](phase5-automation/00-overview.md) |
| Phase 6 — SaaS | 从单用户工具升级为多用户服务 | Phase 5 | [phase6-saas/00-overview.md](phase6-saas/00-overview.md) |

## 阶段依赖关系

```text
Phase 1 (MVP)
    │
    ▼
Phase 2 (一致性) ─┬─→ Phase 3 (叙事)
                  │
                  └─→ Phase 4 (风格)
                        │
                  ┌─────┘
                  ▼
            Phase 5 (自动化)
                  │
                  ▼
            Phase 6 (SaaS)
```

- Phase 2 是 Phase 3 与 Phase 4 的共同前置依赖。
- Phase 3 与 Phase 4 可以并行推进，但都依赖一致性治理基线。
- Phase 5 以前面质量保障体系为前提，将其接入自动驾驶与规模化执行。
- Phase 6 以前述自动化与 API 完整性为基础，进入多租户和 SaaS 能力建设。

## 使用规则

- 当目标是理解项目总体演进顺序时，先阅读本页。
- 当目标是为某个 phase 继续做 OpenSpec、需求梳理或文档细化时，进入对应 `00-overview.md`。
- 当目标是补充某个具体能力细节时，再从 phase overview 按需进入专题文档。
- 本页不承载每个 phase 的完整后端、前端和数据细节；这些细节留在 phase overview 与 topic 文档中维护。
