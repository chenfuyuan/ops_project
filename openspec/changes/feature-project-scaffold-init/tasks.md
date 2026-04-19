## 1. 项目骨架

- [x] 1.1 在 `app/` 下创建 `bootstrap`、`interfaces`、`shared`、`modules` 等顶层应用结构
- [x] 1.2 创建 `tests/unit`、`tests/integration`、`tests/e2e` 测试目录
- [x] 1.3 仅在必要位置添加占位文件，以保持预期的骨架边界

## 2. 启动装配与 HTTP 运行链路

- [x] 2.1 实现 `app/main.py` 作为应用入口
- [x] 2.2 实现 `app/bootstrap/` 下的装配文件，使应用创建与路由注册集中在装配层
- [x] 2.3 在 `app/interfaces/http/` 下建立 HTTP 路由结构并注册健康检查接口
- [x] 2.4 添加请求上下文中间件占位，但不引入任何业务相关行为

## 3. 共享基础与模块模板

- [x] 3.1 在 `app/shared/kernel/` 下添加稳定横切基础能力的最小占位文件
- [x] 3.2 在 `app/shared/infra/` 下添加配置、日志等非业务基础能力的最小占位文件
- [x] 3.3 编写 `app/modules/README.md`，明确模块边界规则与公开 API 约束
- [x] 3.4 添加可复用的模块模板，包含 `api/`、`application/`、`domain/`、`infrastructure/` 与 `module.py`

## 4. 项目配置与验证

- [x] 4.1 添加约定基础栈所需的项目配置文件，包括 `pyproject.toml` 与 `.env.example`
- [x] 4.2 添加本地运行所需的开发入口文件，如 `README.md`、`Makefile` 与最小辅助脚本
- [x] 4.3 添加应用启动与健康检查的最小验证覆盖
- [x] 4.4 验证骨架在未配置数据库的情况下可以成功启动
