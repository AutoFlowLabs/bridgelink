# 🌉 BridgeLink

[![PyPI version](https://badge.fury.io/py/bridgelink.svg)](https://badge.fury.io/py/bridgelink)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**BridgeLink** is a production-ready CLI tool that exposes your local Android devices remotely via the NativeBridge platform, making them accessible from anywhere with secure tunneling powered by bore.

## ✨ Features

- 🚀 **One-Command Setup** - Install and configure in seconds
- 📱 **Multi-Device Support** - Manage multiple Android devices simultaneously
- 🔐 **Secure Tunneling** - API key-based authentication via NativeBridge
- 🌍 **Remote Access** - Access devices from anywhere in the world
- 🤖 **Auto-Installation** - Automatically installs bore tunnel and ADB
- 💻 **Cross-Platform** - Works on macOS, Linux, and Windows
- 🔄 **Background Management** - Tunnels run in the background
- 📊 **Device Tracking** - Track device state and connection URLs

## 🚀 Quick Start

### 1. Install

```bash
pip install bridgelink
```

### 2. Install Dependencies

```bash
bridgelink install
```

This automatically installs bore tunnel and ADB.

### 3. Set API Key

Get your key from [NativeBridge Dashboard](https://nativebridge.io/dashboard/api-keys):

```bash
export NB_API_KEY='Nb-kNGB.your-api-key-here'
```

### 4. Add Device

```bash
bridgelink devices add <device-serial>
```

### 5. Access Remotely

```bash
adb connect <tunnel-url>
```

## 📖 Documentation

- **[Complete Implementation Summary](COMPLETE_IMPLEMENTATION_SUMMARY.md)** - Full technical overview
- **[Local Testing Guide](TESTING_LOCALLY.md)** - Test without PyPI release
- **[PyPI Release Guide](PYPI_RELEASE.md)** - Publishing to PyPI
- **[API Documentation](https://docs.nativebridge.io/bridgelink)** - Full API reference

## 🤝 Support

- Email: support@nativebridge.io
- Issues: https://github.com/nativebridge/bridgelink/issues
- Docs: https://docs.nativebridge.io/bridgelink

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

Made with ❤️ by the [NativeBridge](https://nativebridge.io) team
