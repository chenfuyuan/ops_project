## 1. 项目骨架与入口搭建

- [x] 1.1 创建 `app/business`、`app/capabilities`、`app/interfaces`、`app/shared`、`app/bootstrap` 五个顶层目录骨架
- [x] 1.2 建立 API 进程入口与基础应用装配入口
- [x] 1.3 建立 Worker 进程入口与任务应用装配入口
- [x] 1.4 为 `shared`、`interfaces`、`bootstrap` 建立最小可承接的子目录与模块占位

## 2. 基础设施基座接入

- [x] 2.1 建立统一配置加载与环境变量解析基座
- [x] 2.2 建立 PostgreSQL 连接管理与 SQLAlchemy 基础接入
- [x] 2.3 建立 Alembic 迁移基座与初始迁移结构
- [x] 2.4 建立 Redis 基础接入与缓存/协调的承接位置
- [x] 2.5 建立 Celery 应用配置、任务注册基座与 Worker 接线
- [x] 2.6 建立 S3-compatible Object Storage 客户端封装与对象引用承接基座

## 3. 边界与模块模板落地

- [x] 3.1 为 `business` 建立符合 `workflow/`、`nodes/`、`node.py / service.py / dto.py / entities.py / rules.py / ports.py / infrastructure/` 职责划分的模板结构
- [x] 3.2 为 `business/**/workflow` 建立最小骨架，并明确编排、注册、状态流转与实现细节的边界
- [x] 3.3 为 `workflow/state.py` 或等价状态模块补充高敏感边界说明，避免其演化为无边界全局上下文
- [x] 3.4 为 `capabilities` 建立无业务语义的最小能力结构模板
- [x] 3.5 为 `interfaces/http` 建立请求入口、路由组织与健康检查基础结构
- [x] 3.6 为 `shared/infra`、`shared/kernel`、`shared/events` 建立基础模块模板
- [x] 3.7 在 `bootstrap` 中集中定义依赖装配与实现选择边界，并避免把边界适配职责回流到 `shared/infra`

## 4. 治理与测试基线接入

- [x] 4.1 建立 import 方向约束或等价的架构检查机制
- [x] 4.2 建立针对 `service.py`、`workflow` 直接依赖实现细节的架构测试基线
- [x] 4.3 建立 `interfaces` 禁止直接依赖 `business/**/infrastructure/*` 的架构测试或等价检查
- [x] 4.4 建立 `capabilities` 禁止依赖 `business` 的架构测试或等价检查
- [x] 4.5 建立 `shared` 禁止引入业务语义模块的架构测试或等价检查
- [x] 4.6 建立 `shared`、`capabilities`、`workflow/state.py`、`business/**/ports.py`、`business/**/infrastructure/*` 的高敏感评审说明与准入清单
- [x] 4.7 建立单元测试、集成测试、端到端测试、架构测试的测试目录骨架
- [x] 4.8 补充目录命名、端口命名与基础设施实现命名规范的项目内说明
- [x] 4.9 建立 `uv + pyproject.toml + uv.lock` 的依赖与环境管理基线，固定 `Python 3.13`，统一 `uv sync` / `uv run` 约定，并按 `runtime / dev / test` 管理依赖分组

## 5. 最小可运行验证

- [x] 5.1 验证 API 进程可启动并暴露基础健康检查入口
- [x] 5.2 验证 Worker 进程可启动并加载任务应用配置
- [x] 5.3 验证配置、数据库迁移、Redis、对象存储等基础接入点可被装配，且未引入具体业务模型或业务逻辑
- [x] 5.4 验证治理检查与测试骨架可执行，并确认未引入具体业务实现、示例业务流程或示例业务表结构
