from enum import StrEnum

from pydantic import BaseModel, Field


class CostTier(StrEnum):
    """模型 profile 的中性成本等级。"""

    LOW = "low"
    BALANCED = "balanced"
    HIGH = "high"


class AiGatewayProfileConfig(BaseModel):
    """单个 capability profile 到具体模型能力来源的配置映射。"""

    name: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    capability_tags: list[str] = Field(default_factory=list)
    context_window: int = Field(gt=0)
    cost_tier: CostTier
    timeout_seconds: float = Field(gt=0)
    retry_attempts: int = Field(ge=0)


class AiGatewayProviderConfig(BaseModel):
    """外部模型 provider 的非敏感连接配置。"""

    name: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    base_url: str = Field(min_length=1)
    api_key_env: str = Field(min_length=1)


class AiGatewayConfig(BaseModel):
    """结构化配置文件中的 AI 网关配置根对象。"""

    profiles: list[AiGatewayProfileConfig]
    providers: list[AiGatewayProviderConfig]
