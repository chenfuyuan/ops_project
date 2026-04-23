---
title: Phase 1 — API 端点设计
version: 1.0
date: 2026-04-20
---

# API 端点设计

## 基础约定

- 基础路径：`/api/v1`
- 响应格式：JSON
- 错误格式：`{"error": "错误描述", "detail": {...}}`
- 分页：`?page=1&page_size=20`
- 流式端点使用 SSE（Server-Sent Events）
- 路由委托：所有路由处理函数通过 DI 获取对应模块的 facade，不直接实例化内部服务

## 小说管理 — `novel` 模块

```
POST   /api/v1/novels                    创建小说项目
GET    /api/v1/novels                    获取小说列表
GET    /api/v1/novels/{novel_id}         获取小说详情
PUT    /api/v1/novels/{novel_id}         更新小说信息
DELETE /api/v1/novels/{novel_id}         删除小说项目
```

### POST /api/v1/novels

创建小说项目。请求体包含 title、premise、genre、language 和 structure_config（total_chapters、words_per_chapter）。响应返回创建的小说对象（含生成的 id 和 created_at）。

## 大纲管理 — `outline` 模块

```
POST   /api/v1/novels/{novel_id}/outline/generate       触发大纲生成（可指定起始步骤）
GET    /api/v1/novels/{novel_id}/outline                 获取大纲（含五步产物）
PUT    /api/v1/novels/{novel_id}/outline/core-seed       编辑核心种子
PUT    /api/v1/novels/{novel_id}/outline/world-building  编辑世界观
PUT    /api/v1/novels/{novel_id}/outline/three-act       编辑三幕结构
POST   /api/v1/novels/{novel_id}/outline/regenerate/{step}  重新生成指定步骤
```

### POST /api/v1/novels/{novel_id}/outline/generate

触发大纲生成。支持断点续跑。请求体可选指定 `start_from_step`。

响应为 SSE 流式，事件类型：
- `step_start` — 步骤开始（含 step 序号和 name）
- `step_complete` — 步骤完成（含 step 序号、name 和 result）
- `complete` — 全部完成

## 角色管理 — `character` 模块

```
GET    /api/v1/novels/{novel_id}/characters              获取角色列表
GET    /api/v1/novels/{novel_id}/characters/{char_id}    获取角色详情（含最新状态）
PUT    /api/v1/novels/{novel_id}/characters/{char_id}    编辑角色信息
GET    /api/v1/novels/{novel_id}/characters/{char_id}/states  获取角色状态历史
```

## 蓝图管理 — `blueprint` 模块

```
POST   /api/v1/novels/{novel_id}/blueprints/generate     触发蓝图生成
GET    /api/v1/novels/{novel_id}/blueprints              获取蓝图列表
GET    /api/v1/novels/{novel_id}/blueprints/{chapter_num} 获取单章蓝图
PUT    /api/v1/novels/{novel_id}/blueprints/{chapter_num} 编辑单章蓝图
POST   /api/v1/novels/{novel_id}/blueprints/regenerate   重新生成指定批次
```

### POST /api/v1/novels/{novel_id}/blueprints/generate

触发蓝图生成。请求体可选指定 `start_chapter`。

响应为 SSE 流式，事件类型：
- `batch_start` — 批次开始（含 batch 序号和 chapters 范围）
- `batch_complete` — 批次完成（含 chapters_generated 数量）
- `complete` — 全部完成（含 total_chapters）

## 章节管理 — `chapter` 模块

```
GET    /api/v1/novels/{novel_id}/chapters                获取章节列表
GET    /api/v1/novels/{novel_id}/chapters/{chapter_num}  获取章节详情（含内容）
PUT    /api/v1/novels/{novel_id}/chapters/{chapter_num}  编辑章节内容（触发章后管线）
DELETE /api/v1/novels/{novel_id}/chapters/{chapter_num}  删除章节
```

### 章节生成（流水线）

```
POST   /api/v1/novels/{novel_id}/chapters/{chapter_num}/generate  触发章节生成
GET    /api/v1/novels/{novel_id}/chapters/{chapter_num}/pipeline  获取流水线状态和中间产物
POST   /api/v1/novels/{novel_id}/chapters/{chapter_num}/pipeline/resume  断点续跑
```

### POST /api/v1/novels/{novel_id}/chapters/{chapter_num}/generate

触发单章生成流水线。请求体可选指定 `resume_from`（阶段名，如 "draft"），用于断点续跑。

响应为 SSE 流式，事件类型：
- `stage_start` — 阶段开始（含 stage 名称和 chapter_num）
- `stage_complete` — 阶段完成（含 stage、chapter_num、tokens_used 等统计）
- `draft_chunk` — Draft 阶段的流式文本块（含 content）
- `complete` — 全部完成（含 chapter_num、word_count、total_tokens）

### GET /api/v1/novels/{novel_id}/chapters/{chapter_num}/pipeline

获取流水线中间产物（用于调试和审查）。

响应包含 chapter_num 和 stages 对象。stages 中每个阶段的结构如下：

| 阶段 | 返回字段 | 说明 |
|------|---------|------|
| plan | status, output, tokens_used, duration_ms | output 含 must_keep、must_avoid 等约束列表 |
| compose | status, output, duration_ms | output 含各层 token 分配（t0_tokens、t2_tokens、t3_tokens） |
| draft | status, tokens_used, duration_ms | 写作阶段，耗时最长 |
| commit | status, tokens_used, duration_ms | 章后处理（摘要、状态更新等） |

每个阶段的 status 为 completed / pending / failed。

## 伏笔管理 — `blueprint` 模块

```
GET    /api/v1/novels/{novel_id}/foreshadowing           获取伏笔列表（可按状态过滤）
GET    /api/v1/novels/{novel_id}/foreshadowing/{id}      获取伏笔详情
PUT    /api/v1/novels/{novel_id}/foreshadowing/{id}      编辑伏笔
POST   /api/v1/novels/{novel_id}/foreshadowing           手动创建伏笔
```

### GET /api/v1/novels/{novel_id}/foreshadowing

查询参数：`?status=open&status=resolved`

响应为分页列表，每个伏笔条目包含：

| 字段 | 说明 |
|------|------|
| id | 伏笔 ID |
| description | 伏笔描述 |
| status | 状态（open / resolved / abandoned） |
| planted_chapter | 植入章节号 |
| last_advanced_chapter | 最近推进章节号 |
| resolved_chapter | 解决章节号（未解决时为空） |
| related_characters | 关联角色 ID 列表 |

外层包含 items 数组和 total 总数。

## 摘要查询 — `chapter` 模块

```
GET    /api/v1/novels/{novel_id}/summaries               获取章节摘要列表
GET    /api/v1/novels/{novel_id}/summaries/{chapter_num}  获取单章摘要
```

## AI 网关配置 — `ai_gateway` 模块

```
GET    /api/v1/ai-gateway/profiles            获取所有模型配置
POST   /api/v1/ai-gateway/profiles            创建模型配置
PUT    /api/v1/ai-gateway/profiles/{id}       更新模型配置
DELETE /api/v1/ai-gateway/profiles/{id}       删除模型配置
POST   /api/v1/ai-gateway/profiles/{id}/test  测试模型连接
```

### POST /api/v1/ai-gateway/profiles

请求体字段：

| 字段 | 说明 |
|------|------|
| name | 配置名称（如 "GPT-4o 写作"） |
| provider | 提供商类型（openai_compatible 等） |
| base_url | API 基础地址 |
| api_key | API 密钥 |
| model | 模型名称 |
| task_type | 任务类型（draft / plan / commit 等） |
| params | 模型参数（temperature、max_tokens 等） |
| is_default | 是否为该任务类型的默认配置 |

### POST /api/v1/ai-gateway/profiles/{id}/test

测试模型连接是否正常。发送一个简单的测试请求。

响应包含 success（布尔值）、model（模型名称）、response_time_ms（响应耗时毫秒）和 message（状态描述）。
