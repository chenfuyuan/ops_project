# HTTP 请求测试

这个目录存放可由 REST Client 类编辑器插件直接运行的 `.http` 请求，用于本地手动验证 API 入口。

## 启动本地 API

仅验证基础健康检查时可以直接启动：

```bash
uv run uvicorn app.api:app --host 127.0.0.1 --port 8000
```

验证大纲生成接口时，应使用 Docker Compose 中的 PostgreSQL，并先执行迁移：

```bash
docker compose up -d --build postgres redis
docker compose run --rm api /app/.venv/bin/alembic upgrade head
docker compose up -d api worker
```

然后访问 `http://127.0.0.1:8000`。

## 验证应用健康检查

运行 `health.http`，预期 `/health` 返回 `200` 和 `{"status":"ok"}`。

## 验证大纲生成

运行 `outline.http`，按顺序执行创建种子、生成骨架、确认骨架、展开卷、编辑章节和获取完整大纲请求。

其中创建和获取种子只依赖 PostgreSQL；生成骨架和展开卷会调用 AI 网关，因此需要先完成下面的 AI 网关配置。

## 验证 AI 网关

运行 `ai_gateway.http`，请求应用提供的 `/ai-gateway/availability` 和 `/ai-gateway/generate` 测试接口。

未配置网关时，预期 `/ai-gateway/availability` 返回 `503`，并且响应中的 `configured` 为 `false`。

配置网关时，使用同一份 AI 网关配置文件，不再为 availability 单独配置地址和密钥：

```bash
cp config/ai_gateway.example.json config/ai_gateway.json
```

在 `config/ai_gateway.json` 中配置 provider、profile 和模型名，然后在启动 API 前设置：

```bash
AI_GATEWAY_CONFIG_PATH="config/ai_gateway.json" \
AI_GATEWAY_API_KEY="replace-locally-do-not-commit" \
uv run uvicorn app.api:app --host 127.0.0.1 --port 8000
```

`/ai-gateway/availability` 会读取 `AI_GATEWAY_CONFIG_PATH` 指向的配置文件，使用第一个 provider 的 `base_url` 和 `api_key_env` 对应的密钥进行健康探测。

不要把真实 token、密钥或内部网关地址提交到仓库。
