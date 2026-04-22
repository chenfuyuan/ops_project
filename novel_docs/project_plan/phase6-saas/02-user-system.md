---
title: Phase 6.2 — 用户系统
version: 1.0
date: 2026-04-20
parent: Phase 6 — SaaS 化
---

# 用户系统

## 概述

实现完整的用户注册、登录、认证体系。支持邮箱密码和 OAuth2 两种方式，使用 JWT 进行 API 鉴权，所有数据查询按 user_id 隔离。

---

## 1. 数据模型

### 1.1 用户表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | UUID v4 |
| email | TEXT UNIQUE NOT NULL | 邮箱 |
| password_hash | TEXT | bcrypt 哈希，OAuth 用户可为 NULL |
| oauth_provider | TEXT | OAuth 提供商：google / github / NULL |
| oauth_id | TEXT | OAuth 提供商的用户 ID |
| display_name | TEXT NOT NULL | 显示名称 |
| avatar_url | TEXT | 头像 URL |
| role | TEXT NOT NULL | 角色：user / admin（默认 user） |
| plan | TEXT NOT NULL | 套餐：free / pro / enterprise（默认 free） |
| is_active | BOOLEAN NOT NULL | 是否启用（默认 TRUE） |
| email_verified | BOOLEAN NOT NULL | 邮箱是否已验证（默认 FALSE） |
| created_at / updated_at | TIMESTAMP | 时间戳 |

索引：email 唯一索引；(oauth_provider, oauth_id) 条件索引（oauth_provider 非 NULL 时）。

### 用户 API Key 管理表

| 字段 | 说明 |
|------|------|
| id | 主键 |
| user_id | 关联用户（级联删除） |
| provider | LLM 提供商：openai / anthropic / deepseek 等 |
| encrypted_key | AES-256 加密存储的 API Key |
| label | 用户自定义标签 |
| created_at | 创建时间 |

### Refresh Token 表

| 字段 | 说明 |
|------|------|
| id | 主键 |
| user_id | 关联用户（级联删除） |
| token_hash | SHA-256 哈希（不存明文） |
| expires_at | 过期时间 |
| created_at | 创建时间 |

### 1.2 用户实体

User 实体包含上述所有字段，以及两个派生属性：is_oauth_user（oauth_provider 非空）和 is_admin（role == admin）。角色枚举：USER / ADMIN。套餐枚举：FREE / PRO / ENTERPRISE。

---

## 2. 认证方式

### 2.1 邮箱 + 密码

PasswordAuthService 负责邮箱密码认证：

注册流程：
1. 检查邮箱是否已注册
2. 密码强度校验（至少 8 位，至少包含一个数字）
3. 使用 bcrypt 哈希密码
4. 创建用户记录

登录流程：
1. 按邮箱查找用户
2. 验证密码哈希
3. 检查账户是否启用
4. 返回用户对象

### 2.2 OAuth2（Google / GitHub）

OAuthService 负责 OAuth2 认证，支持 Google 和 GitHub。

OAuth 回调处理流程：
1. 用授权码（code）换取 access_token
2. 用 access_token 获取用户信息（邮箱、名称、头像）
3. 查找或创建用户（_get_or_create_user）

用户查找/创建逻辑：
1. 先按 OAuth ID 查找已有用户
2. 再按邮箱查找（可能之前用密码注册过），找到则关联 OAuth 信息
3. 都未找到则创建新用户（OAuth 邮箱视为已验证）

---

## 3. JWT Token 管理

### 3.1 Token 生成与验证

TokenService 负责 JWT 的生成、验证和轮换。

Access Token：
- 有效期 15 分钟
- Payload 包含 sub（用户 ID）、email、role、plan、type="access"、exp、iat
- 使用 HS256 算法签名

Refresh Token：
- 有效期 7 天
- Payload 包含 sub、type="refresh"、jti（唯一标识，用于撤销）、exp、iat
- 数据库存储 token 的 SHA-256 哈希（不存明文）

Token 刷新（轮换策略）：
1. 验证 refresh token 签名和类型
2. 验证 token 哈希在数据库中存在
3. 删除旧 token，生成新的 access + refresh token 对
4. 检查用户是否存在且启用

撤销：revoke_all_tokens 删除用户所有 refresh token（用于密码修改、账户安全等场景）。

### 3.2 Token 响应格式

响应包含 access_token、refresh_token、token_type（"bearer"）、expires_in（900 秒）。

---

## 4. API 鉴权中间件

### 4.1 依赖注入

三个鉴权依赖：

- get_current_user：从 JWT Token 中提取当前用户，验证用户存在且启用
- get_current_admin：要求管理员权限
- require_plan(min_plan)：要求最低套餐等级（按 FREE < PRO < ENTERPRISE 排序）

### 4.2 查询隔离

所有路由注入当前用户，查询自动按 user_id scope。列表接口按 user.id 过滤，详情接口同时校验 novel_id 和 user_id 归属权。

---

## 5. 认证 API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/auth/register` | 邮箱密码注册，返回 Token |
| `POST` | `/api/auth/login` | 邮箱密码登录，返回 Token |
| `GET` | `/api/auth/callback/google` | Google OAuth2 回调 |
| `GET` | `/api/auth/callback/github` | GitHub OAuth2 回调 |
| `POST` | `/api/auth/refresh` | 刷新 Access Token |
| `POST` | `/api/auth/logout` | 登出（撤销所有 Refresh Token） |
| `GET` | `/api/auth/me` | 获取当前用户信息 |

---

## 6. 角色权限

### 6.1 角色定义

| 角色 | 说明 | 权限 |
|------|------|------|
| user | 普通用户 | CRUD 自己的小说、使用配额内的生成功能 |
| admin | 管理员 | 所有 user 权限 + 用户管理 + 系统配置 + 查看全局统计 |

### 6.2 管理员 API

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/admin/users` | 列出所有用户（分页） |
| `PATCH` | `/api/admin/users/{user_id}/plan` | 修改用户套餐 |
| `PATCH` | `/api/admin/users/{user_id}/active` | 启用/禁用用户 |
| `GET` | `/api/admin/stats` | 系统统计概览（总用户数、30 天活跃用户、总小说数、月度 token 消耗和成本） |
