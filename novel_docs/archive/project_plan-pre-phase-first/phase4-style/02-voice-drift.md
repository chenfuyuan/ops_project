---
title: Phase 4 — 语音漂移检测
version: 1.0
date: 2026-04-20
---

# 语音漂移检测 (VoiceDriftDetector)

## 概述

长篇小说生成过程中，LLM 的输出风格会逐渐偏离目标风格（"漂移"）。本模块提供双模式检测：统计模式（零 LLM 成本）和 LLM 模式（~500 tokens/章），在 PostChapterPipeline 中自动执行。漂移超阈值时触发定向重写建议，而非回滚整章。

## 双模式架构

VoiceDriftDetector 支持三种运行模式：statistical（纯统计）、llm（纯 LLM）、both（双模式）。

检测流程：

1. 根据 mode 参数决定执行哪些检测
2. 统计模式：纯数学计算，从三个维度衡量章节与指纹的统计距离
3. LLM 模式：调用 LLM 对比章节文本与风格指南的语义一致性
4. 双模式综合评分：统计 40% + LLM 60%（LLM 对语义风格更敏感）
5. 综合分低于阈值则判定为漂移

检测结果包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| combined_score | float | 综合评分 0-1（1=完全一致，0=完全偏离） |
| statistical | StatDriftScore / None | 统计模式评分 |
| llm | LLMDriftScore / None | LLM 模式评分 |
| is_drifted | bool | combined_score < threshold |
| drifted_paragraphs | list | 漂移最严重的段落列表 |

漂移配置字段：

| 字段 | 默认值 | 说明 |
|------|--------|------|
| threshold | 0.68 | 低于此值视为漂移，触发重写建议 |
| mode | "both" | 检测模式："statistical" / "llm" / "both" |
| stat_weight | 0.4 | 统计模式权重 |
| llm_weight | 0.6 | LLM 模式权重 |
| auto_rewrite | false | 是否自动触发重写（默认仅建议） |
| paragraph_drift_top_n | 3 | 标记漂移最严重的 N 个段落 |

## 模式一：统计模式（零成本）

纯数学计算，无 LLM 调用。从三个维度衡量当前章节与风格指纹的统计距离。

### 1. 句长分布 KL 散度

计算章节句长分布与指纹句长分布的 KL 散度。将句长按 bucket（0-5, 6-10, 11-20, 21-30, 31-50, 50+）构建直方图，归一化为概率分布（加 Laplace 平滑避免零概率），计算 KL(P || Q)。映射到 0-1 分数（KL=0 → score=1，KL>=2 → score≈0）。

### 2. 词频余弦相似度

计算章节词频向量与指纹词频向量的余弦相似度。在参考词表的维度上构建向量，计算归一化后的余弦相似度，返回 0-1 分数。

### 3. 对话比例偏差

计算章节对话比例与指纹对话比例的绝对偏差，映射到 0-1 分数（偏差 0 → 1.0，偏差 >= 0.4 → 0.0）。

### 统计模式综合评分

三个维度加权平均：句长 KL 40% + 词频余弦 35% + 对话偏差 25%。

统计评分结果字段：

| 字段 | 说明 |
|------|------|
| score | 综合统计分 0-1 |
| kl_sentence_length | 句长 KL 散度分 |
| cosine_word_freq | 词频余弦相似度 |
| dialogue_deviation | 对话比例偏差分 |
| details | 各维度原始数值 |

## 模式二：LLM 模式（~500 tokens/章）

LLM 对比章节文本与风格指南的语义一致性，捕捉统计模式无法检测的风格偏移（如叙事口吻变化、修辞手法偏离）。

### LLM 提示词

System prompt 设定为专业文学风格一致性评审员。User prompt 包含目标风格指南和待评估章节（采样后的文本），要求从以下维度评估风格一致性（每个维度 0-1 分）：

1. voice_consistency：叙事口吻是否与风格指南一致
2. vocabulary_match：用词风格是否匹配
3. rhythm_match：句式节奏是否匹配
4. imagery_match：意象和修辞是否匹配
5. overall：综合评分

对于评分低于 0.7 的维度，要求指出具体偏离的段落和原因。输出为结构化 JSON，包含各维度分数和 deviations 列表（每项含 dimension、paragraph_index、description、suggestion）。

### 章节采样策略（控制 token 消耗）

采样章节文本控制在 ~400 tokens 以内。策略：首段 + 尾段 + 随机 3 个中间段 + 整体统计摘要。短章节（<=5 段）直接全文。

### LLM 评分结果字段

| 字段 | 说明 |
|------|------|
| score | overall 综合分 0-1 |
| voice_consistency | 叙事口吻一致性 |
| vocabulary_match | 用词匹配度 |
| rhythm_match | 节奏匹配度 |
| imagery_match | 意象匹配度 |
| deviations | 具体偏离项列表（含 dimension、paragraph_index、description、suggestion） |

## 漂移阈值与处理

### 阈值配置

默认阈值 0.68，可在小说级别覆盖（存入 novels 表的 structure_config JSON 或扩展字段）。

| 分数区间 | 含义 | 处理 |
|---------|------|------|
| 0.85-1.0 | 风格高度一致 | 无需处理 |
| 0.68-0.85 | 轻微偏移，可接受 | 记录但不告警 |
| 0.50-0.68 | 明显漂移 | 触发定向重写建议 |
| 0.30-0.50 | 严重漂移 | 强烈建议重写，标记为 warning |
| 0.00-0.30 | 风格完全偏离 | 建议整章重写，标记为 critical |

### 漂移处理：定向重写建议

漂移超阈值时，不回滚整章，而是识别漂移最严重的段落并给出具体调整建议。

DriftHandler 处理流程：

1. 判断是否漂移（is_drifted），未漂移则返回无需操作
2. 对每个段落（>=20 字）独立评分
3. 按漂移程度排序，取最严重的 top_n 个段落
4. 为每个漂移段落分析原因并生成建议（检查句长偏差、对话密度偏差等）
5. 生成 DriftReport，包含 severity（warning/critical）、漂移段落列表和人类可读摘要

漂移段落信息包含：段落序号、段落原文（截断到 200 字）、漂移分数、具体问题列表、调整建议列表。

## 集成 PostChapterPipeline

漂移检测在 PostChapterPipeline 的"分析评分"步骤中执行：

1. 获取小说的激活风格指纹
2. 如果存在指纹，执行漂移检测（根据配置的 mode）
3. 执行 AI 检测评分（见 03-anti-ai-rules.md）
4. 将漂移分数和 AI 检测分数持久化到 style_scores 表
5. 如果检测到漂移，生成 DriftReport 并通过事件总线通知前端（voice_drift_warning 事件）

## 漂移趋势追踪

除了单章检测，还需追踪跨章节的漂移趋势。DriftTrendAnalyzer 分析最近 N 章（默认 10 章）的漂移趋势：

1. 获取最近 N 章的漂移分数
2. 对分数序列做线性回归
3. 根据斜率判断趋势：
   - 斜率 < -0.02：风格一致性持续下降（deteriorating），建议检查风格指南是否需要更新
   - 斜率 > 0.02：风格一致性在改善（improving）
   - 其他：稳定（stable）
4. 数据不足 3 章时返回 insufficient_data
