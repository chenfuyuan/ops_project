# Person Up Ops Project

## 应用代码最小 CI 命令

- 静态与结构校验：`uv run ruff check app tests`
- 架构边界检查：`uv run python -m unittest discover -s tests/architecture`
- 测试校验层默认测试集合：`uv run python -m unittest discover -s tests/unit`
- 可运行性与构建确认层：`uv run python -m unittest discover -s tests/integration`
