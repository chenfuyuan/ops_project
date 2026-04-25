import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.bootstrap.ai_gateway import create_ai_gateway_facade
from app.capabilities.ai_gateway import AiGatewayFacade


class AiGatewayBootstrapTest(unittest.TestCase):
    def test_create_ai_gateway_facade_wires_file_config_and_provider(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "ai_gateway.json"
            config_path.write_text(
                json.dumps(
                    {
                        "profiles": [
                            {
                                "name": "balanced_text",
                                "provider": "primary-openai-compatible",
                                "model": "gpt-compatible-small",
                                "capability_tags": ["text"],
                                "context_window": 32_000,
                                "cost_tier": "balanced",
                                "timeout_seconds": 30,
                                "retry_attempts": 1,
                            }
                        ],
                        "providers": [
                            {
                                "name": "primary-openai-compatible",
                                "kind": "openai-compatible",
                                "base_url": "https://example.test/v1",
                                "api_key_env": "AI_GATEWAY_API_KEY",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with patch.dict("os.environ", {"AI_GATEWAY_CONFIG_PATH": str(config_path)}):
                facade = create_ai_gateway_facade()

        self.assertIsInstance(facade, AiGatewayFacade)


if __name__ == "__main__":
    unittest.main()
