# Changelog

All notable changes to BridgeLink will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2024-11-23

### Changed - 🔧 Simplified Installation
- **Deferred Tool Installation**: ADB and bore are no longer installed during package installation
  - Tools are now installed via `bridgelink setup` command
  - Reduces installation complexity and Homebrew/PPA build issues
  - Users have explicit control over when tools are installed
- **Homebrew Formula Simplified**: Removed `post_install` hook
  - No longer auto-installs bore during `brew install`
  - Users run `bridgelink setup` after installation
  - Fixes Xcode dependency issues on macOS
- **Updated Quick Start**: All installation methods now include `bridgelink setup` step

### Fixed
- Fixed Homebrew installation failing due to Xcode version check
- Fixed `certifi` SHA256 mismatch in Homebrew formula
- Fixed PPA name in README (now `ppa:himanshukukreja/bridgelink`)

### Documentation
- Updated README with `bridgelink setup` in all installation methods
- Clarified that `bridgelink setup` installs ADB and bore

## [0.2.1] - 2024-11-23

### Added - Multi-Platform Distribution
- **Homebrew Support (macOS)**: Install via `brew install AutoFlowLabs/tap/bridgelink`
  - Created Homebrew formula with all Python dependencies
  - Set up AutoFlowLabs/homebrew-tap repository
- **PPA Support (Ubuntu/Debian)**: Install via `sudo add-apt-repository ppa:himanshukukreja/bridgelink`
  - Created Debian package configuration
  - Set up Launchpad PPA for automated builds
  - Supports Ubuntu Jammy (22.04) and later
- **Manual Release Documentation**: Comprehensive guide at `docs/MANUAL_RELEASE.md`
  - Step-by-step Homebrew release instructions
  - Step-by-step PPA release instructions
  - Troubleshooting guide for common issues
  - Quick reference scripts for faster releases

### Changed
- **Simplified CI/CD Pipeline**: `release.yml` now focuses on PyPI releases only
  - Removed automated Homebrew/PPA jobs (now manual for reliability)
  - Cleaner, faster release workflow
  - Manual steps documented in `docs/MANUAL_RELEASE.md`

### Documentation
- Added `docs/MANUAL_RELEASE.md` - Complete manual release guide
- Updated `packaging/README.md` with GitHub secrets documentation
- Updated Homebrew tap README with installation instructions
- Added virtual environment setup instructions for all platforms

## [0.2.0] - 2025-01-21

### Added - 🔄 Auto-Activation Feature
- **Auto-Activation**: Devices can now automatically reconnect when plugged back in!
  - New `--auto-activate` flag for `devices add` command
  - New `set-auto-activate on/off` command to toggle for existing devices
  - Auto-activation preference stored per device in backend (`auto_activate` field)
  - Connection monitor daemon automatically detects newly connected devices
  - Auto-creates tunnels and updates backend without manual intervention
- **Connection Monitor Daemon**: New background service for auto-activation
  - Polls ADB for newly connected devices every 1 second (fast!)
  - Automatically starts when auto-activation is enabled for any device
  - Processes only devices with `auto_activate: true` preference
  - Logs to `~/.bridgelink/connection_monitor.log`
- **New API Endpoints**:
  - `PATCH /v1/bridgelink/devices/{serial}/auto-activate` - Toggle auto-activation
  - `GET /v1/bridgelink/devices/auto-activate/candidates` - Get eligible devices
- **Enhanced Device Listing**: Shows auto-activation status with 🔄 indicator
- **Comprehensive Documentation**: Added `AUTO_ACTIVATION_FEATURE.md` with:
  - Feature overview and architecture
  - Usage examples and workflows
  - API documentation
  - Testing scenarios
  - Security considerations

### Changed - ⚡ Performance Improvements
- **5x Faster Disconnect/Reconnect Detection**: Reduced polling interval from 5s to **1 second**
  - Health monitor now polls every 1s (was 5s)
  - Connection monitor polls every 1s (was 5s)
  - Devices disconnect detection: ~1s (was ~5s)
  - Devices reconnect detection: ~1-2s total (was ~5-7s)
  - Full disconnect/reconnect cycle: ~2-3s (was ~10-12s)
- Updated user messaging to reflect "fast detection" in both monitors

### Backend Changes
- **Database Schema**: Added `auto_activate: boolean` field to device documents
  - Defaults to `false` for backward compatibility
  - Preserved across device activations/deactivations
- **Service Functions**:
  - `update_auto_activate()` - Update auto-activation preference
  - `get_auto_activate_devices()` - Get inactive devices with auto-activation enabled
- **Route Handlers**: Updated device endpoints to support auto-activation field

### CLI Changes
- Added `bridgelink.daemon.connection_monitor` module
- Added `bridgelink.daemon.connection_monitor_runner` module
- Added `bridgelink.daemon.background_connection_monitor` module
- Updated `bridgelink.utils.api_client` with auto-activation methods
- Enhanced `devices list` command with auto-activation column
- Auto-start connection monitor when auto-activation is enabled

### Documentation
- Updated README.md with auto-activation feature and 1s polling
- Added AUTO_ACTIVATION_FEATURE.md (400+ lines comprehensive guide)
- Updated all timing references from 5s to 1s throughout documentation
- Added use cases and testing scenarios for auto-activation

### Fixed
- Improved responsiveness of disconnect detection (5x faster)
- Better user experience with near-instant device state updates

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

[0.2.2]: https://github.com/AutoFlowLabs/bridgelink/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/AutoFlowLabs/bridgelink/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/AutoFlowLabs/bridgelink/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/AutoFlowLabs/bridgelink/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/AutoFlowLabs/bridgelink/releases/tag/v0.1.0
