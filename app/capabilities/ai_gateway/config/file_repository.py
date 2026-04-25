import json
import os
from pathlib import Path
from typing import Any

from app.capabilities.ai_gateway.config.models import (
    AiGatewayConfig,
    AiGatewayProfileConfig,
    AiGatewayProviderConfig,
)
from app.capabilities.ai_gateway.contracts.models import CapabilityProfileName
from app.capabilities.ai_gateway.errors import AiGatewayConfigError


class FileAiGatewayConfigRepository:
    """从结构化配置数据中读取 AI 网关 profile 和 provider 配置。

    该实现只允许配置文件保存环境变量引用，真实密钥必须来自运行时环境变量。
    """

    def __init__(self, config: AiGatewayConfig) -> None:
        self._profiles = {profile.name: profile for profile in config.profiles}
        self._providers = {provider.name: provider for provider in config.providers}

    @classmethod
    def from_file(cls, path: Path) -> "FileAiGatewayConfigRepository":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FileAiGatewayConfigRepository":
        cls._reject_plaintext_secrets(data)
        return cls(AiGatewayConfig.model_validate(data))

    def get_profile(self, name: CapabilityProfileName) -> AiGatewayProfileConfig:
        profile_name = str(name)
        try:
            return self._profiles[profile_name]
        except KeyError as exc:
            raise AiGatewayConfigError(
                "AI gateway profile is not configured",
                safe_context={"profile": profile_name},
            ) from exc

    def get_provider(self, name: str) -> AiGatewayProviderConfig:
        try:
            return self._providers[name]
        except KeyError as exc:
            raise AiGatewayConfigError(
                "AI gateway provider is not configured",
                safe_context={"provider": name},
            ) from exc

    def first_provider(self) -> AiGatewayProviderConfig:
        try:
            return next(iter(self._providers.values()))
        except StopIteration as exc:
            raise AiGatewayConfigError("AI gateway provider is not configured") from exc

    def resolve_provider_api_key(self, provider_name: str) -> str:
        provider = self.get_provider(provider_name)
        api_key = os.environ.get(provider.api_key_env)
        if not api_key:
            raise AiGatewayConfigError(
                "AI gateway provider API key environment variable is missing",
                safe_context={"provider": provider_name, "api_key_env": provider.api_key_env},
            )
        return api_key

    @staticmethod
    def _reject_plaintext_secrets(data: dict[str, Any]) -> None:
        for provider in data.get("providers", []):
            if provider.get("api_key"):
                raise AiGatewayConfigError(
                    "AI gateway config must reference API keys through environment variables",
                    safe_context={"provider": provider.get("name")},
                )
