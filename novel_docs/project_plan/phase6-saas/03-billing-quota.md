---
title: Phase 6.3 — 用量追踪与配额管理
version: 1.0
date: 2026-04-20
parent: Phase 6 — SaaS 化
---

# 用量追踪与配额管理

## 概述

追踪每次 LLM 调用的 token 消耗和成本，按套餐限制用量。支持平台托管 Key（计费）和用户自有 Key（不计费）两种模式。

---

## 1. 数据模型

### 1.1 用量记录表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | UUID v4 |
| user_id | TEXT FK | 关联用户 |
| novel_id | TEXT FK | 关联小说（可选） |
| action | TEXT NOT NULL | 操作类型 |
| tokens_used | INTEGER NOT NULL | 实际消耗 token 数 |
| model | TEXT NOT NULL | 使用的模型 |
| cost_cents | INTEGER | 成本（美分），默认 0 |
| is_platform_key | BOOLEAN NOT NULL | 是否使用平台 Key，默认 TRUE |
| metadata | JSONB | 额外信息 |
| created_at | TIMESTAMP | 创建时间 |

索引：(user_id, created_at) 用于月度查询；novel_id 索引；action 索引。

另有月度用量汇总物化视图（monthly_usage_summary），按 user_id 和月份聚合 total_tokens、total_cost_cents、total_requests、platform_tokens、own_key_tokens。通过 cron 或 ARQ 定时任务刷新。

### 1.2 操作类型枚举

| action 值 | 说明 | 典型 token 消耗 |
|-----------|------|----------------|
| outline_generation | 大纲生成（雪花法单步） | 2,000 - 5,000 |
| blueprint_generation | 章节蓝图生成 | 3,000 - 8,000 |
| chapter_generation | 章节内容生成 | 5,000 - 15,000 |
| chapter_audit | 章节审计 | 3,000 - 6,000 |
| chapter_revision | 章节修订 | 5,000 - 12,000 |
| memory_extraction | 记忆提取（摘要/角色/伏笔） | 1,000 - 3,000 |
| style_analysis | 风格分析 | 2,000 - 4,000 |
| style_transfer | 风格迁移/去 AI 化 | 4,000 - 10,000 |
| tension_analysis | 张力分析 | 1,500 - 3,000 |
| theme_agent | 主题代理审查 | 1,000 - 2,000 |

---

## 2. 套餐与配额

### 2.1 套餐定义

每个套餐包含以下配额维度：monthly_tokens（月 token 配额，-1=无限）、max_novels（最大并发小说数）、max_storage_bytes（最大存储空间）、max_collaborators（每部小说最大协作者数）、can_use_premium_models（是否可用高级模型）、can_publish_marketplace（是否可发布到市场）。

### 2.2 套餐对比表

| 特性 | Free | Pro | Enterprise |
|------|------|-----|-----------|
| 月 Token 配额 | 100K | 2M | 无限 |
| 并发小说数 | 1 | 5 | 无限 |
| 存储空间 | 100MB | 5GB | 无限 |
| 协作者数/小说 | 0 | 5 | 无限 |
| 高级模型 | 不可用 | 可用 | 可用 |
| 发布到市场 | 不可 | 可以 | 可以 |
| 自定义 API Key | 可以 | 可以 | 可以 |
| 优先任务队列 | 否 | 是 | 是 |

---

## 3. QuotaManager

QuotaManager 负责配额检查和用量记录。

### 配额检查

- check_quota(user_id, estimated_tokens)：在 LLM 调用前检查月度 token 配额。无限配额直接放行；查询本月已用量（仅计算平台 Key 用量），预估超限则抛出 QuotaExceededError
- check_novel_limit(user_id)：检查小说数量限制
- check_storage_limit(user_id, additional_bytes)：检查存储空间限制

### 用量记录

record_usage(user_id, action, tokens_used, model, novel_id, is_platform_key, metadata)：记录一次 LLM 调用的用量。平台 Key 调用自动计算成本（美分），自有 Key 调用成本为 0。

### 成本计算

按模型和 token 数计算成本，每百万 token 价格（美分）：

| 模型 | 价格/M tokens |
|------|--------------|
| claude-sonnet-4 | 300 |
| claude-haiku-4 | 80 |
| gpt-4o | 250 |
| gpt-4o-mini | 15 |
| deepseek-chat | 14 |
| deepseek-reasoner | 55 |

### 用量摘要

get_usage_summary(user_id) 返回当前月度用量摘要：plan、period_start、platform_tokens_used、own_key_tokens_used、monthly_token_quota、quota_usage_percent、total_cost_cents、novels_count、novels_quota。

---

## 4. 模型代理

### 4.1 平台 Key vs 用户自有 Key

ModelProxy 决定使用平台 Key 还是用户自有 Key。

get_adapter(user_id, task_type, model_override) 流程：

1. 检查用户是否配置了目标模型对应提供商的自有 Key
2. 如果有自有 Key：AES-256 解密后创建适配器，返回 (adapter, is_platform_key=False)，不计费不检查配额
3. 如果无自有 Key：预估 token 消耗并检查配额，使用平台 Key 创建适配器，返回 (adapter, is_platform_key=True)

默认模型映射（按任务类型）：

| 任务类型 | 默认模型 |
|---------|---------|
| outline_generation | claude-sonnet-4 |
| blueprint_generation | claude-sonnet-4 |
| chapter_generation | claude-sonnet-4 |
| chapter_audit | gpt-4o |
| style_analysis | claude-sonnet-4 |
| memory_extraction | gpt-4o-mini |

模型到提供商映射：claude* → anthropic，gpt*/o1*/o3* → openai，deepseek* → deepseek。

Token 预估（用于配额预检）：outline 4K, blueprint 6K, chapter 10K, audit 5K, revision 8K, memory 2K, style 3K, style_transfer 7K。

### 4.2 在生成流水线中集成

章节生成流水线集成配额检查和用量记录：

1. 通过 ModelProxy 获取适配器（自动检查配额）
2. 执行生成
3. 记录用量（含 is_platform_key 标记）

---

## 5. 成本估算

### 5.1 单操作成本估算 API

`GET /api/billing/estimate/{action}`

返回指定操作的预估 token 消耗和成本。支持的操作：outline_generation、outline_full（5步）、blueprint_generation、chapter_generation、chapter_full_pipeline（生成+审计+修订+提取）、batch_10_chapters。

### 5.2 月度用量仪表盘 API

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/billing/usage` | 月度用量仪表盘数据 |
| `GET` | `/api/billing/usage/history?days=30` | 每日用量历史（用于图表） |
| `GET` | `/api/billing/usage/by-novel` | 按小说维度的用量统计 |
| `GET` | `/api/billing/usage/by-action` | 按操作类型的用量统计 |

---

## 6. 用户 API Key 管理

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/settings/api-keys` | 列出用户的 API Key（脱敏显示，仅最后 4 位） |
| `POST` | `/api/settings/api-keys` | 添加 API Key（需验证有效性） |
| `DELETE` | `/api/settings/api-keys/{key_id}` | 删除 API Key |

添加时提交 provider（anthropic/openai/deepseek）、api_key 和可选 label。系统先验证 Key 有效性（尝试调用一次），通过后 AES-256 加密存储。
