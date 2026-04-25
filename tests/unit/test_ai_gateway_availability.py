import unittest

from app.capabilities.ai_gateway import AiGatewayAvailability, AiGatewayFacade
from app.capabilities.ai_gateway.providers.unconfigured_provider import (
    UnconfiguredAiGatewayProvider,
)


class FakeAvailabilityProvider:
    def __init__(self) -> None:
        self.called = False

    def check_availability(self) -> AiGatewayAvailability:
        self.called = True
        return AiGatewayAvailability.available()


class AiGatewayAvailabilityTest(unittest.TestCase):
    def test_unconfigured_provider_reports_unavailable_without_network_access(self) -> None:
        result = UnconfiguredAiGatewayProvider().check_availability()

        self.assertEqual("ai_gateway", result.component)
        self.assertEqual("unavailable", result.status)
        self.assertFalse(result.configured)
        self.assertEqual("AI gateway config path is not configured.", result.reason)

    def test_facade_delegates_availability_check_to_provider(self) -> None:
        provider = FakeAvailabilityProvider()
        facade = AiGatewayFacade(availability_provider=provider)

        result = facade.check_availability()

        self.assertTrue(provider.called)
        self.assertEqual(AiGatewayAvailability.available(), result)


if __name__ == "__main__":
    unittest.main()
