## Why（为什么现在做）

当前仓库仍接近空白状态，缺少一个既能最小运行、又能长期保持模块边界清晰的项目起点。如果现在只追求快速启动而不先固定结构，后续新增模块时很容易退化为普通分层单体，因此需要先完成一次边界优先的骨架初始化。

## What Changes（变更内容）

- 初始化一个“最小可运行”的模块化单体项目骨架，作为后续业务模块接入的统一起点。
- 建立 `app/main.py`、`app/bootstrap/`、`app/interfaces/http/`、`app/shared/`、`app/modules/`、`tests/` 等核心目录职责与边界。
- 提供可启动的 FastAPI 应用入口与健康检查 HTTP 路径，用于验证骨架具备最基本运行能力。
- 明确并固化模块接入模板与约定，使未来模块统一通过 `api/contracts.py` 与 `api/facade.py` 暴露公开能力。
- 初始化基础工程配置，限定当前基础栈为 FastAPI、Pydantic、pytest、ruff。
- 明确排除数据库接线、真实业务模块与其他扩展基础设施，避免范围扩张。

## Capabilities（能力项）

### New Capabilities（新增能力）
- `project-bootstrap`: 定义最小可运行应用骨架、启动入口、装配层职责与基础工程初始化边界。
- `http-health-interface`: 定义最小 HTTP 接口层能力，包括应用可启动、路由注册与健康检查入口。
- `module-scaffold-template`: 定义未来业务模块的标准模板、公开 API 边界与接入约定。

### Modified Capabilities（修改能力）
- 无。

## Impact（影响范围）

- Affected code: `app/`, `tests/`, `scripts/`, `pyproject.toml`, `README.md`, `.env.example`, `Makefile`
- Affected APIs: 最小 HTTP 健康检查接口与应用启动入口
- Dependencies: FastAPI, Pydantic, pytest, ruff
- Systems: 本地开发初始化流程与后续模块接入方式
