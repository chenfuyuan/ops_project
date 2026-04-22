---
title: Phase 4 — 去 AI 化规则引擎与 AI 检测评分
version: 1.0
date: 2026-04-20
---

# 去 AI 化规则引擎 (AntiAIRulesEngine)

## 概述

AI 生成文本有明显的"AI 味"：高频使用特定词汇、句式单调、缺乏个性化表达。本模块维护中英文分别的疲劳词表和禁用句式库，在写作前注入规则（预防）、写作后检测评分（检查），双管齐下降低 AI 痕迹。

## 疲劳词表

### 中文疲劳词表

高频疲劳词（AI 极度偏爱，几乎每章都会出现）：不禁、竟然、居然、缓缓、淡淡、微微、嘴角微扬、眼中闪过一丝、心中一动、暗自思忖、不由得、下意识、情不自禁、若有所思、一股强大的气息、浑身一震、目光如炬、嘴角勾起一抹、深吸一口气、眉头微皱、眼神中透露出、一抹不易察觉的、嘴角露出一丝、心中暗道、脸上露出、不由自主、心头一紧。

中频疲劳词（偶尔使用可以，但 AI 倾向于过度使用）：宛如、犹如、仿佛、恍若、好似、霎时间、刹那间、顷刻间、转瞬之间、一时间、与此同时、紧接着、随即、显然、毫无疑问、不言而喻、众所周知、值得一提的是、令人意想不到的是、内心深处、灵魂深处、骨子里。

### 英文疲劳词表

高频疲劳词（AI 英文写作的标志性表达）：couldn't help but, a sense of, it was as if, little did they know, a wave of, sent shivers down, the weight of, a flicker of, in the blink of an eye, a mix of emotions, the air was thick with, a newfound sense of, the realization hit, an overwhelming sense of, a surge of, the silence was deafening, time seemed to stand still, a knowing smile, exchanged a glance, the gravity of the situation, a palpable tension, steeled himself, squared her shoulders.

中频疲劳词：moreover, furthermore, nevertheless, nonetheless, it is worth noting, needless to say, in the grand scheme of things, at the end of the day, a testament to, served as a reminder, the irony was not lost on, for better or worse, unbeknownst to, much to his chagrin, with bated breath, against all odds.

## 禁用句式模式

### 中文禁用句式

| ID | 名称 | 描述 | 严重度 | 修改建议 |
|---|---|---|---|---|
| zh_consecutive_same_start | 连续相同句首 | 连续 3 句以相同词语开头 | high | 变换句首词语，避免机械重复 |
| zh_excessive_de | 过度使用"的"字结构 | 单句中出现 4 个以上"的" | medium | 精简"的"字结构，使用动词或其他句式替代 |
| zh_template_transition | 模板化过渡句 | 使用 AI 典型的过渡句式（如"就在这时""话音刚落""正当…之际"等） | medium | 用更自然的方式衔接场景 |
| zh_emotion_tell | 直白情感陈述 | 直接告诉读者角色的情感而非展示（如"他感到十分悲伤"） | medium | 通过动作、表情、内心独白展示情感，而非直接陈述 |
| zh_list_three | 三连排比滥用 | AI 偏爱的三段式排比 | low | 减少排比频率，或使用非三段式的排比 |

### 英文禁用句式

| ID | 名称 | 描述 | 严重度 | 修改建议 |
|---|---|---|---|---|
| en_passive_overuse | 过度使用被动语态 | 连续 2 句使用被动语态 | medium | Convert to active voice for more engaging prose |
| en_adverb_dialogue | 对话标签副词滥用 | 对话标签中使用副词（said softly, whispered quietly 等） | medium | Show emotion through action beats instead of adverb-laden dialogue tags |
| en_filter_words | 过滤词 | 使用不必要的感知过滤词（如 he felt that, she noticed that） | low | Remove filter words for more immersive prose |
| en_consecutive_ing | 连续 -ing 开头 | 连续句子以分词短语开头 | medium | Vary sentence openings; avoid consecutive participial phrases |

## 规则库数据结构

规则库存储在 `anti_ai_rules` 表中，支持用户自定义扩展。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | TEXT PK | 规则唯一标识 |
| novel_id | TEXT (nullable) | NULL 表示全局规则，非 NULL 表示小说级覆盖 |
| language | TEXT | 语言标识："zh" 或 "en" |
| rule_type | TEXT | 规则类型："fatigue_word" 或 "banned_pattern" |
| category | TEXT | 严重度："high" / "medium" / "low" |
| content | TEXT | 疲劳词文本或正则表达式 |
| name | TEXT | 规则名称 |
| description | TEXT | 规则描述 |
| suggestion | TEXT | 修改建议 |
| is_builtin | INTEGER | 内置规则不可删除（默认 0） |
| is_enabled | INTEGER | 是否启用（默认 1） |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

索引：在 (novel_id, language, rule_type, is_enabled) 上建立复合索引，用于全局规则与小说级覆盖的合并查询。

### 规则加载逻辑

AntiAIRulesEngine 的 `load_rules` 方法按以下步骤加载规则集：

1. 加载全局规则（novel_id 为 NULL 的记录）
2. 加载小说级覆盖规则
3. 合并：小说级规则覆盖同 ID 的全局规则
4. 过滤已禁用的规则
5. 返回 RuleSet，包含按 category 分组的疲劳词列表和禁用句式列表

## 规则注入 Writer System Prompt

在 Composer 阶段将去 AI 化规则编入规则栈。`_build_anti_ai_prompt` 方法将规则集转为 Writer 可理解的自然语言约束：

- 高频疲劳词 → 生成"禁用词汇（绝对不要使用）"段落，列出词汇（限制注入数量上限 20 个）
- 中频疲劳词 → 生成"限用词汇（每章最多使用 1 次）"段落（限制注入数量上限 15 个）
- 禁用句式 → 生成"禁用句式"段落，每条包含名称、描述和修改建议

## AI 检测评分算法

### 评分模型

AI 检测评分衡量文本的"AI 味"程度，0-1 分（越低越好，0 = 完全无 AI 痕迹）。

AIDetectionScorer 是纯规则引擎，零 LLM 成本。评分流程：

1. 疲劳词检测 → FatigueScore
2. 禁用句式检测 → PatternScore
3. 重复表达检测（跨段落） → RepetitionScore
4. 句式多样性检测 → DiversityScore
5. 加权综合得出最终分数

加权权重：

| 维度 | 权重 |
|---|---|
| 疲劳词 (fatigue) | 0.35 |
| 禁用句式 (pattern) | 0.25 |
| 重复表达 (repetition) | 0.20 |
| 句式多样性 (diversity) | 0.20 |

综合分 > 0.5 时自动标记（flagged）。

### 疲劳词评分

检测疲劳词出现频率，按千字归一化计分：

- 高频疲劳词每出现 1 次（每千字）+0.05
- 中频疲劳词每出现 1 次（每千字）+0.02
- 上限 1.0

返回 FatigueScore，包含总分和匹配列表（每项含词语、出现次数、严重度分类），按出现次数降序排列。

### 禁用句式评分

通过正则匹配检测禁用句式，按严重度加权计分：

| 严重度 | 每匹配 1 次加分 |
|---|---|
| high | +0.10 |
| medium | +0.05 |
| low | +0.02 |

上限 1.0。返回 PatternScore，包含总分和匹配列表（每项含句式 ID、名称、匹配次数、严重度、最多 3 个匹配示例）。

### 重复表达评分

检测跨段落的重复表达。AI 倾向于在不同段落使用相同的描述模式。

算法：提取所有段落的 3-gram 和 4-gram，统计出现 3 次以上的 n-gram。评分 = 重复 n-gram 总出现次数 / 总 n-gram 数量，乘以放大系数 10，上限 1.0。段落少于 3 段时返回 0 分。

返回 RepetitionScore，包含总分和重复短语列表（最多 10 个，按出现次数降序）。

### 句式多样性评分

检测句式多样性。低多样性 = 高 AI 痕迹。从三个维度衡量：

| 维度 | 权重 | 计算方式 |
|---|---|---|
| 句首词多样性 | 0.4 | 不重复句首数 / 总句数 |
| 句长变异系数 | 0.3 | 标准差 / 均值，归一化到 0-1（除以 0.8） |
| 标点多样性 | 0.3 | 中文：不同标点种类数 / 10；英文：种类数 / 8 |

三维度加权求和得到多样性分，AI 检测分 = 1 - 多样性分（多样性越高，AI 分越低）。句子少于 5 句时返回 0 分。

## 综合结果模型

AIDetectionResult 包含以下字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| score | float | 综合 AI 检测分 0-1（越低越好） |
| fatigue | FatigueScore | 疲劳词评分 |
| pattern | PatternScore | 禁用句式评分 |
| repetition | RepetitionScore | 重复表达评分 |
| diversity | DiversityScore | 句式多样性评分 |
| flagged | bool | score > 0.5 自动标记 |
| details | dict | 详细信息 |

## 章节自动标记

AI 检测评分高于阈值的章节自动标记，在前端显示警告。PostChapterPipeline 中，当 `ai_score.flagged` 为 true 时，通过 EventBus 发出 `ai_detection_warning` 事件，携带 novel_id、chapter_id、chapter_num、score 以及 top_issues（取前 3 个疲劳词命中和前 3 个句式问题）。

## 用户自定义规则

用户可以：

1. 禁用内置规则（设置 `is_enabled=0`）
2. 添加自定义疲劳词
3. 添加自定义禁用句式（正则表达式，添加时需验证正则合法性）
4. 在小说级别覆盖全局规则
5. 调整 AI 检测阈值

AntiAIRulesService 提供以下操作：

- `add_custom_word(novel_id, language, word, category)` — 添加自定义疲劳词
- `add_custom_pattern(novel_id, language, name, pattern, severity, suggestion)` — 添加自定义禁用句式，需验证正则表达式合法性
- `toggle_rule(rule_id, enabled)` — 启用/禁用规则
- `get_rule_library(novel_id, language)` — 获取完整规则库（含启用状态），返回按类型和严重度分组的规则列表及启用/禁用统计
