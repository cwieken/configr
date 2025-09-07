"""
Configuration-related exceptions module.

This module defines custom exceptions used throughout the configuration
management system to provide more specific error information when
configuration loading or validation fails.

The module includes:
- ConfigFileNotFoundError: Raised when a configuration file cannot be found
- ConfigValidationError: Raised when configuration validation fails

Typical usage:
    try:
        config = ConfigBase.load(DatabaseConfig)
    except ConfigFileNotFoundError:
        # Handle missing configuration file
    except ConfigValidationError:
        # Handle invalid configuration values
"""


class ConfigFileNotFoundError(FileNotFoundError):
    """Raised when a configuration file is not found."""
    pass


class ConfigValidationError(ValueError):
    """Raised when configuration validation fails."""
    pass


class ConfigLoadError(ValueError):
    """Raised when configuration loading fails."""
    pass
