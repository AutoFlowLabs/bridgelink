# Changelog

All notable changes to BridgeLink will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-01-20

### Added
- **Automatic Background Health Monitoring**: Devices are now automatically monitored for connectivity
  - Daemon automatically starts when first device is added
  - Polls device health every 5 seconds (reduced from 30s)
  - Auto-detects and deactivates disconnected devices
  - Platform-aware health checks (physical devices vs emulators)
  - Daemon automatically stops when all devices are deactivated
- Background daemon manager (`background_monitor.py`)
- Monitor runner process (`monitor_runner.py`)
- Health monitoring state persistence (`~/.bridgelink/monitor.pid`, `monitor.log`)

### Changed
- Health monitoring polling interval reduced from 30s to 5s for faster disconnect detection
- Device add/activate commands now automatically start health monitor daemon
- Device deactivate/daemon stop commands now automatically stop daemon when no devices remain
- Updated user messaging to reflect automatic monitoring
- Removed manual monitor CLI commands (now fully automatic)

### Fixed
- Import errors in health monitor module
- API client initialization requiring API key parameter

### Documentation
- Added comprehensive **Automatic Health Monitoring** section to README.md
- Created **ARCHITECTURE.md** with complete system architecture and data flows
- Updated feature list to highlight automatic monitoring
- Added health monitoring benefits and example flows

## [0.1.0] - 2025-01-19

### Added
- Initial release of BridgeLink
- Device management commands (add, activate, deactivate, list, remove)
- Daemon/tunnel management commands (status, stop, logs, cleanup)
- Automatic installation of bore tunnel and ADB
- Secure tunneling via NativeBridge platform
- Cross-platform support (macOS, Linux, Windows)
- Background tunnel processes
- Device state tracking
- Input validation via ADB
- Smart device activation/reactivation
- Interactive setup wizard
- Configuration management
- Security warnings and best practices

### Documentation
- Complete README with quick start guide
- Security documentation (SECURITY.md)
- Deployment guide (DEPLOYMENT_STEPS.md)
- Local testing guide (LOCAL_TESTING_GUIDE.md)
- PyPI release guide (PYPI_RELEASE.md)

[0.1.1]: https://github.com/AutoFlowLabs/bridgelink/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/AutoFlowLabs/bridgelink/releases/tag/v0.1.0
