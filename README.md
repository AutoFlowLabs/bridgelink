# 🌉 BridgeLink

[![PyPI version](https://badge.fury.io/py/bridgelink.svg)](https://badge.fury.io/py/bridgelink)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**BridgeLink** is a production-ready CLI tool that exposes your local Android devices remotely via the NativeBridge platform, making them accessible from anywhere with secure tunneling powered by bore.

---

## ✨ Features

- 🚀 **One-Command Setup** - Install and configure in seconds
- 📱 **Multi-Device Support** - Manage multiple Android devices simultaneously
- 📡 **WiFi Connection Support** - Connect devices wirelessly via WiFi (no USB cable needed!)
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
- 🔌 **USB & WiFi Support** - Seamlessly handles both USB and wireless connections

---

## 📦 Installation

Choose your preferred installation method:

### Option 1: Homebrew (macOS) - Recommended for Mac users

```bash
# Add the BridgeLink tap
brew tap AutoFlowLabs/tap

# Install BridgeLink
brew install bridgelink

# Run setup to install required tools (ADB, bore)
bridgelink setup
```

---

### Option 2: pip (Linux, Windows, macOS)

#### Method A: Virtual Environment (Recommended)

<details>
<summary><b>macOS / Linux</b></summary>

```bash
# Create virtual environment
python3 -m venv bridgelink-env

# Activate virtual environment
source bridgelink-env/bin/activate

# Install BridgeLink
pip install bridgelink

# Run setup
bridgelink setup
```

</details>

<details>
<summary><b>Windows (Command Prompt)</b></summary>

```cmd
# Create virtual environment
python -m venv bridgelink-env

# Activate virtual environment
bridgelink-env\Scripts\activate.bat

# Install BridgeLink
pip install bridgelink

# Run setup
bridgelink setup
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

# Install BridgeLink
pip install bridgelink

# Run setup
bridgelink setup
```

</details>

> **Note:** Remember to activate the virtual environment each time you open a new terminal session before using BridgeLink.

#### Method B: Global Installation

If you prefer to install globally (not recommended due to potential dependency conflicts):

```bash
# Linux/macOS
pip install bridgelink
# Or with sudo if permission denied:
sudo pip install bridgelink

# Windows (run terminal as Administrator)
pip install bridgelink
```

After installation, run setup:
```bash
bridgelink setup
```

This automatically installs required tools:
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

**Option A: USB Connection (Default)**
Connect your Android device via USB and enable USB debugging.

**Option B: WiFi Connection (Wireless)**
1. Connect your Android device via USB first
2. Ensure both device and computer are on the same WiFi network
3. Use the `--wifi` flag when adding the device (see below)

### 3. Add Device

**USB Connection:**
```bash
bridgelink devices add <device-serial>
```

**WiFi Connection:**
```bash
bridgelink devices add <device-serial> --wifi
```

After WiFi setup completes, you can disconnect the USB cable. The device will remain accessible via WiFi!

### 4. Access Remotely

**Option A: Via ADB Command Line**
```bash
adb connect bridgelink.nativebridge.io:15750
```

**Option B: Via NativeBridge Dashboard**
Visit the [BridgeLink Dashboard](https://nativebridge.io/dashboard/bridgelink) to:
- 📊 View all your registered devices
- 🎮 Start remote device sessions
- 🖥️ Control devices directly from your browser
- 📈 Monitor device status in real-time

> **Dashboard URL:** https://nativebridge.io/dashboard/bridgelink
> (Development: https://trust-me-bro.nativebridge.io/dashboard/bridgelink)

---

## 📋 Commands

### Device Management

```bash
# Add device(s)
bridgelink devices add <serial>                    # USB connection
bridgelink devices add <serial> --wifi             # WiFi connection (USB required initially)
bridgelink devices add <serial1> <serial2>         # Multiple devices
bridgelink devices add <serial> --auto-activate    # Enable auto-activation
bridgelink devices add <serial> --wifi --auto-activate  # WiFi + auto-activation

# Activate existing device
bridgelink devices activate <serial>               # Works with both USB and WiFi devices

# List all devices
bridgelink devices list

# Deactivate device (keeps registration)
bridgelink devices deactivate <serial>
bridgelink devices deactivate                      # Deactivate ALL active devices (with confirmation)
bridgelink devices deactivate --all                # Deactivate ALL active devices

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

### Setup & Installation

```bash
# Run interactive setup (installs bore, ADB, configures API key)
bridgelink setup

# Install both bore and ADB (non-interactive)
bridgelink install

# Install only bore
bridgelink install --bore-only

# Install only ADB
bridgelink install --adb-only
```

---

## 📡 WiFi Connection (Wireless ADB)

BridgeLink supports **wireless ADB connections** via WiFi, allowing you to use your devices without USB cables!

### How It Works

1. **Initial Setup (USB Required):**
   - Connect device via USB
   - Run: `bridgelink devices add <serial> --wifi`
   - BridgeLink will:
     - Enable TCP/IP mode on the device (port 5555)
     - Get the device's WiFi IP address
     - Connect via WiFi (`adb connect <ip>:5555`)
     - Create tunnel using WiFi connection

2. **After Setup:**
   - Disconnect the USB cable
   - Device remains connected via WiFi
   - Tunnel continues working wirelessly
   - Access remotely via BridgeLink URL

### Requirements

- Device and computer must be on the **same WiFi network**
- WiFi must be enabled on the Android device
- USB connection required only for initial setup

### Example Usage

```bash
# Initial setup (USB connected)
bridgelink devices add 1d752b81 --wifi

# Output:
# 📡 Setting up WiFi connection...
#    Step 1/3: Enabling TCP/IP mode on device...
#    ✓ TCP/IP mode enabled on port 5555
#    Step 2/3: Getting device IP address...
#    ✓ Device IP address: 192.168.1.15
#    Step 3/3: Connecting to device via WiFi...
#    ✓ Connected via WiFi: 192.168.1.15:5555
#
# 💡 You can now disconnect the USB cable!

# Now disconnect USB - device stays connected via WiFi!
# Tunnel URL: bridgelink.nativebridge.io:15750
```

### Multiple WiFi Devices

You can connect multiple devices via WiFi simultaneously:

```bash
# Add first device via WiFi
bridgelink devices add device1_serial --wifi

# Add second device via WiFi
bridgelink devices add device2_serial --wifi

# List all devices
bridgelink devices list
# Shows both devices with WiFi connections (IP:5555 format)
```

### WiFi + Auto-Activation

Combine WiFi with auto-activation for ultimate convenience:

```bash
bridgelink devices add <serial> --wifi --auto-activate
```

Now your device will:
- ✅ Connect wirelessly via WiFi
- ✅ Auto-deactivate when disconnected from WiFi
- ✅ Auto-activate when reconnected to WiFi
- ✅ No USB cable needed after initial setup

### Limitations & Notes

- **Reboot:** If you restart the device, it will reset to USB mode. You'll need to run the WiFi setup again (USB cable + `--wifi` flag).
- **Network:** Device and computer must remain on the same WiFi network
- **Battery:** WiFi ADB consumes more battery than USB ADB
- **Performance:** WiFi connection may have slightly higher latency than USB

### Troubleshooting WiFi

**Device not connecting?**
```bash
# Check device IP manually
adb shell ip route | grep src

# Try manual connection
adb connect <device-ip>:5555

# Verify connection
adb devices
```

**Connection lost?**
- Ensure device hasn't gone to sleep (keep screen on during setup)
- Check both devices are on same WiFi network
- Try reconnecting: `adb connect <ip>:5555`

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

## 🌐 NativeBridge Dashboard

After registering a device with BridgeLink, you can manage it through the **NativeBridge Dashboard**.

### Dashboard Features

**Device Management:**
- 📊 View all your BridgeLink devices in one place
- ✅ See device status (active/inactive)
- 🔗 View tunnel URLs for each device
- 📱 Check comprehensive device details:
  - Hardware: Model, manufacturer, CPU, RAM, storage
  - Display: Resolution, density (DPI)
  - Software: Android version, SDK, security patch
  - Connection: Tunnel URL, device type (USB/WiFi)

**Remote Sessions:**
- 🎮 **Start remote device sessions** directly from the browser
- 🖥️ Control devices remotely without ADB command line
- 🖱️ Click, swipe, and interact with your device
- 📸 Take screenshots and record sessions
- 🔄 Real-time device mirroring

**Monitoring:**
- 📈 Monitor device connection status
- ⏱️ View device uptime and availability
- 🔍 Track device usage and sessions

### Accessing the Dashboard

**Production:**
```
https://nativebridge.io/dashboard/bridgelink
```

**Development:**
```
https://trust-me-bro.nativebridge.io/dashboard/bridgelink
```

> **Note:** The dashboard URL is automatically shown when you add or activate a device. Look for the 🌐 icon in the CLI output!

### How It Works

1. **Register Device:**
   ```bash
   bridgelink devices add <device-serial>
   ```

2. **Device Appears in Dashboard:**
   - Automatically registered in your NativeBridge account
   - Visible at the dashboard URL

3. **Start Remote Session:**
   - Click on your device in the dashboard
   - Click "Start Session"
   - Control device from your browser!

### Use Cases

**Web-Based Testing:**
- Test your app without installing ADB
- Share device access with team members
- Demo apps remotely in meetings

**Remote Debugging:**
- Debug issues on physical devices from anywhere
- No need for VPN or complex network setup
- Instant access through secure tunnel

**Device Management:**
- Centralized view of all your test devices
- Quick access to device information
- Easy activation/deactivation

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
