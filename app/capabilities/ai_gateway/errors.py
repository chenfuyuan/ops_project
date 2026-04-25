from typing import Any


class AiGatewayError(Exception):
    """AI 网关对外稳定错误基类。"""

    default_code = "ai_gateway_error"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        safe_context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.default_code
        self.safe_context = safe_context or {}

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class AiGatewayConfigError(AiGatewayError):
    """AI 网关配置缺失、非法或无法解析时抛出。"""

    default_code = "ai_gateway_config_error"


class ProviderCallError(AiGatewayError):
    """外部模型 provider 调用失败时抛出。"""

    default_code = "provider_call_error"


class ProviderTimeoutError(ProviderCallError):
    """外部模型 provider 调用超时时抛出。"""

    default_code = "provider_timeout"


class ProviderResponseError(ProviderCallError):
    """外部模型 provider 响应无法映射为统一响应时抛出。"""

    default_code = "provider_response_error"


class StructuredOutputError(AiGatewayError):
    """模型输出无法按通用结构化约束解析时抛出。"""

    default_code = "structured_output_error"
