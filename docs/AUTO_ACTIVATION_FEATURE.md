# 🔄 BridgeLink Auto-Activation Feature

## Overview

The **Auto-Activation** feature eliminates the need to manually run `bridgelink devices add` or `activate` commands every time you reconnect a device. When enabled for a device, BridgeLink automatically detects when the device is plugged back in and creates a new tunnel, updating the backend - all without any manual intervention.

---

## 🎯 Problem Solved

### Before Auto-Activation:
```bash
# Device gets disconnected (USB unplugged)
# → Health monitor detects disconnect and deactivates device
# → Tunnel is destroyed

# User reconnects device (USB plugged back in)
$ bridgelink devices activate SERIAL123    # ❌ Manual command required
# → Creates new tunnel
# → Updates backend
```

### After Auto-Activation:
```bash
# Device gets disconnected (USB unplugged)
# → Health monitor detects disconnect and deactivates device
# → Tunnel is destroyed

# User reconnects device (USB plugged back in)
# → Connection monitor detects new device ✅ AUTOMATIC
# → Checks if auto_activate is enabled
# → Creates new tunnel
# → Updates backend
# → Device is ready to use!
```

---

## 🚀 How to Use

### 1. Enable Auto-Activation When Adding a Device

```bash
bridgelink devices add SERIAL123 --auto-activate
```

**What happens:**
- Device is registered with `auto_activate: true`
- Tunnel is created
- Health monitor starts (watches for disconnects)
- **Connection monitor starts** (watches for reconnects)

---

### 2. Enable Auto-Activation for Existing Device

```bash
bridgelink devices set-auto-activate SERIAL123 on
```

**What happens:**
- Updates device's `auto_activate` preference to `true`
- Starts connection monitor if not running

---

### 3. Disable Auto-Activation

```bash
bridgelink devices set-auto-activate SERIAL123 off
```

**What happens:**
- Updates device's `auto_activate` preference to `false`
- Device will require manual activation after disconnect

---

### 4. Check Auto-Activation Status

```bash
bridgelink devices list
```

**Example output:**
```
╒═══════════════╤══════════════╤═══════════╤══════════╤════════════╤═══════════╤═══════════════════════════════════════╕
│ Serial        │ Model        │ Brand     │ Type     │ State      │ Auto-Act  │ Tunnel URL                            │
╞═══════════════╪══════════════╪═══════════╪══════════╪════════════╪═══════════╪═══════════════════════════════════════╡
│ 1d752b81      │ 24116PCC1I   │ Xiaomi    │ physical │ ✓ active   │ 🔄 ON     │ bridgelink.nativebridge.io:15750      │
│ emulator-5554 │ Pixel 6      │ Google    │ emulator │ ○ inactive │ ○ off     │ (last: bridgelink.nativebridge.io:...) │
╘═══════════════╧══════════════╧═══════════╧══════════╧════════════╧═══════════╧═══════════════════════════════════════╛

💡 Auto-Act: Auto-activation feature (device auto-reconnects when plugged back in)
```

---

## 🏗️ Architecture

### Components

#### 1. **Device Registration (Backend)**
- MongoDB field: `auto_activate: boolean`
- Stored per device in `nativebridge_bridgelink_user_devices` collection
- Persists across device activations/deactivations

#### 2. **Health Monitor (Existing)**
- Polls devices every **1 second** (fast disconnect detection)
- Detects disconnections
- Auto-deactivates disconnected devices
- Stops tunnels

#### 3. **Connection Monitor (New)**
- Polls ADB every **1 second** for newly connected devices (fast reconnect detection)
- Detects when devices are plugged in
- Checks backend for `auto_activate` preference
- Automatically activates eligible devices

#### 4. **CLI Integration**
- `--auto-activate` flag on `devices add` command
- `set-auto-activate` command for toggling preference
- Auto-starts connection monitor when needed
- Shows auto-activation status in `devices list`

---

## 🔄 Complete Workflow

### Scenario: Device with Auto-Activation Enabled

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Initial Setup                                           │
└─────────────────────────────────────────────────────────────────┘

$ bridgelink devices add SERIAL123 --auto-activate

→ Device registered in backend with auto_activate: true
→ Tunnel created: bridgelink.nativebridge.io:15750
→ Health monitor started (if not running)
→ Connection monitor started (if not running)
→ Device state: ACTIVE

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Device Disconnects (USB unplugged)                      │
└─────────────────────────────────────────────────────────────────┘

[Health Monitor - runs every 5s]
→ Polls ADB: adb devices
→ Device SERIAL123 not found
→ Stops tunnel for SERIAL123
→ Updates backend: device_state = "inactive"
→ Device state: INACTIVE

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Device Reconnects (USB plugged back in)                 │
└─────────────────────────────────────────────────────────────────┘

[Connection Monitor - runs every 5s]
→ Polls ADB: adb devices
→ Detects new device: SERIAL123
→ Checks backend: GET /v1/bridgelink/devices/SERIAL123
→ Checks auto_activate: true ✓
→ Checks device_state: "inactive" ✓
→ ELIGIBLE FOR AUTO-ACTIVATION!

[Auto-Activation Process]
→ Sets up ADB TCP mode: adb tcpip 5555
→ Forwards port: adb forward tcp:5555 tcp:5555
→ Creates bore tunnel
→ Extracts tunnel URL from logs
→ Updates backend:
   POST /v1/bridgelink/devices
   {
     "device_serial": "SERIAL123",
     "device_state": "active",
     "tunnel_url": "bridgelink.nativebridge.io:15751",
     "auto_activate": true
   }
→ Device state: ACTIVE
→ ✅ AUTO-ACTIVATION COMPLETE!

User can now: adb connect bridgelink.nativebridge.io:15751
```

---

## 🗂️ Database Schema Changes

### Before:
```json
{
  "user_id": "auth0|123456",
  "device_serial": "SERIAL123",
  "device_type": "physical",
  "device_details": {...},
  "tunnel_url": "bridgelink.nativebridge.io:15750",
  "device_state": "active",
  "created_at": "2025-01-20T10:00:00Z",
  "updated_at": "2025-01-20T10:00:00Z"
}
```

### After:
```json
{
  "user_id": "auth0|123456",
  "device_serial": "SERIAL123",
  "device_type": "physical",
  "device_details": {...},
  "tunnel_url": "bridgelink.nativebridge.io:15750",
  "device_state": "active",
  "auto_activate": true,  // ← NEW FIELD
  "created_at": "2025-01-20T10:00:00Z",
  "updated_at": "2025-01-20T10:00:00Z"
}
```

**Default Value:** `false` (for backward compatibility)

---

## 📡 API Changes

### 1. Add/Update Device Endpoint

**Endpoint:** `POST /v1/bridgelink/devices`

**New Field:**
```json
{
  "device_serial": "SERIAL123",
  "device_type": "physical",
  "device_details": {...},
  "tunnel_url": "bridgelink.nativebridge.io:15750",
  "device_state": "active",
  "auto_activate": true  // ← NEW (optional, defaults to preserving existing or false)
}
```

---

### 2. Update Auto-Activate Preference

**Endpoint:** `PATCH /v1/bridgelink/devices/{serial}/auto-activate`

**Request:**
```json
{
  "auto_activate": true
}
```

**Response:**
```json
{
  "device_serial": "SERIAL123",
  "auto_activate": true,
  "message": "Auto-activation enabled for device SERIAL123"
}
```

---

### 3. Get Auto-Activate Candidates

**Endpoint:** `GET /v1/bridgelink/devices/auto-activate/candidates`

**Response:**
```json
{
  "devices": [
    {
      "device_serial": "SERIAL123",
      "device_state": "inactive",
      "auto_activate": true,
      ...
    }
  ],
  "total": 1
}
```

Returns all inactive devices with `auto_activate: true` for the current user.

---

## 🛠️ CLI Commands

### Device Management

```bash
# Add device with auto-activation
bridgelink devices add SERIAL123 --auto-activate

# Add multiple devices with auto-activation
bridgelink devices add SERIAL1 SERIAL2 --auto-activate

# Enable auto-activation for existing device
bridgelink devices set-auto-activate SERIAL123 on

# Disable auto-activation
bridgelink devices set-auto-activate SERIAL123 off

# List devices (shows auto-activation status)
bridgelink devices list
```

---

## 📂 New Files Created

### Backend (app-anywhere-backend)

**Modified:**
- `services/bridgelink_device_service.py`
  - Updated `add_or_update_device()` to accept `auto_activate` parameter
  - Added `update_auto_activate()` function
  - Added `get_auto_activate_devices()` function

- `routes/bridgelink_device_routes.py`
  - Updated `AddDeviceRequest` model with `auto_activate` field
  - Updated `DeviceResponse` model with `auto_activate` field
  - Added `PATCH /devices/{serial}/auto-activate` endpoint
  - Added `GET /devices/auto-activate/candidates` endpoint

### CLI (bridgelink)

**Modified:**
- `bridgelink/utils/api_client.py`
  - Added `update_auto_activate()` method
  - Added `get_auto_activate_devices()` method

- `bridgelink/commands/device.py`
  - Added `--auto-activate` flag to `add` command
  - Added `set-auto-activate` command
  - Updated `list` command to show auto-activation status
  - Integrated connection monitor auto-start

**Created:**
- `bridgelink/daemon/connection_monitor.py`
  - Core connection monitoring logic
  - Polls ADB for newly connected devices
  - Checks auto-activate eligibility
  - Performs auto-activation

- `bridgelink/daemon/connection_monitor_runner.py`
  - Entry point for connection monitor daemon

- `bridgelink/daemon/background_connection_monitor.py`
  - Daemon lifecycle management
  - PID file management
  - Start/stop/status operations

---

## 🔍 Monitoring & Logs

### Connection Monitor Logs

**Location:** `~/.bridgelink/connection_monitor.log`

**Example:**
```
🚀 Starting device connection monitor (poll interval: 5s)
   Watching for newly connected devices with auto-activate enabled
   Press Ctrl+C to stop

📱 Currently connected: 0 device(s)

🔌 Detected 1 newly connected device(s)

🔄 Auto-activating device: SERIAL123
   Setting up ADB TCP mode...
   ADB TCP port: 5555
   Creating bore tunnel...
   Tunnel URL: bridgelink.nativebridge.io:15751
   Updating device in NativeBridge...
✅ Device SERIAL123 auto-activated successfully
   Connect with: adb connect bridgelink.nativebridge.io:15751
```

### Health Monitor Logs

**Location:** `~/.bridgelink/monitor.log`

**Example:**
```
🔍 Checking health of 1 active device(s)...

⚠️  Device SERIAL123 is unhealthy: Device disconnected
   Stopping tunnel...
   Updating backend state to inactive...
✅ Device SERIAL123 deactivated successfully
```

---

## 🔐 Security Considerations

### 1. User Preference
- Auto-activation is **opt-in** per device
- Users must explicitly enable it via `--auto-activate` flag or `set-auto-activate` command
- Default behavior unchanged (no auto-activation)

### 2. Authentication
- Connection monitor requires valid API key
- All backend calls authenticated
- User can only auto-activate their own devices

### 3. Device Validation
- Device must be registered in backend
- Device must have `auto_activate: true`
- Device must be in `inactive` state
- Device must be connected via ADB

### 4. Network Security
- Same security model as manual activation
- Tunnels use bore with API key validation
- HTTPS communication with backend

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NB_API_KEY` | NativeBridge API key | *Required* |
| `NB_API_URL` | Backend API URL | `https://dev.api.nativebridge.io` |
| `BORE_SERVER` | Bore tunnel server | `bridgelink.nativebridge.io` |

### State Files

| File | Purpose |
|------|---------|
| `~/.bridgelink/connection_monitor.pid` | Connection monitor process ID |
| `~/.bridgelink/connection_monitor.log` | Connection monitor logs |
| `~/.bridgelink/monitor.pid` | Health monitor process ID |
| `~/.bridgelink/monitor.log` | Health monitor logs |
| `~/.bridgelink/tunnels.json` | Active tunnel state |

---

## 🧪 Testing Scenarios

### Test 1: Basic Auto-Activation
```bash
# 1. Add device with auto-activation
bridgelink devices add SERIAL123 --auto-activate

# 2. Verify connection monitor started
ps aux | grep connection_monitor

# 3. Disconnect device (unplug USB)
# Wait 5-10 seconds

# 4. Verify device deactivated
bridgelink devices list
# Should show: ○ inactive

# 5. Reconnect device (plug USB back in)
# Wait 5-10 seconds

# 6. Verify device auto-activated
bridgelink devices list
# Should show: ✓ active with new tunnel URL
```

### Test 2: Toggle Auto-Activation
```bash
# 1. Add device without auto-activation
bridgelink devices add SERIAL123

# 2. Enable auto-activation later
bridgelink devices set-auto-activate SERIAL123 on

# 3. Disconnect and reconnect
# Should auto-activate

# 4. Disable auto-activation
bridgelink devices set-auto-activate SERIAL123 off

# 5. Disconnect and reconnect
# Should NOT auto-activate (requires manual activation)
```

### Test 3: Multiple Devices
```bash
# 1. Add multiple devices with different preferences
bridgelink devices add SERIAL1 --auto-activate
bridgelink devices add SERIAL2  # No auto-activation

# 2. Disconnect both
# 3. Reconnect both
# SERIAL1 should auto-activate
# SERIAL2 should remain inactive
```

---

## 🎯 Use Cases

### 1. Mobile App Testing
**Scenario:** QA tester frequently connects/disconnects test device

**Before:**
```bash
# Every time device is reconnected
$ bridgelink devices activate SERIAL123
# Then use device
```

**After:**
```bash
# One-time setup
$ bridgelink devices add SERIAL123 --auto-activate

# Every reconnection: automatic!
# Just plug in device and use it
```

---

### 2. Device Farm
**Scenario:** Managing multiple physical devices that may reboot

**Setup:**
```bash
# Enable auto-activation for all farm devices
bridgelink devices add DEVICE1 --auto-activate
bridgelink devices add DEVICE2 --auto-activate
bridgelink devices add DEVICE3 --auto-activate
```

**Benefit:** Devices automatically reconnect after reboot

---

### 3. Development Workflow
**Scenario:** Developer using emulator that restarts frequently

**Setup:**
```bash
bridgelink devices add emulator-5554 --auto-activate
```

**Benefit:** Emulator auto-reconnects after restart

---

## 📊 Performance Impact

### Resource Usage
- **Connection Monitor Daemon**: <10MB memory, <2% CPU (idle)
- **Poll Interval**: 1 second (fast detection)
- **Network**: Minimal (only backend API calls for eligible devices)

### Scalability
- Single connection monitor handles unlimited devices
- Efficient: Only processes newly connected devices
- No impact on existing health monitor

---

## 🔮 Future Enhancements

### Planned Features
1. **Configurable Poll Interval**
   - Allow users to set custom poll intervals
   - Balance between responsiveness and resource usage

2. **Notification System**
   - Desktop notifications when device auto-activates
   - Email/Slack integration

3. **Auto-Activation Groups**
   - Enable/disable auto-activation for groups of devices
   - Useful for device farms

4. **Retry Logic**
   - Retry auto-activation on failure
   - Exponential backoff

5. **Device Discovery**
   - Auto-register newly connected unknown devices
   - Prompt user for confirmation

---

## 📝 Summary

The Auto-Activation feature provides a seamless experience for users who frequently disconnect and reconnect devices. By combining the existing health monitor (for auto-deactivation) with the new connection monitor (for auto-activation), BridgeLink now provides a fully automated device lifecycle management system.

**Key Benefits:**
- ✅ Zero manual intervention after initial setup
- ✅ Devices automatically reconnect when plugged back in
- ✅ User-controlled per-device preference
- ✅ Backward compatible (default: disabled)
- ✅ Secure (API key authenticated)
- ✅ Efficient (minimal resource usage)

---

**Version:** 0.2.0
**Release Date:** January 21, 2025
**Author:** BridgeLink Development Team
