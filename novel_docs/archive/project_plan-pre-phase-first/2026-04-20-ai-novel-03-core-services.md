---
title: AI 长篇小说生成系统 — 核心服务详细设计
version: 1.0
date: 2026-04-20
parent: 2026-04-20-ai-novel-00-overview.md
---

# 核心服务详细设计

## 文档角色

本文档属于**总纲专题**，用于承载跨阶段复用的核心服务设计与服务边界说明。

使用方式：
- 从总纲入口页按需进入
- 为相关 phase 专题补充服务级设计背景
- 不替代具体 phase overview 或单个 topic 文档的职责

## 模块归属

各核心服务分布在不同业务模块中，模块间通过 facade 通信。

| 服务 | 所属模块 | 引入阶段 | 跨模块依赖 |
|------|---------|---------|-----------|
| MemoryEngine | `memory` | Phase 1 | 通过 facade 读取 novel、character、blueprint、chapter |
| ConsistencyChecker | `audit` | Phase 2 | 通过 facade 读取 character、blueprint、chapter |
| ForeshadowingManager | `blueprint` | Phase 1（基础）/ Phase 2（完整生命周期） | blueprint 模块内部 |
| ThemeAgentSystem | `narrative` | Phase 3 | 通过 facade 注入 chapter 流水线 |
| TensionAnalyzer | `narrative` | Phase 3 | 通过 facade 读取 chapter |
| StyleEngine | `style` | Phase 4 | 通过 facade 注入 chapter 流水线 |
| KnowledgeGraphService | `narrative` | Phase 3 | 通过 facade 读取 chapter |
| PostChapterPipeline | `chapter` | Phase 1 | chapter 模块内部 |

跨模块调用示例：MemoryEngine（memory 模块）需要角色数据时，调用 `character_facade.get_current_states(novel_id)` 而非直接查询 character_states 表。

## 1. 记忆引擎 (MemoryEngine) — `modules/memory/`

融合 InkOS 的真相文件理念和 PlotPilot 的事实锁 + 洋葱模型。

### 职责

- 管理小说的全部"记忆"：角色状态、事件历史、伏笔、剧情线、事实锁
- 为 Composer 提供分层上下文查询接口
- 执行洋葱模型的 token 预算分配和裁剪

### 事实锁机制

三类不可变约束，注入 T0 层（永不裁剪）：

**FACT_LOCK — 不可逆事实**
- 角色死亡、重大身份揭示、世界规则确立
- 一旦写入不可修改（除非人工强制覆盖）
- 示例：`{type: "FACT_LOCK", content: "张三在第45章战死", source_chapter: 45}`

**COMPLETED_BEATS — 已完成节拍**
- 已经发生过的剧情节拍，防止重复
- 示例：`{type: "COMPLETED_BEATS", content: "主角已获得火焰之剑", source_chapter: 23}`

**REVEALED_CLUES — 已揭示线索**
- 读者已知的信息，防止矛盾
- 示例：`{type: "REVEALED_CLUES", content: "读者已知反派是主角的父亲", source_chapter: 67}`

### 上下文查询接口

MemoryEngine 提供 `build_context` 方法，接收 novel_id、chapter_num 和 token_budget（默认 30000），按洋葱模型分层组装上下文：

1. 构建 T0 层：事实锁 + 角色锚点 + 活跃伏笔
2. 构建 T1 层：知识图谱 + 摘要 + 剧情线
3. 构建 T2 层：近章全文
4. 构建 T3 层：向量召回

最后按 token 预算裁剪各层，返回完整的上下文包（ContextPayload）。

## 2. 一致性检查服务 (ConsistencyChecker) — `modules/audit/`（Phase 2）

借鉴 InkOS 的多维审计，分阶段实现。

### 审计维度（按阶段引入）

**Phase 2 引入（核心 15 维）：**

| 维度 | 检查内容 | 严重度 |
|------|---------|--------|
| 角色记忆 | 角色不能"知道"未目睹的事件 | critical |
| 角色存活 | 已死亡角色不能出场（除非有合理解释） | critical |
| 物品连续性 | 物品不能凭空出现或消失 | critical |
| 能力连续性 | 角色能力变化需有合理来源 | critical |
| 时间线一致 | 事件时序不能矛盾 | critical |
| 伏笔追踪 | 已植入伏笔是否推进或停滞（>10 章未推进预警） | warning |
| 大纲偏离 | 章节内容是否偏离蓝图设定 | warning |
| 关系连续性 | 角色关系变化需有铺垫 | warning |
| 地理一致 | 角色位置移动需合理 | warning |
| 信息边界 | 角色间信息传递需有渠道 | warning |
| 叙事节奏 | 连续 3+ 章无实质进展 | warning |
| 事实锁违反 | 与已锁定事实矛盾 | critical |
| 已完成节拍重复 | 重复已发生的剧情 | critical |
| 已揭示线索矛盾 | 与读者已知信息矛盾 | critical |
| 字数达标 | 章节字数是否在目标范围内 | info |

**Phase 3 扩展：**
- 张力节奏检查（连续低张力预警）
- 支线停滞检测
- 情感弧线连续性

**Phase 4 扩展：**
- AI 痕迹检测
- 风格漂移检测
- 重复表达检测（跨章节）

### 审计-修订循环

```
Audit → 问题清单
  ├─ critical 问题 → Reviser 自动修订 → 重新 Audit（最多 3 轮）
  ├─ warning 问题 → 标记到 audit_issues 表，人工审核
  └─ info 问题 → 仅记录
```

3 轮后仍有 critical 问题 → 暂停流水线，通知人工介入。

## 3. 伏笔管理器 (ForeshadowingManager) — `modules/blueprint/`

融合 InkOS 的生命周期管理和 PlotPilot 的自动检测。

### 生命周期

```
open → progressing → resolved
  │                    ↑
  └→ deferred ─────────┘
```

- **open：** 刚植入，尚未推进
- **progressing：** 有后续章节推进或强化
- **deferred：** 主动延后（标记原因）
- **resolved：** 已收获/解决

### 自动检测

Reflector 在 Commit 阶段自动检测：
- 新伏笔植入 → 创建 foreshadowing 记录，status=open
- 已有伏笔推进 → 更新 status=progressing，last_advanced_chapter
- 伏笔收获 → 更新 status=resolved，resolved_chapter

### 停滞预警

定期检查（每章 Commit 后）：
- open 状态超过 10 章未推进 → warning
- open 状态超过 20 章未推进 → critical（可能被遗忘）
- progressing 状态超过 15 章未推进 → warning

预警信息注入 Planner 的输入，引导后续章节推进或收获。

## 4. 主题代理系统 (ThemeAgentSystem) — `modules/narrative/`（Phase 3）

借鉴 PlotPilot 的主题代理 + 可插拔技能设计。

### 代理结构

每个主题代理包含：
- **persona：** 写作人设（如"你是一位精通玄幻世界观构建的资深作者"）
- **rules：** 写作规则列表（如"战斗场景必须有力量体系的合理支撑"）
- **world_rules：** 世界观约束（如"修炼等级：练气→筑基→金丹→元婴→化神"）
- **taboos：** 禁忌列表（如"不要出现现代科技词汇"）
- **beat_templates：** 节拍模板（如"突破场景模板"、"宗门大比模板"）
- **skills：** 注册的可插拔技能

### 可插拔技能

技能是跨类型共享的专业知识模块：

| 技能 | 适用类型 | 内容 |
|------|---------|------|
| cultivation_system | 玄幻/仙侠/修仙 | 修炼体系设计规则、突破场景模板 |
| battle_choreography | 玄幻/武侠/都市 | 战斗编排规则、力量对比逻辑 |
| deduction_logic | 悬疑/推理 | 推理逻辑规则、线索布局模板 |
| emotion_pacing | 言情/都市 | 情感节奏控制、关系发展模板 |
| world_building_scifi | 科幻 | 科技设定一致性规则 |
| power_system | LitRPG/升级流 | 数值体系、升级逻辑 |

### 注入时机

主题代理的规则在 Writer 阶段注入：
1. Composer 将主题代理规则编入规则栈（rule stack）
2. Writer 的 system prompt 包含 persona
3. Writer 的 user prompt 包含 rules + world_rules + taboos
4. 匹配到的 beat_template 作为额外指导注入

## 5. 张力分析器 (TensionAnalyzer) — `modules/narrative/`（Phase 3）

借鉴 PlotPilot 的张力评分系统。

### 评分维度

每章评分 0-10，综合考虑：
- 冲突强度（角色间/角色与环境/内心冲突）
- 悬念密度（未解决的问题数量）
- 信息揭示（新信息的重要程度）
- 情感波动（角色情感变化幅度）
- 节奏变化（与前章的对比）

### 预警规则

- 连续 3 章张力 < 3 → warning（节奏拖沓）
- 连续 3 章张力 > 8 → warning（读者疲劳）
- 张力曲线无波动（标准差 < 1）→ warning（节奏单调）

### 可视化

前端展示历史张力曲线（"心电图"），帮助作者直观感受节奏。

## 6. 风格引擎 (StyleEngine) — `modules/style/`（Phase 4）

融合 InkOS 的去 AI 化规则和 PlotPilot 的语音漂移检测。

### 风格指纹

从参考文本提取：
- 统计特征：句长分布、词频、段落长度、对话/叙述比例
- LLM 风格指南：用 LLM 分析参考文本的风格特点，生成写作指导

### 去 AI 化规则

内置规则库（中英文分别维护）：

**中文疲劳词表示例：**
"不禁"、"竟然"、"居然"、"缓缓"、"淡淡"、"微微"、"嘴角微扬"、"眼中闪过一丝"

**英文疲劳词表示例：**
"couldn't help but"、"a sense of"、"it was as if"、"little did they know"

**禁用句式模式：**
- 连续 3 句以相同结构开头
- 过度使用"的"字结构（中文）
- 过度使用被动语态（英文）

### 语音漂移检测

双模式：
- **统计模式（零成本）：** 计算当前章与风格指纹的统计距离（句长分布 KL 散度、词频余弦相似度）
- **LLM 模式（~500 tokens/章）：** LLM 对比当前章与风格指南的一致性

漂移阈值：0.68（可配置）。低于阈值时触发定向重写建议，而非回滚整章。

## 7. 知识图谱服务 (KnowledgeGraphService) — `modules/narrative/`（Phase 3）

借鉴 PlotPilot 的三元组提取。

### 三元组结构

```
(主语, 谓语, 宾语) + 来源章节 + 标签 + 置信度
```

示例：
- `(张三, 持有, 火焰之剑)` chapter=23, tags=["物品"], confidence=1.0
- `(李四, 暗恋, 王五)` chapter=15, tags=["关系","情感"], confidence=0.8
- `(黑风寨, 位于, 青云山北麓)` chapter=5, tags=["地理"], confidence=1.0

### 信息边界查询

支持查询"角色 X 在第 N 章时知道什么"：
1. 查找角色 X 在 ≤N 章出场的所有章节
2. 收集这些章节中角色 X 在场时产生的三元组
3. 排除角色 X 不在场时发生的事件

这对一致性审计的"角色记忆"维度至关重要。

### 冲突检测

新三元组写入时检查是否与已有三元组矛盾：
- `(张三, 持有, 火焰之剑)` vs `(张三, 失去, 火焰之剑)` → 需要确认时序
- `(黑风寨, 位于, 青云山北麓)` vs `(黑风寨, 位于, 南海之滨)` → 矛盾

## 8. 章后统一管线 (PostChapterPipeline) — `modules/chapter/`

借鉴 PlotPilot 的核心设计：无论人写还是 AI 写，同一套后处理。

### 触发条件

章节内容确认后（无论来源是 AI 生成、人工编写、还是人工编辑后的 AI 草稿），统一执行。

### 管线步骤

```
1. Reflector 提取 → JSON Delta
   - 章节摘要
   - 角色状态变更
   - 新伏笔 / 伏笔推进 / 伏笔收获
   - 知识图谱三元组
   - 事实锁候选（需人工确认或自动规则判定）

2. Schema 校验 → Pydantic 验证 Delta 合法性

3. 状态持久化
   - 写入 chapter_summaries
   - 更新 character_states（新增一条记录，不修改历史）
   - 更新 foreshadowing
   - 写入 triples
   - 写入 fact_locks（如有）

4. 向量索引 → 章节文本分段入 ChromaDB

5. 分析评分
   - 张力评分 → tension_scores
   - 风格评分 → style_scores（Phase 4）

6. 剧情线更新 → 检查 storylines 进度，标记停滞
```

### 幂等性

管线设计为幂等——对同一章节重复执行不会产生重复数据。通过 chapter_id + chapter_num 做唯一约束，重复执行时先清除旧数据再写入。
