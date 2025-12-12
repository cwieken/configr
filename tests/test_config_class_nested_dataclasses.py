from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock, patch

from configr.base import ConfigBase
from configr.config_class import config_class


def test_nested_dataclass_loading():
    """Test loading configuration with nested dataclasses."""

    @config_class(file_name="nested_child.json")
    class ChildConfig:
        name: str
        value: int

    @dataclass
    class ParentConfig:
        title: str
        child: ChildConfig

    # Mock the loader to return test data
    mock_loader = MagicMock()
    mock_loader.load.return_value = {
        "title": "Parent Title",
        "child": {"name": "Child Name", "value": 42},
    }

    with patch.object(ConfigBase, "_get_loader", return_value=mock_loader):
        # Mock the config file path to avoid file system dependency
        ConfigBase.set_config_dir("mock_path")

        # Load the parent config
        config = ConfigBase.load(ParentConfig)

        # Verify that the parent config was loaded correctly
        assert config.title == "Parent Title"

        # Verify that the child config was loaded correctly
        assert isinstance(config.child, ChildConfig)
        assert config.child.name == "Child Name"
        assert config.child.value == 42


def test_deeply_nested_dataclass_loading():
    """Test loading with multiple levels of nested dataclasses."""

    @config_class(file_name="nested_grandchild.json")
    class GrandchildConfig:
        id: int
        description: str

    @dataclass
    class ChildConfig:
        name: str
        grandchild: GrandchildConfig

    @dataclass
    class ParentConfig:
        title: str
        child: ChildConfig

    # Mock the loader to return test data
    mock_loader = MagicMock()
    mock_loader.load.return_value = {
        "title": "Parent Title",
        "child": {
            "name": "Child Name",
            "grandchild": {"id": 123, "description": "Grandchild Description"},
        },
    }

    with patch.object(ConfigBase, "_get_loader", return_value=mock_loader):
        # Mock the config file path to avoid file system dependency
        ConfigBase.set_config_dir("mock_path")

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
        assert config.child.grandchild.description == ("Grandchild Description")


def test_nested_dataclass_with_missing_values():
    """Test loading with nested dataclasses where some values are missing."""

    @config_class(file_name="nested_child.json")
    class ChildConfig:
        name: str
        value: int = 0  # Default value

    @dataclass
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
        },
    }

    with patch.object(ConfigBase, "_get_loader", return_value=mock_loader):
        # Mock the config file path to avoid file system dependency
        ConfigBase.set_config_dir("mock_path")

        # Load the parent config
        config = ConfigBase.load(ParentConfig)

        # Verify that the parent config was loaded correctly
        assert config.title == "Parent Title"

        # Verify that the child config was loaded with default value
        assert isinstance(config.child, ChildConfig)
        assert config.child.name == "Child Name"
        assert config.child.value == 0


def test_nested_dataclass_with_null_value():
    """Test loading where a nested value is null."""

    @dataclass
    class DefaultInitChildConfig:
        """A dataclass that can be initialized with no arguments."""

        name: str = "Default Name"
        value: int = 0

    @dataclass
    class ParentConfig:
        title: str
        child: DefaultInitChildConfig

    # Mock the loader to return data with null child
    mock_loader = MagicMock()
    mock_loader.load.return_value = {
        "title": "Parent Title",
        "child": None,  # Null value for child
    }

    with patch.object(ConfigBase, "_get_loader", return_value=mock_loader):
        # Mock the config file path to avoid file system dependency
        ConfigBase.set_config_dir("mock_path")

        # Load the parent config
        config = ConfigBase.load(ParentConfig)

        # Verify that the parent config was loaded correctly
        assert config.title == "Parent Title"

        # Verify that the child config was initialized with defaults
        assert isinstance(config.child, DefaultInitChildConfig)
        assert config.child.name == "Default Name"
        assert config.child.value == 0


def test_nested_dataclass_with_list():
    """Test loading configuration with a list of nested dataclasses."""

    @dataclass
    class ItemConfig:
        id: int
        name: str

    @config_class(file_name="collection_config.json")
    class CollectionConfig:
        title: str
        items: list[ItemConfig]

    # Mock the loader to return data with a list of items
    mock_loader = MagicMock()
    mock_loader.load.return_value = {
        "title": "My Collection",
        "items": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"},
        ],
    }

    with patch.object(ConfigBase, "_get_loader", return_value=mock_loader):
        # Mock the config file path to avoid file system dependency
        ConfigBase.set_config_dir("mock_path")

        config = ConfigBase.load(CollectionConfig)

        # Verify the collection config was loaded correctly
        assert config.title == "My Collection"
        assert len(config.items) == 3

        # Verify that each item was converted to ItemConfig dataclass
        for i, item in enumerate(config.items, start=1):
            assert isinstance(item, ItemConfig)
            assert item.id == i
            assert item.name == f"Item {i}"


def test_nested_dataclass_with_generic_types():
    """Test loading configs with nested dataclasses using generic types."""

    @dataclass
    class MetadataConfig:
        tags: dict[str, str]
        settings: dict[str, Any]

    @config_class(file_name="app_config.json")
    class AppConfig:
        name: str
        metadata: MetadataConfig

    # Mock the loader to return data with dictionaries
    mock_loader = MagicMock()
    mock_loader.load.return_value = {
        "name": "My App",
        "metadata": {
            "tags": {"env": "production", "region": "us-west"},
            "settings": {"timeout": 30, "retry": True, "debug": False},
        },
    }

    with patch.object(ConfigBase, "_get_loader", return_value=mock_loader):
        # Mock the config file path to avoid file system dependency
        ConfigBase.set_config_dir("mock_path")

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
