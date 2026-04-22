---
title: Phase 2 — 流水线升级与前端变更
version: 1.0
date: 2026-04-20
---

# 流水线升级与前端变更

## 流水线变更

Phase 1 的 4 阶段升级为 6 阶段：

```
Phase 1: Plan → Compose → Draft → Commit
Phase 2: Plan → Compose → Draft → Audit → Revise(循环) → Commit
```

### 编排器变更

流水线编排器升级为支持 Audit-Revise 循环，最大审计轮次为 3 轮：

1. 执行 Plan → Compose → Draft（同 Phase 1）
2. 对 draft 执行审计，保存审计结果，持久化审计问题
3. 通过 SSE 推送审计结果（critical / warning / info 计数）
4. 如果无 critical 问题，推送 audit_passed 事件，进入 Commit
5. 如果有 critical 问题，推送 revise_start 事件，执行修订
6. 保存修订记录（原始哈希 + 修订哈希），用修订后的 draft 回到步骤 2
7. 3 轮后仍有 critical 问题，推送 audit_failed 事件（含 remaining_critical 和 needs_human_review），标记章节需人工审核

### 断点续跑扩展

Phase 2 的 `resume_from` 参数支持新的阶段值：
- `"audit"` — 从审计阶段重跑（使用已有的 draft）
- `"revise"` — 从修订阶段重跑（使用已有的 draft + audit 结果）

### 中间产物扩展

`pipeline_artifacts` 表新增记录类型：

| stage | 内容 |
|-------|------|
| `audit_round_1` | 第 1 轮审计结果（问题清单） |
| `revise_round_1` | 第 1 轮修订记录（变更摘要） |
| `audit_round_2` | 第 2 轮审计结果 |
| `revise_round_2` | 第 2 轮修订记录 |
| `audit_round_3` | 第 3 轮审计结果 |
| `revise_round_3` | 第 3 轮修订记录 |

### SSE 事件扩展

新增事件类型：

| 事件 | 数据字段 | 说明 |
|------|---------|------|
| audit_start | round | 审计开始 |
| audit_complete | round, critical, warning, info | 审计完成，含各严重度计数 |
| revise_start | round, issues_to_fix | 修订开始，含待修复问题数 |
| revise_complete | round | 修订完成 |
| audit_passed | total_rounds | 审计通过，含总轮次 |
| audit_failed | rounds_exhausted, remaining_critical, needs_human_review | 审计失败，需人工介入 |

## 新增 API 端点

**审计相关：**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/novels/{id}/chapters/{num}/audit | 获取审计结果 |
| POST | /api/v1/novels/{id}/chapters/{num}/audit/rerun | 重新审计 |
| PUT | /api/v1/novels/{id}/audit-issues/{issue_id} | 更新审计问题状态（忽略/确认） |

**事实锁：**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/novels/{id}/fact-locks | 获取事实锁列表 |
| POST | /api/v1/novels/{id}/fact-locks | 手动创建事实锁 |
| PUT | /api/v1/novels/{id}/fact-locks/{id} | 编辑事实锁 |
| PUT | /api/v1/novels/{id}/fact-locks/{id}/confirm | 确认待确认的事实锁 |
| DELETE | /api/v1/novels/{id}/fact-locks/{id} | 删除事实锁 |

## 前端变更汇总

### 写作工作台变更

**流水线进度指示器升级：**
- 原来：Plan → Compose → Draft → Commit（4 步）
- 现在：Plan → Compose → Draft → Audit → (Revise ↔ Audit) → Commit（6 步 + 循环）
- 审计循环用动画表示当前轮次
- 审计通过显示绿色勾，失败显示红色叉

**审计结果面板（写作工作台右栏新增 Tab）：**
- 按严重度分组：Critical（红色）/ Warning（橙色）/ Info（灰色）
- 每个问题显示：维度图标、描述、位置、建议
- Critical 问题：显示自动修订状态（已修复/修订中/修订失败）
- Warning 问题：显示"忽略"按钮
- 点击问题 → 编辑器跳转到对应位置并高亮

**人工审核模式：**
- 当审计失败（3 轮后仍有 critical）时，进入人工审核模式
- 编辑器左侧显示问题列表，右侧显示章节内容
- 用户可以直接编辑章节修复问题
- 每个问题有"标记为已修复"和"忽略"按钮
- 全部处理完后，点击"继续"推进到 Commit

### 新增页面

**事实锁管理页 `/novels/:id/fact-locks`：**

布局：分组列表

分组：
- FACT_LOCK（不可逆事实）— 红色标签
- COMPLETED_BEATS（已完成节拍）— 蓝色标签
- REVEALED_CLUES（已揭示线索）— 紫色标签
- 待确认 — 黄色标签，闪烁提示

每条显示：
- 内容
- 类型标签
- 来源章节
- 创建方式（自动提取 / 手动添加）
- 操作：编辑 / 删除 / 确认（待确认项）

顶部操作：
- "手动添加事实锁"按钮
- 按类型过滤

### 伏笔台账页增强

- 新增伏笔时间线可视化（见 04-foreshadowing-lifecycle.md）
- 停滞预警高亮
- 新增 deferred 状态的管理操作

### 项目仪表盘增强

新增统计卡片：
- 审计通过率（最近 20 章）
- 平均修订轮次
- 活跃事实锁数量（分类型）
- 停滞伏笔数量（warning + critical）
