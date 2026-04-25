import unittest


class AiGatewayPublicExportsTest(unittest.TestCase):
    def test_root_package_exports_stable_public_contract(self) -> None:
        from app.capabilities.ai_gateway import (
            AiGatewayConfigError,
            AiGatewayFacade,
            AiGatewayRequest,
            AiGatewayResponse,
            CapabilityProfileName,
            OutputMode,
            ProviderCallError,
            ProviderTimeoutError,
            StructuredOutputError,
        )

        self.assertEqual("AiGatewayFacade", AiGatewayFacade.__name__)
        self.assertEqual("AiGatewayRequest", AiGatewayRequest.__name__)
        self.assertEqual("AiGatewayResponse", AiGatewayResponse.__name__)
        self.assertEqual("CapabilityProfileName", CapabilityProfileName.__name__)
        self.assertEqual("OutputMode", OutputMode.__name__)
        self.assertTrue(issubclass(AiGatewayConfigError, Exception))
        self.assertTrue(issubclass(ProviderCallError, Exception))
        self.assertTrue(issubclass(ProviderTimeoutError, ProviderCallError))
        self.assertTrue(issubclass(StructuredOutputError, Exception))


if __name__ == "__main__":
    unittest.main()
