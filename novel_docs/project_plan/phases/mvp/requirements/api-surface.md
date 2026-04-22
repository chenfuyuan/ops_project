# MVP API 入口

## Goal

为小说项目创建、大纲生成、蓝图管理、章节产出和状态读取提供一致的应用入口，支撑前端或其他调用方使用 MVP 能力。

## User Value

MVP 不会被局限在脚本式操作中，团队可以围绕稳定入口构建页面、测试和后续工作流。

## Success Criteria

- MVP 核心流程都具备可被调用的入口需求。
- 调用入口的边界与业务需求对应，而不是直接泄露实现细节。
- 该卡片可以作为未来单个 change 的上游输入。

## Scope

- 小说项目与创作流程的主要交互入口
- 面向前端或其他调用方的能力暴露需求
- 与创作状态读取相关的最小访问要求

## Non-goals

- OpenAPI 设计细节
- 鉴权与多租户模型
- 自动化控制接口

## Dependencies / Prerequisites

- [chapter-pipeline](chapter-pipeline.md)
- [memory-baseline](memory-baseline.md)

## Notes

- 未来 change 应把“哪些能力需要对外暴露”拆成明确接口契约。
- 历史参考：[`phase1-mvp/07-api-endpoints.md`](../../../../archive/project_plan-pre-phase-first/phase1-mvp/07-api-endpoints.md)
