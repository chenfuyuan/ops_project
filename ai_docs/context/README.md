# Context

这个目录用于存放任务阶段或阶段性工作的 AI 上下文。这类内容在一小段时间内有价值，但不适合沉淀为 `ai_docs/rules/` 中的长期规则。

## 这里应该放什么
- 当当前实现重点跨越多个相关任务时，对该重点的简洁总结。
- 在某个活跃阶段里，能帮助 AI 做出更好判断的临时项目上下文。
- 将多个源文档连接成一份简短 AI 可读任务上下文的整理说明。
- 比单个 prompt 更宽一些，但又不足以成为长期规则的短期 migration、refactor 或 rollout 背景。

## 这里不应该放什么
- 应该放在 `ai_docs/rules/` 中的稳定编码规则。
- 应该放在 `ai_docs/examples/` 中的标准实现模式。
- 原始会议记录、长对话文本或大段复制文档。
- 已经过期、不会再影响当前工作的任务笔记。

## 编写建议
这里的上下文文件应当：
- 简短
- 明确范围
- 明确为什么这份上下文重要
- 让 AI 能快速扫描理解

优先写简洁总结，而不是复制源材料。

## 建议的文件结构
一份 context 文件通常应包含：
- scope
- current objective
- constraints
- non-goals
- decisions already made
- 必要时附上源文档链接或路径

## 命名建议
使用能表达当前主题或阶段的名字，例如：
- `bootstrap_context.md`
- `refactor_context.md`
- `migration_constraints.md`

避免使用模糊名称，例如：
- `notes.md`
- `temp.md`
- `misc_context.md`

## 维护规则
当这些文件不再相关时，应删除或重写。这个目录应保持小而新。
