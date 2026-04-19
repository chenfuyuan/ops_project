class AppError(Exception):
    """Base exception for shared application concerns."""


class ConfigurationError(AppError):
    """Raised when required application configuration is invalid."""
