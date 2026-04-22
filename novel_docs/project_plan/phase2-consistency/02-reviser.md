---
title: Phase 2 — 审计-修订循环
version: 1.0
date: 2026-04-20
---

# 审计-修订循环（Reviser Agent）

## 概述

当 Auditor 发现 critical 问题时，Reviser 自动修订章节内容。修订后重新审计，循环直到 critical 问题清零或达到最大轮次。

## 循环流程

```
Draft → Audit
         │
         ├─ 无 critical → 直接进入 Commit
         │
         └─ 有 critical → Revise → Re-audit
                           │
                           ├─ 无 critical → Commit
                           │
                           └─ 有 critical → Revise → Re-audit (第2轮)
                                              │
                                              ├─ 无 critical → Commit
                                              │
                                              └─ 有 critical → Revise → Re-audit (第3轮)
                                                                │
                                                                └─ 仍有 critical → 暂停，通知人工
```

最大循环轮次：3 轮。

## Reviser Agent 设计

**输入：**
- 当前章节草稿
- critical 问题清单（含位置和修复建议）
- 相关的状态数据（角色状态、事实锁等，与问题相关的部分）

**LLM 调用设计：**

系统角色为小说修订专家，执行最小化修改。输入包括待修订章节、需修复的 critical 问题清单（含位置和建议）、以及与问题相关的参考状态数据。LLM 只修改有问题的段落，保持其余内容不变，输出修订后的完整章节文本。

## 修订策略

### 最小化修改原则

Reviser 的核心原则是最小化修改：
- 只改有问题的段落，不动其他内容
- 优先通过措辞调整解决，而非重写段落
- 如果问题涉及情节逻辑，可以添加过渡句而非删除内容

### 修订记录

每轮修订记录到 `pipeline_artifacts`，包含：
- stage: "revise"
- round: 轮次编号
- 输入：待修复的问题清单、原始内容哈希
- 输出：修订后内容哈希、变更摘要列表（描述每处修改）

### 人工介入

3 轮后仍有 critical 问题时：
1. 章节状态标记为 `needs_review`
2. 前端显示审计问题列表，高亮未解决的 critical 问题
3. 用户可以：
   - 手动编辑章节修复问题
   - 标记某个问题为"忽略"（如果认为审计误判）
   - 触发重新审计
4. 所有 critical 问题解决或忽略后，手动推进到 Commit

### Warning 问题处理

Warning 级别的问题不触发自动修订：
- 存入 `audit_issues` 表，`resolved=0`
- 前端在写作工作台的右栏显示
- 用户可以选择修复或忽略
- 不阻塞 Commit 阶段

## 流水线编排器升级

Audit-Revise 循环集成到流水线中，在 Plan → Compose → Draft 之后执行：

1. 对 draft 执行审计，保存审计结果到 pipeline_artifacts 和 audit_issues 表
2. 如果无 critical 问题，直接进入 Commit
3. 如果有 critical 问题，执行修订，保存修订记录，用修订后的 draft 重新审计
4. 重复步骤 1-3，最多 3 轮
5. 3 轮后仍有 critical 问题，暂停流水线，通知人工介入（不进入 Commit）
6. 通过审计后，用最终 draft 进入 Commit
