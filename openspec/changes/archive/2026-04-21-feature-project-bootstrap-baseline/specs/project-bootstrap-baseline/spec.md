## ADDED Requirements

### Requirement: 项目初始化骨架必须定义工作流编排与节点模板
系统初始化方案 MUST 体现该项目作为工作流编排型后端的默认业务组织方式。`business` 下的骨架 MUST 为 `workflow/` 与 `nodes/` 预留承接结构，并明确 `workflow` 负责流程拓扑、节点注册与状态流转，`node.py` 负责节点入口适配，`service.py` 负责业务用例编排，`dto.py / entities.py / rules.py / ports.py / infrastructure/` 各自承担稳定职责。`workflow` MUST NOT 承载具体业务实现或直接依赖外部 SDK、ORM、HTTP client 与存储实现。

#### Scenario: 初始化方案定义 workflow 与 nodes 承接结构
- **WHEN** 团队根据初始化方案建立 `business` 内部骨架
- **THEN** 方案中包含 `workflow/` 与 `nodes/` 的承接结构，并能表达工作流编排与节点实现的职责分离

#### Scenario: workflow 层不直接承载实现细节
- **WHEN** 团队依据初始化方案设计 `workflow` 相关模块
- **THEN** `workflow` 只负责编排、注册和状态流转，而不直接依赖 SDK、ORM、HTTP client 或存储实现

#### Scenario: workflow state 被视为高敏感边界
- **WHEN** 团队设计 `workflow/state.py` 或等价状态模块
- **THEN** 方案中将其视为高敏感区域，并要求最小化跨节点共享状态，避免演化为无边界全局上下文

### Requirement: 项目初始化骨架必须建立固定顶层边界
系统初始化方案 MUST 建立以 `app/` 为根的固定顶层结构，并在该结构中明确区分 `business`、`capabilities`、`interfaces`、`shared` 与 `bootstrap` 五类模块边界。该要求 MUST 作为后续实现的默认准入约束，不得在初始化阶段以技术分层目录替代业务边界表达。

#### Scenario: 初始化骨架定义顶层目录
- **WHEN** 团队根据项目初始化方案创建工程骨架
- **THEN** 工程结构中存在 `app/business`、`app/capabilities`、`app/interfaces`、`app/shared` 与 `app/bootstrap` 五个顶层区域

#### Scenario: 新代码需要按边界归属进入顶层模块
- **WHEN** 后续实现需要新增模块或文件
- **THEN** 新增内容 MUST 按顶层语义边界归入对应区域，而不能以 `utils`、`common2`、`misc` 等模糊目录替代

### Requirement: 项目初始化骨架必须定义默认运行时拓扑
系统初始化方案 MUST 定义 `API 进程 + Worker 进程` 的默认运行时形态，并明确 PostgreSQL、Redis 与 S3-compatible Object Storage 的职责分工。初始化阶段 MAY 只建立基础接入点，但 MUST 保留后续实现这些运行时角色的清晰承接位置。

#### Scenario: 初始化方案包含 API 与 Worker 入口
- **WHEN** 团队按照初始化方案建立应用入口
- **THEN** 方案中同时包含 API 入口与 Worker 入口的承接方式

#### Scenario: 初始化方案明确基础设施职责
- **WHEN** 团队查阅初始化规格以接入基础设施
- **THEN** 可以明确区分 PostgreSQL 用于核心持久化、Redis 用于缓存与轻量协调、S3-compatible Object Storage 用于文件与产物存储

### Requirement: 业务边界必须通过 ports 与 infrastructure 防腐
系统初始化方案 MUST 规定业务对外部能力、外部系统和通用能力的接入通过 `ports + infrastructure` 模式完成。`service.py`、`rules.py`、`entities.py` 等业务核心文件 MUST NOT 直接依赖供应商 SDK、HTTP client、ORM 具体实现或 capability 的具体实现。

#### Scenario: 业务调用通用能力遵循边界链路
- **WHEN** 业务节点需要调用通用能力或外部依赖
- **THEN** 调用链路遵循 `service -> ports -> infrastructure`，而不是由业务核心文件直接依赖实现细节

#### Scenario: 初始化方案约束业务核心文件的直接依赖
- **WHEN** 团队依据初始化方案设计业务节点结构
- **THEN** 方案中明确禁止 `service.py` 直接依赖 SDK、HTTP client、ORM 或 capability 具体实现

### Requirement: 初始化方案必须建立基础设施接入基座
系统初始化方案 MUST 为配置加载、数据库迁移、异步任务、缓存和对象存储建立基础接入基座，但 MUST NOT 因此引入具体业务表结构、业务任务或业务对象模型。系统级基础设施能力 SHOULD 放入 `shared/infra`，运行时装配与实现来源选择 MUST 集中在 `bootstrap`，而业务侧与 capability 侧的 `infrastructure` MUST 分别承担边界适配、协议转换、数据映射与错误归一化职责。

#### Scenario: 初始化阶段建立无业务语义的接入基座
- **WHEN** 团队实现数据库迁移、Celery、Redis 或对象存储的初始化接入
- **THEN** 接入内容只包含通用基座与装配边界，不包含具体业务模型或业务流程逻辑

#### Scenario: 运行时实现选择集中在 bootstrap
- **WHEN** 团队需要区分本地、远端、mock 或不同 provider 的实现方式
- **THEN** 这些实现选择在 `bootstrap` 或边界适配区完成，而不是分散到业务代码中

### Requirement: 初始化方案必须同时定义治理基线
系统初始化方案 MUST 将治理要求视为初始化范围的一部分，至少覆盖 import 方向约束、架构测试、命名规范、测试分层与高敏感评审区域。治理要求 MUST 作为可执行约束进入后续实现，而不能仅作为非约束性建议保留。`interfaces` MUST NOT 直接依赖 `business/**/infrastructure/*`，`capabilities` MUST NOT 依赖 `business`，`shared` MUST NOT 引入业务语义模块，相关依赖禁令 MUST 有对应的架构测试或等价自动检查承接。

#### Scenario: 初始化方案定义架构测试关注点
- **WHEN** 团队根据初始化方案建立测试与检查机制
- **THEN** 方案中包含对依赖方向、`service.py` 直接依赖实现细节、`shared` 越界、`capabilities` 越界与 `interfaces` 越界等问题的架构测试要求

#### Scenario: 初始化方案标记高敏感评审区域
- **WHEN** 团队评审进入 `shared/`、`capabilities/`、`workflow/state.py`、`business/**/ports.py` 或 `business/**/infrastructure/*` 的变更
- **THEN** 这些变更按高敏感区域处理，并以更高标准检查边界与准入是否被破坏

#### Scenario: 关键依赖禁令可被自动检查
- **WHEN** 团队接入初始化阶段的治理机制
- **THEN** 至少可以检查 `interfaces` 不直接依赖业务侧 `infrastructure`、`capabilities` 不依赖 `business`、`shared` 不承载业务语义模块

### Requirement: 初始化范围不得扩展到非目标内容
系统初始化方案 MUST 明确限制范围，只覆盖项目骨架、运行时基线、基础设施接入点与治理护栏。系统 MUST NOT 在本 change 中引入具体业务域设计、CI/CD 流水线、云资源拓扑、详细运维 SOP 或未经确认的微服务拆分工作。

#### Scenario: 后续任务拆解保持在初始化边界内
- **WHEN** 团队根据该 change 继续生成设计或任务
- **THEN** 生成内容只包含项目骨架与基础接入点相关工作，而不包含业务实现或生产平台建设事项

#### Scenario: 初始化规格阻止范围漂移
- **WHEN** 有人试图将该 change 扩展为业务需求、部署体系或服务拆分设计
- **THEN** 规格可明确判定这些内容超出本 change 的目标与非目标边界
