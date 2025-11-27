# 📡 WiFi Connection Guide

Complete guide for using BridgeLink with wireless ADB connections over WiFi.

---

## Table of Contents

1. [Overview](#overview)
2. [How It Works](#how-it-works)
3. [Setup Requirements](#setup-requirements)
4. [Step-by-Step Setup](#step-by-step-setup)
5. [Multiple WiFi Devices](#multiple-wifi-devices)
6. [WiFi + Auto-Activation](#wifi--auto-activation)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)
9. [Limitations](#limitations)
10. [Technical Details](#technical-details)

---

## Overview

BridgeLink supports **wireless ADB connections** via WiFi, allowing you to:

- ✅ Use devices without USB cables (after initial setup)
- ✅ Move freely with your device while maintaining connection
- ✅ Reduce wear on USB ports
- ✅ Support multiple WiFi devices simultaneously
- ✅ Combine with auto-activation for zero-maintenance operation

---

## How It Works

### Connection Flow

```
[Android Device] ←WiFi→ [Computer] ←bore tunnel→ [bridgelink.nativebridge.io] ←Internet→ [Remote User]
     │                      │
     └─ WiFi IP: 192.168.1.15:5555
                            └─ Port Forward: localhost:5556 → 192.168.1.15:5555
                            └─ Bore: localhost:5556 → public:15750
```

### What Happens When You Use `--wifi` Flag

1. **Enable TCP/IP Mode**: Enables ADB over WiFi on the Android device (port 5555)
2. **Get IP Address**: Retrieves device's WiFi IP address from the device
3. **WiFi Connection**: Connects to device wirelessly via `adb connect <ip>:5555`
4. **Tunnel Creation**: Creates bore tunnel using WiFi connection
5. **USB Disconnect**: You can now disconnect the USB cable!

---

## Setup Requirements

### Network Requirements

- ✅ Android device connected to WiFi
- ✅ Computer connected to **same WiFi network** as device
- ✅ WiFi network allows device-to-device communication (some corporate/public WiFi networks block this)

### Device Requirements

- ✅ Android device with USB debugging enabled
- ✅ USB cable (required only for initial setup)
- ✅ Device screen stays on during setup (recommended)

### Software Requirements

- ✅ BridgeLink installed (`bridgelink setup`)
- ✅ ADB installed (auto-installed by BridgeLink)
- ✅ NativeBridge API key set (`NB_API_KEY` environment variable)

---

## Step-by-Step Setup

### Basic WiFi Setup

1. **Connect device via USB**
   ```bash
   # Verify device is connected
   adb devices
   # Output: 1d752b81    device
   ```

2. **Add device with WiFi flag**
   ```bash
   bridgelink devices add 1d752b81 --wifi
   ```

3. **Follow the prompts**
   ```
   📡 Setting up WiFi connection...
      Step 1/3: Enabling TCP/IP mode on device...
      ✓ TCP/IP mode enabled on port 5555
      Step 2/3: Getting device IP address...
      ✓ Device IP address: 192.168.1.15
      Step 3/3: Connecting to device via WiFi...
      ✓ Connected via WiFi: 192.168.1.15:5555

   💡 You can now disconnect the USB cable!
      The device will remain connected via WiFi.

   🔧 Setting up ADB port forwarding...
      Local ADB port: 5556

   🌉 Creating bore tunnel...
      Tunnel URL: bridgelink.nativebridge.io:15750

   ✅ SUCCESS
   Device 192.168.1.15:5555 is now active!
   Connect from anywhere:
     adb connect bridgelink.nativebridge.io:15750

   🌐 Manage device in NativeBridge Dashboard:
      https://nativebridge.io/dashboard/bridgelink
      → View device status, start remote sessions, and control your device
   ```

4. **Disconnect USB cable**
   - Your device is now fully wireless!
   - The tunnel continues working over WiFi

5. **Access via Dashboard (Optional)**
   - Visit https://nativebridge.io/dashboard/bridgelink
   - Your device will appear in the dashboard
   - Click "Start Session" to control device from browser

### Verifying WiFi Connection

```bash
# List devices - should show IP:port format
adb devices

# Output:
# 192.168.1.15:5555    device  ← WiFi connection
# 1d752b81             device  ← USB connection (if still connected)

# List BridgeLink devices
bridgelink devices list

# Shows:
# Serial: 192.168.1.15:5555 (WiFi)
# Tunnel URL: bridgelink.nativebridge.io:15750
```

---

## Multiple WiFi Devices

You can manage multiple WiFi-connected devices simultaneously.

### Scenario: Two Devices via WiFi

```bash
# Device 1: Connect first device via WiFi
bridgelink devices add device1_serial --wifi
# Output: WiFi IP: 192.168.1.15:5555

# Device 2: Connect second device via WiFi
bridgelink devices add device2_serial --wifi
# Output: WiFi IP: 192.168.1.20:5555

# Verify both devices
adb devices
# Output:
# 192.168.1.15:5555    device
# 192.168.1.20:5555    device

# List all BridgeLink devices
bridgelink devices list
# Shows both devices with their WiFi IPs and tunnel URLs
```

### Mixed USB + WiFi Devices

You can have some devices on USB and others on WiFi:

```bash
# USB device
bridgelink devices add usb_device_serial

# WiFi device
bridgelink devices add wifi_device_serial --wifi

# List shows both:
# usb_device_serial (USB)
# 192.168.1.15:5555 (WiFi)
```

---

## WiFi + Auto-Activation

Combine WiFi with auto-activation for maximum convenience:

```bash
bridgelink devices add <serial> --wifi --auto-activate
```

### What This Does

1. ✅ Sets up WiFi connection
2. ✅ Enables auto-activation in backend
3. ✅ Device auto-deactivates when WiFi connection drops
4. ✅ Device auto-activates when WiFi reconnects

### Use Case: Daily Workflow

**Initial Setup (Once):**
```bash
# Monday: Set up device with WiFi + auto-activation
bridgelink devices add 1d752b81 --wifi --auto-activate

# Disconnect USB cable
# Work wirelessly all day!
```

**Daily Usage (Automated):**
```bash
# Tuesday morning: Turn on device WiFi
# → Device automatically connects to WiFi
# → BridgeLink detects connection
# → Auto-activates device
# → Tunnel created automatically
# → Device is remotely accessible!

# No manual commands needed! 🎉
```

---

## Advanced Usage

### Manual WiFi Connection (Without BridgeLink Flag)

If you prefer manual control:

```bash
# 1. Enable TCP/IP mode on device
adb -s <serial> tcpip 5555

# 2. Get device IP
adb -s <serial> shell ip route | grep src

# 3. Connect via WiFi
adb connect <device-ip>:5555

# 4. Add to BridgeLink (using WiFi connection)
bridgelink devices add <device-ip>:5555
```

### Switching Between USB and WiFi

**USB to WiFi:**
```bash
# Currently on USB
bridgelink devices deactivate <usb-serial>

# Switch to WiFi
bridgelink devices add <usb-serial> --wifi
```

**WiFi to USB:**
```bash
# Currently on WiFi
bridgelink devices deactivate <device-ip>:5555

# Connect USB cable
adb usb

# Add via USB
bridgelink devices add <usb-serial>
```

### Custom WiFi Port

By default, ADB over WiFi uses port 5555. To use a different port:

```bash
# Enable TCP/IP on custom port
adb tcpip 5556

# Connect with custom port
adb connect <device-ip>:5556

# Add to BridgeLink
bridgelink devices add <device-ip>:5556
```

---

## Troubleshooting

### Device IP Not Found

**Problem:** `❌ Could not get IP address for device`

**Solutions:**
1. Ensure device is connected to WiFi:
   ```bash
   adb shell ip route
   # Should show WiFi interface (wlan0)
   ```

2. Check WiFi is enabled on device (Settings → WiFi)

3. Verify same network:
   ```bash
   # Get device IP
   adb shell ip route | grep src

   # Get computer IP
   ifconfig | grep "inet "

   # Both should have same network prefix (e.g., 192.168.1.x)
   ```

### WiFi Connection Failed

**Problem:** `❌ Failed to connect to device via WiFi`

**Solutions:**
1. Try manual connection:
   ```bash
   adb connect <device-ip>:5555
   ```

2. Check firewall/network settings
   - Some networks block device-to-device communication
   - Try a different WiFi network

3. Restart ADB server:
   ```bash
   adb kill-server
   adb start-server
   adb connect <device-ip>:5555
   ```

### Connection Drops Frequently

**Problem:** WiFi connection keeps disconnecting

**Solutions:**
1. Keep device screen on during operation
2. Disable battery optimization for ADB
3. Use a stable WiFi network
4. Move device closer to WiFi router
5. Check for network interference

### Device Reverts to USB After Reboot

**Problem:** After rebooting device, WiFi connection is lost

**Expected Behavior:** This is normal! Android resets to USB mode after reboot.

**Solution:** Re-run WiFi setup:
```bash
# Connect USB cable
bridgelink devices add <serial> --wifi

# Disconnect USB cable
```

---

## Limitations

### 1. Reboot Behavior
- **Limitation:** Device resets to USB mode after reboot
- **Workaround:** Re-run `--wifi` setup (requires USB cable)

### 2. Network Requirements
- **Limitation:** Device and computer must be on same network
- **Workaround:** Use mobile hotspot or VPN to create shared network

### 3. Battery Consumption
- **Limitation:** WiFi ADB uses more battery than USB
- **Workaround:** Keep device charged or monitor battery level

### 4. Latency
- **Limitation:** Slightly higher latency than USB
- **Impact:** Minimal for most operations; noticeable for large file transfers

### 5. Network Isolation
- **Limitation:** Some corporate/public WiFi networks isolate devices
- **Workaround:** Use personal hotspot or configure network settings

---

## Technical Details

### Port Forwarding (WiFi vs USB)

**USB Connection:**
```
Device USB → localhost:5555 → bore → public:15750
```

**WiFi Connection:**
```
Device WiFi (192.168.1.15:5555) → localhost:5556 → bore → public:15750
```

### Serial Identifier Format

- **USB:** Device serial number (e.g., `1d752b81`)
- **WiFi:** IP address + port (e.g., `192.168.1.15:5555`)

### ADB Detection

BridgeLink automatically detects WiFi connections:

```python
# Internal detection logic
def is_wifi_connection(serial: str) -> bool:
    # WiFi: 192.168.1.15:5555
    # USB: 1d752b81
    return ':' in serial and serial.split(':')[0].replace('.', '').isdigit()
```

### Health Monitoring

WiFi devices are monitored the same way as USB devices:
- Health monitor polls every 1 second
- Checks if device is still in `adb devices` output
- Auto-deactivates if connection lost

---

## Best Practices

### 1. Initial Setup
✅ Keep device screen on during WiFi setup
✅ Ensure strong WiFi signal
✅ Test connection before disconnecting USB

### 2. Daily Usage
✅ Use auto-activation for convenience
✅ Keep device on charger if battery drains quickly
✅ Monitor connection quality

### 3. Multiple Devices
✅ Document each device's WiFi IP address
✅ Use descriptive device names
✅ Consider using DHCP reservations for consistent IPs

### 4. Security
✅ Disconnect WiFi when not in use
✅ Use secure WiFi networks (avoid public WiFi)
✅ Deactivate devices when done: `bridgelink devices deactivate <ip>:5555`

---

## Summary

WiFi connection in BridgeLink provides:
- 🔌 **Wireless operation** - No USB cable needed after setup
- 🚀 **Easy setup** - One flag: `--wifi`
- 🔄 **Auto-activation support** - Fully automated lifecycle
- 📱 **Multi-device** - Support for multiple WiFi devices
- 🌐 **Remote access** - Same remote access as USB devices

Get started now:
```bash
bridgelink devices add <your-device-serial> --wifi --auto-activate
```

Enjoy wireless freedom! 📡✨
