---
title: Phase 1 — LLM 适配层与多模型路由
version: 1.0
date: 2026-04-20
---

# LLM 适配层与多模型路由

## 设计目标

- 统一接口：上层代码不关心具体用的是哪个模型/提供商
- 多模型路由：不同任务类型（规划、写作、提取等）可配置不同模型
- 可扩展：新增提供商只需实现适配器接口
- 流式支持：写作任务需要流式输出到前端

## 核心接口

LLMAdapter 是统一的适配器协议（Protocol），所有提供商实现此接口。核心方法：

| 方法 | 说明 |
|------|------|
| invoke | 同步调用，返回完整响应（含 content、token 用量、模型名） |
| stream | 流式调用，返回异步迭代器，逐块产出文本 |

通用参数：messages（消息列表，含 role 和 content）、temperature、max_tokens、response_format（JSON mode 支持）。

消息格式：每条消息包含 role（system/user/assistant）和 content 字段。

响应格式：包含 content（文本内容）、prompt_tokens、completion_tokens、total_tokens、model 字段。

## 适配器实现

### OpenAI 兼容适配器

覆盖所有兼容 OpenAI API 格式的提供商：

- OpenAI (GPT-4o, GPT-4o-mini)
- DeepSeek
- Qwen (通义千问)
- Ollama (本地模型)
- SiliconFlow
- 火山引擎
- 其他兼容端点

适配器通过 httpx AsyncClient 调用 `/chat/completions` 端点。初始化时接收 base_url、api_key、model 三个参数。invoke 方法发送同步请求并解析响应；stream 方法使用 SSE 流式读取，逐块 yield 文本内容。

### Anthropic 原生适配器

Phase 1 可选实现，如果用户需要直接调用 Claude API（非兼容端点）。使用 anthropic SDK 的 AsyncAnthropic 客户端，自动将 system message 分离为独立参数（Anthropic API 要求）。

## 多模型路由

### LLM Profile 配置

通过 `llm_profiles` 表存储模型配置，每条记录包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | str | 唯一标识 |
| name | str | 显示名称，如 "GPT-4o 写作" |
| provider | str | openai_compatible / anthropic |
| base_url | str? | OpenAI 兼容端点 URL |
| api_key | str | API Key（加密存储） |
| model | str | 模型 ID |
| task_type | str | plan / draft / audit / reflect / summarize / general |
| params | dict | temperature, max_tokens 等默认参数 |
| is_default | bool | 是否为该 task_type 的默认配置 |

### 任务类型定义

| task_type | 用途 | 推荐配置 |
|-----------|------|---------|
| `plan` | Planner 规划章节意图 | 强模型，temperature=0.7 |
| `draft` | Writer 生成章节内容 | 强模型，temperature=0.8，max_tokens=8000 |
| `reflect` | Reflector 提取状态 | 中等模型，temperature=0.3，JSON mode |
| `summarize` | 生成摘要 | 轻量模型，temperature=0.3 |
| `outline` | 大纲生成（雪花法各步） | 强模型，temperature=0.7 |
| `blueprint` | 蓝图生成 | 强模型，temperature=0.6 |
| `general` | 通用/兜底 | 中等模型 |

### 路由器实现

LLMRouter 按任务类型路由到对应的 LLM 适配器。路由逻辑：

1. 根据 task_type 从 llm_profiles 表查找默认配置
2. 如果没有专用配置，回退到 task_type="general" 的配置
3. 如果仍无配置，抛出 ConfigError
4. 根据 profile 的 provider 字段创建对应的适配器实例（带缓存，同一 profile 复用适配器）

路由器对外暴露 invoke 和 stream 两个方法，上层代码只需指定 task_type，无需关心具体模型。

## 通用工具

### 结构化输出提取

`extract_json` 工具函数：调用 LLM 获取结构化 JSON 输出，带重试和修复。流程：

1. 以 JSON mode 调用 LLM
2. 使用容错 JSON 解析（json_repair）处理不完美的输出
3. 用 Pydantic schema 校验结构
4. 如果解析或校验失败，将错误信息追加到对话中让 LLM 修复
5. 最多重试 2 次

### 重试与错误处理

LLM 调用统一使用指数退避重试策略：遇到超时或 HTTP 错误时，最多重试 2 次，每次延迟翻倍（基础延迟 1 秒）。

### Token 计数

用于洋葱模型的预算管理。粗略估算规则：中文约 1.5 字/token，英文约 0.75 词/token。

## API Key 安全

- API Key 在数据库中加密存储（使用 `cryptography.fernet`）
- 加密密钥通过环境变量 `ENCRYPTION_KEY` 提供
- API 响应中 Key 只返回掩码版本（`sk-***xxx`）
- Phase 1 单用户场景下安全要求适中，Phase 6 SaaS 时需升级为密钥管理服务
