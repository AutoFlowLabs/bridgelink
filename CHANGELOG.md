# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Device auto-discovery
- Device health monitoring
- Automatic tunnel reconnection
- Web dashboard
- Device groups

## [0.1.0] - 2024-11-20

### Added
- Initial release of BridgeLink CLI
- Automatic bore tunnel binary installation for macOS, Linux, Windows
- Automatic ADB installation from Google
- Device management commands (`add`, `list`, `deactivate`, `remove`)
- Daemon management commands (`status`, `logs`, `cleanup`)
- Configuration commands (`show`, `set-api-key`, `reset`)
- Interactive setup wizard
- Background tunnel management with state persistence
- NativeBridge API integration for device tracking
- API key-based authentication
- Multi-device support
- Cross-platform support (macOS ARM/Intel, Linux x64, Windows x64)
- Comprehensive documentation
- GitHub Actions CI/CD pipeline
- Automatic PyPI release workflow
- Automated testing on multiple platforms and Python versions

### Features
- **One-command installation**: `pip install bridgelink`
- **Auto-dependency installation**: Automatically installs bore and ADB
- **Secure tunneling**: API key authentication via NativeBridge
- **Remote access**: Access Android devices from anywhere
- **Background management**: Tunnels run seamlessly in background
- **User-friendly CLI**: Simple, intuitive commands
- **Production-ready**: Clean code, comprehensive error handling

### Technical Details
- Python 3.8+ support
- Click-based CLI framework
- Subprocess management with psutil
- HTTP client with requests
- MongoDB integration for device tracking
- Tunnel state persistence in `~/.bridgelink/`
- Individual log files per device
- Process lifecycle management

### Documentation
- Complete user guide (README.md)
- Local testing guide (TESTING_LOCALLY.md)
- PyPI release guide (PYPI_RELEASE.md)
- GitHub Actions setup guide (GITHUB_ACTIONS_SETUP.md)
- Complete implementation summary
- Quick start guide
- API documentation

### Backend Integration
- Device CRUD API endpoints (`/v1/devices`)
- bore tunnel validation API (`/v1/bore/validate-api-key`)
- MongoDB collection with proper indexes
- User isolation and security
- Device state management (active/inactive)

### Infrastructure
- GitHub Actions workflows for CI/CD
- Automated testing on Ubuntu, macOS, Windows
- Python 3.8, 3.9, 3.10, 3.11, 3.12 support
- Automatic PyPI publishing on production branch push
- TestPyPI integration for pre-release testing
- GitHub release creation with artifacts
- Code quality checks (flake8, black, isort, mypy)
- Security scanning (safety, bandit)
