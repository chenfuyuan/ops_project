from app.capabilities.ai_gateway.contracts.response import AiGatewayAvailability


class StaticUnavailableAiGatewayProvider:
    """不访问网络，返回安全的 AI 网关不可用诊断结果。"""

    def __init__(self, *, configured: bool, reason: str) -> None:
        self._configured = configured
        self._reason = reason

    def check_availability(self) -> AiGatewayAvailability:
        """返回不含敏感信息的不可用状态。"""
        return AiGatewayAvailability.unavailable(
            configured=self._configured,
            reason=self._reason,
        )


class UnconfiguredAiGatewayProvider(StaticUnavailableAiGatewayProvider):
    """在缺少 AI 网关配置文件路径时返回安全的不可用诊断结果。"""

    def __init__(self) -> None:
        super().__init__(
            configured=False,
            reason="AI gateway config path is not configured.",
        )
