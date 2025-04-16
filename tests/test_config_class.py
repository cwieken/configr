import pytest
import dataclasses
from unittest.mock import patch, MagicMock

from src.config_class import config_class
from src.base import ConfigBase


@pytest.fixture
def mock_loaders():
    """Mock the ConfigBase.get_available_loaders method"""
    with patch.object(ConfigBase, 'get_available_loaders', return_value={
        '.json': 'JSONConfigLoader',
        '.yaml': 'YAMLConfigLoader',
        '.yml': 'YAMLConfigLoader'
    }) as mock:
        yield mock


def test_config_class_basic_usage(mock_loaders):
    """Test basic usage of config_class decorator without arguments"""

    @config_class
    class TestConfig:
        name: str
        value: int

    # Check that it's a dataclass
    assert dataclasses.is_dataclass(TestConfig)

    # Check default file name (snake case of class name + .json)
    assert hasattr(TestConfig, '_config_file_name')
    assert TestConfig._config_file_name == 'test_config.json'


def test_config_class_with_file_name(mock_loaders):
    """Test config_class decorator with custom file name"""

    @config_class(file_name="custom_config.json")
    class TestConfig:
        name: str
        value: int

    assert dataclasses.is_dataclass(TestConfig)
    assert TestConfig._config_file_name == "custom_config.json"


def test_config_class_with_yaml_extension(mock_loaders):
    """Test config_class decorator with YAML file extension"""

    @config_class(file_name="config.yaml")
    class TestConfig:
        name: str
        value: int

    assert TestConfig._config_file_name == "config.yaml"

def test_config_class_with_complex_name(mock_loaders):
    """Test config_class decorator with a complex class name"""

    @config_class
    class APIServiceConfig:
        url: str
        timeout: int

    # Should convert APIServiceConfig to api_service_config.json
    assert APIServiceConfig._config_file_name == "api_service_config.json"


def test_config_class_without_extension(mock_loaders):
    """Test config_class decorator with file name without extension"""

    @config_class(file_name="config_without_extension")
    class TestConfig:
        name: str
        value: int

    # Should add default extension (.json)
    assert TestConfig._config_file_name == "config_without_extension.json"


def test_config_class_with_unsupported_extension(mock_loaders):
    """Test config_class decorator with unsupported file extension"""

    @config_class(file_name="config.txt")
    class TestConfig:
        name: str
        value: int

    # Should keep the extension but it will cause an error when loading
    assert TestConfig._config_file_name == "config.txt.json"


def test_config_class_with_different_loaders(mock_loaders):
    """Test config_class with different available loaders"""
    # Change the mock to return different loaders
    mock_loaders.return_value = {
        '.toml': 'TOMLConfigLoader',
        '.ini': 'INIConfigLoader'
    }

    @config_class
    class TestConfig:
        name: str
        value: int

    # Should use the first available loader extension
    assert TestConfig._config_file_name == "test_config.toml"


def test_config_class_with_empty_loaders(mock_loaders):
    """Test config_class with no available loaders"""
    # Change the mock to return empty loaders
    mock_loaders.return_value = {}

    # Should raise an error
    with pytest.raises(IndexError):
        @config_class
        class TestConfig:
            name: str
            value: int
