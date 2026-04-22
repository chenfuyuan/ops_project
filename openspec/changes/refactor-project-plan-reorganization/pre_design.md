# pre_design — novel_docs/project_plan 重整方案

## 1. Problem framing

当前 `novel_docs/project_plan/` 下的文档存在以下问题：

- 以“大而全的预设计”方式组织，过早进入架构、数据模型、模块拆分和阶段细节
- phase、专题设计、实现方向混杂在一起，阅读路径和使用边界不清晰
- 文档重心偏“提前定义解法”，而不是“先整理需求和边界”
- 如果继续沿用这套结构，后续很容易在真正开始需求之前就产生大量失真的设计文档

本次要解决的核心问题不是“继续补齐规划”，而是：

- 把现有规划资产降维整理为**路线图 + 需求拆分**结构
- 将“设计”延后到未来真正启动某个需求时再做
- 让 phase 成为路线图容器，而不是设计容器
- 让单个需求成为未来创建 change 的稳定起点

## 2. Why now

现在整理是必要的，因为：

- 当前文档已经开始影响后续思考方式，容易把项目继续推向“先设计完整系统，再找需求落点”
- 如果不尽快收敛结构，后续继续增量修改这些文档，只会让边界更混乱
- 现在正适合先建立一套更轻的需求整理方式，为未来按需进入 OpenSpec 做准备

## 3. Goals

本次整理的目标是：

1. 将 `novel_docs/project_plan/` 重建为清晰、轻量的前期规划入口
2. 按 **phase-first** 方式组织路线图
3. 在每个 phase 下按“一个需求一张卡片”进行拆分
4. 让需求卡片只表达目标、价值、边界、成功标准，不表达实现设计
5. 为未来按需创建 OpenSpec change 建立稳定映射关系

## 4. Non-goals

本次明确不做：

- 不提前创建 `openspec/changes/*`
- 不提前生成 `proposal.md`、`design.md`、`tasks.md`
- 不输出接口设计、数据模型设计、模块拆分设计
- 不在 phase 文档中继续保留“大设计总纲”
- 不试图一次性定义完整系统实现方案

## 5. Requirement understanding

这次工作的本质不是“写新规划文档”，而是“重建规划文档的职责边界”。

需求本身包含三层意思：

### 5.1 对旧文档的处理
现有 `novel_docs/project_plan/` 下的文档应视为旧规划资产，整体归档到独立的归档目录中，不再作为主入口继续维护。

归档要求：

- 旧文档必须统一移动到单独的 archive 位置
- 新结构不得与旧规划文档长期并存于同一主路径下形成双入口
- 归档后的旧文档仅作为历史参考，不再承担当前规划职责

### 5.2 对新结构的要求
新的 `project_plan` 仍然放在 `novel_docs/project_plan/` 下，但它应只承担：

- 项目路线图导航
- 按 phase 组织需求
- 按需求卡片承载边界定义

### 5.3 对未来工作方式的要求
未来真正开始某个需求时，再从单张需求卡片进入 OpenSpec，一张卡片对应一个 change，而不是现在提前铺开。

## 6. Constraints / Invariants

以下约束是后续整理时必须遵守的硬边界：

1. **phase 只是路线图分组，不是执行单元**
2. **真正的执行单元永远是未来的单个需求 change**
3. **`project_plan` 阶段只整理需求，不做设计**
4. **单张需求卡片必须能独立表达“要不要做、做什么、不做什么”**
5. **overview 页面只能作为导航，不得重新膨胀成总设计文档**
6. **不能重新把接口、数据、模块、流程实现细节提前写进去**
7. **旧文档必须统一归档到独立位置，不能与新结构在主入口下混放**

这些边界后续不能被推翻，否则会回到旧问题。

## 7. Architecture direction

推荐的整体结构方向是：

### 7.1 顶层采用 phase-first
`project_plan/` 下以 phase 为一级组织单位，表达路线图演进顺序。

### 7.2 phase 采用轻量标准文档集
每个 phase 只保留：

- `00-overview.md`
- `requirements.md`
- `requirements/<slug>.md`

### 7.3 单需求卡片作为未来 change 的前置载体
单张需求卡片是未来进入 OpenSpec 的最小稳定单元。

### 7.4 旧规划资产与新结构物理分离
旧规划文档必须统一归档到独立目录，新生成的 `project_plan` 结构只承载当前路线图与需求资产，避免新旧内容在同一主路径下混用。

## 8. Chosen structure

目标目录结构如下：

```text
novel_docs/project_plan/
├─ 00-overview.md
└─ phases/
   ├─ phase-1-mvp/
   │  ├─ 00-overview.md
   │  ├─ requirements.md
   │  └─ requirements/
   │     ├─ outline-generation.md
   │     ├─ blueprint-generation.md
   │     └─ chapter-pipeline.md
   ├─ phase-2-consistency/
   ├─ phase-3-narrative/
   ├─ phase-4-style/
   ├─ phase-5-automation/
   └─ phase-6-saas/
```

文件命名规则：

- phase 目录使用稳定英文 slug，如 `phase-1-mvp`
- 单需求卡片使用不带序号的英文 slug，如 `outline-generation.md`
- 不使用中文文件名
- 不使用序号 + slug 作为需求卡片名

## 9. File responsibilities

### 9.1 `project_plan/00-overview.md`
职责：

- 项目目标
- phase 路线图
- 阅读路径
- 当前不做什么

不应包含：

- 详细需求说明
- 实现设计
- 数据模型
- 接口设计
- 技术细节

### 9.2 `phases/<phase>/00-overview.md`
职责：

- phase 目标
- phase 边界
- 进入标准 / 退出标准
- 与其他 phase 的关系

不应包含：

- 单个需求的详细边界
- 设计解法
- 组件或模块细节

### 9.3 `phases/<phase>/requirements.md`
职责：

- phase 内需求索引
- 状态视图
- 优先级和依赖关系

推荐字段：

- Requirement
- Summary
- Status
- Priority
- Dependencies
- Card

### 9.4 `phases/<phase>/requirements/<slug>.md`
职责：

- 表达单个需求的边界定义

固定字段：

- Title
- Goal
- User Value
- Success Criteria
- Scope
- Non-goals
- Dependencies / Prerequisites
- Notes

不应包含：

- 接口方案
- 数据表设计
- 模块拆分
- 实现步骤
- 详细技术选型

## 10. Key decisions / Trade-offs

### 决策 1：不提前进入 OpenSpec
选择：现在不创建 change  
原因：如果现在就创建 change，会把“整理需求”再次拉回“提前设计”

放弃的替代方案：
- 直接把每个候选需求都提前建成 change
- 先产出 proposal/design/tasks 再筛选需求

### 决策 2：phase 只做路线图分组
选择：phase 不是执行单元  
原因：这样最能保证需求边界稳定，不会让 phase 重新变成大规格容器

放弃的替代方案：
- phase 本身作为强需求单元
- phase 和 change 混用

### 决策 3：需求卡片采用“边界卡片”
选择：只写目标/价值/边界/成功标准  
原因：足够支持未来进入 change，又不会滑向提前设计

放弃的替代方案：
- 只写一句话需求，信息太弱
- 直接写成准设计文档，信息太重

### 决策 4：旧文档整体归档
选择：旧规划资产退出主路径  
原因：避免双入口并存，防止团队继续把旧文档当当前规划基础

放弃的替代方案：
- 新旧长期并存
- 在旧文档上增量改造

## 11. Critical flows

### 11.1 当前阶段的工作流
旧规划资产整理 → 新建轻量 `project_plan` → 按 phase 拆需求 → 形成需求卡片库

### 11.2 未来需求启动流
从某个 `requirements/<slug>.md` 选中目标需求 → 再按需创建一个对应的 OpenSpec change → 在 change 中进入设计与任务拆解

### 11.3 明确禁止的流
先写完整设计 → 再找需求承接  
或  
先批量创建 change → 再回填需求边界

## 12. Success criteria

当以下条件满足时，说明这次整理是成功的：

1. `novel_docs/project_plan/` 成为唯一前期整理入口
2. phase 路线图清晰可导航
3. 每个需求都有独立卡片
4. 卡片内容能清楚表达目标和边界
5. 文档中没有提前展开实现设计
6. 未来可以自然地从单张卡片创建一个 change

## 13. OpenSpec mapping

虽然本次暂不进入 OpenSpec，但后续映射关系需要明确：

- 单张 `requirements/<slug>.md` 是未来创建单个 change 的上游输入
- 后续 `proposal.md` 负责表达“为什么做、改什么”
- 后续 `design.md` 负责表达“怎么做”
- 后续 `tasks.md` 负责表达“怎么拆执行”

当前 `project_plan` 阶段不承接这些职责。

## 14. Generation guardrails

后续无论谁整理这套文档，都必须遵守以下护栏：

### 必须遵守
- phase 是路线图容器
- 单需求卡片是最小边界单元
- 当前阶段只做需求整理，不做设计
- 一张需求卡片未来对应一个 change

### 允许补全
- 补充 phase 间关系说明
- 补充需求卡片的价值、边界和成功标准描述
- 调整需求在 phase 内的顺序和优先级

### 禁止补全
- 脑补实现方案
- 擅自定义接口和数据结构
- 在 overview 中写技术设计
- 在 `requirements.md` 中写任务拆解
- 把单需求卡片扩成设计文档

## 15. Final recommendation

推荐采用：

- `novel_docs/project_plan/` 作为唯一前期规划入口
- `phase-first` 作为结构主轴
- `lightweight requirement cards` 作为未来 change 的前置载体
- 设计延后到需求真正启动时再进入 OpenSpec

这套方案的核心价值不是“把文档写得更完整”，而是“让文档只承担它当前应该承担的职责”。
