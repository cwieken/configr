import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from configr.loaders.loader_base import ConfigLoader
from configr.loaders.loader_json import JSONConfigLoader
from configr.loaders.loader_yaml import YAMLConfigLoader


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def json_config_file(temp_dir):
    """Create a temporary JSON config file."""
    config_data = {
        "name": "test_config",
        "version": "1.0.0",
        "settings": {
            "debug": True,
            "timeout": 30
        }
    }

    file_path = temp_dir / "config.json"
    with open(file_path, 'w') as f:
        json.dump(config_data, f)

    return file_path


@pytest.fixture
def yaml_config_file(temp_dir):
    """Create a temporary YAML config file."""
    yaml_content = """
    name: test_config
    version: 1.0.0
    settings:
      debug: true
      timeout: 30
    """

    file_path = temp_dir / "config.yaml"
    with open(file_path, 'w') as f:
        f.write(yaml_content)

    return file_path


@pytest.fixture
def invalid_json_file(temp_dir):
    """Create an invalid JSON file."""
    file_path = temp_dir / "invalid.json"
    with open(file_path, 'w') as f:
        f.write('{"name": "test", "invalid": }')  # Missing value

    return file_path


@pytest.fixture
def invalid_yaml_file(temp_dir):
    """Create an invalid YAML file."""
    file_path = temp_dir / "invalid.yaml"
    with open(file_path, 'w') as f:
        f.write('name: test\ninvalid: : value')  # Invalid syntax

    return file_path


def test_abstract_config_loader():
    """Test that ConfigLoader is an abstract base class that cannot be instantiated."""
    with pytest.raises(TypeError):
        ConfigLoader().load(Path("some/path"))


def test_json_config_loader(json_config_file):
    """Test loading a valid JSON configuration file."""
    loader = JSONConfigLoader()
    config = loader.load(json_config_file)

    assert isinstance(config, dict)
    assert config["name"] == "test_config"
    assert config["version"] == "1.0.0"
    assert config["settings"]["debug"] is True
    assert config["settings"]["timeout"] == 30


def test_json_config_loader_file_not_found():
    """Test JSONConfigLoader raises an error when file is not found."""
    loader = JSONConfigLoader()
    with pytest.raises(FileNotFoundError):
        loader.load(Path("nonexistent_file.json"))


def test_json_config_loader_invalid_json(invalid_json_file):
    """Test JSONConfigLoader raises an error when JSON is invalid."""
    loader = JSONConfigLoader()
    with pytest.raises(json.JSONDecodeError):
        loader.load(invalid_json_file)


def test_yaml_config_loader(yaml_config_file):
    """Test loading a valid YAML configuration file."""
    try:
        loader = YAMLConfigLoader()
        config = loader.load(yaml_config_file)

        assert isinstance(config, dict)
        assert config["name"] == "test_config"
        assert config["version"] == "1.0.0"
        assert config["settings"]["debug"] is True
        assert config["settings"]["timeout"] == 30
    except ImportError:
        pytest.skip("PyYAML not installed, skipping YAML tests")


def test_yaml_config_loader_file_not_found():
    """Test YAMLConfigLoader raises an error when file is not found."""
    try:
        loader = YAMLConfigLoader()
        with pytest.raises(FileNotFoundError):
            loader.load(Path("nonexistent_file.yaml"))
    except ImportError:
        pytest.skip("PyYAML not installed, skipping YAML tests")


def test_yaml_config_loader_invalid_yaml(invalid_yaml_file):
    """Test YAMLConfigLoader raises an error when YAML is invalid."""
    try:
        import yaml
        loader = YAMLConfigLoader()
        with pytest.raises(yaml.YAMLError):
            loader.load(invalid_yaml_file)
    except ImportError:
        pytest.skip("PyYAML not installed, skipping YAML tests")


@patch('configr.loaders.loader_yaml.YAML_AVAILABLE', False)
def test_yaml_loader_without_yaml_module():
    """Test YAMLConfigLoader raises ImportError when PyYAML is not available."""
    loader = YAMLConfigLoader()
    with pytest.raises(ImportError) as exc:
        loader.load(Path("some_file.yaml"))

    assert "PyYAML is required for YAML support" in str(exc.value)


def test_yaml_available_flag():
    """Test that YAML_AVAILABLE flag is set correctly."""
    from configr.loaders.loader_yaml import YAML_AVAILABLE

    try:
        assert YAML_AVAILABLE is True
    except ImportError:
        assert YAML_AVAILABLE is False
