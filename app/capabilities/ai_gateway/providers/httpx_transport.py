import httpx

from app.capabilities.ai_gateway.errors import ProviderCallError, ProviderTimeoutError


class HttpxJsonTransport:
    """使用 httpx 执行 JSON POST 请求的最小 transport。"""

    def __init__(self, *, client: httpx.Client | None = None) -> None:
        self._client = client

    def post_json(self, *, url: str, headers: dict, payload: dict, timeout: float) -> dict:
        try:
            if self._client is not None:
                response = self._client.post(url, headers=headers, json=payload, timeout=timeout)
            else:
                with httpx.Client(timeout=timeout) as client:
                    response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError("AI provider HTTP call timed out") from exc
        except httpx.HTTPError as exc:
            raise ProviderCallError("AI provider HTTP call failed") from exc
