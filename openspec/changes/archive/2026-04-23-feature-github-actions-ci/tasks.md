## 1. 命令入口校准

- [x] 1.1 对照 `docs/application_minimal_ci_baseline.md`、`pyproject.toml` 与 `tests/` 目录，确认 GitHub Actions 将调用的最小 CI 命令入口
- [x] 1.2 如现有文档中的默认命令入口与仓库真实测试资产存在偏差，补充最小范围修正以保持文档与实现一致

## 2. GitHub Actions workflow 落地

- [x] 2.1 新增 `.github/workflows/ci.yml`，配置 `push` 与 `pull_request` 触发的单 workflow 入口
- [x] 2.2 在 workflow 中配置 `static-and-structure` job，并完成代码检出、Python 3.13 与 `uv` 环境准备及对应检查命令
- [x] 2.3 在 workflow 中配置 `test-suite` job，复用最小默认测试集合并通过 `needs` 依赖静态/结构校验层
- [x] 2.4 在 workflow 中配置 `runtime-validation` job，执行最小可运行性确认并通过 `needs` 依赖测试校验层

## 3. 验证与收尾

- [x] 3.1 在本地或等价环境逐项验证 workflow 所依赖的 `uv` 命令可执行
- [x] 3.2 检查 workflow 的 job 划分、依赖顺序与阻断语义是否符合三层最小流水线模型
- [x] 3.3 如有必要，补充最小说明，使维护者能理解 GitHub Actions workflow 与平台中立基线的职责关系
