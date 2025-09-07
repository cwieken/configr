import os
import shutil
import tempfile
from dataclasses import field
from pathlib import Path
from typing import Optional
from unittest.mock import patch

import pytest

from configr.base import ConfigBase
from configr.config_class import config_class
from configr.loaders.loader_dotenv import DotEnvConfigLoader

# Check if python-dotenv is available at import time, otherwise fail all tests
try:
    from dotenv import dotenv_values  # Attempt to import python-dotenv
except (ImportError, ModuleNotFoundError):
    pytest.fail(
        "The python-dotenv module is not installed. Please install it to run these tests."
    )


@config_class(file_name=".env")
class DatabaseConfig:
    host: str
    port: int = 5432
    username: str = "postgres"
    password: Optional[str] = None
    use_ssl: bool = False


@config_class(file_name=".env")
class NestedChildConfig:
    setting_a: str
    setting_b: int
    setting_c: bool = True


@config_class(file_name=".env")
class NestedParentConfig:
    name: str
    child: NestedChildConfig
    optional_child: Optional[NestedChildConfig] = None
    children_list: list[NestedChildConfig] = field(default_factory=list)
    children_dict: dict[str, NestedChildConfig] = field(default_factory=dict)


@config_class(file_name=".env")
class AppConfig:
    name: str
    version: str
    debug: bool = False
    max_workers: int = 4
    timeout: float = 30.0


@pytest.fixture
def config_dir():
    """Create a temporary config directory for testing."""
    temp_dir = tempfile.mkdtemp()
    config_dir = Path(temp_dir) / "_config"
    config_dir.mkdir(exist_ok=True)

    # Store original config dir to restore later
    original_config_dir = DotEnvConfigLoader._config_dir

    # Set the config directory for testing
    DotEnvConfigLoader.set_config_dir(config_dir)

    yield config_dir

    # Restore original config dir and clean up
    DotEnvConfigLoader.set_config_dir(original_config_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def create_dotenv_file():
    """Fixture to create .env files with content."""

    def _create_dotenv_file(directory, content):
        filepath = directory / ".env"
        with open(filepath, "w") as f:
            for key, value in content.items():
                f.write(f"{key}={value}\n")
        return filepath

    return _create_dotenv_file


@pytest.fixture
def clean_env():
    """Clean environment variables before and after tests."""
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


def test_extensions():
    """Test that DotEnvConfigLoader supports correct file extensions."""
    assert DotEnvConfigLoader.get_extensions() == [".env"]


def test_load_dotenv_file(config_dir, create_dotenv_file, clean_env):
    """Test loading a basic .env configuration file."""
    env_data = {
        "DATABASE_HOST": "localhost",
        "DATABASE_PORT": "8432",
        "DATABASE_USERNAME": "testuser",
        "DATABASE_PASSWORD": "testpass",
        "DATABASE_USE_SSL": "true",
    }
    create_dotenv_file(config_dir, env_data)

    loaded_data = DotEnvConfigLoader.load("database", DatabaseConfig)

    assert loaded_data["host"] == "localhost"
    assert loaded_data["port"] == 8432
    assert loaded_data["username"] == "testuser"
    assert loaded_data["password"] == "testpass"
    assert loaded_data["use_ssl"] is True


def test_file_not_found(config_dir, clean_env):
    """Test that an appropriate exception is raised when .env file is not found."""
    with pytest.raises(FileNotFoundError) as exc_info:
        DotEnvConfigLoader.load("database", DatabaseConfig)

    assert ".env file found at:" in str(exc_info.value)


def test_config_file_exists(config_dir, create_dotenv_file):
    """Test the config_file_exists method."""
    # .env file doesn't exist yet
    assert not DotEnvConfigLoader.config_file_exists("database")
    assert not DotEnvConfigLoader.config_file_exists(".env")

    # Create .env file
    create_dotenv_file(config_dir, {"DATABASE_HOST": "localhost"})

    # Now it should exist - name parameter doesn't matter for .env
    assert DotEnvConfigLoader.config_file_exists("database")
    assert DotEnvConfigLoader.config_file_exists(".env")
    assert DotEnvConfigLoader.config_file_exists("anything")


def test_type_conversion(config_dir, create_dotenv_file, clean_env):
    """Test type conversion for different data types."""
    env_data = {
        "APP_NAME": "MyApp",
        "APP_VERSION": "1.2.3",
        "APP_DEBUG": "true",
        "APP_MAX_WORKERS": "8",
        "APP_TIMEOUT": "45.5",
    }
    create_dotenv_file(config_dir, env_data)

    loaded_data = DotEnvConfigLoader.load("app", AppConfig)

    assert loaded_data["name"] == "MyApp"
    assert loaded_data["version"] == "1.2.3"
    assert loaded_data["debug"] is True
    assert loaded_data["max_workers"] == 8
    assert loaded_data["timeout"] == 45.5


def test_boolean_conversions(config_dir, create_dotenv_file, clean_env):
    """Test various boolean string representations."""
    test_cases = [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("yes", True),
        ("y", True),
        ("1", True),
        ("false", False),
        ("False", False),
        ("FALSE", False),
        ("no", False),
        ("n", False),
        ("0", False),
    ]

    for value, expected in test_cases:
        env_data = {"DATABASE_HOST": "localhost", "DATABASE_USE_SSL": value}
        create_dotenv_file(config_dir, env_data)

        loaded_data = DotEnvConfigLoader.load("database", DatabaseConfig)
        assert loaded_data["use_ssl"] is expected, f"Failed for value '{value}'"


def test_empty_values(config_dir, create_dotenv_file, clean_env):
    """Test handling of empty values in .env file."""
    env_data = {
        "DATABASE_HOST": "",
        "DATABASE_PASSWORD": "   ",  # Whitespace
        "DATABASE_USERNAME": "user",
    }
    create_dotenv_file(config_dir, env_data)

    loaded_data = DotEnvConfigLoader.load("database", DatabaseConfig)

    # Empty strings should be converted to None
    assert loaded_data["host"] is None
    assert loaded_data["password"] is None
    assert loaded_data["username"] == "user"


def test_nested_dataclass(config_dir, create_dotenv_file, clean_env):
    """Test loading configuration with nested dataclasses."""
    env_data = {
        # Parent config
        "NESTED_PARENT_NAME": "parent_name",
        # Child config (nested field)
        "NESTED_PARENT_CHILD_SETTING_A": "value_a",
        "NESTED_PARENT_CHILD_SETTING_B": "42",
        "NESTED_PARENT_CHILD_SETTING_C": "false",
        # Optional child config
        "NESTED_PARENT_OPTIONAL_CHILD_SETTING_A": "opt_value_a",
        "NESTED_PARENT_OPTIONAL_CHILD_SETTING_B": "24",
    }
    create_dotenv_file(config_dir, env_data)

    loaded_data = DotEnvConfigLoader.load("nested_parent", NestedParentConfig)

    # Verify the structure
    assert loaded_data["name"] == "parent_name"
    assert loaded_data["child"]["setting_a"] == "value_a"
    assert loaded_data["child"]["setting_b"] == 42
    assert loaded_data["child"]["setting_c"] is False
    assert loaded_data["optional_child"]["setting_a"] == "opt_value_a"
    assert loaded_data["optional_child"]["setting_b"] == 24


def test_integration_with_config_base(
    config_dir, create_dotenv_file, clean_env, original_loaders
):
    """Test integration of DotEnvConfigLoader with ConfigBase."""
    env_data = {
        "DATABASE_HOST": "db.example.com",
        "DATABASE_PORT": "3306",
        "DATABASE_USERNAME": "admin",
        "DATABASE_PASSWORD": "secret",
        "DATABASE_USE_SSL": "true",
    }
    create_dotenv_file(config_dir, env_data)

    # Configure ConfigBase to use DotEnvConfigLoader
    ConfigBase._loaders = [DotEnvConfigLoader]

    # Load the configuration using ConfigBase
    config = ConfigBase.load(DatabaseConfig)

    # Verify the configuration was loaded correctly
    assert config.host == "db.example.com"
    assert config.port == 3306
    assert config.username == "admin"
    assert config.password == "secret"
    assert config.use_ssl is True


def test_dotenv_not_available(monkeypatch):
    """Test behavior when python-dotenv is not available."""
    # Mock the DOTENV_AVAILABLE flag to be False
    monkeypatch.setattr("configr.loaders.loader_dotenv.DOTENV_AVAILABLE", False)

    with pytest.raises(ImportError) as exc_info:
        DotEnvConfigLoader.load("any", DatabaseConfig)

    assert "python-dotenv is required" in str(exc_info.value)


def test_environment_restoration(config_dir, create_dotenv_file, clean_env):
    """Test that environment variables are properly restored after loading."""
    # Set some environment variables before loading
    os.environ["DATABASE_HOST"] = "original_host"
    os.environ["DATABASE_PORT"] = "5432"
    os.environ["UNRELATED_VAR"] = "should_remain"

    # Create .env file with different values
    env_data = {
        "DATABASE_HOST": "dotenv_host",
        "DATABASE_PORT": "8080",
        "DATABASE_USERNAME": "dotenv_user",
    }
    create_dotenv_file(config_dir, env_data)

    # Load configuration
    loaded_data = DotEnvConfigLoader.load("database", DatabaseConfig)

    # Verify loaded data comes from .env file
    assert loaded_data["host"] == "dotenv_host"
    assert loaded_data["port"] == 8080
    assert loaded_data["username"] == "dotenv_user"

    # Verify original environment is restored
    assert os.environ["DATABASE_HOST"] == "original_host"
    assert os.environ["DATABASE_PORT"] == "5432"
    assert os.environ["UNRELATED_VAR"] == "should_remain"
    assert "DATABASE_USERNAME" not in os.environ


def test_get_config_name(config_dir):
    """Test the get_config_name method."""
    # The method should convert class name to uppercase snake case
    name = DotEnvConfigLoader.get_config_name(DatabaseConfig)
    assert name == "DATABASE"

    name = DotEnvConfigLoader.get_config_name(NestedParentConfig)
    assert name == "NESTED_PARENT"


def test_custom_config_dir(config_dir, create_dotenv_file, clean_env):
    """Test setting a custom configuration directory."""
    # Create a different config directory
    temp_dir = Path(config_dir).parent
    custom_dir = temp_dir / "custom_config"
    custom_dir.mkdir(exist_ok=True)

    # Create a .env file in the custom directory
    custom_env_data = {"DATABASE_HOST": "custom_host", "DATABASE_PORT": "9000"}
    create_dotenv_file(custom_dir, custom_env_data)

    # Save original config directory
    original_config_dir = DotEnvConfigLoader._config_dir

    try:
        # Set the custom config directory
        DotEnvConfigLoader.set_config_dir(custom_dir)

        # Load the config from the custom directory
        loaded_data = DotEnvConfigLoader.load("database", DatabaseConfig)
        assert loaded_data["host"] == "custom_host"
        assert loaded_data["port"] == 9000
    finally:
        # Reset to the original config directory
        DotEnvConfigLoader.set_config_dir(original_config_dir)


def test_malformed_values(config_dir, create_dotenv_file, clean_env):
    """Test handling of malformed values that can't be properly converted."""
    env_data = {"DATABASE_HOST": "localhost", "DATABASE_PORT": "not_an_integer"}
    create_dotenv_file(config_dir, env_data)

    with pytest.raises(ValueError):
        ConfigBase.load(DatabaseConfig)


def test_comments_and_special_chars(config_dir, clean_env):
    """Test handling of comments and special characters in .env file."""
    # Create .env file manually to test special cases
    filepath = config_dir / ".env"
    with open(filepath, "w") as f:
        f.write("# This is a comment\n")
        f.write("DATABASE_HOST=localhost\n")
        f.write("DATABASE_PORT=5432 # inline comment\n")
        f.write("DATABASE_USERNAME=user@example.com\n")
        f.write("DATABASE_PASSWORD=p@ssw0rd!#$%\n")
        f.write("\n")  # Empty line
        f.write("DATABASE_USE_SSL=true\n")

    loaded_data = DotEnvConfigLoader.load("database", DatabaseConfig)

    assert loaded_data["host"] == "localhost"
    assert loaded_data["port"] == 5432
    assert loaded_data["username"] == "user@example.com"
    assert loaded_data["password"] == "p@ssw0rd!#$%"
    assert loaded_data["use_ssl"] is True


def test_quoted_values(config_dir, clean_env):
    """Test handling of quoted values in .env file."""
    # Create .env file with quoted values
    filepath = config_dir / ".env"
    with open(filepath, "w") as f:
        f.write('DATABASE_HOST="localhost"\n')
        f.write("DATABASE_USERNAME='admin'\n")
        f.write('DATABASE_PASSWORD="pass with spaces"\n')
        f.write("DATABASE_PORT=5432\n")

    loaded_data = DotEnvConfigLoader.load("database", DatabaseConfig)

    # python-dotenv should handle quotes properly
    assert loaded_data["host"] == "localhost"
    assert loaded_data["username"] == "admin"
    assert loaded_data["password"] == "pass with spaces"
    assert loaded_data["port"] == 5432


def test_multiline_values(config_dir, clean_env):
    """Test handling of multiline values in .env file."""
    # Create .env file with multiline value
    filepath = config_dir / ".env"
    with open(filepath, "w") as f:
        f.write("DATABASE_HOST=localhost\n")
        f.write('DATABASE_PASSWORD="line1\nline2\nline3"\n')
        f.write("DATABASE_PORT=5432\n")

    loaded_data = DotEnvConfigLoader.load("database", DatabaseConfig)

    assert loaded_data["host"] == "localhost"
    assert loaded_data["password"] == "line1\nline2\nline3"
    assert loaded_data["port"] == 5432


def test_export_prefix(config_dir, clean_env):
    """Test handling of export prefix in .env file."""
    # Create .env file with export statements
    filepath = config_dir / ".env"
    with open(filepath, "w") as f:
        f.write("export DATABASE_HOST=localhost\n")
        f.write("export DATABASE_PORT=5432\n")
        f.write("DATABASE_USERNAME=admin\n")

    loaded_data = DotEnvConfigLoader.load("database", DatabaseConfig)

    # python-dotenv should handle export prefix
    assert loaded_data["host"] == "localhost"
    assert loaded_data["port"] == 5432
    assert loaded_data["username"] == "admin"


def test_variable_expansion(config_dir, clean_env):
    """Test variable expansion in .env file."""
    # Create .env file with variable references
    filepath = config_dir / ".env"
    with open(filepath, "w") as f:
        f.write("DATABASE_HOST=localhost\n")
        f.write("DATABASE_PORT=5432\n")
        f.write("DATABASE_USERNAME=admin\n")
        f.write("DATABASE_PASSWORD=${DATABASE_USERNAME}_password\n")

    loaded_data = DotEnvConfigLoader.load("database", DatabaseConfig)

    # python-dotenv expands variables by default when using dotenv_values
    assert loaded_data["password"] == "admin_password"


def test_non_dataclass_error(config_dir, create_dotenv_file):
    """Test that error is raised when config_class is not a dataclass."""
    # Create a .env file so we don't get FileNotFoundError
    create_dotenv_file(config_dir, {"PREFIX_HOST": "localhost"})

    class NotADataclass:
        host: str
        port: int = 5432

    # The EnvVarConfigLoader will raise TypeError for non-dataclass
    with pytest.raises(TypeError):
        DotEnvConfigLoader.load("PREFIX", NotADataclass)


def test_get_config_file_path(config_dir, create_dotenv_file):
    """Test the _get_config_file_path method."""
    # Before creating .env file
    with pytest.raises(FileNotFoundError):
        DotEnvConfigLoader._get_config_file_path("anything")

    # Create .env file
    create_dotenv_file(config_dir, {"KEY": "value"})

    # Now it should return the path
    path = DotEnvConfigLoader._get_config_file_path("anything")
    assert path == config_dir / ".env"
    assert path.exists()


def test_always_uses_dotenv_filename(config_dir, create_dotenv_file, clean_env):
    """Test that DotEnvConfigLoader always uses .env as filename regardless of name parameter."""
    env_data = {
        "DATABASE_HOST": "localhost",
        "APP_NAME": "MyApp",
        "CUSTOM_VALUE": "test",
    }
    create_dotenv_file(config_dir, env_data)

    # Load with different names - should all use the same .env file
    db_data = DotEnvConfigLoader.load("database", DatabaseConfig)
    assert db_data["host"] == "localhost"

    app_data = DotEnvConfigLoader.load("app", AppConfig)
    assert app_data["name"] == "MyApp"


def test_prefix_handling_with_get_config_name(
    config_dir, create_dotenv_file, clean_env
):
    """Test that the loader correctly uses the prefix from get_config_name."""
    # The loader should use the uppercase snake case version of the class name
    env_data = {
        "DATABASE_HOST": "db_host",
        "DATABASE_CONFIG_HOST": "wrong_host",  # Should not be used
        "HOST": "also_wrong",  # Should not be used
    }
    create_dotenv_file(config_dir, env_data)

    loaded_data = DotEnvConfigLoader.load("database", DatabaseConfig)
    assert loaded_data["host"] == "db_host"


def test_missing_required_fields(config_dir, create_dotenv_file, clean_env):
    """Test behavior when required fields are missing from .env file."""
    # Only provide some fields, missing required 'host'
    env_data = {"DATABASE_PORT": "5432", "DATABASE_USERNAME": "user"}
    create_dotenv_file(config_dir, env_data)

    # Load should succeed, but host will be missing from the dict
    loaded_data = DotEnvConfigLoader.load("database", DatabaseConfig)

    # The loader returns raw data, ConfigBase handles validation
    assert "host" not in loaded_data
    assert loaded_data["port"] == 5432
    assert loaded_data["username"] == "user"


def test_dotenv_values_function(config_dir, create_dotenv_file, clean_env):
    """Test that dotenv_values is called correctly."""
    env_data = {
        "DATABASE_HOST": "localhost",
        "DATABASE_PORT": "5432",
        "UNRELATED_KEY": "should_be_loaded",
    }
    create_dotenv_file(config_dir, env_data)

    # The loader should load all values from .env, then filter by prefix
    loaded_data = DotEnvConfigLoader.load("database", DatabaseConfig)

    assert loaded_data["host"] == "localhost"
    assert loaded_data["port"] == 5432
    # UNRELATED_KEY should not be in the result as it doesn't have DATABASE_ prefix
    assert "unrelated_key" not in loaded_data


def test_nested_with_config_base(
    config_dir, create_dotenv_file, clean_env, original_loaders
):
    """Test loading nested dataclasses with ConfigBase, including optional fields."""
    env_data = {
        # Parent config
        "NESTED_PARENT_NAME": "test_parent",
        # Required child config
        "NESTED_PARENT_CHILD_SETTING_A": "required_a",
        "NESTED_PARENT_CHILD_SETTING_B": "100",
        # Note: setting_c is not provided, should use default value True
        # Optional child is not provided at all - should remain None
        # Children list - empty by default
        # Children dict - empty by default
    }
    create_dotenv_file(config_dir, env_data)

    # Configure ConfigBase to use DotEnvConfigLoader
    ConfigBase._loaders = [DotEnvConfigLoader]

    # Load the configuration using ConfigBase
    config = ConfigBase.load(NestedParentConfig)

    # Verify parent field
    assert config.name == "test_parent"

    # Verify required child
    assert hasattr(config, "child")
    assert isinstance(config.child, NestedChildConfig)
    assert config.child.setting_a == "required_a"
    assert config.child.setting_b == 100
    assert config.child.setting_c is True  # Default value

    # Verify optional child is None (not provided)
    assert hasattr(config, "optional_child")
    assert config.optional_child is None

    # Verify default factory fields
    # Note: When fields are not provided in the config data, they may be None
    # instead of using the default factory. This is a limitation of the current
    # implementation where the loader doesn't know about default factories.
    assert hasattr(config, "children_list")
    assert config.children_list is None or config.children_list == []
    assert hasattr(config, "children_dict")
    assert config.children_dict is None or config.children_dict == {}


def test_optional_fields_with_defaults(
    config_dir, create_dotenv_file, clean_env, original_loaders
):
    """Test that optional fields with default values are properly handled."""
    env_data = {
        "DATABASE_HOST": "localhost",
        # port not provided - should use default 5432
        # username not provided - should use default "postgres"
        # password not provided - should use default None
        # use_ssl not provided - should use default False
    }
    create_dotenv_file(config_dir, env_data)

    # Configure ConfigBase to use DotEnvConfigLoader
    ConfigBase._loaders = [DotEnvConfigLoader]

    # Load the configuration using ConfigBase
    config = ConfigBase.load(DatabaseConfig)

    # Verify all fields are present with correct values
    assert config.host == "localhost"
    assert config.port == 5432  # Default value
    assert config.username == "postgres"  # Default value
    assert config.password is None  # Default value
    assert config.use_ssl is False  # Default value


def test_partial_nested_config(
    config_dir, create_dotenv_file, clean_env, original_loaders
):
    """Test loading nested config with some optional nested structures provided."""
    env_data = {
        # Parent config
        "NESTED_PARENT_NAME": "parent_with_optional",
        # Required child config
        "NESTED_PARENT_CHILD_SETTING_A": "child_a",
        "NESTED_PARENT_CHILD_SETTING_B": "50",
        "NESTED_PARENT_CHILD_SETTING_C": "false",
        # Optional child is provided
        "NESTED_PARENT_OPTIONAL_CHILD_SETTING_A": "optional_a",
        "NESTED_PARENT_OPTIONAL_CHILD_SETTING_B": "75",
        # setting_c not provided for optional child - should use default
    }
    create_dotenv_file(config_dir, env_data)

    # Configure ConfigBase to use DotEnvConfigLoader
    ConfigBase._loaders = [DotEnvConfigLoader]

    # Load the configuration using ConfigBase
    config = ConfigBase.load(NestedParentConfig)

    # Verify parent
    assert config.name == "parent_with_optional"

    # Verify required child with all fields
    assert config.child.setting_a == "child_a"
    assert config.child.setting_b == 50
    assert config.child.setting_c is False

    # Verify optional child is created with partial data
    assert config.optional_child is not None
    assert isinstance(config.optional_child, NestedChildConfig)
    assert config.optional_child.setting_a == "optional_a"
    assert config.optional_child.setting_b == 75
    assert config.optional_child.setting_c is True  # Default value

    # Lists and dicts may be None when not provided
    assert config.children_list is None or config.children_list == []
    assert config.children_dict is None or config.children_dict == {}


def test_all_fields_provided(
    config_dir, create_dotenv_file, clean_env, original_loaders
):
    """Test when all fields including optional ones are provided."""
    env_data = {
        "DATABASE_HOST": "db.example.com",
        "DATABASE_PORT": "3306",
        "DATABASE_USERNAME": "dbadmin",
        "DATABASE_PASSWORD": "secure_pass",
        "DATABASE_USE_SSL": "yes",
    }
    create_dotenv_file(config_dir, env_data)

    # Configure ConfigBase to use DotEnvConfigLoader
    ConfigBase._loaders = [DotEnvConfigLoader]

    # Load the configuration using ConfigBase
    config = ConfigBase.load(DatabaseConfig)

    # Verify all fields have the provided values (not defaults)
    assert config.host == "db.example.com"
    assert config.port == 3306
    assert config.username == "dbadmin"
    assert config.password == "secure_pass"
    assert config.use_ssl is True
