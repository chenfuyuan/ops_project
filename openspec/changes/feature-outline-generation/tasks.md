## 1. 模块骨架与领域模型

- [x] 1.1 创建 `app/business/novel_generate/` 目录结构（`__init__.py`、`nodes/__init__.py`、`nodes/outline/__init__.py`）
- [x] 1.2 实现 `nodes/outline/entities.py`：定义 `Seed`、`Skeleton`、`SkeletonVolume`、`ChapterSummary`、`Outline` 领域模型及 `SkeletonStatus`、`OutlineStatus` 枚举
- [x] 1.3 实现 `nodes/outline/dto.py`：定义创建种子、编辑卷、编辑章节的输入输出 DTO

## 2. Ports 与规则

- [x] 2.1 实现 `nodes/outline/ports.py`：定义 `OutlineRepository(Protocol)` 和 `OutlineAiPort(Protocol)` 接口
- [x] 2.2 实现 `nodes/outline/rules.py`：种子字段完整性校验、骨架确认前置检查（DRAFT → CONFIRMED）、展开前骨架必须已确认

## 3. 数据库持久化

- [x] 3.1 创建 `nodes/outline/infrastructure/__init__.py` 和 `nodes/outline/infrastructure/repository.py`：实现 `OutlineRepositoryImpl`，包含 SQLAlchemy ORM 模型和全部 repository 方法
- [x] 3.2 创建数据库迁移：`outline_seeds`、`outline_skeletons`、`outline_skeleton_volumes`、`outline_chapter_summaries`、`outlines` 五张表

## 4. AI 适配器

- [x] 4.1 创建 `nodes/outline/infrastructure/ai_adapter.py`：实现 `OutlineAiAdapter`，桥接 `AiGatewayFacade`
- [x] 4.2 定义骨架生成和章节展开的 JSON Schema（`StructuredOutputConstraint`）
- [x] 4.3 实现 `generate_skeleton(seed)` — 将种子翻译为 `AiGatewayRequest`（STRUCTURED 模式），解析 `structured_content` 为 `list[SkeletonVolume]`
- [x] 4.4 实现 `expand_volume(seed, skeleton, volume)` — 将种子+骨架+目标卷翻译为 `AiGatewayRequest`，解析为 `list[ChapterSummary]`

## 5. 业务服务

- [x] 5.1 实现 `nodes/outline/service.py`：`OutlineNodeService.__init__` 接收 `OutlineRepository` 和 `OutlineAiPort`
- [x] 5.2 实现 `create_seed()` — 校验种子字段完整性，持久化并返回
- [x] 5.3 实现 `get_seed()` — 按 ID 获取种子
- [x] 5.4 实现 `generate_skeleton()` — 调用 AI port 生成骨架，持久化 Skeleton + SkeletonVolume 列表；若种子已有骨架则覆盖
- [x] 5.5 实现 `confirm_skeleton()` — 校验骨架为 DRAFT，变更为 CONFIRMED
- [x] 5.6 实现 `expand_volume()` — 校验骨架已确认，调用 AI port 逐卷展开，持久化 ChapterSummary 列表；若该卷已有章节则覆盖
- [x] 5.7 实现 `update_volume()` — 更新卷内容，标记该卷下已有章节为过期
- [x] 5.8 实现 `update_chapter()` — 更新章节摘要内容
- [x] 5.9 实现 `get_outline()` — 聚合种子、骨架、卷、章节摘要，判定大纲状态（IN_PROGRESS / COMPLETE）

## 6. HTTP 端点

- [x] 6.1 创建 `app/interfaces/http/outline.py`：定义 FastAPI router
- [x] 6.2 实现 `POST /api/outlines/seeds` — 创建种子
- [x] 6.3 实现 `GET /api/outlines/seeds/{seed_id}` — 获取种子
- [x] 6.4 实现 `POST /api/outlines/seeds/{seed_id}/skeleton` — 生成骨架
- [x] 6.5 实现 `GET /api/outlines/skeletons/{skeleton_id}` — 获取骨架（含卷列表）
- [x] 6.6 实现 `PATCH /api/outlines/skeletons/volumes/{volume_id}` — 编辑骨架卷
- [x] 6.7 实现 `POST /api/outlines/skeletons/{skeleton_id}/confirm` — 确认骨架
- [x] 6.8 实现 `POST /api/outlines/skeletons/{skeleton_id}/expand/{volume_id}` — 展开指定卷
- [x] 6.9 实现 `PATCH /api/outlines/chapters/{chapter_id}` — 编辑章节摘要
- [x] 6.10 实现 `GET /api/outlines/seeds/{seed_id}/outline` — 获取完整大纲

## 7. Bootstrap 装配

- [x] 7.1 创建 `app/bootstrap/novel_generate.py`：装配 `OutlineRepositoryImpl`、`OutlineAiAdapter`、`OutlineNodeService`
- [x] 7.2 在 `app/bootstrap/api.py` 中注册 outline router
- [x] 7.3 配置 AI 网关 capability profile（`outline-skeleton`、`outline-chapter-expansion`）

## 8. 集成测试

- [x] 8.1 测试创建种子（成功 + 缺失字段）
- [x] 8.2 测试生成骨架（成功 + 种子不存在 + 重新生成覆盖）
- [x] 8.3 测试编辑骨架卷（更新内容 + 章节标记过期）
- [x] 8.4 测试确认骨架（DRAFT → CONFIRMED + 重复确认）
- [x] 8.5 测试展开卷章节（成功 + 骨架未确认拒绝 + 重新展开覆盖）
- [x] 8.6 测试编辑章节摘要
- [x] 8.7 测试获取完整大纲（完整展开 + 部分展开 + 无骨架）
- [x] 8.8 测试 AI port 抽象边界：确认 business 层无 `app.capabilities` 直接 import
