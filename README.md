# 🌉 BridgeLink

[![PyPI version](https://badge.fury.io/py/bridgelink.svg)](https://badge.fury.io/py/bridgelink)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**BridgeLink** is a production-ready CLI tool that exposes your local Android devices remotely via the NativeBridge platform, making them accessible from anywhere with secure tunneling powered by bore.

---

## ✨ Features

- 🚀 **One-Command Setup** - Install and configure in seconds
- 📱 **Multi-Device Support** - Manage multiple Android devices simultaneously
- 🔐 **Secure Tunneling** - API key-based authentication via NativeBridge
- 🌍 **Remote Access** - Access devices from anywhere in the world
- 🤖 **Auto-Installation** - Automatically installs bore tunnel and ADB
- 💻 **Cross-Platform** - Works on macOS, Linux, and Windows
- 🔄 **Background Management** - Tunnels run in the background as daemons
- 📊 **Device Tracking** - Track device state and connection URLs in real-time
- ✅ **Input Validation** - Validates device serials via ADB before backend calls
- 🎯 **Smart Activation** - Intelligently reactivates existing devices

---

## 🚀 Quick Start

### 1. Install BridgeLink

```bash
pip install bridgelink
```

### 2. Install Dependencies

```bash
bridgelink install
```

This automatically installs:
- **bore** - Tunnel binary for your platform (macOS, Linux, Windows)
- **ADB** - Android Debug Bridge from Google

### 3. Set API Key

Get your API key from [NativeBridge Dashboard](https://nativebridge.io/dashboard/api-keys):

```bash
export NB_API_KEY='Nb-kNGB.your-api-key-here'
```

### 4. Connect Your Device

Connect your Android device via USB and enable USB debugging.

### 5. Add Device

```bash
bridgelink devices add <device-serial>
```

### 6. Access Remotely

```bash
adb connect bridgelink.nativebridge.io:15750
```

---

## 📋 Commands

### Device Management

```bash
# Add device(s)
bridgelink devices add <serial>
bridgelink devices add <serial1> <serial2>  # Multiple devices

# Activate existing device
bridgelink devices activate <serial>

# List all devices
bridgelink devices list

# Deactivate device (keeps registration)
bridgelink devices deactivate <serial>

# Remove device completely
bridgelink devices remove <serial>
```

### Daemon Management

```bash
# Check tunnel status
bridgelink daemon status

# View tunnel logs
bridgelink daemon logs <serial>

# Stop specific tunnel
bridgelink daemon stop <serial>

# Clean up dead tunnels
bridgelink daemon cleanup
```

### Installation

```bash
# Install both bore and ADB
bridgelink install

# Install only bore
bridgelink install --bore-only

# Install only ADB
bridgelink install --adb-only
```

---

## 📖 Documentation

- **[Complete Command Reference](docs/README.md)** - All commands with examples
- **[Deployment Guide](docs/DEPLOYMENT_STEPS.md)** - Backend setup and deployment
- **[Activate Command](docs/ACTIVATE_COMMAND_GUIDE.md)** - Smart device activation
- **[Validation Flow](docs/VALIDATION_FLOW.md)** - Security and input validation
- **[Local Testing](docs/LOCAL_TESTING_GUIDE.md)** - Test before PyPI release
- **[PyPI Release](docs/PYPI_RELEASE.md)** - Publishing guide
- **[Quick Start](docs/QUICK_START.md)** - Quick reference

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NB_API_KEY` | NativeBridge API key | *Required* |
| `NB_API_URL` | Backend API URL | `https://dev.api.nativebridge.io` |
| `BORE_SERVER` | Bore tunnel server | `bridgelink.nativebridge.io` |

### State Directory

BridgeLink stores configuration in `~/.bridgelink/`:
- `tunnels.json` - Tunnel state
- `tunnel_<serial>.log` - Individual tunnel logs

---

## 🛡️ Security

- ✅ **ADB Validation** - Device serials validated before backend calls
- ✅ **API Key Auth** - Secure authentication for all operations
- ✅ **User Isolation** - Each user only sees their own devices
- ✅ **HTTPS** - Encrypted communication with backend

---

## 🤝 Support

- **Email:** support@nativebridge.io
- **Issues:** https://github.com/AutoFlowLabs/bridgelink/issues
- **Docs:** https://docs.nativebridge.io/bridgelink
- **API Key:** https://nativebridge.io/dashboard/api-keys

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

Made with ❤️ by the [NativeBridge](https://nativebridge.io) team
