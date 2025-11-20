# BridgeLink Documentation

Complete documentation for BridgeLink - NativeBridge CLI tool for remote Android device access.

---

## 📚 Documentation Index

### Getting Started
- **[Main README](../README.md)** - Quick start and overview
- **[Quick Start Guide](QUICK_START.md)** - Quick command reference
- **[Local Testing Guide](LOCAL_TESTING_GUIDE.md)** - Test locally before PyPI release
- **[Security Guide](SECURITY.md)** - Security best practices ⚠️ **IMPORTANT**

### Command Guides
- **[Complete Command Reference](#complete-command-reference)** - All commands with examples
- **[Activate Command Guide](ACTIVATE_COMMAND_GUIDE.md)** - Smart device activation feature
- **[Daemon Management](DAEMON_MANAGEMENT.md)** - Tunnel and process management

### Deployment & Release
- **[Deployment Steps](DEPLOYMENT_STEPS.md)** - Backend setup and deployment
- **[PyPI Release Guide](PYPI_RELEASE.md)** - Publishing to PyPI
- **[GitHub Actions Setup](GITHUB_ACTIONS_SETUP.md)** - CI/CD pipeline configuration

### Technical Documentation
- **[Complete Implementation](COMPLETE_IMPLEMENTATION_SUMMARY.md)** - Full technical overview
- **[Validation Flow](VALIDATION_FLOW.md)** - Security and input validation
- **[Project Status](PROJECT_STATUS.md)** - Current status and next steps
- **[CI/CD Summary](CICD_COMPLETE_SUMMARY.md)** - CI/CD overview

### Reference
- **[Changelog](CHANGELOG.md)** - Version history
- **[Final Summary](FINAL_SUMMARY_AND_NEXT_STEPS.md)** - Complete summary

---

## Complete Command Reference

### Installation & Setup

#### Install BridgeLink
```bash
pip install bridgelink
```

#### Install Dependencies
```bash
bridgelink install                # Install both bore and ADB
bridgelink install --bore-only    # Install only bore tunnel
bridgelink install --adb-only     # Install only ADB
```

#### Check Version
```bash
bridgelink --version
```

#### Get Help
```bash
bridgelink --help                 # Main help
bridgelink devices --help         # Device commands
bridgelink daemon --help          # Daemon commands
```

---

### Device Management Commands

#### Add Device
Register a new device or reactivate an existing one.

```bash
# Single device
bridgelink devices add <device-serial>

# Multiple devices (space-separated)
bridgelink devices add <serial1> <serial2> <serial3>

# Multiple devices (comma-separated)
bridgelink devices add <serial1>,<serial2>,<serial3>
```

**Examples:**
```bash
bridgelink devices add 1d752b81
bridgelink devices add 1d752b81 emulator-5554
bridgelink devices add 1d752b81,emulator-5554,2a3b4c5d
```

**What it does:**
- ✅ Validates device serial via ADB
- ✅ Gets device information (brand, model, Android version)
- ✅ Sets up ADB TCP mode
- ✅ Creates bore tunnel in background
- ✅ Registers device in NativeBridge backend
- ✅ Returns tunnel URL for remote access

---

#### Activate Device
Reactivate an existing registered device that is currently inactive.

```bash
bridgelink devices activate <device-serial>
```

**Smart behavior:**
- If device is **inactive** → Reactivates it with new tunnel
- If device is **active** → Shows current tunnel URL
- If device is **not registered** → Prompts to register it now

**Example:**
```bash
bridgelink devices activate 1d752b81
```

See **[Activate Command Guide](ACTIVATE_COMMAND_GUIDE.md)** for detailed documentation.

---

#### List Devices
View all registered devices and their status.

```bash
# Table format (default)
bridgelink devices list

# JSON format
bridgelink devices list --format json
```

**Example output:**
```
╒══════════╤════════════╤══════════╤══════════╤════════════╤════════════════════════════════════════════╕
│ Serial   │ Model      │ Brand    │ Type     │ State      │ Tunnel URL                                 │
╞══════════╪════════════╪══════════╪══════════╪════════════╪════════════════════════════════════════════╡
│ 1d752b81 │ 24116PCC1I │ Xiaomi   │ physical │ ✓ active   │ bridgelink.nativebridge.io:15750           │
│ emulator │ Pixel 6    │ Google   │ emulator │ ○ inactive │ (last: bridgelink.nativebridge.io:12345)   │
╘══════════╧════════════╧══════════╧══════════╧════════════╧════════════════════════════════════════════╛
```

**Visual indicators:**
- `✓ active` - Device has live tunnel running
- `○ inactive` - Device is registered but tunnel is stopped
- `(last: ...)` - Shows last tunnel URL for inactive devices

---

#### Deactivate Device
Stop the tunnel but keep device registration.

```bash
bridgelink devices deactivate <device-serial>
```

**What it does:**
- ✅ Stops bore tunnel process
- ✅ Updates device state to `inactive` in backend
- ✅ Keeps device registration (can reactivate later)

**Example:**
```bash
bridgelink devices deactivate 1d752b81
```

---

#### Remove Device
Completely delete device from NativeBridge.

```bash
bridgelink devices remove <device-serial>
```

**Confirmation prompt:**
```
Are you sure you want to remove this device? [y/N]:
```

**What it does:**
- ✅ Stops bore tunnel process
- ✅ Deletes device from backend database
- ⚠️ **Cannot be undone** (must re-add to use again)

**Example:**
```bash
bridgelink devices remove 1d752b81
```

---

### Daemon Management Commands

#### Check Tunnel Status
View all running bore tunnels.

```bash
bridgelink daemon status
```

**Example output:**
```
╒═══════════════╤════════════════════════════════════╤══════════════╤═══════╤═════════════════════╕
│ Device Serial │ Tunnel URL                         │ Local Port   │ PID   │ Started At          │
╞═══════════════╪════════════════════════════════════╪══════════════╪═══════╪═════════════════════╡
│ 1d752b81      │ bridgelink.nativebridge.io:15750   │ 5555         │ 12345 │ 2025-01-20 10:30:15 │
│ emulator-5554 │ bridgelink.nativebridge.io:15751   │ 5556         │ 12346 │ 2025-01-20 10:31:22 │
╘═══════════════╧════════════════════════════════════╧══════════════╧═══════╧═════════════════════╛

Total active tunnels: 2
```

---

#### View Tunnel Logs
View logs for a specific device tunnel.

```bash
# View last 50 lines (default)
bridgelink daemon logs <device-serial>

# View last N lines
bridgelink daemon logs <device-serial> --lines 100

# Follow logs in real-time
bridgelink daemon logs <device-serial> --follow
```

**Examples:**
```bash
bridgelink daemon logs 1d752b81
bridgelink daemon logs 1d752b81 -n 200
bridgelink daemon logs 1d752b81 -f
```

---

#### Stop Tunnel
Stop a specific device tunnel.

```bash
bridgelink daemon stop <device-serial>
```

**What it does:**
- ✅ Terminates bore tunnel process
- ✅ Removes from active tunnels list
- ⚠️ Does **not** update backend (use `deactivate` for that)

**Example:**
```bash
bridgelink daemon stop 1d752b81
```

---

#### Cleanup Dead Tunnels
Remove dead/orphaned tunnel processes from state.

```bash
bridgelink daemon cleanup
```

**What it does:**
- ✅ Checks all tracked tunnels
- ✅ Removes entries for dead processes
- ✅ Cleans up state file

---

## Command Comparison

| Command | Backend Call | Tunnel Action | Use Case |
|---------|-------------|---------------|----------|
| `add` | ✅ Register/Update | ✅ Create | First time or re-add device |
| `activate` | ✅ Update if exists | ✅ Create | Reactivate existing device |
| `deactivate` | ✅ Update state | ✅ Stop | Temporarily stop device |
| `remove` | ✅ Delete | ✅ Stop | Permanently remove device |
| `list` | ✅ Fetch all | - | View device status |
| `daemon status` | - | - | View running tunnels |
| `daemon stop` | - | ✅ Stop | Stop tunnel only |

---

## Typical Workflows

### First Time Setup
```bash
# 1. Install
pip install bridgelink
bridgelink install

# 2. Set API key
export NB_API_KEY='Nb-kNGB.xxx'

# 3. Add device
bridgelink devices add 1d752b81

# 4. Use device remotely
adb connect bridgelink.nativebridge.io:15750
```

### Daily Usage
```bash
# Morning: Activate devices
bridgelink devices activate 1d752b81
bridgelink devices activate emulator-5554

# Check status
bridgelink devices list
bridgelink daemon status

# Evening: Deactivate when done
bridgelink devices deactivate 1d752b81
bridgelink devices deactivate emulator-5554
```

### Maintenance
```bash
# View tunnel logs
bridgelink daemon logs 1d752b81

# Clean up dead tunnels
bridgelink daemon cleanup

# Remove old devices
bridgelink devices remove old-device-serial
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NB_API_KEY` | NativeBridge API key | *Required* |
| `NB_API_URL` | Backend API URL | `https://dev.api.nativebridge.io` |
| `BORE_SERVER` | Bore tunnel server | `bridgelink.nativebridge.io` |
| `DEBUG` | Enable debug logging | `false` |

### Configuration Files

BridgeLink stores configuration and state in `~/.bridgelink/`:

```
~/.bridgelink/
├── tunnels.json              # Tunnel state (PIDs, URLs, ports)
├── tunnel_<serial>.log       # Individual tunnel logs
└── config.json               # User configuration (future)
```

---

## Troubleshooting

### No Devices Found
```bash
❌ No Android devices found via ADB
```

**Solution:**
1. Check USB connection: `adb devices`
2. Enable USB debugging on device
3. Authorize computer on device screen
4. Reconnect and retry

### Invalid Device Serial
```bash
❌ Device 'abc123' is not a valid connected device
Connected devices: 1d752b81, emulator-5554
```

**Solution:**
- Check device serial is correct
- Ensure device is connected (`adb devices`)
- Use correct serial from connected devices list

### API Key Issues
```bash
❌ API key validation failed
```

**Solution:**
```bash
# 1. Check API key is set
echo $NB_API_KEY

# 2. Set correct API key
export NB_API_KEY='Nb-kNGB.your-actual-key'

# 3. Get API key from dashboard
# https://nativebridge.io/dashboard/api-keys
```

### Tunnel Creation Failed
```bash
❌ Failed to create tunnel for 1d752b81
```

**Solution:**
1. Check bore server is reachable: `ping bridgelink.nativebridge.io`
2. View tunnel logs: `bridgelink daemon logs 1d752b81`
3. Check ADB TCP mode: `adb devices`
4. Retry: `bridgelink devices activate 1d752b81`

---

## Support

- **Email:** support@nativebridge.io
- **Issues:** https://github.com/AutoFlowLabs/bridgelink/issues
- **Docs:** https://docs.nativebridge.io/bridgelink
- **API Key:** https://nativebridge.io/dashboard/api-keys

---

Made with ❤️ by the [NativeBridge](https://nativebridge.io) team
