# 大纲生成功能 HTTP 测试文档

## 1. 测试目标

通过 HTTP 接口验证大纲生成功能的本地完整流程：

1. 启动 PostgreSQL、Redis。
2. 执行数据库迁移。
3. 启动 API 和 worker。
4. 通过 HTTP 创建故事种子。
5. 查询种子。
6. 调用 AI 网关生成骨架。
7. 查询骨架。
8. 编辑骨架卷。
9. 确认骨架。
10. 调用 AI 网关展开卷章节。
11. 编辑章节摘要。
12. 获取完整大纲。

大纲数据会持久化到 Docker Compose 中的 PostgreSQL。

---

## 2. 前置条件

确保当前在项目根目录：

```bash
cd /Users/simon/code/person_up/ops_project
```

需要本机可用：

```bash
docker
docker compose
uv
```

---

## 3. 启动 PostgreSQL 和 Redis

```bash
docker compose up -d --build postgres redis
```

确认服务状态：

```bash
docker compose ps
```

PostgreSQL 配置来自 `docker-compose.yml`：

```yaml
POSTGRES_DB: person_up
POSTGRES_USER: person_up
POSTGRES_PASSWORD: person_up
```

API 使用的数据库地址是：

```text
postgresql+psycopg://person_up:person_up@postgres:5432/person_up
```

---

## 4. 执行数据库迁移

```bash
docker compose run --rm api /app/.venv/bin/alembic upgrade head
```

可选：检查表是否创建成功。

```bash
docker compose exec postgres psql -U person_up -d person_up -c "\dt"
```

预期能看到类似表：

```text
outline_seeds
outline_skeletons
outline_skeleton_volumes
outline_chapter_summaries
outlines
```

---

## 5. 配置 AI 网关

如果只测试创建和查询 seed，可以跳过本节。

如果要测试“生成骨架”和“展开卷章节”，需要配置 AI 网关。

复制示例配置：

```bash
cp config/ai_gateway.example.json config/ai_gateway.json
```

编辑：

```text
config/ai_gateway.json
```

确认里面有以下 profile，并把模型名替换为本地可用模型：

```json
"outline-skeleton"
```

```json
"outline-chapter-expansion"
```

启动 API 前设置密钥：

```bash
export AI_GATEWAY_API_KEY="replace-locally-do-not-commit"
```

不要提交真实 token、密钥或内部网关地址。

---

## 6. 启动 API 和 worker

```bash
docker compose up -d api worker
```

检查健康状态：

```bash
curl -i http://127.0.0.1:8000/health
```

预期：

```http
HTTP/1.1 200 OK
```

响应体：

```json
{"status":"ok"}
```

---

## 7. 使用 `.http` 文件测试

项目已经提供 HTTP 测试文件：

```text
tests/http/outline.http
```

可用 VS Code REST Client、JetBrains HTTP Client 等工具打开并逐条执行。

文件顶部变量：

```http
@baseUrl = http://127.0.0.1:8000
@seedId = replace-with-seed-id
@skeletonId = replace-with-skeleton-id
@volumeId = replace-with-volume-id
@chapterId = replace-with-chapter-id
```

测试时按顺序执行请求，并把上一步响应里的 ID 填回变量。

---

## 8. 使用 curl 手动测试

### 8.1 健康检查

```bash
curl -i http://127.0.0.1:8000/health
```

---

### 8.2 创建故事种子

```bash
curl -s -X POST http://127.0.0.1:8000/api/outlines/seeds \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "群星回声",
    "genre": "科幻",
    "protagonist": "失忆领航员",
    "core_conflict": "殖民舰队争夺唯一航道",
    "story_direction": "主角逐步发现自己曾关闭航道",
    "additional_notes": "偏群像，带悬疑感"
  }'
```

响应中记录：

```json
{
  "id": "seed-id"
}
```

后续命令用真实 ID 替换：

```bash
SEED_ID="replace-with-seed-id"
```

---

### 8.3 查询故事种子

```bash
curl -s http://127.0.0.1:8000/api/outlines/seeds/$SEED_ID
```

预期返回刚创建的 seed 内容。

---

### 8.4 生成骨架

需要 AI 网关可用。

```bash
curl -s -X POST http://127.0.0.1:8000/api/outlines/seeds/$SEED_ID/skeleton
```

响应中记录：

```json
{
  "id": "skeleton-id",
  "volumes": [
    {
      "id": "volume-id"
    }
  ]
}
```

设置变量：

```bash
SKELETON_ID="replace-with-skeleton-id"
VOLUME_ID="replace-with-volume-id"
```

---

### 8.5 查询骨架

```bash
curl -s http://127.0.0.1:8000/api/outlines/skeletons/$SKELETON_ID
```

---

### 8.6 编辑骨架卷

```bash
curl -s -X PATCH http://127.0.0.1:8000/api/outlines/skeletons/volumes/$VOLUME_ID \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "第一卷：失落航道",
    "turning_point": "主角发现自己与航道封锁事件有关"
  }'
```

---

### 8.7 确认骨架

```bash
curl -s -X POST http://127.0.0.1:8000/api/outlines/skeletons/$SKELETON_ID/confirm
```

确认后骨架状态应变为：

```json
"status": "confirmed"
```

---

### 8.8 展开卷章节

需要 AI 网关可用。

```bash
curl -s -X POST http://127.0.0.1:8000/api/outlines/skeletons/$SKELETON_ID/expand/$VOLUME_ID
```

响应中记录章节 ID：

```json
[
  {
    "id": "chapter-id"
  }
]
```

设置变量：

```bash
CHAPTER_ID="replace-with-chapter-id"
```

---

### 8.9 编辑章节摘要

```bash
curl -s -X PATCH http://127.0.0.1:8000/api/outlines/chapters/$CHAPTER_ID \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "第一章：冷冻舱苏醒",
    "summary": "主角在异常警报中醒来，发现舰队已经偏离航道。"
  }'
```

---

### 8.10 获取完整大纲

```bash
curl -s http://127.0.0.1:8000/api/outlines/seeds/$SEED_ID/outline
```

预期返回：

```json
{
  "seed": {},
  "skeleton": {},
  "chapters_by_volume": {},
  "status": "complete"
}
```

如果部分卷还没有展开章节，状态可能是：

```json
"status": "in_progress"
```

---

## 9. 最小 PostgreSQL 冒烟测试

如果暂时不配置 AI 网关，可以只验证 PostgreSQL 持久化链路。

### 创建 seed

```bash
curl -s -X POST http://127.0.0.1:8000/api/outlines/seeds \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "群星回声",
    "genre": "科幻",
    "protagonist": "失忆领航员",
    "core_conflict": "殖民舰队争夺唯一航道",
    "story_direction": "主角逐步发现自己曾关闭航道",
    "additional_notes": "偏群像，带悬疑感"
  }'
```

### 查询 seed

```bash
curl -s http://127.0.0.1:8000/api/outlines/seeds/$SEED_ID
```

只要创建和查询成功，就说明：

- API 已连接 PostgreSQL。
- 迁移已生效。
- outline seed 数据可以持久化和读取。

---

## 10. 常见问题

### 10.1 返回 503：outline service is not configured

说明 API 启动时没有拿到：

```text
PERSON_UP_DATABASE_URL
```

请使用 Docker Compose 启动 API：

```bash
docker compose up -d api
```

不要只用裸命令启动：

```bash
uv run uvicorn app.api:app
```

除非你手动设置了 `PERSON_UP_DATABASE_URL`。

---

### 10.2 数据库表不存在

如果看到 relation/table 不存在，重新执行迁移：

```bash
docker compose run --rm api /app/.venv/bin/alembic upgrade head
```

---

### 10.3 PostgreSQL 密码认证失败

如果出现：

```text
password authentication failed for user "person_up"
```

通常是旧 Docker volume 已经用不同账号或密码初始化过。

当前 Compose 使用的命名 volume 是：

```text
person_up_postgres_data
```

不要随意删除 volume。若确实需要清理数据库，应先确认不会丢失需要保留的数据。

---

### 10.4 生成骨架或展开卷失败

这两个接口会调用 AI 网关：

```text
POST /api/outlines/seeds/{seed_id}/skeleton
POST /api/outlines/skeletons/{skeleton_id}/expand/{volume_id}
```

请检查：

1. `config/ai_gateway.json` 是否存在。
2. `AI_GATEWAY_API_KEY` 是否已设置。
3. profile 是否包含：
   - `outline-skeleton`
   - `outline-chapter-expansion`
4. 模型名是否替换为真实可用模型。
5. 网关 base URL 是否可访问。

---

## 11. 停止本地服务

```bash
docker compose down
```

如果只想停止容器但保留 PostgreSQL 数据，使用上面命令即可。

不要默认加 `-v`，因为：

```bash
docker compose down -v
```

会删除数据库 volume。
