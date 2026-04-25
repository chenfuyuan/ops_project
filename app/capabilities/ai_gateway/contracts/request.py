from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.capabilities.ai_gateway.contracts.models import (
    AiGatewayMessage,
    CapabilityProfileName,
    OutputMode,
    StructuredOutputConstraint,
)

_IMPLEMENTATION_DETAIL_PROFILE_TERMS = ("provider", "model", "api_key", "base_url")


class AiGatewayRequest(BaseModel):
    """调用方提交给 AI 网关的中性模型能力请求。

    请求只表达 profile、消息、输出模式和通用结构化约束，不包含 provider、model、密钥或业务任务语义。
    """

    capability_profile: CapabilityProfileName
    messages: list[AiGatewayMessage] = Field(min_length=1)
    output_mode: OutputMode
    structured_output: StructuredOutputConstraint | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_gateway_boundary(self) -> "AiGatewayRequest":
        profile = str(self.capability_profile).lower()
        if any(term in profile for term in _IMPLEMENTATION_DETAIL_PROFILE_TERMS):
            raise ValueError(
                "capability_profile must not expose implementation details"
            )
        if self.output_mode is OutputMode.STRUCTURED and self.structured_output is None:
            raise ValueError("structured output mode requires structured_output")
        return self
