## Why

`novel_docs/project_plan/` 当前大量文件名仍使用英文 slug，和文档正文的中文语境不一致，也提高了人工浏览、检索与目录理解成本。现在先将该目录下的文件名统一替换为中文，能让这套项目规划材料更贴近实际阅读方式，并为后续继续维护中文规划入口打下基础。

## What Changes

- 将 `novel_docs/project_plan/` 下现有英文文件名按语义重命名为中文文件名。
- 同步更新 `project_plan` 目录内因文件重命名而受影响的相对链接引用。
- 保持当前目录结构、文档内容边界与 phase/requirement 卡片关系不变，仅调整命名与引用一致性。
- 不在本次变更中新增规划内容、重写文档结构或引入新的 OpenSpec 实现需求。

## Capabilities

### New Capabilities
- `project-plan-chinese-filenames`: 规范 `novel_docs/project_plan/` 规划文档使用中文文件名，并要求相关内部引用在重命名后保持可用。

### Modified Capabilities
- 无

## Impact

- 影响目录：`novel_docs/project_plan/`
- 影响内容：各 phase 总览、requirements 汇总页、requirement card 之间的相对链接
- 影响系统：文档导航、人工检索与后续基于该目录继续生成规划材料的流程
- 不涉及运行时代码、API、依赖升级或外部系统变更
