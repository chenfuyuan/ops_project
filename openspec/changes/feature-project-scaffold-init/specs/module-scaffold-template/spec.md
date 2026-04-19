## ADDED Requirements

### Requirement: 模块脚手架定义标准模块布局
系统必须为未来模块提供 `app/modules/<module_name>/` 下的标准模块结构。

#### Scenario: 开发者基于模板创建新模块
- **WHEN** 开发者使用文档化的模块模板创建新模块
- **THEN** 新模块必须包含 `api/`、`application/`、`domain/`、`infrastructure/` 与 `module.py` 作为标准结构

### Requirement: 模块只暴露公开 API 边界
系统必须规定跨模块访问只能通过 `api/contracts.py` 与 `api/facade.py` 完成。

#### Scenario: 一个模块依赖另一个模块
- **WHEN** 某个模块需要调用另一个模块的能力
- **THEN** 调用方模块必须只依赖提供方模块的公开 API 边界，并且不得直接依赖其 `application/`、`domain/` 或 `infrastructure/` 内部实现

### Requirement: 初始骨架不包含示例业务模块
系统必须通过模板和文档来支持模块创建，而不是在初始骨架中附带示例业务模块。

#### Scenario: 初始骨架创建时不包含领域示例
- **WHEN** 初始项目骨架被生成
- **THEN** `app/modules/` 必须只包含未来模块创建所需的模板或文档，而不得包含带有领域行为的占位业务模块
