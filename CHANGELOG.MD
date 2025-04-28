# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - Unreleased

### Added

- Support for non-file based configuration loaders
- `EnvVarConfigLoader` for loading configuration from environment variables
- Abstract `ConfigLoader` class as a base for all loaders
- Configuration loader registry system in `ConfigBase`
- Type conversion utilities for environment variables

### Changed

- Restructured loader system to distinguish between file-based and non-file loaders
- Improved configuration file detection and loading mechanism
- Enhanced error handling for configuration loading
- Refactored `FileConfigLoader` to extend the new `ConfigLoader` abstract class

### Fixed

- Type validation for nested dataclass structures
- Edge cases in configuration file discovery
- Error messages for configuration validation failures

## [0.1.1] - 2025-04-18

### Fixed

- Documentation improvements in code comments
- Minor typo corrections

## [0.1.0] - 2025-04-18

### Added

- Initial release
- Support for JSON and YAML configuration files
- Dataclass-based configuration schema definition
- Type validation for configuration values
- `config_class` decorator for easy configuration class creation