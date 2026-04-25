import json
from typing import Any, Protocol

from app.capabilities.ai_gateway.config.models import (
    AiGatewayProfileConfig,
    AiGatewayProviderConfig,
)
from app.capabilities.ai_gateway.contracts.models import OutputMode
from app.capabilities.ai_gateway.contracts.request import AiGatewayRequest
from app.capabilities.ai_gateway.contracts.response import AiGatewayResponse, TokenUsage
from app.capabilities.ai_gateway.errors import (
    ProviderCallError,
    ProviderResponseError,
    ProviderTimeoutError,
    StructuredOutputError,
)


class JsonHttpTransport(Protocol):
    """OpenAI-compatible provider 使用的最小 JSON HTTP transport。"""

    def post_json(self, *, url: str, headers: dict, payload: dict, timeout: float) -> dict:
        """发送 JSON POST 请求并返回 JSON 字典。"""


class OpenAICompatibleProvider:
    """通过 OpenAI-compatible HTTP 协议访问外部模型 provider。"""

    def __init__(self, *, transport: JsonHttpTransport) -> None:
        self._transport = transport

    def generate(
        self,
        *,
        request: AiGatewayRequest,
        profile: AiGatewayProfileConfig,
        provider_config: AiGatewayProviderConfig,
        api_key: str,
    ) -> AiGatewayResponse:
        attempts = profile.retry_attempts + 1
        last_error: ProviderCallError | None = None
        for attempt in range(attempts):
            try:
                raw_response = self._transport.post_json(
                    url=self._chat_completions_url(provider_config.base_url),
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    payload=self._payload(request, profile),
                    timeout=profile.timeout_seconds,
                )
                return self._response(raw_response, request.output_mode)
            except TimeoutError as exc:
                last_error = ProviderTimeoutError(
                    "AI provider call timed out",
                    safe_context={"provider": provider_config.name, "attempt": attempt + 1},
                )
            except ProviderCallError:
                raise
            except Exception as exc:
                last_error = ProviderCallError(
                    "AI provider call failed",
                    safe_context={"provider": provider_config.name, "attempt": attempt + 1},
                )
        if last_error is not None:
            raise last_error
        raise ProviderCallError("AI provider call failed")

    def _payload(self, request: AiGatewayRequest, profile: AiGatewayProfileConfig) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": profile.model,
            "messages": [
                {"role": message.role.value, "content": message.content}
                for message in request.messages
            ],
        }
        if request.output_mode is OutputMode.STRUCTURED:
            structured_output = request.structured_output
            if structured_output is None:
                raise StructuredOutputError("Structured output constraint is required")
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": structured_output.name,
                    "schema": structured_output.json_schema,
                },
            }
        return payload

    def _response(self, raw_response: dict[str, Any], output_mode: OutputMode) -> AiGatewayResponse:
        try:
            content = raw_response["choices"][0]["message"]["content"]
            usage = raw_response.get("usage", {})
            token_usage = TokenUsage(
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
            )
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderResponseError("AI provider response could not be mapped") from exc

        metadata = {}
        if raw_response.get("id"):
            metadata["provider_response_id"] = raw_response["id"]

        if output_mode is OutputMode.STRUCTURED:
            try:
                structured_content = json.loads(content)
            except json.JSONDecodeError as exc:
                raise StructuredOutputError("AI provider response is not valid structured output") from exc
            return AiGatewayResponse(
                output_mode=output_mode,
                structured_content=structured_content,
                usage=token_usage,
                metadata=metadata,
            )

        return AiGatewayResponse(
            output_mode=output_mode,
            content=content,
            usage=token_usage,
            metadata=metadata,
        )

    def _chat_completions_url(self, base_url: str) -> str:
        return f"{base_url.rstrip('/')}/chat/completions"
