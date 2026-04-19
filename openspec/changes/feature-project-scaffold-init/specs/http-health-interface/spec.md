## ADDED Requirements

### Requirement: HTTP 接口层暴露健康检查能力
系统必须在最小可运行骨架中提供 HTTP 健康检查接口。

#### Scenario: 健康检查接口返回成功响应
- **WHEN** 客户端请求配置好的健康检查路由
- **THEN** 系统必须返回表示应用正在运行的成功响应

### Requirement: HTTP 层保持为接口适配层
系统必须将 HTTP 相关职责限制在 `app/interfaces/http/` 中，并且不得在路由定义中嵌入业务模块内部实现。

#### Scenario: 路由处理保持稳定边界
- **WHEN** 脚手架注册 HTTP 路由
- **THEN** 路由层必须只处理路由、Schema、中间件等传输相关职责，而不能直接依赖模块内部的 application 或 infrastructure 代码

### Requirement: 请求上下文中间件具有明确扩展点
系统必须提供请求上下文中间件占位，使后续可以在不改变路由归属的前提下扩展跨请求元数据处理能力。

#### Scenario: 中间件占位存在但不承载业务行为
- **WHEN** 脚手架被创建
- **THEN** HTTP 中间件区域必须包含请求上下文扩展点，且其中不得编码任何业务特定逻辑
