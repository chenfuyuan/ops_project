---
title: Phase 6.5 — 模板市场
version: 1.0
date: 2026-04-20
parent: Phase 6 — SaaS 化
---

# 模板市场

## 概述

用户可以将自己创建的主题代理、风格指纹、大纲模板等资源发布到公共市场，其他用户可以浏览、下载、评分和评论。形成社区驱动的资源生态。

---

## 1. 数据模型

### 1.1 市场物品表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| type | TEXT NOT NULL | 资源类型 |
| name | TEXT NOT NULL | 名称 |
| description | TEXT | 描述 |
| author_id | TEXT FK | 作者 ID |
| content | JSONB NOT NULL | 资源内容（结构化 JSON） |
| version | TEXT | 版本号（默认 1.0.0） |
| tags | TEXT[] | 标签数组 |
| downloads | INTEGER | 下载次数（默认 0） |
| rating_sum | INTEGER | 评分总和（默认 0） |
| rating_count | INTEGER | 评分次数（默认 0） |
| is_public | BOOLEAN | 发布状态（默认 FALSE） |
| is_approved | BOOLEAN | 审核状态（默认 FALSE） |
| moderation_note | TEXT | 审核备注 |
| created_at / updated_at | TIMESTAMP | 时间戳 |

索引：type、author_id、(is_public, is_approved)、downloads DESC、tags（GIN 索引）。

### 评分表

| 字段 | 说明 |
|------|------|
| item_id + user_id | 联合主键 |
| score | 1-5 分 |
| created_at | 评分时间 |

### 评论表

| 字段 | 说明 |
|------|------|
| id | 主键 |
| item_id | 关联物品（级联删除） |
| user_id | 评论者 |
| content | 评论内容 |
| parent_id | 回复某条评论（可选） |
| created_at | 创建时间 |

### 下载记录表

| 字段 | 说明 |
|------|------|
| id | 主键 |
| item_id | 关联物品（级联删除） |
| user_id | 下载者 |
| created_at | 下载时间 |

唯一约束：(item_id, user_id)，每人每资源只记录一次下载。

### 1.2 资源类型

| type 值 | 说明 | content 结构 |
|---------|------|-------------|
| theme_agent | 主题代理配置 | name, description, system_prompt, check_dimensions, examples |
| style_fingerprint | 风格指纹 | metrics, vocabulary_profile, sentence_patterns, reference_samples |
| outline_template | 大纲模板 | genre, structure, premise_template, act_structure, chapter_count_range |
| character_template | 角色模板 | archetype, traits, background_template, arc_type |
| prompt_template | 提示词模板 | task_type, system_prompt, user_prompt_template, variables |

### 1.3 资源实体

MarketplaceItem 实体包含上述所有字段，以及派生属性 average_rating（rating_sum / rating_count，无评分时为 0）。

---

## 2. 发布流程

### 2.1 流程图

```
用户创建资源 → 本地使用/测试 → 提交发布 → [审核队列] → 审核通过 → 公开可见
                                              ↓
                                         审核拒绝 → 通知用户修改
```

### 2.2 发布服务

PublishService 负责资源发布管理：

publish 流程：
1. 检查套餐权限（需要 Pro 或以上）
2. 验证资源类型合法性
3. 验证 content 结构完整性（每种类型有必填字段）
4. 创建记录（is_public=True, is_approved=False，需要审核）

update 流程：
1. 验证资源归属权
2. 更新允许修改的字段（不允许修改 id、author_id、downloads、rating 等）
3. 内容变更需要重新审核（is_approved 重置为 False）

unpublish：下架资源（is_public=False）。

content 必填字段验证：

| 资源类型 | 必填字段 |
|---------|---------|
| theme_agent | name, system_prompt |
| style_fingerprint | metrics |
| outline_template | genre, structure |
| character_template | archetype |
| prompt_template | task_type, system_prompt |

---

## 3. 浏览与搜索

### 3.1 市场 API

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/marketplace` | 浏览市场资源 |
| `GET` | `/api/marketplace/{item_id}` | 获取资源详情（含完整 content 和评论） |

浏览接口支持查询参数：type（按类型过滤）、tag（按标签过滤）、search（搜索关键词）、sort（排序：downloads / rating / newest，默认 downloads）、page、page_size。仅返回 is_public=True 且 is_approved=True 的资源。

列表响应每项包含：id、type、name、description、author_name、author_avatar、version、tags、downloads、average_rating、rating_count、created_at。

详情响应额外包含完整 content 和 comments 列表。

---

## 4. 下载与导入

`POST /api/marketplace/{item_id}/download`

下载/导入资源到用户的项目中。下载记录去重（每人每资源只计一次），首次下载时递增 downloads 计数。返回资源 type 和 content。

导入后的资源存储位置：

| 资源类型 | 导入目标 |
|---------|---------|
| theme_agent | 用户的主题代理列表 |
| style_fingerprint | 用户的风格指纹库 |
| outline_template | 创建小说时的模板选项 |
| character_template | 角色创建时的模板选项 |
| prompt_template | 用户的自定义提示词库 |

---

## 5. 评分与评论

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/marketplace/{item_id}/rate` | 评分（1-5 分，每人只能评一次，可修改） |
| `GET` | `/api/marketplace/{item_id}/comments` | 获取资源评论（分页） |
| `POST` | `/api/marketplace/{item_id}/comments` | 发表评论（支持回复） |

评分规则：分数范围 1-5，不能给自己的资源评分。已评分时更新评分（调整 rating_sum 差值），未评分时新增（rating_count + 1）。

评论支持 parent_id 实现回复功能。

---

## 6. 内容审核

### 6.1 审核策略

本阶段采用简单的人工审核 + 基础自动检查。

ModerationService 自动检查流程：
1. 关键词过滤（违规关键词正则匹配，自动拒绝）
2. 内容长度检查（content 序列化后不超过 500KB）
3. 结构完整性检查（名称不少于 2 字符）

自动检查通过后进入人工审核队列。小规模阶段可配置为自动通过。

### 6.2 管理员审核 API

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/admin/marketplace/pending` | 查看待审核资源 |
| `POST` | `/api/admin/marketplace/{item_id}/approve` | 通过审核 |
| `POST` | `/api/admin/marketplace/{item_id}/reject` | 拒绝审核（需提供原因） |

---

## 7. 用户的"我的发布"

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/marketplace/my/items` | 查看我发布的资源（含未审核/已下架） |
| `GET` | `/api/marketplace/my/downloads` | 查看我下载过的资源 |
