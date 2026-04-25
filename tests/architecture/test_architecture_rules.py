from pathlib import Path
import ast
import unittest

ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = ROOT / "app"


class ArchitectureRulesTest(unittest.TestCase):
    def test_service_and_workflow_do_not_import_infra_details(self) -> None:
        forbidden = {"sqlalchemy", "boto3", "redis", "requests", "httpx"}
        for path in APP_ROOT.glob("business/**/service.py"):
            self._assert_forbidden_imports(path, forbidden)
        for path in APP_ROOT.glob("business/**/workflow/*.py"):
            self._assert_forbidden_imports(path, forbidden)

    def test_interfaces_do_not_depend_on_business_infrastructure(self) -> None:
        for path in APP_ROOT.glob("interfaces/**/*.py"):
            self._assert_not_importing(path, "app.business", ".infrastructure")

    def test_capabilities_do_not_depend_on_business(self) -> None:
        for path in APP_ROOT.glob("capabilities/**/*.py"):
            self._assert_no_prefix(path, "app.business")

    def test_ai_gateway_keeps_provider_details_internal(self) -> None:
        provider_internal_import = "app.capabilities.ai_gateway.providers"
        allowed_roots = {
            APP_ROOT / "capabilities" / "ai_gateway",
            APP_ROOT / "bootstrap",
        }
        for path in APP_ROOT.glob("**/*.py"):
            if any(path.is_relative_to(root) for root in allowed_roots):
                continue
            self._assert_no_prefix(path, provider_internal_import)

    def test_ai_gateway_does_not_contain_business_task_terms(self) -> None:
        business_terms = {"outline", "blueprint", "chapter", "大纲", "蓝图", "章节"}
        for path in APP_ROOT.glob("capabilities/ai_gateway/**/*.py"):
            lowered = path.read_text().lower()
            for term in business_terms:
                self.assertNotIn(term, lowered, f"{path} contains business term {term}")

    def test_shared_does_not_depend_on_business_modules(self) -> None:
        for path in APP_ROOT.glob("shared/**/*.py"):
            self._assert_no_prefix(path, "app.business")

    def _assert_forbidden_imports(self, path: Path, forbidden: set[str]) -> None:
        for name in self._imports(path):
            self.assertNotIn(name.split(".")[0], forbidden, f"{path} imports {name}")

    def _assert_not_importing(self, path: Path, prefix: str, suffix: str) -> None:
        for name in self._imports(path):
            self.assertFalse(
                name.startswith(prefix) and suffix in name, f"{path} imports {name}"
            )

    def _assert_no_prefix(self, path: Path, prefix: str) -> None:
        for name in self._imports(path):
            self.assertFalse(name.startswith(prefix), f"{path} imports {name}")

    def _imports(self, path: Path) -> list[str]:
        tree = ast.parse(path.read_text() or "", filename=str(path))
        names: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module)
        return names


if __name__ == "__main__":
    unittest.main()
