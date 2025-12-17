# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-12-17

### Fixed
- Fixed "500 Internal Server Error" when attempting to reconfigure the integration
- Added reconfigure flow to allow updating NoIP credentials without removing the integration
- Enhanced 2FA notice in configuration flow descriptions for both initial setup and reconfiguration
- Improved handling of missing hostnames configuration

### Added
- Reconfigure flow for updating credentials (username and password)
- More prominent 2FA warnings in both English and Spanish translations
- Success message when reconfiguration is completed

## [0.1.0] - 2025-12-11

### Added
- Initial release of NoIP Monitor integration for Home Assistant
- Full UI configuration support through config flow
- Options flow for editing configuration from the UI
- Support for multiple NoIP hostnames/groups monitoring
- Independent sensor entity for each configured hostname
- "Disconnected" state when IP is unavailable
- Automatic IP updates every 5 minutes
- Dynamic icons (lan-connect/lan-disconnect) based on connection status
- Rich sensor attributes including hostname, status, response, and error information
- NoIP API client with authentication validation
- Support for both English and Spanish localization
- HACS compatibility with hacs.json configuration
- Comprehensive README documentation with installation and usage examples
- GitHub Actions workflows for automated validation (Ruff + Mypy + Hassfest)
- GitHub Actions workflow for automated releases
- Code quality tools configuration (mypy.ini, requirements.txt)
- Complete .gitignore for Python projects

### Features
- Monitor dynamic IP addresses from NoIP DDNS service
- Configure multiple hostnames via comma-separated list in options
- Unique device grouping all sensors under one NoIP Monitor device
- Persistent state across Home Assistant restarts
- Error handling for authentication failures, timeouts, and connection issues
- Coordinator-based updates for efficient API usage

[0.1.0]: https://github.com/Geek-MD/NoIP_Monitor/releases/tag/v0.1.0
