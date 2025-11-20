# 🏗️ BridgeLink Architecture & Flow

## Overview

BridgeLink is a CLI tool that creates secure tunnels to expose local Android devices remotely via the NativeBridge platform. This document covers the complete system architecture, data flow, and component interactions.

---

## 🎯 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User's Machine                          │
│                                                                 │
│  ┌──────────────┐      ┌─────────────────┐                    │
│  │   Android    │◄────►│   BridgeLink    │                    │
│  │   Device     │ USB  │   CLI + Daemon  │                    │
│  │  (Physical/  │      │                 │                    │
│  │  Emulator)   │      └────────┬────────┘                    │
│  └──────────────┘               │                              │
│         ▲                       │                              │
│         │ ADB TCP               │ bore tunnel                  │
│         │ (localhost:5555)      │                              │
│         │                       ▼                              │
│  ┌──────┴───────────────────────────────────┐                 │
│  │     bore Tunnel Process (Background)     │                 │
│  │  Local Port: 5555 → Remote: 12345        │                 │
│  └──────────────┬───────────────────────────┘                 │
│                 │                                              │
└─────────────────┼──────────────────────────────────────────────┘
                  │
                  │ HTTPS (encrypted)
                  │
      ┌───────────▼────────────┐
      │   bore Server          │
      │  bridgelink.           │
      │  nativebridge.io       │
      └───────────┬────────────┘
                  │
      ┌───────────▼────────────┐
      │  NativeBridge Backend  │
      │  (API + Database)      │
      │  - Device Registry     │
      │  - Tunnel URLs         │
      │  - Device State        │
      └────────────────────────┘
                  ▲
                  │
      ┌───────────┴────────────┐
      │   Remote Users         │
      │   adb connect          │
      │   bridgelink....:12345 │
      └────────────────────────┘
```

---

## 🧩 Component Architecture

### 1. CLI Layer (`bridgelink/cli.py` & `commands/`)

**Purpose**: User-facing command interface

**Components**:
- `cli.py` - Main entry point
- `commands/device.py` - Device management (add, activate, deactivate, list, remove)
- `commands/daemon.py` - Daemon/tunnel management (status, stop, logs, cleanup)
- `commands/config.py` - Configuration management
- `commands/setup.py` - Interactive setup wizard

**Responsibilities**:
- Parse user commands and options
- Validate input parameters
- Orchestrate lower-level components
- Display user-friendly output
- Handle errors gracefully

---

### 2. Daemon Layer (`bridgelink/daemon/`)

**Purpose**: Background process management

#### 2.1 Tunnel Manager (`tunnel_manager.py`)

**Responsibilities**:
- Setup ADB TCP mode on devices
- Create and manage bore tunnel processes
- Track tunnel state (PID, URL, port, device type)
- Stop tunnels and clean up processes
- Port forwarding management

**State Management**:
- State File: `~/.bridgelink/tunnels.json`
- Log Files: `~/.bridgelink/tunnel_{serial}.log`

**Key Methods**:
```python
setup_adb_tcp(device_serial) → port
create_tunnel(device_serial, local_port, api_key, device_type) → tunnel_info
stop_tunnel(device_serial) → bool
list_active_tunnels() → List[Dict]
get_tunnel_info(device_serial) → Dict
cleanup_dead_tunnels()
```

#### 2.2 Background Health Monitor (`background_monitor.py`)

**Responsibilities**:
- Manage health monitor daemon lifecycle
- Track daemon PID
- Start/stop monitoring process
- Ensure single daemon instance

**State Management**:
- PID File: `~/.bridgelink/monitor.pid`
- Log File: `~/.bridgelink/monitor.log`

**Key Methods**:
```python
is_running() → bool
start(api_key, poll_interval=5) → bool
stop() → bool
ensure_running(api_key) → bool
status() → Dict
```

#### 2.3 Device Health Monitor (`device_health_monitor.py`)

**Responsibilities**:
- Poll ADB for device connectivity
- Detect disconnected/offline devices
- Auto-stop tunnels for unhealthy devices
- Update backend device state
- Platform-aware health checks

**Monitoring Logic**:
- **Physical Devices**: Must be in "device" state
- **Emulators**: Can be in "device" or "offline" state
- **Poll Interval**: 5 seconds (default)

**State Management**:
- State File: `~/.bridgelink/health_monitor.json`

**Key Methods**:
```python
get_adb_device_status(device_serial) → str  # "device" | "offline" | "disconnected"
check_device_health(device_serial, device_type) → Dict
handle_unhealthy_device(device_serial, reason)
poll_once() → Dict
start_monitoring()
```

#### 2.4 Monitor Runner (`monitor_runner.py`)

**Purpose**: Standalone daemon process entry point

**Execution**:
```bash
python -m bridgelink.daemon.monitor_runner --api-key KEY --interval 5
```

**Responsibilities**:
- Run as detached background process
- Handle shutdown signals (SIGTERM, SIGINT)
- Execute continuous monitoring loop

---

### 3. Utilities Layer (`bridgelink/utils/`)

#### 3.1 ADB Manager (`adb.py`)

**Responsibilities**:
- List connected Android devices
- Get device information (model, brand, Android version)
- Execute ADB commands
- Detect device type (physical/emulator)

**Key Methods**:
```python
list_devices() → List[str]
get_device_info(device_serial) → DeviceInfo
```

#### 3.2 API Client (`api_client.py`)

**Responsibilities**:
- Communicate with NativeBridge backend
- Manage API authentication
- CRUD operations for devices

**Endpoints**:
- `POST /api/bridgelink/devices` - Register/update device
- `GET /api/bridgelink/devices` - List user's devices
- `GET /api/bridgelink/devices/{serial}` - Get device by serial
- `PATCH /api/bridgelink/devices/{serial}/state` - Update device state
- `DELETE /api/bridgelink/devices/{serial}` - Delete device

**Key Methods**:
```python
validate_api_key() → Dict
add_device(device_data) → Dict
list_devices() → List[Dict]
get_device(device_serial) → Dict
update_device_state(device_serial, state) → Dict
delete_device(device_serial) → bool
```

#### 3.3 bore Installer (`bore_installer.py`)

**Responsibilities**:
- Auto-detect platform (macOS, Linux, Windows)
- Download platform-specific bore binary
- Install to `~/.local/bin/bore`
- Make executable and configure PATH
- Version management

**Key Methods**:
```python
is_installed() → bool
install() → None
get_version() → str
get_bore_command() → str
```

#### 3.4 ADB Installer (`adb_installer.py`)

**Responsibilities**:
- Install Android Debug Bridge
- Platform-specific installation (brew, apt, choco)
- Verify installation

---

## 🔄 Data Flow Diagrams

### Flow 1: Adding a Device

```
User
  │
  │ bridgelink devices add SERIAL123
  ▼
┌─────────────────────────────────────────┐
│  CLI: commands/device.py                │
│  1. Validate API key                    │
│  2. Check device via ADB                │
│  3. Get device info                     │
└─────────┬───────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│  Tunnel Manager                         │
│  1. Setup ADB TCP mode (tcpip 5555)     │
│  2. Forward port (adb forward tcp:5555) │
│  3. Start bore tunnel process           │
│  4. Extract tunnel URL from logs        │
│  5. Save tunnel state with device_type  │
└─────────┬───────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│  API Client                             │
│  POST /api/bridgelink/devices           │
│  {                                      │
│    device_serial: "SERIAL123",          │
│    device_type: "physical",             │
│    device_state: "active",              │
│    tunnel_url: "host:12345"             │
│  }                                      │
└─────────┬───────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│  Background Monitor Daemon              │
│  1. Check if daemon running             │
│  2. If not, start daemon process        │
│  3. Save PID to monitor.pid             │
└─────────┬───────────────────────────────┘
          │
          ▼
    ┌─────────┐
    │ SUCCESS │
    └─────────┘
```

---

### Flow 2: Automatic Health Monitoring

```
Background Daemon (Every 5 seconds)
  │
  ▼
┌──────────────────────────────────────────┐
│  Device Health Monitor                   │
│  1. Load active tunnels from state       │
└─────────┬────────────────────────────────┘
          │
          │ For each tunnel:
          ▼
┌──────────────────────────────────────────┐
│  ADB Health Check                        │
│  1. Execute: adb devices -l              │
│  2. Parse device state                   │
│     - "device" (online)                  │
│     - "offline" (emulator)               │
│     - "unauthorized"                     │
│     - not found (disconnected)           │
└─────────┬────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────┐
│  Health Evaluation                       │
│  IF physical device:                     │
│    ✓ healthy if "device"                 │
│    ✗ unhealthy otherwise                 │
│  IF emulator:                            │
│    ✓ healthy if "device" or "offline"    │
│    ✗ unhealthy otherwise                 │
└─────────┬────────────────────────────────┘
          │
          ├─ Healthy ──► Continue monitoring
          │
          └─ Unhealthy ──► Auto-Deactivate
                           │
                           ▼
              ┌────────────────────────────┐
              │  1. Stop tunnel            │
              │  2. Call API to set state  │
              │     to "inactive"          │
              │  3. Log action             │
              └────────────────────────────┘
```

---

### Flow 3: Deactivating a Device

```
User
  │
  │ bridgelink devices deactivate SERIAL123
  ▼
┌─────────────────────────────────────────┐
│  CLI: commands/device.py                │
│  1. Validate API key                    │
│  2. Get device from backend             │
│  3. Check if already inactive           │
└─────────┬───────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│  Tunnel Manager                         │
│  1. Get tunnel info                     │
│  2. Kill bore process (SIGTERM)         │
│  3. Remove from tunnels.json            │
└─────────┬───────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│  API Client                             │
│  PATCH /api/bridgelink/devices/         │
│        SERIAL123/state                  │
│  { state: "inactive" }                  │
└─────────┬───────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│  Check Remaining Active Devices         │
│  1. List active tunnels                 │
│  2. If count == 0:                      │
│     → Stop health monitor daemon        │
│     → Remove monitor.pid                │
└─────────┬───────────────────────────────┘
          │
          ▼
    ┌─────────┐
    │ SUCCESS │
    └─────────┘
```

---

### Flow 4: Device Disconnect Detection (Automatic)

```
Physical Device USB Disconnected
  │
  │ (5 seconds later)
  ▼
┌──────────────────────────────────────────┐
│  Background Daemon Poll                  │
│  adb devices -l                          │
│  → Device not found                      │
└─────────┬────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────┐
│  Health Monitor: handle_unhealthy_device │
│  Reason: "Device disconnected"           │
└─────────┬────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────┐
│  1. Get tunnel info                      │
│  2. Call tunnel_manager.stop_tunnel()    │
│     → Kill bore process                  │
│     → Remove from state                  │
└─────────┬────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────┐
│  3. Call api_client.update_device_state()│
│     PATCH /api/bridgelink/devices/       │
│           {serial}/state                 │
│     { state: "inactive" }                │
└─────────┬────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────┐
│  4. Log to monitor.log                   │
│     "✅ Device deactivated successfully"  │
└─────────┬────────────────────────────────┘
          │
          ▼
    ┌──────────────┐
    │  Continues   │
    │  Monitoring  │
    └──────────────┘
```

---

## 💾 State Management

### Local State Files

All state stored in: `~/.bridgelink/`

#### 1. `tunnels.json` - Active Tunnels
```json
{
  "SERIAL123": {
    "pid": 12345,
    "url": "bridgelink.nativebridge.io:15750",
    "local_port": 5555,
    "log_file": "/Users/user/.bridgelink/tunnel_SERIAL123.log",
    "started_at": 1641234567.89,
    "device_type": "physical"
  }
}
```

#### 2. `monitor.pid` - Health Monitor Process
```
67890
```

#### 3. `health_monitor.json` - Monitor State
```json
{
  "last_check": "2025-01-20T10:30:00Z",
  "monitored_devices": ["SERIAL123", "emulator-5554"]
}
```

#### 4. `tunnel_{serial}.log` - Tunnel Logs
```
[2025-01-20 10:00:00] Starting bore tunnel...
[2025-01-20 10:00:01] listening at bridgelink.nativebridge.io:15750
[2025-01-20 10:00:01] Tunnel established
```

#### 5. `monitor.log` - Health Monitor Logs
```
🔍 Checking health of 2 active device(s)...
✓ SERIAL123: OK (device)
✓ emulator-5554: OK (offline)
```

---

## 🔌 Backend Integration

### NativeBridge API Endpoints

#### Device Schema
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "user_id": "user_abc123",
  "device_serial": "SERIAL123",
  "device_type": "physical",  // or "emulator"
  "device_details": {
    "brand": "Google",
    "model": "Pixel 6",
    "android_version": "13",
    "sdk_version": "33"
  },
  "tunnel_url": "bridgelink.nativebridge.io:15750",
  "device_state": "active",  // or "inactive"
  "created_at": "2025-01-20T10:00:00Z",
  "updated_at": "2025-01-20T10:30:00Z"
}
```

#### Key API Calls

**1. Add/Update Device**
```http
POST /api/bridgelink/devices
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "device_serial": "SERIAL123",
  "device_type": "physical",
  "device_details": {...},
  "tunnel_url": "host:port",
  "device_state": "active"
}
```

**2. Update Device State**
```http
PATCH /api/bridgelink/devices/SERIAL123/state
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "state": "inactive"
}
```

**3. List Devices**
```http
GET /api/bridgelink/devices
Authorization: Bearer {api_key}

Response: [{device}, {device}, ...]
```

---

## 🔐 Security Model

### Authentication
- **API Key**: Required for all backend operations
- **Format**: `Nb-kNGB.{random_string}`
- **Storage**: Environment variable `NB_API_KEY`
- **Transmission**: Bearer token in Authorization header

### Tunnel Security
- **bore Server**: TLS/HTTPS encryption
- **API Key Validation**: Before creating tunnels
- **No Public Discovery**: Tunnels only known to registered users

### Best Practices
- Treat tunnel URLs as secrets
- Deactivate devices when not in use
- Rotate API keys periodically
- Monitor active devices regularly

---

## ⚡ Performance Characteristics

### Health Monitoring
- **Poll Interval**: 5 seconds
- **Detection Time**: Max 5 seconds for disconnects
- **Resource Usage**: Minimal (single ADB command per poll)
- **Scalability**: Single daemon monitors unlimited devices

### Tunnel Performance
- **Latency**: +10-50ms (bore overhead)
- **Throughput**: Network-dependent
- **Reliability**: Auto-reconnect via bore

### State Management
- **File I/O**: Minimal (only on state changes)
- **Memory**: <10MB for daemon process
- **CPU**: <1% during idle monitoring

---

## 🛠️ Error Handling & Recovery

### Automatic Recovery Scenarios

1. **Tunnel Process Dies**
   - Detected by: `list_active_tunnels()` checks process existence
   - Action: Remove from state, mark device inactive

2. **Health Monitor Crashes**
   - Detected by: Stale PID file on next device add
   - Action: Clean up PID file, restart daemon

3. **Device Disconnects**
   - Detected by: Health monitor polling
   - Action: Auto-deactivate device and tunnel

4. **API Call Failures**
   - Retry: Not implemented (TODO)
   - Logging: Error logged to monitor.log
   - User Impact: Local state may be inconsistent

### Manual Recovery Commands

```bash
# Clean up dead tunnels
bridgelink daemon cleanup

# Force stop all tunnels
bridgelink daemon stop --all

# Re-activate device
bridgelink devices activate SERIAL
```

---

## 📊 Monitoring & Debugging

### Log Files

1. **Tunnel Logs**: `~/.bridgelink/tunnel_{serial}.log`
   - bore process output
   - Connection establishment
   - Errors and warnings

2. **Monitor Logs**: `~/.bridgelink/monitor.log`
   - Health check results
   - Device disconnections
   - Auto-deactivation actions

### Debug Mode

```bash
# Enable debug output
export DEBUG=1
bridgelink devices list
```

### Status Commands

```bash
# Check tunnel status
bridgelink daemon status

# View tunnel logs
bridgelink daemon logs SERIAL123

# List devices
bridgelink devices list
```

---

## 🔮 Future Enhancements

### Planned Features

1. **Retry Logic**
   - Retry failed API calls
   - Exponential backoff

2. **Notifications**
   - Slack/Email on device disconnect
   - Webhook support

3. **Multi-User Support**
   - Share devices across team
   - Role-based access

4. **Metrics & Analytics**
   - Device uptime tracking
   - Tunnel usage statistics
   - Performance monitoring

5. **Advanced Health Checks**
   - ADB connectivity test
   - Network latency monitoring
   - Automatic tunnel restart

---

## 📚 Key Design Decisions

### 1. Why Background Daemon?
- **Problem**: Polling in foreground blocks terminal
- **Solution**: Detached daemon process
- **Benefit**: Users can close terminal, monitoring continues

### 2. Why 5-Second Polling?
- **Trade-off**: Fast detection vs. resource usage
- **Decision**: 5s provides good balance
- **Rationale**: ADB commands are fast (~50ms)

### 3. Why Platform-Aware Health Checks?
- **Problem**: Emulators can be "offline" but functional
- **Solution**: Different rules for physical vs. emulator
- **Benefit**: Reduces false positives

### 4. Why Auto-Start/Stop Daemon?
- **Problem**: Users forget to start/stop monitoring
- **Solution**: Automatic lifecycle management
- **Benefit**: Zero-maintenance, always optimal

---

## 🎯 Conclusion

BridgeLink provides a robust, automated solution for exposing Android devices remotely with minimal user intervention. The architecture prioritizes:

- ✅ **Simplicity** - One command to add devices
- ✅ **Reliability** - Automatic health monitoring
- ✅ **Performance** - Fast disconnect detection
- ✅ **Maintainability** - Self-managing daemon
- ✅ **Scalability** - Single daemon for all devices

For more information, see:
- [README.md](../README.md) - User guide
- [SECURITY.md](SECURITY.md) - Security best practices
- [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md) - Backend deployment
