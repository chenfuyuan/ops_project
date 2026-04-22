from pathlib import Path
import unittest


class GithubActionsCiWorkflowTest(unittest.TestCase):
    def test_ci_workflow_exists_and_maps_three_layer_pipeline(self) -> None:
        root = Path(__file__).resolve().parents[2]
        workflow = root / ".github" / "workflows" / "ci.yml"

        self.assertTrue(workflow.exists())

        contents = workflow.read_text()

        self.assertIn("on:", contents)
        self.assertIn("push:", contents)
        self.assertIn("pull_request:", contents)
        self.assertIn("quality-preflight:", contents)
        self.assertIn("static-and-architecture:", contents)
        self.assertIn("test-suite:", contents)
        self.assertIn("runtime-validation:", contents)
        self.assertIn("needs: quality-preflight", contents)
        self.assertIn("needs: static-and-architecture", contents)
        self.assertIn("needs: test-suite", contents)

    def test_ci_workflow_reuses_minimal_uv_command_entrypoints(self) -> None:
        root = Path(__file__).resolve().parents[2]
        contents = (root / ".github" / "workflows" / "ci.yml").read_text()

        self.assertIn("python-version: '3.13'", contents)
        self.assertIn("astral-sh/setup-uv", contents)
        self.assertIn("uv sync --group dev --group test", contents)
        self.assertIn("uv run ruff check app tests", contents)
        self.assertIn(
            "uv run python -m unittest discover -s tests/architecture", contents
        )
        self.assertIn("uv run python -m unittest discover -s tests/unit", contents)
        self.assertIn(
            "uv run python -m unittest discover -s tests/integration", contents
        )


if __name__ == "__main__":
    unittest.main()
