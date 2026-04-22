## MODIFIED Requirements

### Requirement: CI/CD 主文档必须与现有基线文档分层协作
系统 MUST 通过新增或重构一篇 CI/CD 主文档来承载阶段模型、默认门禁、可发布制品、受控部署边界与文档职责映射；同时 MUST 保持 `docs/release_change_and_rollback.md`、`docs/security_baseline.md`、`docs/deployment_environment_baseline.md` 各自专题职责不被吞并。对于应用代码的最小 CI 落地约束，系统 MUST 允许通过独立的下游 capability 进一步定义默认覆盖对象、最小流水线分层与阻断门禁，而不是继续把这些实践细节混写到主基线中。后续文档补充 MUST 采用定向联动方式，而不是由 CI/CD 主文档重写全部发布、安全、部署或应用代码实践内容。

#### Scenario: CI/CD 主文档作为治理中枢
- **WHEN** 团队查阅新增或重构后的 CI/CD 相关文档
- **THEN** 可以从主文档获得统一的 CI/CD 阶段与交付闭环定义
- **AND** 可以看到它与发布、安全、部署文档之间清晰的职责关系

#### Scenario: 现有专题文档职责保持稳定
- **WHEN** 团队补充发布、安全或部署文档
- **THEN** 这些文档仍各自负责专题基线
- **AND** 不会因为 CI/CD 主文档的引入而失去原有职责边界

#### Scenario: 应用代码最小 CI 实践以下游 capability 承接
- **WHEN** 团队需要把通用 CI/CD 主基线继续下沉为应用代码的最小 CI 实践
- **THEN** 可以通过独立 capability 定义覆盖对象、三层最小流水线模型与默认阻断门禁
- **AND** 不需要把这些下游实践细节继续回填到 CI/CD 主基线中
