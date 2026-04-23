# CLAUDE.md

本仓库将长期生效的 AI 编码指引统一放在 `ai_docs/` 中。

## 默认阅读顺序
在本仓库中工作时，进行非简单代码修改前，应优先阅读以下文件：

1. `ai_docs/00_readme.md`
2. `ai_docs/rules/architecture_rules.md`
3. `ai_docs/rules/naming_rules.md`
4. `ai_docs/rules/tech_stack_baseline.md`
5. `ai_docs/rules/testing_rules.md`
6. `ai_docs/rules/coding_style_rules.md`
7. `ai_docs/rules/review_checklist.md`
8. 在生成或重构业务层代码时，按需阅读 `ai_docs/examples/` 下的相关文件

## 如何使用 `ai_docs/`
- 将 `ai_docs/rules/` 视为默认长期生效的编码规则。
- 将 `ai_docs/examples/` 视为优先参考的实现模式。
- 当这些文件与较旧的重复说明同时存在时，优先使用这里的内容。
- 除非用户明确覆盖，否则生成代码时应遵循这些规则。

## OpenSpec 边界
- 不要把 `openspec/` 下的文档重复整理到 `ai_docs/`。
- 当 OpenSpec 工作流处于激活状态时，应将 `openspec/` 下的文档视为任务级上下文。
- `ai_docs/` 用于存放跨多个任务都稳定适用的 AI 指导信息。

## 实现要求
- 遵循 `app/business`、`app/capabilities`、`app/interfaces`、`app/shared`、`app/bootstrap` 下定义的架构边界。
- 保持业务核心文件不直接包含 SDK、HTTP client 和 ORM 实现细节。
- 使用业务定义的 `ports`，并在 `infrastructure/` 中提供适配器实现。
- 将运行时装配和实现选择集中放在 `bootstrap`。
- 使用 `uv` 作为依赖管理和命令执行的基线。

## 更新规则
当仓库约定发生变化时，更新 `ai_docs/` 中对应的文件，确保未来 AI 的工作持续与仓库约定保持一致。
