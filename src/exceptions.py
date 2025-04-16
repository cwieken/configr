class ConfigFileNotFoundError(FileNotFoundError):
    """Raised when a configuration file is not found."""
    pass


class ConfigValidationError(ValueError):
    """Raised when configuration validation fails."""
    pass