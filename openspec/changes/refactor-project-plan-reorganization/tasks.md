## 1. 归档旧规划资产

- [ ] 1.1 盘点 `novel_docs/project_plan/` 现有旧规划文档，并确定统一的 archive 目录结构与迁移范围
- [ ] 1.2 将旧的总览、架构、数据模型、专题设计和旧 phase 文档整体移动到独立 archive 位置，确保主路径不再保留双入口
- [ ] 1.3 校验归档后的旧文档仅作为历史参考存在，并在新主入口中避免继续把它们当作当前规划入口引用

## 2. 重建 project_plan 顶层路线图入口

- [ ] 2.1 重写 `novel_docs/project_plan/00-overview.md`，仅保留项目目标、phase 路线图、阅读路径与当前不做什么
- [ ] 2.2 新建或整理 `novel_docs/project_plan/phases/` 目录，使 phase 以稳定英文 slug 作为一级分组
- [ ] 2.3 检查顶层入口与目录命名是否符合“phase-first、无设计膨胀、无中文文件名、无序号需求卡片名”的约束

## 3. 为各 phase 建立轻量标准文档集

- [ ] 3.1 为每个目标 phase 创建或重构 `00-overview.md`，只表达 phase 目标、边界、进入标准、退出标准和 phase 关系
- [ ] 3.2 为每个目标 phase 创建或重构 `requirements.md`，只表达需求索引、状态、优先级、依赖关系与卡片链接
- [ ] 3.3 清理 phase 目录下不再符合新职责边界的设计型文档，确保 phase 目录只围绕概览、索引与需求卡片组织

## 4. 生成单需求卡片并建立未来 change 映射

- [ ] 4.1 按 phase 拆分出独立需求卡片，确保每张卡片聚焦单一需求边界
- [ ] 4.2 为每张 `requirements/<slug>.md` 补齐 Title、Goal、User Value、Success Criteria、Scope、Non-goals、Dependencies / Prerequisites 与 Notes
- [ ] 4.3 检查每张卡片是否足以作为未来单个 OpenSpec change 的上游输入，且未提前引入接口、数据模型、模块拆分或实现步骤

## 5. 整体验证与收口

- [ ] 5.1 通读 `novel_docs/project_plan/` 新结构，确认它已成为唯一前期规划入口，且新旧内容未在主路径混放
- [ ] 5.2 检查 overview、phase 文档、requirements 索引与单需求卡片之间的阅读路径是否清晰可导航
- [ ] 5.3 对照本 change 的 proposal、design 与 specs 自检，确认当前文档重整只完成需求整理职责，没有提前展开设计或任务拆解之外的内容
