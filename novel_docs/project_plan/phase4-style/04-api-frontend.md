---
title: Phase 4 — 新增 API 端点与前端变更
version: 1.0
date: 2026-04-20
---

# 新增 API 端点与前端变更

## 新增 API 端点

### 风格指纹 API

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/novels/{id}/style-fingerprints` | 分析参考文本，创建风格指纹 |
| `GET` | `/api/v1/novels/{id}/style-fingerprints` | 获取小说的所有风格指纹 |
| `GET` | `/api/v1/novels/{id}/style-fingerprints/{fp_id}` | 获取指纹详情（含完整统计数据和风格指南） |
| `PATCH` | `/api/v1/novels/{id}/style-fingerprints/{fp_id}` | 编辑风格指南（用户手动微调） |
| `POST` | `/api/v1/novels/{id}/style-fingerprints/{fp_id}/activate` | 激活指纹（同时停用其他指纹） |
| `POST` | `/api/v1/novels/{id}/style-fingerprints/{fp_id}/deactivate` | 停用指纹 |
| `POST` | `/api/v1/novels/{id}/style-fingerprints/{fp_id}/re-extract` | 重新提取指纹 |

创建指纹时提交名称和参考文本，响应包含完整的 StyleFingerprint（统计数据 + 风格指南）。统计数据包含句长分布（mean, median, std, percentiles）、段落特征（mean_length, short_ratio, long_ratio）、对话特征（dialogue_ratio, dialogue_density）。风格指南包含 narrative_voice 和 raw_guide。

列表接口返回摘要信息（id、name、is_active、language、created_at）。编辑接口支持修改 name 和 guide.raw_guide。激活某指纹时其他指纹自动停用。

### 风格评分 API

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/novels/{id}/style-scores` | 获取风格评分列表 |
| `GET` | `/api/v1/novels/{id}/style-scores/{chapter_id}` | 获取单章风格评分详情 |
| `GET` | `/api/v1/novels/{id}/style-scores/drift-warnings` | 获取漂移预警 |
| `PATCH` | `/api/v1/novels/{id}/drift-config` | 更新漂移配置 |

风格评分列表支持查询参数：chapter_start/chapter_end（按章节范围过滤）、flagged_only（仅返回被标记的章节）。每项包含 chapter_num、voice_drift_score、ai_detection_score、flagged 状态。列表响应附带 summary（平均漂移分、平均 AI 分、被标记章节数、总章节数）。

单章详情包含完整的漂移检测结果（统计模式三维度 + LLM 模式四维度 + 漂移段落列表）和 AI 检测结果（四维度分数 + 疲劳词命中列表 + 句式问题列表）。

漂移预警包含两类：chapter_drift（单章漂移超阈值）和 trend_deteriorating（最近 N 章风格持续下降）。每条预警含 severity、涉及章节、分数和 top_issues。

漂移配置支持修改 threshold、mode（statistical/llm/both）和 auto_rewrite 开关。

### 去 AI 化规则 API

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/anti-ai-rules` | 获取规则库 |
| `POST` | `/api/v1/anti-ai-rules` | 添加自定义规则 |
| `PATCH` | `/api/v1/anti-ai-rules/{rule_id}` | 启用/禁用规则 |
| `DELETE` | `/api/v1/anti-ai-rules/{rule_id}` | 删除自定义规则（仅 is_builtin=false） |

获取规则库支持查询参数：novel_id（获取小说级规则含全局合并结果）、language（按语言过滤）、rule_type（按类型过滤）。响应包含规则列表（每项含 id、novel_id、language、rule_type、category、content、name、description、suggestion、is_builtin、is_enabled）和 summary（total、enabled、disabled、builtin、custom 计数）。

添加自定义规则时，疲劳词提交 novel_id、language、rule_type="fatigue_word"、category、content；禁用句式额外提交 name、description、suggestion，content 为正则表达式。内置规则只能禁用不能删除。

## 前端变更

### 新增页面

#### 风格配置页 `/novels/:id/style`

小说级别的风格管理中心，包含三个 Tab：

**Tab 1：风格指纹**
- 当前激活的指纹卡片（高亮显示）
  - 名称、创建时间、语言
  - 关键统计数据摘要（平均句长、对话比例、词汇丰富度）
  - 风格指南预览（可展开查看完整内容）
  - 「编辑指南」按钮 → 弹出编辑器，可修改 raw_guide
  - 「停用」按钮
- 其他指纹列表
  - 每项显示名称、创建时间
  - 「激活」按钮、「删除」按钮
- 「新建指纹」按钮
  - 弹出对话框：输入名称 + 粘贴参考文本
  - 提交后显示加载状态（LLM 分析中）
  - 完成后展示提取结果预览

**Tab 2：去 AI 化规则**
- 规则统计卡片：总规则数、已启用、已禁用、自定义数
- 疲劳词列表（分高频/中频两组）
  - 每个词旁边有开关（启用/禁用）
  - 「添加自定义词」按钮
- 禁用句式列表
  - 每项显示：名称、描述、严重度标签、开关
  - 「添加自定义句式」按钮 → 弹出表单（名称、正则、严重度、建议）
- 语言切换（中文/英文）

**Tab 3：漂移配置**
- 漂移阈值滑块（0-1，默认 0.68）
- 检测模式选择（统计/LLM/双模式）
- 自动重写开关
- 标记漂移段落数量设置

#### 风格评分面板（写作工作台右栏新增 Tab）

写作工作台右栏新增「风格」Tab，展示当前章节的风格评分：

风格一致性区域：
- 漂移评分仪表盘（0-1 圆环图，绿/黄/红三色区间）
- 统计模式三维度条形图（句长 KL / 词频余弦 / 对话偏差）
- LLM 模式四维度雷达图（口吻 / 用词 / 节奏 / 意象）
- 漂移段落列表（如有）：段落序号 + 预览文本 + 问题标签 + 修改建议，点击跳转到编辑器对应位置

AI 检测区域：
- AI 检测分仪表盘（0-1 圆环图，绿=低AI味，红=高AI味）
- 四维度条形图（疲劳词 / 句式 / 重复 / 多样性）
- 疲劳词命中列表：词语 + 出现次数 + 严重度标签，点击高亮编辑器中所有出现位置
- 句式问题列表：问题名称 + 匹配次数，点击跳转到第一个匹配位置

#### 风格趋势图（项目仪表盘增强）

项目仪表盘新增风格趋势区域：

- 双轴折线图（ECharts）
  - 左 Y 轴：漂移评分（0-1，越高越好）— 蓝色实线
  - 右 Y 轴：AI 检测分（0-1，越低越好）— 红色实线
  - X 轴：章节号
  - 阈值参考线（漂移阈值 0.68 灰色虚线）
  - 被标记章节用红色圆点标注
- 统计卡片
  - 平均漂移分
  - 平均 AI 检测分
  - 被标记章节数
  - 漂移趋势（改善/稳定/恶化）

### 写作工作台增强

#### 漂移预警横幅

当章节生成完成后，如果检测到漂移，在编辑器顶部显示预警横幅，包含风格一致性评分、主要问题摘要，以及「查看详情」和「忽略」按钮。

#### AI 检测标记横幅

AI 检测分过高时显示横幅，包含检测评分、命中的疲劳词摘要，以及「查看详情」和「一键高亮疲劳词」按钮。

#### 编辑器内高亮

- 疲劳词高亮：在编辑器中用浅红色背景标记所有命中的疲劳词
- 漂移段落高亮：用浅黄色左边框标记漂移最严重的段落
- 高亮可通过工具栏按钮开关

### 实时 SSE 事件

风格相关的 SSE 事件（通过现有 EventBus 推送）：

| 事件类型 | 数据内容 | 触发时机 |
|---------|---------|---------|
| voice_drift_warning | novel_id, chapter_id, DriftReport | 漂移检测完成且超阈值 |
| ai_detection_warning | novel_id, chapter_id, score, top_issues | AI 检测分超阈值 |
| fingerprint_extracted | novel_id, fingerprint_id, name | 指纹提取完成 |
