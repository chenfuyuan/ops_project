## Why

大纲生成 MVP 已经暴露出复杂业务 node 缺少渐进式架构演进规则的问题：多个独立业务行为开始堆积在单一 `service.py` 中，后续 AI 生成或重构代码时容易继续扩大这个模式。现在需要把业务 node 的轻量 DDD 演进规则，以及 pre_design / OpenSpec 流程必须考虑架构设计的要求，沉淀进 `ai_docs` 和 OpenSpec 产物，避免后续需求只按功能清单推进而忽略长期架构边界。

## What Changes

- 建立 business node 的渐进式轻量 DDD 演进规则：简单 node 保持轻量，复杂 node 按 `facade + application/use_cases + domain + infrastructure` 演进。
- 将演进触发依据定义为业务/领域复杂度信号，而不是单纯行数、方法数、类数量等数字阈值。
- 明确 `facade.py`、`application/use_cases/`、`domain/`、`infrastructure/`、`node.py` 在复杂 node 中的职责边界。
- 明确 repository 是领域模型/聚合的获取与保存边界，拆分应按业务资源或聚合，而不是按 ORM record、mapper、事务等技术细节主导。
- 将“pre_design / OpenSpec 流程必须显式考虑架构设计”的规则沉淀到 `ai_docs`，要求后续需求评估架构边界、演进路径和是否需要同步 AI 规范。
- 以后续 outline 重构作为首个应用对象，将当前 service-heavy 结构迁移到渐进式轻量 DDD node 结构。
- 不把整个 `novel_generate` 立即升级为 domain-level bounded context；只有多个 node 共享稳定领域模型、repository 或领域服务时再评估。

## Capabilities

### New Capabilities

- `node-architecture-evolution`: 定义业务 node 的渐进式轻量 DDD 演进能力，包括复杂度信号、目标结构、职责边界、AI 规范沉淀和 OpenSpec 架构设计检查要求。

### Modified Capabilities

- `outline-generation`: 调整大纲生成能力的内部架构要求，使 outline 作为首个复杂 node 应用 `facade + application/use_cases + domain + infrastructure` 结构；不改变现有 HTTP API、AI gateway 能力契约或大纲生成业务行为。

## Impact

- 影响 `ai_docs/rules/architecture_rules.md`：需要新增 business node 渐进式演进规则、复杂 node 目标结构和 OpenSpec 架构设计检查要求。
- 影响 `ai_docs/examples/`：需要新增或更新 node 演进、facade/use case、repository、workflow node 相关样例，避免后续 AI 继续模仿旧 `service.py` 单文件承载模式。
- 影响 `app/business/novel_generate/nodes/outline/`：后续实现阶段将迁移为轻量 DDD node 结构。
- 影响 `app/interfaces/http/outline.py` 与 `app/bootstrap/novel_generate.py`：后续实现阶段需要改为依赖新的 outline facade。
- 影响 outline 相关测试：需要调整单元测试边界到 use case / facade，并保留 HTTP 和 repository 集成测试。
- 可能影响架构测试：需要新增或调整测试以守护复杂 node 不继续向单一 `service.py` 堆积业务行为。
- 不新增外部运行时依赖，不改变现有数据库表、HTTP API 路径或 AI gateway capability 契约。
