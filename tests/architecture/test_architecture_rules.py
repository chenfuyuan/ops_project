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

    def test_business_core_does_not_depend_on_capabilities(self) -> None:
        for path in APP_ROOT.glob("business/**/*.py"):
            if "/infrastructure/" in path.as_posix():
                continue
            self._assert_no_prefix(path, "app.capabilities")

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

    def test_api_bootstrap_does_not_import_generation_provider_at_module_load(
        self,
    ) -> None:
        bootstrap_path = APP_ROOT / "bootstrap" / "ai_gateway.py"
        forbidden_top_level_imports = {
            "app.capabilities.ai_gateway.providers.httpx_transport",
            "app.capabilities.ai_gateway.providers.openai_compatible",
        }
        tree = ast.parse(bootstrap_path.read_text(), filename=str(bootstrap_path))

        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module:
                self.assertNotIn(
                    node.module,
                    forbidden_top_level_imports,
                    f"{bootstrap_path} imports optional generation provider at module load",
                )

    def test_docker_api_starts_without_runtime_uv_sync(self) -> None:
        dockerfile = (ROOT / "Dockerfile").read_text()
        compose = (ROOT / "docker-compose.yml").read_text()

        self.assertIn('/app/.venv/bin/uvicorn", "app.api:app"', dockerfile)
        self.assertIn('/app/.venv/bin/uvicorn", "app.api:app"', compose)
        self.assertNotIn('"uv", "run", "uvicorn", "app.api:app"', dockerfile)
        self.assertNotIn('"uv", "run", "uvicorn", "app.api:app"', compose)

    def test_docker_api_receives_ai_gateway_runtime_config(self) -> None:
        compose = (ROOT / "docker-compose.yml").read_text()

        self.assertIn("AI_GATEWAY_CONFIG_PATH: /app/config/ai_gateway.json", compose)
        self.assertIn("AI_GATEWAY_API_KEY: ${AI_GATEWAY_API_KEY}", compose)
        self.assertIn(
            "./config/ai_gateway.json:/app/config/ai_gateway.json:ro", compose
        )

    def test_ai_gateway_does_not_contain_business_task_terms(self) -> None:
        business_terms = {"outline", "blueprint", "chapter", "大纲", "蓝图", "章节"}
        for path in APP_ROOT.glob("capabilities/ai_gateway/**/*.py"):
            lowered = path.read_text().lower()
            for term in business_terms:
                self.assertNotIn(term, lowered, f"{path} contains business term {term}")

    def test_outline_domain_does_not_depend_on_outer_layers(self) -> None:
        forbidden_prefixes = (
            "app.business.novel_generate.nodes.outline.application",
            "app.business.novel_generate.nodes.outline.infrastructure",
            "app.capabilities",
            "app.interfaces",
            "sqlalchemy",
            "fastapi",
            "httpx",
            "requests",
        )
        for path in APP_ROOT.glob(
            "business/novel_generate/nodes/outline/domain/**/*.py"
        ):
            for prefix in forbidden_prefixes:
                self._assert_no_prefix(path, prefix)

    def test_complex_outline_node_does_not_keep_flat_service_module(self) -> None:
        service_path = (
            APP_ROOT
            / "business"
            / "novel_generate"
            / "nodes"
            / "outline"
            / "service.py"
        )

        self.assertFalse(
            service_path.exists(),
            "complex outline node must use facade/use cases, not service.py",
        )

    def test_complex_outline_node_exposes_workflow_adapter(self) -> None:
        node_path = (
            APP_ROOT
            / "business"
            / "novel_generate"
            / "nodes"
            / "outline"
            / "node.py"
        )

        self.assertTrue(
            node_path.exists(),
            "complex outline node must expose node.py as workflow adapter",
        )

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
