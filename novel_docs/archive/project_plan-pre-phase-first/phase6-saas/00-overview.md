---
title: Phase 6 — SaaS 化
version: 2.0
date: 2026-04-20
goal: 从单用户工具变成多用户服务
prerequisite: Phase 5
---

# Phase 6 — SaaS 化

## 文档角色

本文档属于 **Phase 主线层 overview**，只承担本阶段的目标、范围、完成标准、非目标与子主题入口，不承载跨阶段 topic 的完整设计细节。

阅读方式：先阅读总纲入口与阶段路线，再阅读本 overview，最后按需进入本阶段专题文档。

## 阶段目标

将已验证的单用户系统转变为多用户 SaaS 服务。核心变更：基础设施升级、用户认证、计费配额、协作功能、模板市场。

## 完成标准

- PostgreSQL 多租户隔离完成（user_id 字段 + facade 层过滤）
- 文件存储 → S3/MinIO 对象存储迁移完成
- ARQ 任务队列就绪，Docker Compose 部署方案可用
- 用户注册/登录可用（邮箱密码 + OAuth2 + JWT）
- 用量追踪和配额管理可用，模型代理支持平台/自有 Key
- 小说协作（owner/editor/viewer）和章节批注可用
- 模板市场上线，支持发布、浏览、下载、评分

## 不包含

- 实时协同编辑（本阶段使用乐观锁，不做 CRDT/OT）
- 支付网关集成（本阶段仅做配额管理，不接入 Stripe 等）
- 自定义域名 / 白标方案

## 文档索引

### 本阶段专题

| 文档 | 内容 |
|------|------|
| [01-infrastructure.md](01-infrastructure.md) | 基础设施升级：PostgreSQL、对象存储、任务队列、部署架构 |
| [02-user-system.md](02-user-system.md) | 用户系统：注册登录、OAuth2、JWT、角色权限 |
| [03-billing-quota.md](03-billing-quota.md) | 用量追踪与配额管理：计费记录、套餐、模型代理 |
| [04-collaboration.md](04-collaboration.md) | 协作功能：共享、权限矩阵、章节批注、邀请机制 |
| [05-marketplace.md](05-marketplace.md) | 模板市场：资源发布、浏览下载、评分评论、内容审核 |

### 相关总纲 / 横切专题

| 文档 | 角色 | 用途 |
|------|------|------|
| [../2026-04-20-ai-novel-01-architecture.md](../2026-04-20-ai-novel-01-architecture.md) | 总纲专题 | 补充系统架构与部署演进背景 |
| [../2026-04-20-ai-novel-02-data-model.md](../2026-04-20-ai-novel-02-data-model.md) | 总纲专题 | 补充数据模型与存储基线 |
| [../common-components.md](../common-components.md) | 横切专题 | 按需参考 SaaS 与跨 phase 可复用组件 |
