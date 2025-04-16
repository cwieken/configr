import os
import tempfile
import json
import yaml
import pytest
from pathlib import Path
from dataclasses import dataclass
from unittest.mock import patch, MagicMock

from src.base import ConfigBase
from src.exceptions import ConfigFileNotFoundError


@dataclass
class TestConfig:
    name: str
    value: int
    enabled: bool = True


@dataclass
class CustomNameConfig:
    host: str
    port: int
    _config_file_name = "custom_config.json"


@pytest.fixture
def config_dir():
    """Create a temporary directory for test configs"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_config_dir(config_dir, monkeypatch):
    """Patch the ConfigBase._config_dir to use our temporary directory"""
    monkeypatch.setattr(ConfigBase, '_config_dir', str(config_dir))
    return config_dir


@pytest.fixture
def test_configs(mock_config_dir):
    """Create test configuration files"""
    # Create JSON config
    json_config = {
        "name": "test",
        "value": 42,
        "enabled": True
    }
    json_path = mock_config_dir / "test_config.json"
    with open(json_path, 'w') as f:
        json.dump(json_config, f)

    # Create YAML config
    yaml_config = {
        "name": "yaml_test",
        "value": 100,
        "enabled": False
    }
    yaml_path = mock_config_dir / "test_config.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_config, f)

    # Create custom named config
    custom_config = {
        "host": "localhost",
        "port": 5432
    }
    custom_path = mock_config_dir / "custom_config.json"
    with open(custom_path, 'w') as f:
        json.dump(custom_config, f)

    # Create config with extra fields
    extra_config = {
        "name": "extra",
        "value": 123,
        "enabled": True,
        "extra_field": "should be ignored"
    }
    extra_path = mock_config_dir / "extra_config.json"
    with open(extra_path, 'w') as f:
        json.dump(extra_config, f)

    return mock_config_dir


def test_config_path_property(mock_config_dir):
    """Test the config_path property returns the correct path"""
    config_base = ConfigBase()
    assert config_base.get_config_path() == mock_config_dir


def test_load_json_config(test_configs):
    """Test loading a JSON configuration file"""
    config = ConfigBase.load(TestConfig)
    assert isinstance(config, TestConfig)
    assert config.name == "test"
    assert config.value == 42
    assert config.enabled is True


def test_load_yaml_config(test_configs):
    """Test loading a YAML configuration file"""
    config = ConfigBase.load(TestConfig)
    assert isinstance(config, TestConfig)
    assert config.name == "yaml_test"
    assert config.value == 100
    assert config.enabled is False


def test_load_with_class_name(test_configs):
    """Test loading a config using the class's default name"""
    # Create a config file with the default name
    default_config = {
        "name": "default",
        "value": 999
    }
    default_path = test_configs / "test_config.json"
    with open(default_path, 'w') as f:
        json.dump(default_config, f)

    config = ConfigBase.load(TestConfig)
    assert config.name == "default"
    assert config.value == 999


def test_load_with_custom_file_name(test_configs):
    """Test loading a config with a custom file name from the class"""
    config = ConfigBase.load(CustomNameConfig)
    assert config.host == "localhost"
    assert config.port == 5432


def test_file_not_found(test_configs):
    """Test that an error is raised when the config file doesn't exist"""
    with pytest.raises(ConfigFileNotFoundError):
        ConfigBase.load(TestConfig, "nonexistent.json")


def test_unsupported_extension(test_configs):
    """Test that an error is raised for unsupported file extensions"""
    # Create a file with unsupported extension
    with open(test_configs / "test.txt", 'w') as f:
        f.write("name: test\nvalue: 42\nenabled: true")

    with pytest.raises(ValueError):
        ConfigBase.load(TestConfig, "test.txt")


def test_not_a_dataclass(test_configs):
    """Test that an error is raised when the config class is not a dataclass"""

    class NotADataclass:
        pass

    with pytest.raises(TypeError):
        ConfigBase.load(NotADataclass)


def test_filter_extra_fields(test_configs):
    """Test that extra fields in the config file are filtered out"""
    config = ConfigBase.load(TestConfig, "extra_config.json")
    # Verify the dataclass doesn't have the extra field
    with pytest.raises(AttributeError):
        config.extra_field


def test_config_dir_from_env(monkeypatch):
    """Test that the config directory can be set from environment variable"""
    # Set environment variable
    monkeypatch.setenv("CONFIG_DIR", "/custom/config/path")
    # Reset the class to pick up the environment variable
    monkeypatch.setattr(ConfigBase, '_config_dir', os.environ.get('CONFIG_DIR', '_config'))

    config_base = ConfigBase()
    assert str(config_base.get_config_path()) == "/custom/config/path"
