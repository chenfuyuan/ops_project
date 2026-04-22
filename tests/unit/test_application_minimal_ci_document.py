from pathlib import Path
import unittest


class ApplicationMinimalCiDocumentTest(unittest.TestCase):
    def test_application_minimal_ci_document_defines_three_layer_model(self) -> None:
        root = Path(__file__).resolve().parents[2]
        contents = (root / "docs" / "application_minimal_ci_baseline.md").read_text()

        self.assertIn("## 默认覆盖对象", contents)
        self.assertIn("## 三层最小流水线模型", contents)
        self.assertIn("### 1. 静态与结构校验层", contents)
        self.assertIn("### 2. 测试校验层", contents)
        self.assertIn("### 3. 可运行性与构建确认层", contents)

    def test_application_minimal_ci_document_keeps_scope_platform_neutral(self) -> None:
        root = Path(__file__).resolve().parents[2]
        contents = (root / "docs" / "application_minimal_ci_baseline.md").read_text()

        self.assertIn("不定义文档一致性门禁", contents)
        self.assertIn("不定义受控部署、发布后验证、回滚入口或其他 CD 内容", contents)
        self.assertIn(
            "不定义 GitHub Actions、GitLab CI、Jenkins 或其他平台配置语法", contents
        )

    def test_application_minimal_ci_document_declares_uv_command_baseline(self) -> None:
        root = Path(__file__).resolve().parents[2]
        contents = (root / "docs" / "application_minimal_ci_baseline.md").read_text()

        self.assertIn("`pyproject.toml` 已声明 `uv` 为依赖管理与命令执行基线", contents)
        self.assertIn("## 校验要点", contents)

    def test_application_minimal_ci_document_records_current_check_assets(self) -> None:
        root = Path(__file__).resolve().parents[2]
        contents = (root / "docs" / "application_minimal_ci_baseline.md").read_text()

        self.assertIn("## 当前最小校验资产", contents)
        self.assertIn("`ruff` 作为格式或静态检查工具", contents)
        self.assertIn("`tests/architecture/test_architecture_rules.py`", contents)
        self.assertIn("`tests/integration/test_runtime_validation.py`", contents)

    def test_application_minimal_ci_document_records_default_execution_order(
        self,
    ) -> None:
        root = Path(__file__).resolve().parents[2]
        contents = (root / "docs" / "application_minimal_ci_baseline.md").read_text()

        self.assertIn("## 三层默认执行顺序", contents)
        self.assertIn("1. 先执行静态与结构校验层", contents)
        self.assertIn("2. 再执行测试校验层", contents)
        self.assertIn("3. 最后执行可运行性与构建确认层", contents)
        self.assertIn("映射为串行 stage 或等价阻断作业", contents)

    def test_readme_records_minimal_ci_command_entrypoints(self) -> None:
        root = Path(__file__).resolve().parents[2]
        contents = (root / "README.md").read_text()

        self.assertIn("## 应用代码最小 CI 命令", contents)
        self.assertIn("uv run ruff check app tests", contents)
        self.assertIn(
            "uv run python -m unittest discover -s tests/architecture", contents
        )
        self.assertIn("uv run python -m unittest discover -s tests/unit", contents)
        self.assertNotIn(
            "uv run python -m unittest discover -s tests/unit && uv run python -m unittest discover -s tests/architecture",
            contents,
        )
        self.assertIn(
            "uv run python -m unittest discover -s tests/integration", contents
        )


if __name__ == "__main__":
    unittest.main()
