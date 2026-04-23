# AI 文档

这个目录用于存放为在本仓库中工作的 AI 助手整理过的文档。

## 这里应该放什么
- 会影响生成代码方式的稳定规则。
- 对多个任务都持续有帮助的精简项目指引。
- 展示推荐实现风格的样例模式。

## 这里不应该放什么
- 临时任务笔记或一次性的调试上下文。
- 已经有足够精简 AI 版本时，再重复复制一份原始文档。

## 建议的 AI 阅读顺序
1. `rules/architecture_rules.md`
2. `rules/naming_rules.md`
3. `rules/tech_stack_baseline.md`
4. `rules/testing_rules.md`
5. `rules/coding_style_rules.md`
6. `rules/review_checklist.md`
7. 有样例时再阅读 `examples/README.md`

## 维护规则
当 `docs/` 中的源规则发生变化时，应同步更新这里对应的精简文件，确保 AI 使用的指引与仓库保持一致。
当 `docs/` 描述的是目标态架构或容器化方向时，AI 文档也应同步保留“当前仓库是否已存在对应工程产物”的事实边界，避免把未来状态误写成已落地能力。
