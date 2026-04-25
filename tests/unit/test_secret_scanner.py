import importlib.util
import sys
from pathlib import Path


SCANNER_PATH = Path(__file__).resolve().parents[2] / "scripts" / "scan_secrets.py"


def load_scanner():
    spec = importlib.util.spec_from_file_location("scan_secrets", SCANNER_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["scan_secrets"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_scan_diff_blocks_high_risk_secret() -> None:
    scanner = load_scanner()
    openai_key = "sk-proj-" + "abcdefghijklmnopqrstuvwxyz123456"
    diff = f"""diff --git a/app/example.py b/app/example.py
+++ b/app/example.py
@@ -0,0 +1 @@
+OPENAI_API_KEY = \"{openai_key}\"
"""

    findings = scanner.scan_diff(diff)

    assert len(findings) == 1
    assert findings[0].path == "app/example.py"
    assert findings[0].line == 1
    assert findings[0].pattern == "openai_key"


def test_scan_diff_blocks_github_token() -> None:
    scanner = load_scanner()
    github_token = "ghp_" + "abcdefghijklmnopqrstuvwxyz1234567890"
    diff = f"""diff --git a/app/example.py b/app/example.py
+++ b/app/example.py
@@ -0,0 +1 @@
+GITHUB_TOKEN={github_token}
"""

    findings = scanner.scan_diff(diff)

    assert len(findings) == 1
    assert findings[0].pattern == "github_token"


def test_scan_diff_allows_documented_placeholders() -> None:
    scanner = load_scanner()
    diff = """diff --git a/.env.example b/.env.example
+++ b/.env.example
@@ -0,0 +1,2 @@
+AI_GATEWAY_API_KEY=replace-locally-do-not-commit
+TOKEN=${AI_GATEWAY_API_KEY}
"""

    findings = scanner.scan_diff(diff)

    assert findings == []


def test_scan_diff_blocks_plaintext_generic_secret() -> None:
    scanner = load_scanner()
    diff = """diff --git a/config/service.json b/config/service.json
+++ b/config/service.json
@@ -0,0 +1,3 @@
+{
+  \"api_key\": \"real-service-key-1234567890\"
+}
"""

    findings = scanner.scan_diff(diff)

    assert len(findings) == 1
    assert findings[0].path == "config/service.json"
    assert findings[0].line == 2
    assert findings[0].pattern == "generic_secret_assignment"


def test_scan_diff_does_not_flag_variable_flow() -> None:
    scanner = load_scanner()
    diff = """diff --git a/app/bootstrap/ai_gateway.py b/app/bootstrap/ai_gateway.py
+++ b/app/bootstrap/ai_gateway.py
@@ -0,0 +1,3 @@
+api_key = repository.resolve_provider_api_key(provider_config.name)
+provider.generate(api_key=api_key)
+request.add_header(\"Authorization\", f\"Bearer {self._api_key}\")
"""

    findings = scanner.scan_diff(diff)

    assert findings == []
