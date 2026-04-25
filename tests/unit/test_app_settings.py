import unittest

from app.bootstrap.settings import load_settings


class AppSettingsTest(unittest.TestCase):
    def test_settings_do_not_define_separate_ai_gateway_probe_configuration(self) -> None:
        settings = load_settings()

        self.assertFalse(hasattr(settings, "ai_gateway_base_url"))
        self.assertFalse(hasattr(settings, "ai_gateway_health_path"))
        self.assertFalse(hasattr(settings, "ai_gateway_timeout_seconds"))
        self.assertFalse(hasattr(settings, "ai_gateway_api_key"))


if __name__ == "__main__":
    unittest.main()
