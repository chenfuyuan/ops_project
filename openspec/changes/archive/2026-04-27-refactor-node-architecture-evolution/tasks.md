## 1. 更新 AI 架构规则

- [x] 1.1 更新 `ai_docs/rules/architecture_rules.md`，新增 business node 渐进式演进模型：简单 node、复杂 node 轻量 DDD、domain-level bounded context 三档。
- [x] 1.2 在 `ai_docs/rules/architecture_rules.md` 中明确复杂 node 目标结构：`facade.py`、`application/use_cases/`、`domain/`、`infrastructure/`、`node.py`。
- [x] 1.3 在 `ai_docs/rules/architecture_rules.md` 中明确演进判断以业务/领域职责信号为主，数字阈值只作为辅助提醒。
- [x] 1.4 在 `ai_docs/rules/architecture_rules.md` 中明确 repository 是领域模型/聚合的获取与保存边界，不按 ORM record、mapper、事务等技术细节主导拆分。
- [x] 1.5 在 `ai_docs/rules/architecture_rules.md` 中新增 pre_design / OpenSpec 流程必须显式考虑架构设计的规则。
- [x] 1.6 更新 `ai_docs/rules/review_checklist.md`，加入复杂 node 演进、facade/use case/domain/infrastructure 职责边界和 OpenSpec 架构设计检查项。

## 2. 更新 AI 样例文档

- [x] 2.1 新增 `ai_docs/examples/standard_node_evolution.md`，展示简单 node、复杂 node 轻量 DDD、domain-level bounded context 的演进判断和目录结构。
- [x] 2.2 新增或更新 facade/use case 样例，说明 `facade.py` 只做入口与横切协调，一个业务行为一个 use case。
- [x] 2.3 更新 `ai_docs/examples/standard_service.md`，避免其继续被理解为复杂 node 的唯一业务承载层；必要时标注为轻量 node 旧模式或替换为新的 facade/use case 模式。
- [x] 2.4 更新 `ai_docs/examples/standard_ports.md`，补充 domain repository 抽象与传统 port 的关系，以及 repository 按领域资源/聚合定义的规则。
- [x] 2.5 更新 `ai_docs/examples/standard_workflow_node.md`，说明 workflow-facing `node.py` 应调用 node facade，而不是直接深入 use case 或 infrastructure。
- [x] 2.6 更新 `ai_docs/examples/README.md`，加入新增/调整后的样例索引。

## 3. 建立 outline 复杂 node 目录结构

- [x] 3.1 在 `app/business/novel_generate/nodes/outline/` 下创建 `facade.py`、`application/`、`application/use_cases/`、`domain/`、`infrastructure/persistence/`、`infrastructure/ai/` 结构。
- [x] 3.2 将现有 command/response DTO 按职责迁移到 application 层，保持 HTTP 响应模型与现有 API 兼容。
- [x] 3.3 将 `Seed`、`Skeleton`、`SkeletonVolume`、`ChapterSummary`、`Outline`、状态枚举和值对象迁移到 `domain/models.py`。
- [x] 3.4 将 seed 完整性、skeleton 状态转换、outline 完整性判定等领域规则迁移到 `domain/rules.py`。
- [x] 3.5 将 `OutlineRepository` 等 repository 抽象迁移到 `domain/repositories.py`，保持按 outline 领域资源/聚合定义。
- [x] 3.6 明确 AI 生成 port 的放置方式，使 application/use case 只依赖抽象，不直接依赖 `app.capabilities`。

## 4. 拆分 outline 应用层 use cases 与 facade

- [x] 4.1 实现 `create_seed` use case，迁移创建结构化种子相关编排。
- [x] 4.2 实现 `get_seed` use case，迁移种子读取相关编排。
- [x] 4.3 实现 `generate_skeleton` use case，迁移 seed → skeleton 生成编排。
- [x] 4.4 实现 `confirm_skeleton` use case，迁移 skeleton 确认编排。
- [x] 4.5 实现 `expand_volume` use case，迁移 confirmed skeleton → chapter summaries 展开编排。
- [x] 4.6 实现 `update_volume` use case，迁移卷编辑和章节过期标记编排。
- [x] 4.7 实现 `update_chapter` use case，迁移章节摘要编辑编排。
- [x] 4.8 实现 `get_outline` use case，迁移完整大纲聚合读取编排。
- [x] 4.9 实现 `OutlineFacade`，对外暴露现有业务入口方法，负责依赖聚合、转发和必要横切协调，不承载具体业务规则。

## 5. 迁移 outline infrastructure 适配实现

- [x] 5.1 将 SQLAlchemy repository 实现迁移到 `infrastructure/persistence/outline_repository.py`，保持实现 `domain/repositories.py` 中的 `OutlineRepository` 抽象。
- [x] 5.2 在 persistence 实现内部保留或组织 ORM records、entity mapping 和事务逻辑，但不改变 repository 的领域边界。
- [x] 5.3 将 AI gateway adapter 迁移到 `infrastructure/ai/`，保持大纲业务 prompt、schema、响应映射位于 business outline node 内。
- [x] 5.4 确保 `capabilities/ai_gateway` 不新增 outline、chapter blueprint、chapter generation 等业务语义。
- [x] 5.5 更新 outline 包内 import，移除对旧 `service.py`、`entities.py`、`rules.py`、`ports.py` 路径的依赖。

## 6. 更新接口、装配与旧结构清理

- [x] 6.1 更新 `app/bootstrap/novel_generate.py`，装配 `OutlineFacade` 及其 use cases、repository、AI adapter。
- [x] 6.2 更新 `app/interfaces/http/outline.py`，使 HTTP 层依赖 outline facade 的稳定入口。
- [x] 6.3 保持现有 HTTP API 路径、请求/响应语义和错误映射不变。
- [x] 6.4 删除或迁移旧 `service.py`，不得保留继续承载业务逻辑的兼容壳。
- [x] 6.5 清理不再使用的旧平铺文件或导入路径，避免无意义 re-export。

## 7. 更新测试与架构守护

- [x] 7.1 调整 outline 单元测试，使业务行为测试落到 use case / facade 边界。
- [x] 7.2 保留并修正 outline HTTP integration 测试，确认外部 API 行为不变。
- [x] 7.3 保留并修正 outline repository integration 测试，确认持久化行为不变。
- [x] 7.4 保留并修正 outline AI adapter 测试，确认 STRUCTURED 请求、schema 和响应映射不变。
- [x] 7.5 新增或调整架构测试，守护 domain 不依赖 infrastructure/capabilities/HTTP/ORM/SDK。
- [x] 7.6 新增或调整架构测试，守护 capability 不吸收 outline 业务语义。
- [x] 7.7 评估是否新增复杂 node 禁止继续扩展单一 `service.py` 大泥球的架构测试；若不新增，需在实现说明中说明原因。

## 8. 验证

- [x] 8.1 运行 `uv run pytest tests/unit`，确认单元测试通过。
- [x] 8.2 运行 `uv run pytest tests/integration`，确认集成测试通过。
- [x] 8.3 运行 `uv run pytest tests/architecture`，确认架构测试通过。
- [x] 8.4 运行项目 CI 等价检查，确认重构和 AI 文档更新未破坏现有质量门禁。
- [x] 8.5 如具备明确授权、目标环境和命令，按项目规则执行 Docker / CD 验证；若会影响共享环境或需要凭证，先向用户确认。
