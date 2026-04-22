---
title: Phase 3 — 新增 API 端点与前端变更
version: 1.0
date: 2026-04-20
---

# 新增 API 端点与前端变更

## 新增 API 端点

### 张力分析

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/novels/{id}/tension` | 获取张力曲线数据 |
| `GET` | `/api/v1/novels/{id}/tension/warnings` | 获取张力预警列表 |

张力曲线响应包含每章的张力评分（total + 5 个维度分数 + 分析文本）以及蓝图规划的参考张力值。

预警响应包含预警类型（low_tension_streak / high_tension_streak / monotone_pacing / blueprint_deviation）、严重度、涉及章节、建议。

### 主题代理

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/theme-agents` | 获取所有主题代理 |
| `GET` | `/api/v1/theme-agents/{id}` | 获取代理详情（含技能内容） |
| `PUT` | `/api/v1/theme-agents/{id}` | 编辑代理 |
| `POST` | `/api/v1/theme-agents` | 创建自定义代理 |
| `DELETE` | `/api/v1/theme-agents/{id}` | 删除自定义代理（内置不可删） |
| `GET` | `/api/v1/theme-skills` | 获取所有技能 |
| `GET` | `/api/v1/theme-skills/{id}` | 获取技能详情 |
| `PUT` | `/api/v1/theme-skills/{id}` | 编辑技能 |
| `POST` | `/api/v1/theme-skills` | 创建自定义技能 |
| `DELETE` | `/api/v1/theme-skills/{id}` | 删除自定义技能 |

### 知识图谱

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/novels/{id}/knowledge-graph` | 获取知识图谱数据（用于可视化） |
| `GET` | `/api/v1/novels/{id}/knowledge-graph/character/{char_id}/knowledge` | 角色信息边界查询 |

知识图谱端点支持查询参数：character_id（按角色过滤）、chapter_start/chapter_end（按章节范围过滤）、tags（按标签过滤）、limit（限制返回数量）。

响应包含 nodes（实体列表，含 id、type、triple_count）和 edges（关系列表，含 source、target、predicate、source_chapter）。

角色信息边界查询支持 up_to_chapter 参数，返回角色在指定章节时知道的所有事实，包含三元组、来源章节和获知方式。

### 剧情线

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/novels/{id}/storylines` | 获取剧情线列表 |
| `POST` | `/api/v1/novels/{id}/storylines` | 手动创建剧情线 |
| `PUT` | `/api/v1/novels/{id}/storylines/{sl_id}` | 编辑剧情线 |
| `DELETE` | `/api/v1/novels/{id}/storylines/{sl_id}` | 删除剧情线 |

## 前端变更

### 新增页面

**张力分析页 `/novels/:id/tension`：**
- 张力曲线图（ECharts 折线图）
- 蓝图规划参考线叠加
- 预警区域高亮
- 预警列表
- 点击数据点跳转到章节

**主题代理配置页 `/novels/:id/theme`：**
- 当前小说关联的代理信息
- 代理详情：persona、rules、world_rules、taboos
- 关联技能列表
- 节拍模板列表
- 编辑按钮（跳转到代理编辑页）

**主题代理管理页 `/settings/theme-agents`：**
- 内置代理列表（不可删除，可编辑副本）
- 自定义代理列表
- 创建新代理按钮
- 技能管理 Tab

**知识图谱页 `/novels/:id/knowledge-graph`：**
- 力导向图可视化
- 左侧过滤面板：按角色/章节/标签
- 点击节点显示详情
- 信息边界查询面板（选择角色 + 章节号）

**剧情线页 `/novels/:id/storylines`：**
- 剧情线列表（主线/支线 A/B/C）
- 每条显示：名称、状态、当前进度、最后推进章节
- 停滞预警标记
- 手动创建/编辑

### 写作工作台增强

右栏新增 Tab：
- **张力** Tab：当前章节张力雷达图 + 与前章对比
- **知识图谱** Tab：与当前章节相关的三元组子图
- **主题** Tab：当前生效的主题代理规则摘要

### 项目仪表盘增强

新增统计卡片：
- 平均张力分
- 张力预警数量
- 知识图谱三元组总数
- 活跃剧情线数量
