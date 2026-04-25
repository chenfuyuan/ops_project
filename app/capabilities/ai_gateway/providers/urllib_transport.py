import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.capabilities.ai_gateway.errors import ProviderCallError, ProviderTimeoutError


class UrllibJsonTransport:
    """使用标准库执行 JSON POST 请求，避免运行时依赖测试 HTTP 客户端。"""

    def post_json(
        self, *, url: str, headers: dict, payload: dict, timeout: float
    ) -> dict:
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8")
        except TimeoutError as exc:
            raise ProviderTimeoutError("AI provider HTTP call timed out") from exc
        except (HTTPError, URLError, OSError) as exc:
            raise ProviderCallError("AI provider HTTP call failed") from exc

        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise ProviderCallError("AI provider returned invalid JSON") from exc
