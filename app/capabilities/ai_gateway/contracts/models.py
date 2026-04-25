from enum import StrEnum
from typing import Any, NewType

from pydantic import BaseModel, ConfigDict, Field


CapabilityProfileName = NewType("CapabilityProfileName", str)


class OutputMode(StrEnum):
    """AI 网关支持的中性输出模式。"""

    TEXT = "text"
    STRUCTURED = "structured"


class MessageRole(StrEnum):
    """AI 网关公开契约中的中性消息角色。"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class AiGatewayMessage(BaseModel):
    """单条模型输入消息，不承载任何创作业务语义。"""

    role: MessageRole
    content: str = Field(min_length=1)


class StructuredOutputConstraint(BaseModel):
    """调用方提供的通用结构化输出约束。"""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1)
    json_schema: dict[str, Any] = Field(alias="schema")
