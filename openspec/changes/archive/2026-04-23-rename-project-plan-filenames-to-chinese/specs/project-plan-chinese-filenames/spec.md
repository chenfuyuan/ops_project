## ADDED Requirements

### Requirement: 规划文档文件名必须完成中文化重命名
系统必须将 `novel_docs/project_plan/` 范围内纳入本次变更的英文文件名重命名为表达相同语义的中文文件名，并保持原有目录层级不变。

#### Scenario: 重命名 phase 总览与索引文件
- **WHEN** 执行本次文档重命名变更
- **THEN** `project_plan` 根目录、各 `phases/<phase>/` 目录以及各 `requirements/` 子目录中的目标文件必须从英文文件名改为对应中文文件名
- **THEN** 不得新增、删除或移动既有目录层级

#### Scenario: 保持 requirement card 集合不变
- **WHEN** 完成文件名重命名
- **THEN** 每个 phase 下已有 requirement card 的数量与语义边界必须保持不变
- **THEN** 不得借重命名之机新增新的需求卡片或移除既有需求卡片

### Requirement: 文档内部引用必须与新文件名保持一致
系统必须同步更新 `novel_docs/project_plan/` 内受影响的相对链接，使所有因文件名变更涉及的文档导航在重命名后仍可正确解析。

#### Scenario: 更新 overview 到 phase 文档的链接
- **WHEN** 根目录总览页引用各 phase 总览页
- **THEN** 相对链接必须指向重命名后的中文文件名

#### Scenario: 更新索引页到 requirement card 的链接
- **WHEN** `requirements.md` 或等效索引文档引用 requirement card
- **THEN** 相对链接必须指向对应的中文文件名
- **THEN** 链接文本可以保持既有中文业务名称，不要求与文件名完全一致

### Requirement: 本次变更不得扩展到文档内容重写
系统必须将本次变更限定为文件名与必要链接修正，不得引入超出命名一致性范围的内容重写、结构重组或实现设计扩展。

#### Scenario: 保持正文边界不变
- **WHEN** 完成本次变更后复查文档内容
- **THEN** 允许出现因链接更新带来的最小文本改动
- **THEN** 不得新增架构设计、任务拆解、数据模型或实现细节章节

#### Scenario: 保持 phase 与 requirement 关系不变
- **WHEN** 比较变更前后的 `project_plan` 规划结构
- **THEN** phase 顺序、requirement 归属关系与依赖描述必须保持原意不变
