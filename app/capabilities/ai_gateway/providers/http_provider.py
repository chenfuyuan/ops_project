import logging
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from app.capabilities.ai_gateway.contracts.response import AiGatewayAvailability

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class HttpAiGatewayAvailabilityProvider:
    """通过 HTTP 健康接口检查外部 AI 网关是否可达。"""

    def __init__(
        self,
        *,
        base_url: str,
        health_path: str,
        timeout_seconds: float,
        api_key: str | None,
    ) -> None:
        self._base_url = base_url
        self._health_path = health_path
        self._timeout_seconds = timeout_seconds
        self._api_key = api_key

    def check_availability(self) -> AiGatewayAvailability:
        """访问配置的健康接口，并把传输失败转换为安全的不可用结果。"""
        url = urljoin(f"{self._base_url.rstrip('/')}/", self._health_path.lstrip("/"))
        try:
            request = Request(url, method="GET")
            if self._api_key:
                request.add_header("Authorization", f"Bearer {self._api_key}")

            logger.info("ai_gateway_availability_check_started", extra={"url": url})
            with urlopen(request, timeout=self._timeout_seconds) as response:
                status_code = response.status
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            logger.warning(
                "ai_gateway_availability_check_failed",
                extra={"url": url, "error_type": type(exc).__name__},
            )
            return AiGatewayAvailability.unavailable(
                configured=True,
                reason="AI gateway availability check failed.",
            )

        if 200 <= status_code < 300:
            logger.info(
                "ai_gateway_availability_check_completed",
                extra={"url": url, "status_code": status_code},
            )
            return AiGatewayAvailability.available()

        logger.warning(
            "ai_gateway_availability_check_unhealthy",
            extra={"url": url, "status_code": status_code},
        )
        return AiGatewayAvailability.unavailable(
            configured=True,
            reason="AI gateway availability check failed.",
        )
