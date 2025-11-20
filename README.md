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
- 🔍 **Automatic Health Monitoring** - Auto-detects and deactivates disconnected devices (5s polling)
- 📊 **Device Tracking** - Track device state and connection URLs in real-time
- ✅ **Input Validation** - Validates device serials via ADB before backend calls
- 🎯 **Smart Activation** - Intelligently reactivates existing devices
- 🛡️ **Platform-Aware Detection** - Different health checks for physical devices vs emulators

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
bridgelink devices deactivate              # Deactivate ALL active devices (with confirmation)
bridgelink devices deactivate --all        # Deactivate ALL active devices

# Remove device completely
bridgelink devices remove <serial>
```

### Daemon Management

```bash
# Check tunnel status
bridgelink daemon status

# View tunnel logs
bridgelink daemon logs <serial>

# Stop tunnel(s)
bridgelink daemon stop <serial>            # Stop specific tunnel
bridgelink daemon stop                     # Stop ALL tunnels (with confirmation)
bridgelink daemon stop --all               # Stop ALL tunnels

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

## 🔍 Automatic Health Monitoring

BridgeLink includes **automatic background health monitoring** that runs seamlessly without any manual intervention.

### How It Works

1. **Auto-Start**: When you add the first device, a background daemon automatically starts
2. **Continuous Monitoring**: Checks device connectivity every 5 seconds
3. **Smart Detection**:
   - **Physical Devices**: Must be in "device" state (strict)
   - **Emulators**: Can be in "device" or "offline" state (lenient)
4. **Auto-Cleanup**: When devices disconnect, automatically:
   - Stops the tunnel
   - Updates backend state to "inactive"
   - No stale connections!
5. **Auto-Stop**: When all devices are deactivated, the daemon automatically stops

### What This Means for You

✅ **No Manual Monitoring** - Everything happens automatically
✅ **Fast Detection** - Disconnects detected within 5 seconds
✅ **Clean State** - No stale tunnels or active states
✅ **Zero Maintenance** - Daemon manages itself

### Example Flow

```bash
# 1. Add a device
$ bridgelink devices add emulator-5554
🔍 Starting background health monitor...
   ✅ Health monitor started
💡 Health monitoring is active - disconnected devices will be auto-deactivated

# 2. Device gets physically disconnected
#    (Background daemon automatically detects and deactivates)
#    Logs to ~/.bridgelink/monitor.log:
#    ⚠️  Device emulator-5554 is unhealthy: Device disconnected
#       Stopping tunnel...
#       Updating backend state to inactive...
#    ✅ Device emulator-5554 deactivated successfully

# 3. Deactivate last device
$ bridgelink devices deactivate emulator-5554
🔍 No active devices remaining, stopping health monitor...
   ✅ Health monitor stopped
```

### Daemon Location

- **PID File**: `~/.bridgelink/monitor.pid`
- **Log File**: `~/.bridgelink/monitor.log`
- **State File**: `~/.bridgelink/health_monitor.json`

---

## 📖 Documentation

For complete documentation, visit the [GitHub repository](https://github.com/AutoFlowLabs/bridgelink).

**Key Guides:**
- **[Security Guide](https://github.com/AutoFlowLabs/bridgelink/blob/main/docs/SECURITY.md)** - Security best practices ⚠️ **READ FIRST**
- **[Complete Command Reference](https://github.com/AutoFlowLabs/bridgelink/blob/main/docs/README.md)** - All commands with examples
- **[Deployment Guide](https://github.com/AutoFlowLabs/bridgelink/blob/main/docs/DEPLOYMENT_STEPS.md)** - Backend setup and deployment
- **[Local Testing](https://github.com/AutoFlowLabs/bridgelink/blob/main/docs/LOCAL_TESTING_GUIDE.md)** - Test before PyPI release
- **[PyPI Release](https://github.com/AutoFlowLabs/bridgelink/blob/main/docs/PYPI_RELEASE.md)** - Publishing guide

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

## 🙏 Acknowledgments

- **[bore](https://github.com/ekzhang/bore)** - Fast, simple TCP tunnel
- **[ADB](https://developer.android.com/studio/command-line/adb)** - Android Debug Bridge by Google
- **[Click](https://click.palletsprojects.com/)** - Python CLI framework
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

Made with ❤️ by the [NativeBridge](https://nativebridge.io) team
