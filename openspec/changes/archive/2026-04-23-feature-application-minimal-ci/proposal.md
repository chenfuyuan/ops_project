## Why

当前仓库已经通过 `cicd-baseline` 定义了平台中立的 CI/CD 治理边界，但仍缺少一层专门面向应用代码的最小 CI 实践定义，来回答默认覆盖哪些代码、最小分几层、哪些检查属于阻断项。现在补上这层约束，可以让后续 OpenSpec 文档与具体流水线实现稳定收敛到同一套应用代码准入模型，而不必在抽象原则和平台细节之间反复摇摆。

## What Changes

- 新增一个面向应用代码的最小 CI 实践 capability，用于定义默认覆盖范围、最小流水线分层、默认阻断门禁与平台中立映射边界。
- 在该 capability 中明确最小 CI 仅覆盖应用代码与其直接相关测试，不扩展到文档门禁、CD 或平台配置实现。
- 约束后续设计按“静态与结构校验层 / 测试校验层 / 可运行性与构建确认层”组织最小 CI 实践，而不是只给出一组未分层命令。
- 修改 `cicd-baseline` 的相关要求表达，明确它作为主基线负责通用治理边界，而应用代码最小 CI 实践作为下游能力承接更具体的落地约束。

## Capabilities

### New Capabilities
- `application-minimal-ci`: 定义应用代码默认应经过的最小 CI 实践，包括覆盖对象、三层最小流水线模型、默认阻断门禁与平台中立约束。

### Modified Capabilities
- `cicd-baseline`: 明确通用 CI/CD 主基线与应用代码最小 CI 实践之间的职责分层，避免将下游实践细节继续混写在主基线中。

## Impact

- OpenSpec change：新增 `specs/application-minimal-ci/spec.md`，并为 `cicd-baseline` 增加对应 delta spec。
- 文档治理：后续 `proposal.md`、`design.md`、`tasks.md` 将围绕应用代码 CI 最小实践展开，而不进入 CD 或平台配置。
- 仓库约束：后续实现将主要影响 `app/`、`tests/` 及其最小 CI 校验方式的定义，不改变外部 API 或运行时系统边界。
