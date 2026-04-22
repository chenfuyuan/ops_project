---
title: Phase 6.4 — 协作功能
version: 1.0
date: 2026-04-20
parent: Phase 6 — SaaS 化
---

# 协作功能

## 概述

支持多用户围绕同一部小说进行协作。通过角色权限控制访问级别，支持章节批注和评论，提供邮件邀请和分享链接两种协作入口。本阶段使用乐观锁避免冲突，不实现实时协同编辑。

---

## 1. 数据模型

### 1.1 小说协作者表

| 字段 | 说明 |
|------|------|
| novel_id | 小说 ID（联合主键，级联删除） |
| user_id | 用户 ID（联合主键，级联删除） |
| role | 角色：owner / editor / viewer（默认 viewer） |
| invited_by | 邀请人 ID |
| created_at | 加入时间 |

### 章节评论/批注表

| 字段 | 说明 |
|------|------|
| id | 主键 |
| chapter_id | 关联章节（级联删除） |
| user_id | 评论者 |
| content | 评论内容 |
| position_start | 批注起始位置（字符偏移，可选） |
| position_end | 批注结束位置（可选） |
| parent_id | 回复某条评论（可选） |
| resolved | 是否已解决（默认 FALSE） |
| resolved_by | 解决者 |
| created_at / updated_at | 时间戳 |

### 邀请表

| 字段 | 说明 |
|------|------|
| id | 主键 |
| novel_id | 小说 ID |
| invited_email | 被邀请人邮箱 |
| role | 邀请角色（默认 viewer） |
| invited_by | 邀请人 ID |
| token | 邀请链接 token（唯一） |
| accepted | 是否已接受（默认 FALSE） |
| expires_at | 过期时间 |
| created_at | 创建时间 |

### 分享链接表

| 字段 | 说明 |
|------|------|
| id | 主键 |
| novel_id | 小说 ID |
| created_by | 创建者 ID |
| token | 链接 token（唯一） |
| role | 通过链接加入的默认角色（默认 viewer） |
| max_uses | 最大使用次数（NULL=无限） |
| used_count | 已使用次数（默认 0） |
| is_active | 是否有效（默认 TRUE） |
| expires_at | 过期时间（NULL=永不过期） |
| created_at | 创建时间 |

---

## 2. 权限矩阵

### 2.1 角色权限定义

| 操作 | owner | editor | viewer |
|------|-------|--------|--------|
| 查看小说/章节 | 可以 | 可以 | 可以 |
| 编辑章节内容 | 可以 | 可以 | 不可 |
| 触发 AI 生成 | 可以 | 可以 | 不可 |
| 添加/回复评论 | 可以 | 可以 | 可以 |
| 解决评论 | 可以 | 可以 | 不可 |
| 修改小说设置 | 可以 | 不可 | 不可 |
| 管理协作者 | 可以 | 不可 | 不可 |
| 生成分享链接 | 可以 | 不可 | 不可 |
| 删除小说 | 可以 | 不可 | 不可 |
| 修改 LLM 配置 | 可以 | 不可 | 不可 |
| 导出小说 | 可以 | 可以 | 可以 |

### 2.2 权限检查

PermissionService 提供权限检查：

- check_permission(novel_id, user_id, permission)：检查用户对某部小说是否有指定权限，返回布尔值
- require_permission(novel_id, user_id, permission)：要求权限，无权限则抛出 403
- get_user_role(novel_id, user_id)：获取用户在某部小说中的角色

权限枚举：VIEW, EDIT_CHAPTER, GENERATE, COMMENT, RESOLVE_COMMENT, CONFIGURE, MANAGE_COLLABORATORS, SHARE, DELETE, EXPORT。

### 2.3 在路由中使用

所有涉及小说操作的路由注入 PermissionService，在执行业务逻辑前调用 require_permission 检查权限。

---

## 3. 章节评论与批注

### 3.1 评论类型

评论分为两种：
- 普通评论：无位置信息，针对整章
- 行内批注：有 position_start 和 position_end，标注章节中的具体文本范围

评论支持回复（通过 parent_id 形成树形结构）和解决标记（resolved）。

### 3.2 评论 API

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/novels/{novel_id}/chapters/{chapter_id}/comments` | 列出章节评论（树形结构） |
| `POST` | `/api/novels/{novel_id}/chapters/{chapter_id}/comments` | 创建评论或批注 |
| `POST` | `/api/novels/{novel_id}/chapters/{chapter_id}/comments/{comment_id}/resolve` | 标记评论为已解决 |

列出评论支持 include_resolved 参数（默认不包含已解决的评论）。创建评论时提交 content，可选 position_start/position_end（行内批注）和 parent_id（回复）。

---

## 4. 邀请与分享

### 4.1 邮件邀请

InviteService 负责邮件邀请流程：

invite_by_email 流程：
1. 检查被邀请人是否已是协作者
2. 创建邀请记录（含随机 token，7 天有效期）
3. 发送邀请邮件（含邀请链接）

accept_invite 流程：
1. 验证邀请存在、未被接受、未过期
2. 验证当前用户邮箱与邀请邮箱匹配
3. 添加为协作者
4. 标记邀请为已接受

### 4.2 分享链接

ShareService 负责分享链接管理：

- create_share_link(novel_id, created_by, role, max_uses, expires_days)：生成分享链接，返回 share_url、token、role、max_uses、expires_at
- join_via_link(token, user_id)：通过分享链接加入协作。验证链接有效性（存在、活跃、未过期、未达使用上限），检查是否已是协作者，添加为协作者并递增使用计数
- revoke_share_link(link_id, user_id)：撤销分享链接

### 4.3 协作者管理 API

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/novels/{novel_id}/collaborators` | 列出所有协作者 |
| `POST` | `/api/novels/{novel_id}/collaborators/invite` | 邀请协作者（邮箱 + 角色） |
| `PATCH` | `/api/novels/{novel_id}/collaborators/{user_id}/role` | 修改协作者角色（仅 editor/viewer，不能修改 owner） |
| `DELETE` | `/api/novels/{novel_id}/collaborators/{user_id}` | 移除协作者（不能移除自己或 owner） |

---

## 5. 并发控制

### 5.1 乐观锁

本阶段不实现实时协同编辑（CRDT/OT），使用乐观锁处理并发冲突。

chapters 表新增 version 字段（INTEGER，默认 1）。更新时检查版本号：WHERE id = $1 AND version = $2，同时 version + 1。如果 affected rows = 0，说明版本已变（被其他人修改），返回 409 Conflict。

### 5.2 冲突处理流程

1. 用户 A 打开章节（获取 version=3）
2. 用户 B 打开同一章节（获取 version=3）
3. 用户 A 保存修改（version=3 → 4，成功）
4. 用户 B 保存修改（version=3 → 4，失败，返回 409 Conflict）
5. 前端提示用户 B："章节已被其他人修改，请刷新后重试"
6. 用户 B 刷新获取最新内容（version=4），手动合并修改后重新保存

### 5.3 未来演进

后续版本可考虑：
- WebSocket 实时通知（其他人正在编辑的提示）
- 基于 Yjs 的 CRDT 实时协同编辑
- 操作历史和版本对比（diff）
