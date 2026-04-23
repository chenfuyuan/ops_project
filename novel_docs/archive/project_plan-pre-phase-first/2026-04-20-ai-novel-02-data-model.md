---
title: AI 长篇小说生成系统 — 数据模型与存储设计
version: 1.0
date: 2026-04-20
parent: 2026-04-20-ai-novel-00-overview.md
---

# 数据模型与存储设计

## 文档角色

本文档属于**总纲专题**，承载跨多个 phase 共享的数据模型与存储设计基线。

使用方式：
- 从总纲入口页按需进入
- 为多个 phase 的专题设计提供统一的数据与存储背景
- 不替代具体 phase overview 对阶段目标与范围的表达

## 存储策略

| 存储 | 用途 | 后续 SaaS 升级 |
|------|------|---------------|
| PostgreSQL | 所有结构化状态（SQLAlchemy 2.0 ORM，每模块独立模型） | 增加连接池 + 多租户隔离 |
| ChromaDB | 章节/知识向量 | → 托管向量数据库 |
| 文件系统 | 章节全文、中间产物大文本 | → 对象存储 (S3) |

## 表设计

### novels 表：小说主体信息

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| title | TEXT | 标题（必填） |
| premise | TEXT | 前提/梗概 |
| genre | TEXT | 类型（必填） |
| language | TEXT | 语言，默认 zh（zh / en） |
| theme_agent_id | TEXT | 关联的主题代理 |
| structure_config | JSON | 章节数、每章字数等结构配置 |
| autopilot_status | TEXT | 自动驾驶状态，默认 IDLE（IDLE / RUNNING / PAUSED / ERROR / COMPLETED） |
| autopilot_stage | TEXT | 运行中的具体阶段（MACRO_PLANNING / ACT_PLANNING / WRITING / AUDITING / PAUSED_FOR_REVIEW） |
| current_beat_index | INTEGER | 当前节拍索引，默认 0 |
| error_count | INTEGER | 错误计数，默认 0 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### novel_architecture 表：大纲（雪花法产物）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| novel_id | TEXT FK | 关联小说 |
| core_seed | TEXT | 核心种子 |
| world_building | TEXT | 世界观 |
| three_act_structure | JSON | 三幕结构 |
| checkpoint | TEXT | 断点恢复：last_completed_step |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### characters 表：角色

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| novel_id | TEXT FK | 关联小说 |
| name | TEXT | 角色名（必填） |
| surface_pursuit | TEXT | 表层追求 |
| deep_desire | TEXT | 深层欲望 |
| soul_need | TEXT | 灵魂需求 |
| arc_design | JSON | 弧线设计：初始→触发→认知失调→转变→终态 |
| relationship_web | JSON | 与其他角色的关系 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### character_states 表：角色状态历史

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| character_id | TEXT FK | 关联角色 |
| chapter_num | INTEGER | 章节号（0 = 初始状态） |
| items | JSON | 持有物品 |
| abilities | JSON | 能力列表 |
| physical_state | TEXT | 身体状态 |
| mental_state | TEXT | 心理状态 |
| location | TEXT | 当前位置（用于地理一致性审计） |
| relationships | JSON | 当前关系网快照 |
| key_events | TEXT | 本章关键事件 |
| created_at | TIMESTAMP | 创建时间 |

### chapter_blueprints 表：章节蓝图

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| novel_id | TEXT FK | 关联小说 |
| chapter_num | INTEGER | 章节号（与 novel_id 联合唯一） |
| title | TEXT | 章节标题 |
| positioning | TEXT | 角色/事件/主题定位 |
| core_function | TEXT | 核心功能：advance / twist / reveal |
| suspense_density | INTEGER | 悬念密度（1-5） |
| foreshadow_ops | JSON | 伏笔操作列表：植入/强化/收获 + 目标伏笔 ID |
| disruption_level | INTEGER | 认知颠覆度（1-5） |
| summary | TEXT | 一句话概要 |
| created_at | TIMESTAMP | 创建时间 |

### chapters 表：章节

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| novel_id | TEXT FK | 关联小说 |
| chapter_num | INTEGER | 章节号（与 novel_id 联合唯一） |
| title | TEXT | 章节标题 |
| content_path | TEXT | 文件系统中的全文路径 |
| status | TEXT | 状态，默认 draft（draft / audited / revised / final） |
| word_count | INTEGER | 字数 |
| source | TEXT | 来源，默认 ai（ai / human / mixed） |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### chapter_summaries 表：章节摘要

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| chapter_id | TEXT FK | 关联章节 |
| novel_id | TEXT FK | 关联小说 |
| chapter_num | INTEGER | 章节号 |
| summary | TEXT | 摘要内容（必填） |
| key_events | JSON | 事件描述列表 |
| characters_present | JSON | 出场角色 ID 列表 |
| state_changes | JSON | 状态变更列表（entity, field, from, to） |
| created_at | TIMESTAMP | 创建时间 |

### foreshadowing 表：伏笔台账

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| novel_id | TEXT FK | 关联小说 |
| description | TEXT | 伏笔描述（必填） |
| status | TEXT | 状态，默认 open（Phase 1: open/resolved；Phase 2+: open/progressing/deferred/resolved） |
| planted_chapter | INTEGER | 植入章节（必填） |
| resolved_chapter | INTEGER | 收获章节 |
| last_advanced_chapter | INTEGER | 最后推进章节 |
| related_characters | JSON | 关联角色 ID 列表 |
| notes | TEXT | 备注 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### fact_locks 表：事实锁

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| novel_id | TEXT FK | 关联小说 |
| fact_type | TEXT | 类型（必填）：FACT_LOCK / COMPLETED_BEATS / REVEALED_CLUES |
| content | TEXT | 事实内容（必填） |
| source_chapter | INTEGER | 来源章节（必填） |
| related_entity_id | TEXT | 关联的角色/地点/物品 ID |
| created_at | TIMESTAMP | 创建时间 |

### triples 表：知识图谱三元组

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| novel_id | TEXT FK | 关联小说 |
| subject | TEXT | 主语（必填） |
| predicate | TEXT | 谓语（必填） |
| object | TEXT | 宾语（必填） |
| source_chapter | INTEGER | 来源章节（必填） |
| tags | JSON | 标签列表 |
| confidence | REAL | 置信度，默认 1.0 |
| created_at | TIMESTAMP | 创建时间 |

### storylines 表：剧情线

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| novel_id | TEXT FK | 关联小说 |
| name | TEXT | 剧情线名称（必填） |
| description | TEXT | 描述 |
| storyline_type | TEXT | 类型，默认 main（main / sub_a / sub_b / sub_c） |
| status | TEXT | 状态，默认 active（active / stagnant / completed） |
| current_progress | TEXT | 当前进度 |
| last_advanced_chapter | INTEGER | 最后推进章节 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### tension_scores 表：张力评分

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| novel_id | TEXT FK | 关联小说 |
| chapter_id | TEXT FK | 关联章节 |
| score | REAL | 评分（0-10） |
| analysis | TEXT | 分析说明 |
| created_at | TIMESTAMP | 创建时间 |

### style_scores 表：风格评分

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| novel_id | TEXT FK | 关联小说 |
| chapter_id | TEXT FK | 关联章节 |
| voice_drift_score | REAL | 语音漂移分数（0-1，越高越一致） |
| ai_detection_score | REAL | AI 检测分数（0-1，越低越好） |
| details | JSON | 详细信息 |
| created_at | TIMESTAMP | 创建时间 |

### audit_issues 表：审计问题

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| novel_id | TEXT FK | 关联小说 |
| chapter_id | TEXT FK | 关联章节 |
| dimension | TEXT | 审计维度（必填） |
| severity | TEXT | 严重度（必填）：critical / warning / info |
| description | TEXT | 问题描述（必填） |
| resolved | INTEGER | 是否已解决，默认 0 |
| resolved_by | TEXT | 解决方式：auto / human |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### pipeline_artifacts 表：流水线中间产物

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| chapter_id | TEXT FK | 关联章节 |
| stage | TEXT | 阶段（必填）：plan / compose / draft / audit / revise / commit |
| input_json | JSON | 输入数据 |
| output_json | JSON | 输出数据 |
| llm_profile_used | TEXT | 使用的 LLM 配置 |
| token_usage | JSON | Token 用量（prompt_tokens, completion_tokens, total_tokens） |
| duration_ms | INTEGER | 耗时（毫秒） |
| created_at | TIMESTAMP | 创建时间 |

### theme_agents 表：主题代理配置

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| genre | TEXT | 类型（必填，可有多个同类型代理，如"都市玄幻"和"传统玄幻"） |
| language | TEXT | 语言，默认 zh |
| persona | TEXT | 写作人设 |
| rules | JSON | 写作规则列表 |
| world_rules | TEXT | 世界观约束 |
| taboos | JSON | 禁忌列表 |
| beat_templates | JSON | 节拍模板 |
| skills | JSON | 可插拔技能 ID 列表 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### theme_skills 表：主题技能

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| name | TEXT | 技能名称（必填） |
| description | TEXT | 描述 |
| content | JSON | 技能内容（规则、模板等） |
| applicable_genres | JSON | 适用类型列表 |
| created_at | TIMESTAMP | 创建时间 |

### ai_gateway_profiles 表：AI 模型配置

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 主键 |
| name | TEXT | 配置名称（必填） |
| provider | TEXT | 提供商（必填）：openai_compatible / anthropic / custom |
| base_url | TEXT | API 地址 |
| model | TEXT | 模型名称（必填） |
| task_type | TEXT | 任务类型（必填）：plan / draft / audit / reflect / summarize / general |
| params | JSON | 参数配置（temperature, max_tokens 等） |
| is_default | INTEGER | 是否默认，默认 0 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

## ChromaDB Collections

### chapter_vectors

章节文本分段后的向量索引，用于语义检索相关上下文。

- **分段策略：** 按段落或固定 token 数切分（~500 tokens/段）
- **元数据：** novel_id, chapter_num, segment_index, character_mentions
- **用途：** Composer 在 T3 层做向量召回

### knowledge_vectors

外部导入知识的向量索引。

- **来源：** 用户导入的参考资料（世界观设定文档、角色百科等）
- **元数据：** novel_id, source_file, category
- **用途：** 丰富上下文，特别是世界观相关的细节

## 洋葱模型上下文层级

| 层级 | 内容 | Token 预算 | 裁剪策略 |
|------|------|-----------|---------|
| T0（永不裁剪） | 事实锁、角色锚点（主要角色当前状态）、当前幕摘要、活跃伏笔（open + progressing） | ~4K | 始终全量注入 |
| T1（可压缩） | 知识图谱相关子网、近期幕摘要、剧情线状态、章节意图 | ~6K | 超预算时 LLM 压缩 |
| T2（动态水位线） | 最近 N 章全文（N 根据剩余预算动态调整） | ~15K | 从最远章开始裁剪 |
| T3（优先牺牲） | 向量召回结果 | 剩余预算 | 按相关度排序，从低到高裁剪 |

总预算目标：~30K tokens（为 LLM 输出留空间）。具体数值根据所用模型的上下文窗口动态调整。

## 文件系统结构

```
<project_root>/
  data/
    <novel_id>/
      chapters/
        chapter_001.md
        chapter_002.md
        ...
      artifacts/
        chapter_001/
          plan.json        -- 章节意图
          context.json     -- 上下文包
          rules.yaml       -- 规则栈
          trace.json       -- 输入追踪
          audit.json       -- 审计结果
          delta.json       -- 状态变更 Delta
        ...
      exports/
        novel_export.epub
  vectorstore/
    chroma/                -- ChromaDB 持久化目录
```

PostgreSQL 数据库通过 `shared/infra/db.py` 管理连接，DATABASE_URL 配置在 `.env` 中。
