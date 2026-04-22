# MVP Requirements Index

本页只负责维护 Phase 1 的需求索引、状态、优先级和依赖关系，详细边界统一放在对应的 requirement card 中。

| Requirement | Summary | Status | Priority | Dependencies | Card |
| --- | --- | --- | --- | --- | --- |
| Project scaffold | 建立 MVP 所需的工程与运行基础 | 待进入 change | P0 | 无 | [project-scaffold](requirements/project-scaffold.md) |
| LLM routing | 让创作流程可按任务接入和切换模型 | 待进入 change | P0 | project-scaffold | [llm-routing](requirements/llm-routing.md) |
| Outline generation | 把小说种子整理成可编辑的大纲流程 | 待进入 change | P0 | project-scaffold, llm-routing | [outline-generation](requirements/outline-generation.md) |
| Chapter blueprints | 将大纲拆成可逐章推进的蓝图单元 | 待进入 change | P0 | outline-generation | [chapter-blueprints](requirements/chapter-blueprints.md) |
| Chapter pipeline | 支持逐章生成与人工审核的主流程 | 待进入 change | P0 | chapter-blueprints, llm-routing | [chapter-pipeline](requirements/chapter-pipeline.md) |
| Memory baseline | 记录创作过程中持续可用的核心状态 | 待进入 change | P1 | chapter-pipeline | [memory-baseline](requirements/memory-baseline.md) |
| API surface | 暴露 MVP 所需的交互入口 | 待进入 change | P1 | chapter-pipeline, memory-baseline | [api-surface](requirements/api-surface.md) |
| Authoring workspace | 提供支持 MVP 流程的基础前端工作台 | 待进入 change | P1 | api-surface | [authoring-workspace](requirements/authoring-workspace.md) |
