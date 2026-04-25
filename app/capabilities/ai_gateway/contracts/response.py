from typing import Any

from pydantic import BaseModel, Field, computed_field

from app.capabilities.ai_gateway.contracts.models import OutputMode


class TokenUsage(BaseModel):
    """AI 网关对外暴露的中性 token 使用量摘要。"""

    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)

    @computed_field
    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class AiGatewayResponse(BaseModel):
    """AI 网关返回给调用方的 provider-neutral 响应。"""

    output_mode: OutputMode
    content: str | None = None
    structured_content: dict[str, Any] | list[Any] | None = None
    usage: TokenUsage
    metadata: dict[str, Any] = Field(default_factory=dict)


class AiGatewayAvailability(BaseModel):
    """AI 网关诊断接口使用的中性可用性结果。"""

    component: str = "ai_gateway"
    status: str
    configured: bool
    reason: str | None = None

    @classmethod
    def available(cls) -> "AiGatewayAvailability":
        """表示 AI 网关已配置且健康探测成功。"""
        return cls(status="available", configured=True)

    @classmethod
    def unavailable(cls, *, configured: bool, reason: str) -> "AiGatewayAvailability":
        """表示 AI 网关当前不可用，并返回不含敏感信息的原因。"""
        return cls(status="unavailable", configured=configured, reason=reason)
