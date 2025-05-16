import dataclasses
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

import pytest

from configr.base import ConfigBase
from configr.config_class import config_class
from configr.exceptions import ConfigFileNotFoundError
from configr.loaders.loader_yaml import YAMLConfigLoader

# Check if PyYAML is available at import time, otherwise fail all tests
try:
    import yaml  # Attempt to import pyyaml
except (ImportError, ModuleNotFoundError):
    pytest.fail(
        "The pyyaml module is not installed. Please install it to run these tests."
    )


@config_class(file_name="database")
class DatabaseConfig:
    host: str
    port: int = 5432
    username: str = "postgres"
    password: Optional[str] = None
    use_ssl: bool = False


@config_class(file_name="nested_child")
class NestedChildConfig:
    setting_a: str
    setting_b: int
    setting_c: bool = True


@config_class
class NestedParentConfig:
    name: str
    child: NestedChildConfig
    optional_child: Optional[NestedChildConfig] = None
    children_list: list[NestedChildConfig] = dataclasses.field(default_factory=list)
    children_dict: dict[str, NestedChildConfig] = dataclasses.field(
        default_factory=dict
    )


@pytest.fixture
def config_dir():
    """Create a temporary config directory for testing."""
    temp_dir = tempfile.mkdtemp()
    config_dir = Path(temp_dir) / "_config"
    config_dir.mkdir(exist_ok=True)

    # Store original config dir to restore later
    original_config_dir = YAMLConfigLoader._config_dir

    # Set the config directory for testing
    YAMLConfigLoader.set_config_dir(config_dir)

    yield config_dir

    # Restore original config dir and clean up
    YAMLConfigLoader.set_config_dir(original_config_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def create_yaml_file():
    """Fixture to create YAML files with content."""

    def _create_yaml_file(directory, filename, content):
        filepath = directory / filename
        with open(filepath, 'w') as f:
            yaml.dump(content, f)
        return filepath

    return _create_yaml_file


@pytest.fixture
def original_loaders():
    """Save and restore ConfigBase loaders."""
    original = ConfigBase._loaders.copy()
    yield
    ConfigBase._loaders = original


def test_extensions():
    """Test that YAMLConfigLoader supports correct file extensions."""
    assert YAMLConfigLoader.get_extensions() == ['.yaml', '.yml']


def test_load_yaml_file(config_dir, create_yaml_file):
    """Test loading a basic YAML configuration file."""
    config_data = {
        'host': 'localhost',
        'port': 8432,
        'username': 'testuser',
        'password': 'testpass',
        'use_ssl': True
    }
    create_yaml_file(config_dir, 'database.yaml', config_data)

    loaded_data = YAMLConfigLoader.load('database', DatabaseConfig)
    assert loaded_data == config_data


def test_load_yaml_file_with_yaml_extension(config_dir, create_yaml_file):
    """Test loading a YAML file with .yaml extension."""
    config_data = {
        'host': 'localhost',
        'port': 8432
    }
    create_yaml_file(config_dir, 'database.yaml', config_data)

    loaded_data = YAMLConfigLoader.load('database', DatabaseConfig)
    assert loaded_data == config_data


def test_load_yaml_file_with_yml_extension(config_dir, create_yaml_file):
    """Test loading a YAML file with .yml extension."""
    config_data = {
        'host': 'localhost',
        'port': 8432
    }
    create_yaml_file(config_dir, 'database.yml', config_data)

    loaded_data = YAMLConfigLoader.load('database', DatabaseConfig)
    assert loaded_data == config_data


def test_file_not_found(config_dir):
    """Test that an appropriate exception is raised when a config file is not found."""
    with pytest.raises(ConfigFileNotFoundError):
        YAMLConfigLoader.load('nonexistent', DatabaseConfig)


def test_extension_precedence(config_dir, create_yaml_file):
    """Test that file extension precedence works correctly when multiple files exist."""
    yaml_data = {'host': 'from_yaml', 'port': 1000}
    yml_data = {'host': 'from_yml', 'port': 2000}

    create_yaml_file(config_dir, 'precedence.yaml', yaml_data)
    create_yaml_file(config_dir, 'precedence.yml', yml_data)

    # The .yaml extension should be checked first based on the order in the ext list
    loaded_data = YAMLConfigLoader.load('precedence', DatabaseConfig)
    assert loaded_data == yaml_data

    # If we remove the .yaml file, it should fall back to .yml
    os.remove(config_dir / 'precedence.yaml')
    loaded_data = YAMLConfigLoader.load('precedence', DatabaseConfig)
    assert loaded_data == yml_data


def test_config_file_exists(config_dir, create_yaml_file):
    """Test the config_file_exists method."""
    create_yaml_file(config_dir, 'exists.yaml', {'test': 'data'})

    assert YAMLConfigLoader.config_file_exists('exists')
    assert YAMLConfigLoader.config_file_exists('exists.yaml')
    assert not YAMLConfigLoader.config_file_exists('notexists')
    assert not YAMLConfigLoader.config_file_exists('notexists.yaml')
    assert not YAMLConfigLoader.config_file_exists('notexists.yml')


def test_complex_yaml_structure(config_dir, create_yaml_file):
    """Test loading a YAML file with a complex structure."""
    config_data = {
        'name': 'parent_config',
        'child': {
            'setting_a': 'value_a',
            'setting_b': 42,
            'setting_c': False
        },
        'optional_child': {
            'setting_a': 'opt_value_a',
            'setting_b': 24
        },
        'children_list': [
            {
                'setting_a': 'list_a_1',
                'setting_b': 101
            },
            {
                'setting_a': 'list_a_2',
                'setting_b': 102,
                'setting_c': True
            }
        ],
        'children_dict': {
            'key1': {
                'setting_a': 'dict_a_1',
                'setting_b': 201
            },
            'key2': {
                'setting_a': 'dict_a_2',
                'setting_b': 202,
                'setting_c': False
            }
        }
    }
    create_yaml_file(config_dir, 'nested.yaml', config_data)

    loaded_data = YAMLConfigLoader.load('nested', NestedParentConfig)

    # Verify the structure remains intact through loading
    assert loaded_data == config_data
    assert loaded_data['child']['setting_a'] == 'value_a'
    assert loaded_data['children_list'][1]['setting_b'] == 102
    assert loaded_data['children_dict']['key2']['setting_c'] is False


def test_integration_with_config_base(config_dir, create_yaml_file, original_loaders):
    """Test integration of YAMLConfigLoader with ConfigBase."""
    config_data = {
        'host': 'db.example.com',
        'port': 3306,
        'username': 'admin',
        'password': 'secret',
        'use_ssl': True
    }
    create_yaml_file(config_dir, 'database.yaml', config_data)

    # Configure ConfigBase to use YAMLConfigLoader
    ConfigBase._loaders = [YAMLConfigLoader]

    # Load the configuration using ConfigBase
    config = ConfigBase.load(DatabaseConfig)

    # Verify the configuration was loaded correctly
    assert config.host == 'db.example.com'
    assert config.port == 3306
    assert config.username == 'admin'
    assert config.password == 'secret'  # noqa: S105
    assert config.use_ssl is True


def test_yaml_format_error(config_dir):
    """Test handling of YAML format errors."""
    # Create a malformed YAML file
    filepath = config_dir / 'malformed.yaml'
    with open(filepath, 'w') as f:
        f.write('host: localhost\nport: 8432\ninvalid_yaml-\n')

    with pytest.raises(yaml.YAMLError):
        YAMLConfigLoader.load('malformed', DatabaseConfig)


def test_yaml_not_available(monkeypatch):
    """Test behavior when PyYAML is not available."""
    # Mock the YAML_AVAILABLE flag to be False
    monkeypatch.setattr("configr.loaders.loader_yaml.YAML_AVAILABLE", False)

    with pytest.raises(ImportError):
        YAMLConfigLoader.load('any', DatabaseConfig)


def test_custom_config_dir(config_dir, create_yaml_file):
    """Test setting a custom configuration directory."""
    # Create a different config directory
    temp_dir = Path(config_dir).parent
    custom_dir = temp_dir / "custom_config"
    custom_dir.mkdir(exist_ok=True)

    # Create a YAML file in the custom directory
    custom_config_data = {'host': 'custom_host', 'port': 9000}
    create_yaml_file(custom_dir, 'database.yaml', custom_config_data)

    # Save original config directory
    original_config_dir = YAMLConfigLoader._config_dir

    try:
        # Set the custom config directory
        YAMLConfigLoader.set_config_dir(custom_dir)

        # Load the config from the custom directory
        loaded_data = YAMLConfigLoader.load('database', DatabaseConfig)
        assert loaded_data == custom_config_data
    finally:
        # Reset to the original config directory
        YAMLConfigLoader.set_config_dir(original_config_dir)
