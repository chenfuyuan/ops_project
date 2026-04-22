---
title: Phase 4 — 风格指纹系统
version: 1.0
date: 2026-04-20
---

# 风格指纹系统 (StyleFingerprint)

## 概述

从用户提供的参考文本中提取风格特征，生成可量化的"风格指纹"，注入 Writer 的 system prompt，引导 LLM 模仿目标风格写作。每部小说可关联多个指纹，按需激活/停用。

## 风格指纹组成

指纹由两部分组成：统计指纹（纯计算，零 LLM 成本）+ LLM 风格指南（一次性 LLM 调用）。

### 1. 统计指纹 (StatisticalFingerprint)

从参考文本中提取的量化特征，用于后续漂移检测的基准线。包含以下维度：

**句长分布 (SentenceLengthDist)：**

| 字段 | 说明 |
|------|------|
| mean | 平均句长（字符数） |
| median | 中位句长 |
| std | 标准差 |
| percentiles | 分位数（10/25/50/75/90） |
| histogram | 按 bucket 分布：0-5, 6-10, 11-20, 21-30, 31-50, 50+ |

**段落特征 (ParagraphFeatures)：**

| 字段 | 说明 |
|------|------|
| mean_length | 平均段落长度（句数） |
| mean_char_length | 平均段落字符数 |
| std_length | 段落长度标准差 |
| short_ratio | 短段落占比（<=2 句） |
| long_ratio | 长段落占比（>=8 句） |

**词频特征 (WordFrequencyProfile)：**

| 字段 | 说明 |
|------|------|
| top_words | top-200 高频词（去停用词后）的归一化频率 |
| hapax_ratio | 仅出现一次的词占比（词汇丰富度指标） |
| type_token_ratio | 词种/词次比 |

**对话特征 (DialogueFeatures)：**

| 字段 | 说明 |
|------|------|
| dialogue_ratio | 对话文本占总文本的比例 (0-1) |
| avg_dialogue_length | 平均单句对话长度 |
| dialogue_density | 每千字对话次数 |
| tag_ratio | 带说话标签的对话占比 |

**节奏模式 (RhythmPattern)：**

| 字段 | 说明 |
|------|------|
| short_long_alternation | 短长句交替频率 (0-1) |
| burst_ratio | 连续短句（<=8字）出现的频率（动作/紧张场景指标） |
| flow_ratio | 连续长句（>=25字）出现的频率（描写/抒情指标） |
| sentence_length_autocorr | 句长自相关系数（衡量句长变化的平滑度） |

### 2. LLM 风格指南 (StyleGuide)

一次 LLM 调用，分析参考文本的文学风格特征，生成自然语言的写作指导。

| 字段 | 说明 |
|------|------|
| narrative_voice | 叙事视角与口吻 |
| sentence_style | 句式偏好描述 |
| vocabulary_tone | 用词风格与调性 |
| imagery_preference | 意象与修辞偏好 |
| pacing_style | 节奏风格 |
| dialogue_style | 对话风格 |
| raw_guide | 完整风格指南文本（直接注入 prompt） |

LLM 提取时要求从以上 6 个维度分析参考文本，并生成一段 200-300 字的综合风格指南，用"你应该..."的祈使句式，可直接作为写作指导注入 AI 写作系统。

## 指纹提取流程

StyleFingerprintExtractor 执行以下步骤：

1. 统计指纹提取（纯计算，毫秒级）：分句、分段、计算句长分布、段落特征、词频（去停用词后 top-200）、对话特征、节奏模式
2. LLM 风格指南提取（一次调用，~1000 tokens）：分析参考文本的文学风格，生成结构化风格描述

分句策略按语言区分：中文按句号/问号/叹号/省略号分句，英文按 . ! ? 分句。对话特征提取按语言使用不同的引号和说话标签模式。

## 数据库存储

style_fingerprints 表字段：

| 字段 | 说明 |
|------|------|
| id | 主键 |
| novel_id | 关联小说（外键） |
| name | 用户自定义名称，如"金庸风格"、"余华风格" |
| reference_text_hash | 参考文本 SHA256，用于去重 |
| statistical | StatisticalFingerprint 序列化（JSON） |
| style_guide | StyleGuide 序列化（JSON） |
| is_active | 是否激活（0=停用，1=激活） |
| reference_text_path | 参考文本文件路径（可选保留原文） |
| language | 语言（默认 zh） |
| created_at / updated_at | 时间戳 |

每部小说可有多个指纹，但同时只激活一个（通过唯一索引约束）。

## 注入 Writer System Prompt

风格指纹在 Composer 阶段注入规则栈，Writer 阶段生效：

1. 将 LLM 风格指南的 raw_guide 注入"风格指南"段落
2. 将关键统计特征转为自然语言约束注入"风格量化约束"段落，包括：
   - 句长约束：目标平均句长、中位数、长句上限
   - 段落约束：目标平均句数/段、短段落占比
   - 对话约束：目标对话比例、每千字对话次数
   - 节奏约束：根据 burst_ratio / flow_ratio / short_long_alternation 生成对应偏好描述

Writer System Prompt 注入位置在写作规则之后、写作要求之前，依次为：风格指南、风格量化约束、去 AI 化规则。

## 多指纹管理

### 使用场景

- 同一部小说不同阶段切换风格（如回忆章节用不同风格）
- 用户尝试多种风格后选定一种
- A/B 测试不同风格效果

### 操作逻辑

StyleFingerprintService 提供以下操作：

1. create：创建新指纹（自动提取），新建默认不激活
2. activate：激活指纹（同时停用该小说的其他指纹）
3. deactivate：停用指纹（小说回到无风格约束状态）
4. update_guide：手动编辑风格指南（用户微调 LLM 生成的指南）
5. re_extract：重新提取（参考文本更新后）

## 参考文本要求

- 最小长度：3000 字（中文）/ 2000 词（英文），低于此长度统计特征不可靠
- 推荐长度：10000-50000 字，覆盖多种场景（对话、描写、动作）
- 支持多段文本合并提取（如同一作者的多部作品片段）
- 参考文本不存入数据库正文，仅保存文件路径和 hash
