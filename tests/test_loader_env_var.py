import dataclasses
import os
from typing import Optional
from unittest.mock import patch

import pytest

from configr.base import ConfigBase
from configr.config_class import config_class
from configr.loaders.loader_env_var import EnvVarConfigLoader


@config_class(file_name="database")
class DatabaseConfig:
    host: str
    port: int = 5432
    username: str = "postgres"
    password: Optional[str] = None
    use_ssl: bool = False
    timeout: Optional[int] = 60
    max_connections: Optional[int] = 120


@config_class(file_name="nested")
class NestedChildConfig:
    setting_a: str
    setting_b: int
    setting_c: bool = True


@config_class(file_name="nested")
class NestedParentConfig:
    name: str
    child: NestedChildConfig
    optional_child: Optional[NestedChildConfig] = None
    children_list: list[NestedChildConfig] = dataclasses.field(default_factory=list)
    children_dict: dict[str, NestedChildConfig] = dataclasses.field(
        default_factory=dict
    )


@pytest.fixture
def clean_env():
    """Clear any existing environment variables before each test."""
    # Save current environment
    original_env = os.environ.copy()

    # Clear any existing environment variables for tests
    for key in list(os.environ.keys()):
        if key.startswith(("DATABASE_", "NESTED_", "APP_")):
            del os.environ[key]

    yield

    # Restore original environment variables
    for key in list(os.environ.keys()):
        if key.startswith(("DATABASE_", "NESTED_", "APP_")):
            del os.environ[key]

    for key, value in original_env.items():
        if key.startswith(("DATABASE_", "NESTED_", "APP_")):
            os.environ[key] = value


@pytest.fixture
def original_loaders():
    """Save and restore ConfigBase loaders."""
    original = ConfigBase._loaders.copy()
    yield
    ConfigBase._loaders = original


def test_basic_loading(clean_env):
    """Test basic environment variable loading with different types."""
    os.environ["DATABASE_HOST"] = "localhost"
    os.environ["DATABASE_PORT"] = "8432"
    os.environ["DATABASE_USE_SSL"] = "true"

    config_data = EnvVarConfigLoader.load("DATABASE", DatabaseConfig)

    assert config_data["host"] == "localhost"
    assert config_data["port"] == 8432
    assert config_data["use_ssl"] is True

    # This should not have been loaded as there's no env var
    # instead the default value should be used
    assert config_data["username"] == "postgres"


def test_type_conversion_explicit(clean_env):
    """Test type conversion with explicit type annotations."""
    os.environ["DATABASE_PORT"] = "1234"
    os.environ["DATABASE_USE_SSL"] = "yes"
    os.environ["DATABASE_HOST"] = "test.example.com"

    config_data = EnvVarConfigLoader.load("DATABASE", DatabaseConfig)

    assert config_data["port"] == 1234
    assert config_data["use_ssl"] is True
    assert config_data["host"] == "test.example.com"


def test_type_conversion_implicit(clean_env):
    """Test automatic type conversion for values without explicit annotations."""
    os.environ["DATABASE_TIMEOUT"] = "30.5"  # Should be converted to float
    os.environ["DATABASE_MAX_CONNECTIONS"] = "100"  # Should be converted to int

    config_data = EnvVarConfigLoader.load("DATABASE", DatabaseConfig)

    # These fields are not in the dataclass but should still be loaded with proper types
    assert config_data["timeout"] == 30.5
    assert config_data["max_connections"] == 100


def test_boolean_conversions(clean_env):
    """Test various boolean string representations."""
    test_cases = [
        ("true", True), ("True", True), ("TRUE", True),
        ("yes", True), ("y", True), ("1", True),
        ("false", False), ("False", False), ("FALSE", False),
        ("no", False), ("n", False), ("0", False)
    ]

    for value, expected in test_cases:
        os.environ["DATABASE_USE_SSL"] = value
        config_data = EnvVarConfigLoader.load("DATABASE", DatabaseConfig)
        assert config_data["use_ssl"] is expected, f"Failed for value '{value}'"


def test_empty_values(clean_env):
    """Test handling of empty values."""
    os.environ["DATABASE_HOST"] = ""
    os.environ["DATABASE_PASSWORD"] = "   "  # Whitespace  # noqa: S105

    config_data = EnvVarConfigLoader.load("DATABASE", DatabaseConfig)

    # Empty strings should be converted to None
    assert config_data["host"] is None
    assert config_data["password"] is None


@patch.dict(os.environ, {})
def test_nested_dataclass(clean_env):
    """Test loading configuration with nested dataclasses."""
    # Parent config
    os.environ["NESTED_NAME"] = "parent_name"

    # Child config (nested field)
    os.environ["NESTED_CHILD_SETTING_A"] = "value_a"
    os.environ["NESTED_CHILD_SETTING_B"] = "42"
    os.environ["NESTED_CHILD_SETTING_C"] = "false"

    # Optional child config
    os.environ["NESTED_OPTIONAL_CHILD_SETTING_A"] = "opt_value_a"
    os.environ["NESTED_OPTIONAL_CHILD_SETTING_B"] = "24"

    config_data = ConfigBase.load(NestedParentConfig)

    # Verify parent properties
    assert config_data.name == "parent_name"

    # Verify child properties
    assert hasattr(config_data, "child")
    assert isinstance(config_data.child, NestedChildConfig)
    assert config_data.child.setting_a == "value_a"
    assert config_data.child.setting_b == 42
    assert config_data.child.setting_c is False

    # Verify optional child
    assert hasattr(config_data, "optional_child")
    assert isinstance(config_data.optional_child, NestedChildConfig)
    assert config_data.optional_child.setting_a == "opt_value_a"
    assert config_data.optional_child.setting_b == 24
    # Should use default value for setting_c (not provided in env vars)
    assert config_data.optional_child.setting_c is True


def test_uppercase_handling(clean_env):
    """Test that environment variable names are properly uppercased."""
    os.environ["DATABASE_HOST"] = "should_not_find"
    os.environ["database_host"] = "lowercase_should_not_find"
    os.environ["Database_Host"] = "mixedcase_should_not_find"

    # The loader should look for DATABASE_HOST
    config_data = EnvVarConfigLoader.load("DATABASE", DatabaseConfig)

    # Should find the uppercase version
    assert config_data["host"] == "should_not_find"


def test_integration_with_config_base(clean_env, original_loaders):
    """Test integration with ConfigBase class."""
    os.environ["DATABASE_HOST"] = "db.example.com"
    os.environ["DATABASE_PORT"] = "3306"
    os.environ["DATABASE_USERNAME"] = "admin"
    os.environ["DATABASE_PASSWORD"] = "secret"  # noqa: S105
    os.environ["DATABASE_USE_SSL"] = "true"

    # Configure ConfigBase to use EnvVarConfigLoader
    ConfigBase._loaders = [EnvVarConfigLoader]

    # Load the configuration using ConfigBase
    config = ConfigBase.load(DatabaseConfig)

    # Verify the configuration was loaded correctly
    assert config.host == "db.example.com"
    assert config.port == 3306
    assert config.username == "admin"
    assert config.password == "secret"  # noqa: S105
    assert config.use_ssl is True


def test_malformed_values(clean_env):
    """Test handling of malformed values that can't be properly converted."""
    os.environ["DATABASE_PORT"] = "not_an_integer"

    with pytest.raises(ValueError):
        ConfigBase.load(DatabaseConfig)


def test_prefix_handling(clean_env):
    """Test handling of prefixes in environment variable names."""
    # Setup variables with different prefixes
    os.environ["DATABASE_HOST"] = "db.example.com"
    os.environ["API_HOST"] = "api.example.com"
    os.environ["APP_HOST"] = "app.example.com"

    # Load with DATABASE prefix
    db_config = EnvVarConfigLoader.load("DATABASE", DatabaseConfig)
    assert db_config["host"] == "db.example.com"

    # Should not load variables with different prefixes
    assert "api_host" not in db_config
    assert "app_host" not in db_config


def test_non_dataclass_error():
    """Test that error is raised when config_class is not a dataclass."""

    class NotADataclass:
        host: str
        port: int = 5432

    with pytest.raises(TypeError):
        EnvVarConfigLoader.load("PREFIX", NotADataclass)


def test_full_config_loading(clean_env):
    """Integration test for loading a complete config with nested structures."""
    # Setup parent config
    os.environ["APP_NAME"] = "MyApp"
    os.environ["APP_VERSION"] = "1.0.0"
    os.environ["APP_DEBUG"] = "true"

    # Database config section
    os.environ["APP_DATABASE_HOST"] = "localhost"
    os.environ["APP_DATABASE_PORT"] = "5432"
    os.environ["APP_DATABASE_USERNAME"] = "user"
    os.environ["APP_DATABASE_PASSWORD"] = "pass"  # noqa: S105
    os.environ["APP_DATABASE_USE_SSL"] = "true"

    # API config section
    os.environ["APP_API_URL"] = "https://api.example.com"
    os.environ["APP_API_TIMEOUT"] = "30"
    os.environ["APP_API_RETRY_COUNT"] = "3"

    # Define the app config class structure
    @config_class(file_name="app")
    class ApiConfig:
        url: str
        timeout: int
        retry_count: int = 0

    @config_class(file_name="app")
    class AppConfig:
        name: str
        version: str
        api: ApiConfig
        database: DatabaseConfig
        debug: bool = False

    # Load using EnvVarConfigLoader
    config_data = ConfigBase.load(AppConfig)

    # Verify top-level properties
    assert config_data.name == "MyApp"
    assert config_data.version == "1.0.0"
    assert config_data.debug is True

    # Verify database section
    assert hasattr(config_data, "database")
    assert isinstance(config_data.database, DatabaseConfig)
    assert config_data.database.host == "localhost"
    assert config_data.database.port == 5432
    assert config_data.database.username == "user"
    assert config_data.database.password == "pass"  # noqa: S105
    assert config_data.database.use_ssl is True

    # Verify API section
    assert hasattr(config_data, "api")
    assert isinstance(config_data.api, ApiConfig)
    assert config_data.api.url == "https://api.example.com"
    assert config_data.api.timeout == 30
    assert config_data.api.retry_count == 3
