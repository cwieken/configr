import pytest
import dataclasses
from unittest.mock import patch, MagicMock

from src.config_class import config_class
from src.base import ConfigBase


def test_nested_dataclass_loading():
    """Test loading configuration with nested dataclasses"""

    @config_class(file_name="nested_child.json")
    class ChildConfig:
        name: str
        value: int

    @config_class(file_name="nested_parent.json")
    class ParentConfig:
        title: str
        child: ChildConfig

    # Mock the loader to return test data
    mock_loader = MagicMock()
    mock_loader.load.return_value = {
        "title": "Parent Title",
        "child": {
            "name": "Child Name",
            "value": 42
        }
    }

    with patch.object(ConfigBase, '_get_loader', return_value=mock_loader):
        with patch.object(ConfigBase, '_get_config_file_path', return_value="mock_path"):
            # Load the parent config
            config = ConfigBase.load(ParentConfig)

            # Verify that the parent config was loaded correctly
            assert config.title == "Parent Title"

            # Verify that the child config was loaded correctly
            assert isinstance(config.child, ChildConfig)
            assert config.child.name == "Child Name"
            assert config.child.value == 42


def test_deeply_nested_dataclass_loading():
    """Test loading configuration with multiple levels of nested dataclasses"""

    @config_class(file_name="nested_grandchild.json")
    class GrandchildConfig:
        id: int
        description: str

    @config_class(file_name="nested_child.json")
    class ChildConfig:
        name: str
        grandchild: GrandchildConfig

    @config_class(file_name="nested_parent.json")
    class ParentConfig:
        title: str
        child: ChildConfig

    # Mock the loader to return test data
    mock_loader = MagicMock()
    mock_loader.load.return_value = {
        "title": "Parent Title",
        "child": {
            "name": "Child Name",
            "grandchild": {
                "id": 123,
                "description": "Grandchild Description"
            }
        }
    }

    with patch.object(ConfigBase, '_get_loader', return_value=mock_loader):
        with patch.object(ConfigBase, '_get_config_file_path', return_value="mock_path"):
            # Load the parent config
            config = ConfigBase.load(ParentConfig)

            # Verify that the parent config was loaded correctly
            assert config.title == "Parent Title"

            # Verify that the child config was loaded correctly
            assert isinstance(config.child, ChildConfig)
            assert config.child.name == "Child Name"

            # Verify that the grandchild config was loaded correctly
            assert isinstance(config.child.grandchild, GrandchildConfig)
            assert config.child.grandchild.id == 123
            assert config.child.grandchild.description == "Grandchild Description"


def test_nested_dataclass_with_missing_values():
    """Test loading configuration with nested dataclasses where some values are missing"""

    @config_class(file_name="nested_child.json")
    class ChildConfig:
        name: str
        value: int = 0  # Default value

    @config_class(file_name="nested_parent.json")
    class ParentConfig:
        title: str
        child: ChildConfig

    # Mock the loader to return partial data
    mock_loader = MagicMock()
    mock_loader.load.return_value = {
        "title": "Parent Title",
        "child": {
            "name": "Child Name"
            # Missing "value" field, should use default
        }
    }

    with patch.object(ConfigBase, '_get_loader', return_value=mock_loader):
        with patch.object(ConfigBase, '_get_config_file_path', return_value="mock_path"):
            # Load the parent config
            config = ConfigBase.load(ParentConfig)

            # Verify that the parent config was loaded correctly
            assert config.title == "Parent Title"

            # Verify that the child config was loaded with default value
            assert isinstance(config.child, ChildConfig)
            assert config.child.name == "Child Name"
            assert config.child.value == 0


def test_nested_dataclass_with_null_value():
    """Test loading configuration with nested dataclasses where a nested value is null"""

    @dataclasses.dataclass
    class DefaultInitChildConfig:
        """A dataclass that can be initialized with no arguments"""
        name: str = "Default Name"
        value: int = 0

    @config_class(file_name="nested_parent.json")
    class ParentConfig:
        title: str
        child: DefaultInitChildConfig

    # Mock the loader to return data with null child
    mock_loader = MagicMock()
    mock_loader.load.return_value = {
        "title": "Parent Title",
        "child": None  # Null value for child
    }

    with patch.object(ConfigBase, '_get_loader', return_value=mock_loader):
        with patch.object(ConfigBase, '_get_config_file_path', return_value="mock_path"):
            # Load the parent config
            config = ConfigBase.load(ParentConfig)

            # Verify that the parent config was loaded correctly
            assert config.title == "Parent Title"

            # Verify that the child config was initialized with defaults
            assert isinstance(config.child, DefaultInitChildConfig)
            assert config.child.name == "Default Name"
            assert config.child.value == 0


def test_nested_dataclass_with_list():
    """Test loading configuration with a list of nested dataclasses"""

    from typing import List

    @config_class(file_name="item_config.json")
    class ItemConfig:
        id: int
        name: str

    @config_class(file_name="collection_config.json")
    class CollectionConfig:
        title: str
        items: List[ItemConfig]

    # This test should fail because the current implementation doesn't handle
    # lists of dataclasses automatically. This test documents this limitation.

    # Mock the loader to return data with a list of items
    mock_loader = MagicMock()
    mock_loader.load.return_value = {
        "title": "My Collection",
        "items": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"}
        ]
    }

    with patch.object(ConfigBase, '_get_loader', return_value=mock_loader):
        with patch.object(ConfigBase, '_get_config_file_path', return_value="mock_path"):
            # This should fail because the __load_nested_dataclasses method
            # doesn't check for List[dataclass] types
            config = ConfigBase.load(CollectionConfig)


def test_nested_dataclass_with_type_checking():
    """Test type validation with nested dataclasses"""

    @config_class(file_name="nested_child.json")
    class ChildConfig:
        name: str
        value: int

    @config_class(file_name="nested_parent.json")
    class ParentConfig:
        title: str
        child: ChildConfig

    # Mock the loader to return data with type error (string instead of int)
    mock_loader = MagicMock()
    mock_loader.load.return_value = {
        "title": "Parent Title",
        "child": {
            "name": "Child Name",
            "value": "not-an-integer"  # Type error: string instead of int
        }
    }

    with patch.object(ConfigBase, '_get_loader', return_value=mock_loader):
        with patch.object(ConfigBase, '_get_config_file_path', return_value="mock_path"):
            # Should raise ConfigValidationError due to type mismatch
            from src.exceptions import ConfigValidationError
            with pytest.raises(ConfigValidationError):
                ConfigBase.load(ParentConfig)


def test_nested_dataclass_with_generic_types():
    """Test loading configuration with nested dataclasses using generic types"""

    from typing import Dict, Any

    @config_class(file_name="metadata_config.json")
    class MetadataConfig:
        tags: Dict[str, str]
        settings: Dict[str, Any]

    @config_class(file_name="app_config.json")
    class AppConfig:
        name: str
        metadata: MetadataConfig

    # Mock the loader to return data with dictionaries
    mock_loader = MagicMock()
    mock_loader.load.return_value = {
        "name": "My App",
        "metadata": {
            "tags": {
                "env": "production",
                "region": "us-west"
            },
            "settings": {
                "timeout": 30,
                "retry": True,
                "debug": False
            }
        }
    }

    with patch.object(ConfigBase, '_get_loader', return_value=mock_loader):
        with patch.object(ConfigBase, '_get_config_file_path', return_value="mock_path"):
            # Load the config
            config = ConfigBase.load(AppConfig)

            # Verify the config was loaded correctly
            assert config.name == "My App"
            assert isinstance(config.metadata, MetadataConfig)
            assert config.metadata.tags["env"] == "production"
            assert config.metadata.tags["region"] == "us-west"
            assert config.metadata.settings["timeout"] == 30
            assert config.metadata.settings["retry"] is True
            assert config.metadata.settings["debug"] is False