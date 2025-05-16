import dataclasses
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

from configr.base import ConfigBase
from configr.config_class import config_class
from configr.exceptions import ConfigFileNotFoundError
from configr.loaders.loader_base import FileConfigLoader
from configr.loaders.loader_env_var import EnvVarConfigLoader
from configr.loaders.loader_json import JSONConfigLoader
from configr.loaders.loader_yaml import YAMLConfigLoader


@pytest.fixture
def config_dir():
    """Fixture to create and manage temporary config directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir)
        ConfigBase.set_config_dir(config_dir)

        # Create JSON config file
        json_config = {
            "host": "localhost",
            "port": 5432,
            "debug": True
        }
        with open(config_dir / "database.json", "w") as f:
            json.dump(json_config, f)

        # Create YAML config file
        yaml_config = {
            "api_key": "test_key_123",
            "timeout": 30,
            "retry_attempts": 3
        }
        with open(config_dir / "api_settings.yaml", "w") as f:
            yaml.dump(yaml_config, f)

        # Create YML config file
        yml_config = {
            "log_level": "INFO",
            "log_file": "/var/log/app.log",
            "rotate": True
        }
        with open(config_dir / "logging_config.yml", "w") as f:
            yaml.dump(yml_config, f)

        # Create config file with custom name
        custom_config = {
            "theme": "dark",
            "font_size": 12,
            "show_line_numbers": True
        }
        with open(config_dir / "ui_settings.json", "w") as f:
            json.dump(custom_config, f)

        yield config_dir


def test_config_dir_management(config_dir):
    """Test setting and getting the config directory."""
    # Test with string path
    test_path = "/test/configs"
    ConfigBase.set_config_dir(test_path)

    # Convert to path so it works on all platforms
    for loaders in ConfigBase.get_available_file_loaders():
        assert Path(str(loaders.get_config_path())) == Path(test_path)

    # Test with Path object
    test_path_obj = Path("/var/configs")
    ConfigBase.set_config_dir(test_path_obj)
    for loaders in ConfigBase.get_available_file_loaders():
        assert loaders.get_config_path() == test_path_obj

    # Reset to our test directory
    ConfigBase.set_config_dir(config_dir)


def test_available_loaders():
    """Test getting available loaders."""
    loaders = ConfigBase.get_available_loaders()
    for loader in loaders:
        if isinstance(loader, JSONConfigLoader):
            assert ".json" in loader.ext

        if isinstance(loader, YAMLConfigLoader):
            assert ".yaml" in loader.ext
            assert ".yml" in loader.ext

        if isinstance(loader, EnvVarConfigLoader):
            assert not hasattr(loader, "ext")


def test_config_class_decorator_default_naming():
    """Test config_class decorator with default naming."""

    @config_class
    class DatabaseConfig:
        host: str
        port: int
        debug: bool

    # Check that file name is set to snake case of class name with default extension
    assert DatabaseConfig._config_file_name == "database_config"


def test_config_class_decorator_explicit_naming(config_dir):
    """Test config_class decorator with explicit file naming."""

    @config_class(file_name="database.json")
    class DbConfig:
        host: str
        port: int
        debug: bool

    # Check that file name is set correctly
    assert DbConfig._config_file_name == "database.json"

    # Load the config
    config = ConfigBase.load(DbConfig)
    assert config.host == "localhost"
    assert config.port == 5432
    assert config.debug is True


def test_config_class_decorator_with_extension(config_dir):
    """Test config_class decorator with file name that includes extension."""

    @config_class(file_name="api_settings.yaml")
    class ApiConfig:
        api_key: str
        timeout: int
        retry_attempts: int

    # Check that file name is set correctly
    assert ApiConfig._config_file_name == "api_settings.yaml"

    # Load the config
    config = ConfigBase.load(ApiConfig)
    assert config.api_key == "test_key_123"
    assert config.timeout == 30
    assert config.retry_attempts == 3


def test_config_class_decorator_without_extension(config_dir):
    """Test config_class decorator with file name that doesn't include extension."""

    @config_class(file_name="ui_settings")
    class UiConfig:
        theme: str
        font_size: int
        show_line_numbers: bool

    # Check that default extension was added
    assert UiConfig._config_file_name == "ui_settings"

    # Load the config
    config = ConfigBase.load(UiConfig)
    assert config.theme == "dark"
    assert config.font_size == 12
    assert config.show_line_numbers is True


def test_yml_extension_loading(config_dir):
    """Test loading from configr.yml extension."""

    @config_class(file_name="logging_config.yml")
    class LoggingConfig:
        log_level: str
        log_file: str
        rotate: bool

    # Load the config
    config = ConfigBase.load(LoggingConfig)
    assert config.log_level == "INFO"
    assert config.log_file == "/var/log/app.log"
    assert config.rotate is True


def test_load_with_direct_data():
    """Test loading config directly from dict data."""

    @config_class
    class TestConfig:
        name: str
        value: int

    data = {"name": "test", "value": 42}
    config = ConfigBase.load(TestConfig, config_data=data)

    assert config.name == "test"
    assert config.value == 42


def test_invalid_file_extension(config_dir):
    """Test error when using an unsupported file extension."""

    @config_class(file_name="config.toml")
    class TomlConfig:
        setting: str

    with pytest.raises(ConfigFileNotFoundError) as excinfo:
        ConfigBase.load(TomlConfig)

    assert "Configuration file not found" in str(excinfo.value)


def test_non_dataclass_error():
    """Test error when using a non-dataclass type."""

    class RegularClass:
        _config_file_name = "regular.json"

    with pytest.raises(TypeError) as excinfo:
        ConfigBase.load(RegularClass)

    assert "must be a dataclass" in str(excinfo.value)


def test_missing_config_file_name():
    """Test error when config class doesn't have _config_file_name."""

    # This is a dataclass but without _config_file_name
    @dataclasses.dataclass
    class MissingFileNameConfig:
        setting: str

    with pytest.raises(ValueError) as excinfo:
        ConfigBase.load(MissingFileNameConfig)

    assert "must have a _config_file_name attribute" in str(excinfo.value)


def test_multiple_extensions_handling(config_dir):
    """Test handling of files with multiple extensions."""
    # Create config file with multiple extensions
    config_data = {"version": "1.0", "enabled": True}
    with open(config_dir / "app.config.json", "w") as f:
        json.dump(config_data, f)

    @config_class(file_name="app.config.json")
    class AppConfig:
        version: str
        enabled: bool

    config = ConfigBase.load(AppConfig)
    assert config.version == "1.0"
    assert config.enabled is True


def test_filter_extra_fields(config_dir):
    """Test that extra fields in a config file are filtered out."""
    # Create config with extra fields
    config_data = {
        "host": "localhost",
        "port": 5432,
        "extra_field": "this should be ignored"
    }

    with open(config_dir / "db_with_extra.json", "w") as f:
        json.dump(config_data, f)

    @config_class(file_name="db_with_extra.json")
    class DbWithExtraConfig:
        host: str
        port: int

    config = ConfigBase.load(DbWithExtraConfig)
    assert config.host == "localhost"
    assert config.port == 5432
    # Verify that extra_field was filtered out
    assert not hasattr(config, "extra_field")


def test_custom_loader(config_dir):
    """Test adding a custom loader."""
    # Create an empty config file for the custom loader
    open(config_dir / "test.custom", "a").close()

    # Define a mock custom loader
    class CustomLoader(FileConfigLoader, MagicMock):
        ext: list[str] = [".custom"]

        @classmethod
        def load(cls, name: str, config_class: type) -> dict:
            return {"custom": "value"}

    # Add custom loader to ConfigBase
    ConfigBase.add_loader(CustomLoader)
    try:
        @config_class(file_name="test.custom")
        class CustomConfig:
            custom: str

        # We don't need an actual file since our mock loader ignores the path
        config = ConfigBase.load(CustomConfig)
        assert config.custom == "value"

    finally:
        # Restore original loaders
        ConfigBase.remove_loader(".custom")
