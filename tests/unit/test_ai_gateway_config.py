import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.capabilities.ai_gateway import AiGatewayConfigError, CapabilityProfileName
from app.capabilities.ai_gateway.config import (
    AiGatewayProfileConfig,
    AiGatewayProviderConfig,
    CostTier,
    FileAiGatewayConfigRepository,
)


class AiGatewayConfigTest(unittest.TestCase):
    def test_profile_config_captures_neutral_model_capability(self) -> None:
        profile = AiGatewayProfileConfig(
            name="balanced_text",
            provider="primary-openai-compatible",
            model="gpt-compatible-small",
            capability_tags=["text", "balanced"],
            context_window=32_000,
            cost_tier=CostTier.BALANCED,
            timeout_seconds=30.0,
            retry_attempts=2,
        )

        self.assertEqual("balanced_text", profile.name)
        self.assertEqual("primary-openai-compatible", profile.provider)
        self.assertEqual(CostTier.BALANCED, profile.cost_tier)
        self.assertEqual(32_000, profile.context_window)

    def test_provider_config_references_secret_environment_variable(self) -> None:
        provider = AiGatewayProviderConfig(
            name="primary-openai-compatible",
            kind="openai-compatible",
            base_url="https://example.test/v1",
            api_key_env="AI_GATEWAY_API_KEY",
        )

        self.assertEqual("AI_GATEWAY_API_KEY", provider.api_key_env)
        self.assertEqual("openai-compatible", provider.kind)

    def test_repository_contract_returns_profile_and_provider(self) -> None:
        repository = FileAiGatewayConfigRepository.from_dict(self._config_data())

        profile = repository.get_profile(CapabilityProfileName("balanced_text"))
        provider = repository.get_provider(profile.provider)

        self.assertEqual("gpt-compatible-small", profile.model)
        self.assertEqual("https://example.test/v1", provider.base_url)

    def test_example_config_contains_outline_generation_profiles(self) -> None:
        data = json.loads(
            (Path(__file__).resolve().parents[2] / "config" / "ai_gateway.example.json").read_text()
        )
        profile_names = {profile["name"] for profile in data["profiles"]}

        self.assertIn("outline-skeleton", profile_names)
        self.assertIn("outline-chapter-expansion", profile_names)

    def test_repository_loads_structured_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ai_gateway.json"
            path.write_text(json.dumps(self._config_data()), encoding="utf-8")

            repository = FileAiGatewayConfigRepository.from_file(path)

        profile = repository.get_profile(CapabilityProfileName("balanced_text"))
        self.assertEqual("gpt-compatible-small", profile.model)

    def test_repository_returns_default_provider_for_gateway_level_diagnostics(
        self,
    ) -> None:
        repository = FileAiGatewayConfigRepository.from_dict(self._config_data())

        provider = repository.first_provider()

        self.assertEqual("primary-openai-compatible", provider.name)
        self.assertEqual("AI_GATEWAY_API_KEY", provider.api_key_env)

    def test_repository_resolves_provider_api_key_from_environment(self) -> None:
        repository = FileAiGatewayConfigRepository.from_dict(self._config_data())

        with patch.dict("os.environ", {"AI_GATEWAY_API_KEY": "secret-value"}):
            api_key = repository.resolve_provider_api_key("primary-openai-compatible")

        self.assertEqual("secret-value", api_key)

    def test_repository_rejects_missing_environment_secret(self) -> None:
        repository = FileAiGatewayConfigRepository.from_dict(self._config_data())

        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(AiGatewayConfigError):
                repository.resolve_provider_api_key("primary-openai-compatible")

    def test_repository_rejects_plaintext_api_key_in_config(self) -> None:
        data = self._config_data()
        data["providers"][0]["api_key"] = "plaintext-secret"

        with self.assertRaises(AiGatewayConfigError):
            FileAiGatewayConfigRepository.from_dict(data)

    def _config_data(self) -> dict:
        return {
            "profiles": [
                {
                    "name": "balanced_text",
                    "provider": "primary-openai-compatible",
                    "model": "gpt-compatible-small",
                    "capability_tags": ["text", "balanced"],
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


if __name__ == "__main__":
    unittest.main()
