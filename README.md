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
- 🔍 **Automatic Health Monitoring** - Auto-detects and deactivates disconnected devices (1s polling - fast!)
- **🔄 Auto-Activation** - Devices automatically reconnect when plugged back in (1s polling - fast!)
- 📊 **Device Tracking** - Track device state and connection URLs in real-time
- ✅ **Input Validation** - Validates device serials via ADB before backend calls
- 🎯 **Smart Activation** - Intelligently reactivates existing devices
- 🛡️ **Platform-Aware Detection** - Different health checks for physical devices vs emulators

---

## 📦 Installation

Choose your preferred installation method:

### Option 1: Homebrew (macOS) - Recommended for Mac users

```bash
# Add the BridgeLink tap
brew tap AutoFlowLabs/tap

# Install BridgeLink
brew install bridgelink
```

This automatically installs all dependencies including Python and bore tunnel.

---

### Option 2: APT (Debian/Ubuntu) - Recommended for Linux users

```bash
# Add the BridgeLink repository
sudo add-apt-repository ppa:autoflowlabs/bridgelink
sudo apt update

# Install BridgeLink
sudo apt install bridgelink
```

This automatically installs all dependencies including ADB.

---

### Option 3: pip (All platforms) - For Python developers

#### Step 1: Create Virtual Environment (Recommended)

<details>
<summary><b>macOS / Linux</b></summary>

```bash
# Create virtual environment
python3 -m venv bridgelink-env

# Activate virtual environment
source bridgelink-env/bin/activate

# Your prompt should now show (bridgelink-env)
```

</details>

<details>
<summary><b>Windows (Command Prompt)</b></summary>

```cmd
# Create virtual environment
python -m venv bridgelink-env

# Activate virtual environment
bridgelink-env\Scripts\activate.bat

# Your prompt should now show (bridgelink-env)
```

</details>

<details>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
# Create virtual environment
python -m venv bridgelink-env

# Activate virtual environment
bridgelink-env\Scripts\Activate.ps1

# If you get an execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Your prompt should now show (bridgelink-env)
```

</details>

> **Note:** Remember to activate the virtual environment each time you open a new terminal session before using BridgeLink.

#### Step 2: Install BridgeLink

```bash
pip install bridgelink
```

#### Step 3: Install Dependencies (pip only)

```bash
bridgelink install
```

This automatically installs:
- **bore** - Tunnel binary for your platform (macOS, Linux, Windows)
- **ADB** - Android Debug Bridge from Google

---

## 🚀 Quick Start

After installation, follow these steps:

### 1. Set API Key

Get your API key from [NativeBridge Dashboard](https://nativebridge.io/dashboard/api-keys):

**macOS / Linux:**
```bash
export NB_API_KEY='Nb-kNGB.your-api-key-here'
```

**Windows (Command Prompt):**
```cmd
set NB_API_KEY=Nb-kNGB.your-api-key-here
```

**Windows (PowerShell):**
```powershell
$env:NB_API_KEY="Nb-kNGB.your-api-key-here"
```

### 2. Connect Your Device

Connect your Android device via USB and enable USB debugging.

### 3. Add Device

```bash
bridgelink devices add <device-serial>
```

### 4. Access Remotely

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
bridgelink devices add <serial> --auto-activate  # Enable auto-activation

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

# Auto-activation management
bridgelink devices set-auto-activate <serial> on   # Enable auto-activation
bridgelink devices set-auto-activate <serial> off  # Disable auto-activation
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

## 🔍 Automatic Health Monitoring & Auto-Activation

BridgeLink includes **two automatic background monitors** that work together to provide a fully automated device lifecycle:

### 1. Health Monitor (Auto-Deactivation)

**Watches for disconnections and automatically deactivates devices**

1. **Auto-Start**: When you add the first device, a background daemon automatically starts
2. **Continuous Monitoring**: Checks device connectivity every **1 second** (fast!)
3. **Smart Detection**:
   - **Physical Devices**: Must be in "device" state (strict)
   - **Emulators**: Can be in "device" or "offline" state (lenient)
4. **Auto-Cleanup**: When devices disconnect, automatically:
   - Stops the tunnel
   - Updates backend state to "inactive"
   - No stale connections!
5. **Auto-Stop**: When all devices are deactivated, the daemon automatically stops

### 2. Connection Monitor (Auto-Activation) 🆕

**Watches for reconnections and automatically activates devices with auto-activation enabled**

1. **Auto-Start**: When you enable auto-activation for a device, the connection monitor starts
2. **Continuous Watching**: Checks for newly connected devices every **1 second** (fast!)
3. **Smart Activation**: When a device reconnects:
   - Checks if device has `auto_activate` enabled in backend
   - Verifies device is currently inactive
   - Automatically creates tunnel and activates device
4. **Zero Manual Intervention**: Once enabled, devices reconnect automatically when plugged back in

### What This Means for You

✅ **No Manual Monitoring** - Everything happens automatically
✅ **Lightning Fast Detection** - Disconnects/reconnects detected within 1 second!
✅ **Clean State** - No stale tunnels or active states
✅ **Zero Maintenance** - Daemons manage themselves
✅ **Opt-in Auto-Reconnect** - Enable per device as needed

### Example Flow (With Auto-Activation)

```bash
# 1. Add a device with auto-activation enabled
$ bridgelink devices add emulator-5554 --auto-activate
🔍 Starting background health monitor...
   ✅ Health monitor started
🔌 Starting auto-activation connection monitor...
   ✅ Connection monitor started
💡 Health monitoring is active - disconnected devices will be auto-deactivated
🔄 Auto-activation ENABLED - device will auto-reconnect when plugged back in

# 2. Device gets physically disconnected
#    (Health monitor automatically detects and deactivates)
#    Logs to ~/.bridgelink/monitor.log:
#    ⚠️  Device emulator-5554 is unhealthy: Device disconnected
#       Stopping tunnel...
#       Updating backend state to inactive...
#    ✅ Device emulator-5554 deactivated successfully

# 3. Device gets reconnected (USB plugged back in)
#    (Connection monitor automatically detects and activates)
#    Logs to ~/.bridgelink/connection_monitor.log:
#    🔌 Detected 1 newly connected device(s)
#    🔄 Auto-activating device: emulator-5554
#       Setting up ADB TCP mode...
#       Creating bore tunnel...
#       Tunnel URL: bridgelink.nativebridge.io:15751
#    ✅ Device emulator-5554 auto-activated successfully
#
#    ← No manual intervention needed!
```

### Daemon Locations

**Health Monitor:**
- **PID File**: `~/.bridgelink/monitor.pid`
- **Log File**: `~/.bridgelink/monitor.log`
- **State File**: `~/.bridgelink/health_monitor.json`

**Connection Monitor:**
- **PID File**: `~/.bridgelink/connection_monitor.pid`
- **Log File**: `~/.bridgelink/connection_monitor.log`

---

## 📖 Documentation

For complete documentation, visit the [GitHub repository](https://github.com/AutoFlowLabs/bridgelink).

**Key Guides:**
- **[Security Guide](https://github.com/AutoFlowLabs/bridgelink/blob/main/docs/SECURITY.md)** - Security best practices ⚠️ **READ FIRST**
- **[Auto-Activation Feature](https://github.com/AutoFlowLabs/bridgelink/blob/main/docs/AUTO_ACTIVATION_FEATURE.md)** - Detailed auto-activation guide 🆕
- **[Complete Command Reference](https://github.com/AutoFlowLabs/bridgelink/blob/main/docs/README.md)** - All commands with examples
- **[Architecture](https://github.com/AutoFlowLabs/bridgelink/blob/main/docs/ARCHITECTURE.md)** - System architecture and data flow
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
