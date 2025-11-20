# 🧪 BridgeLink - Local Testing Guide

Complete guide for testing BridgeLink locally before releasing to PyPI.

## Prerequisites

- Python 3.8 or higher
- Android device connected via USB
- USB debugging enabled on device
- Git installed

## Quick Test (5 Minutes)

```bash
# 1. Navigate to project
cd /Users/himanshukukreja/autoflow/bridgelink

# 2. Install in editable mode
pip install -e .

# 3. Test CLI
bridgelink --version
bridgelink --help

# 4. Install dependencies
bridgelink install

# 5. Set API key
export NB_API_KEY='Nb-kNGB.your-api-key'

# 6. Add a device
bridgelink devices add <device-serial>

# 7. List devices
bridgelink devices list
```

---

## Method 1: Development Installation (Recommended)

### Step 1: Create Virtual Environment

```bash
cd /Users/himanshukukreja/autoflow/bridgelink

# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

### Step 2: Install in Editable Mode

```bash
# Install package in development mode
pip install -e .

# This installs:
# - bridgelink command
# - All dependencies
# - Links to your source code (changes reflect immediately)
```

### Step 3: Verify Installation

```bash
# Check command is available
which bridgelink
# Should show: .../venv/bin/bridgelink

# Check version
bridgelink --version
# Should show: bridgelink, version 0.1.0

# Check help
bridgelink --help
```

### Step 4: Test Core Commands

```bash
# Install dependencies
bridgelink install
# Should install bore and ADB

# Check bore is installed
bore --version

# Check ADB is installed
adb version
```

### Step 5: Set API Key

```bash
# Set environment variable
export NB_API_KEY='Nb-kNGB.your-api-key-here'

# Or add to shell profile
echo 'export NB_API_KEY="Nb-kNGB.your-api-key"' >> ~/.zshrc
source ~/.zshrc
```

### Step 6: Test Device Management

```bash
# Connect Android device via USB

# Check device is visible
adb devices

# Add device to BridgeLink
bridgelink devices add <device-serial>

# Should:
# - Detect device info (brand, model, Android version)
# - Setup ADB TCP mode
# - Create bore tunnel
# - Register device in backend
# - Show tunnel URL

# List devices
bridgelink devices list

# Should show table with device info
```

### Step 7: Test Daemon Commands

```bash
# Check tunnel status
bridgelink daemon status

# View tunnel logs
bridgelink daemon logs <device-serial>

# Follow logs (Ctrl+C to exit)
bridgelink daemon logs <device-serial> --follow
```

### Step 8: Test Deactivation

```bash
# Deactivate device
bridgelink devices deactivate <device-serial>

# Should:
# - Stop bore tunnel
# - Update device state to inactive
# - Keep device registered

# Verify status changed
bridgelink devices list
```

### Step 9: Test Removal

```bash
# Remove device completely
bridgelink devices remove <device-serial>

# Should:
# - Stop tunnel
# - Delete from backend

# Verify device removed
bridgelink devices list
```

---

## Method 2: Build and Install from Wheel

### Step 1: Build Package

```bash
cd /Users/himanshukukreja/autoflow/bridgelink

# Install build tools
pip install build twine

# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build package
python -m build

# Should create:
# - dist/bridgelink-0.1.0-py3-none-any.whl
# - dist/bridgelink-0.1.0.tar.gz
```

### Step 2: Verify Build

```bash
# Check built files
ls -lh dist/

# Validate package
twine check dist/*

# Should show: PASSED for both files

# Inspect wheel contents
unzip -l dist/bridgelink-0.1.0-py3-none-any.whl
```

### Step 3: Install from Wheel

```bash
# Create fresh virtual environment
python3 -m venv test_venv
source test_venv/bin/activate

# Install from wheel
pip install dist/bridgelink-0.1.0-py3-none-any.whl

# Test
bridgelink --version
bridgelink --help
```

### Step 4: Test Installation

```bash
# Install dependencies
bridgelink install

# Set API key
export NB_API_KEY='your-key'

# Add device
bridgelink devices add <serial>

# List devices
bridgelink devices list
```

### Step 5: Clean Up

```bash
# Deactivate and remove
deactivate
rm -rf test_venv
```

---

## Method 3: Direct Python Execution

### Without Installing

```bash
cd /Users/himanshukukreja/autoflow/bridgelink

# Install dependencies only
pip install click requests psutil colorama tabulate

# Run CLI directly
python -m bridgelink.cli --help

# Install dependencies
python -m bridgelink.cli install

# Add device
export NB_API_KEY='your-key'
python -m bridgelink.cli devices add <serial>
```

---

## Testing Scenarios

### Scenario 1: First-Time User

```bash
# 1. Fresh install
pip install -e .

# 2. No API key set
bridgelink devices add TEST123
# Should show error: "API key not provided"

# 3. Set API key
export NB_API_KEY='Nb-kNGB.xxx'

# 4. No bore installed
bridgelink devices add TEST123
# Should show error: "bore not installed"

# 5. Install bore
bridgelink install

# 6. No device connected
bridgelink devices add TEST123
# Should show error: "device not connected"

# 7. Connect device and add
bridgelink devices add <real-serial>
# Should work!
```

### Scenario 2: Multiple Devices

```bash
# Add multiple devices
bridgelink devices add SERIAL1 SERIAL2 SERIAL3

# Or comma-separated
bridgelink devices add SERIAL1,SERIAL2,SERIAL3

# List all
bridgelink devices list

# Should show all devices in table
```

### Scenario 3: Device Already Exists

```bash
# Add device
bridgelink devices add SERIAL1

# Add same device again
bridgelink devices add SERIAL1

# Should detect existing and skip or update
```

### Scenario 4: Deactivate and Reactivate

```bash
# Add device
bridgelink devices add SERIAL1

# Deactivate
bridgelink devices deactivate SERIAL1

# List - should show inactive
bridgelink devices list

# Add again (reactivate)
bridgelink devices add SERIAL1

# List - should show active
bridgelink devices list
```

### Scenario 5: Tunnel Management

```bash
# Add device
bridgelink devices add SERIAL1

# Check tunnel running
bridgelink daemon status

# View logs
bridgelink daemon logs SERIAL1

# Check process
ps aux | grep bore

# Check tunnel state file
cat ~/.bridgelink/tunnels.json
```

### Scenario 6: Error Handling

```bash
# Invalid API key
export NB_API_KEY='invalid-key'
bridgelink devices add SERIAL1
# Should show: "API key validation failed"

# Device not connected
bridgelink devices add FAKE-SERIAL
# Should show: "Device not connected"

# Deactivate non-existent device
bridgelink devices deactivate NONEXISTENT
# Should show: "Device not found"
```

---

## Platform-Specific Testing

### macOS

```bash
# Test bore installer
bridgelink install --bore-only

# Should download macOS binary
# - ARM64 for M1/M2/M3
# - x64 for Intel

# Verify
file $(which bore)
# Should show: Mach-O 64-bit executable
```

### Linux

```bash
# Test bore installer
bridgelink install --bore-only

# Should download Linux binary
# - x86_64 musl

# Verify
file $(which bore)
# Should show: ELF 64-bit LSB executable
```

### Windows

```powershell
# Test bore installer
bridgelink install --bore-only

# Should download Windows binary
# - x64 .exe

# Verify
where bore
# Should show: C:\...\bore.exe
```

---

## Backend API Testing

### Test API Key Validation

```bash
curl -X POST https://dev.api.nativebridge.io/v1/bore/validate-api-key \
  -H "Content-Type: application/json" \
  -d '{"api_key": "Nb-kNGB.xxx"}'

# Should return:
# {"valid": true, "user_id": "...", "user_email": "..."}
```

### Test Device APIs

```bash
# Add device
curl -X POST https://dev.api.nativebridge.io/v1/devices \
  -H "X-Api-Key: Nb-kNGB.xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "device_serial": "TEST123",
    "device_type": "physical",
    "device_details": {
      "brand": "Test",
      "model": "TestModel",
      "android_version": "14"
    },
    "tunnel_url": "3.6.53.225:12345",
    "device_state": "active"
  }'

# List devices
curl https://dev.api.nativebridge.io/v1/devices \
  -H "X-Api-Key: Nb-kNGB.xxx"

# Get specific device
curl https://dev.api.nativebridge.io/v1/devices/TEST123 \
  -H "X-Api-Key: Nb-kNGB.xxx"

# Update state
curl -X PATCH https://dev.api.nativebridge.io/v1/devices/TEST123/state \
  -H "X-Api-Key: Nb-kNGB.xxx" \
  -H "Content-Type: application/json" \
  -d '{"state": "inactive"}'

# Delete device
curl -X DELETE https://dev.api.nativebridge.io/v1/devices/TEST123 \
  -H "X-Api-Key: Nb-kNGB.xxx"
```

---

## Debugging

### Enable Debug Logging

```bash
# Set debug environment variable (if implemented)
export BRIDGELINK_DEBUG=1

# Run command
bridgelink devices add SERIAL123
```

### Check Tunnel State

```bash
# View tunnel state file
cat ~/.bridgelink/tunnels.json

# Should show:
# {
#   "SERIAL123": {
#     "pid": 12345,
#     "url": "3.6.53.225:54321",
#     "local_port": 5555,
#     "log_file": "...",
#     "started_at": 1234567890.0
#   }
# }
```

### Check bore Process

```bash
# Find bore processes
ps aux | grep bore

# Check specific process
ps -p <PID>

# View tunnel log
tail -f ~/.bridgelink/tunnel_SERIAL123.log
```

### Check ADB Connection

```bash
# List connected devices
adb devices

# Check TCP connection
adb connect localhost:5555

# Shell into device
adb -s localhost:5555 shell
```

---

## Common Issues

### "Command not found: bridgelink"

```bash
# Check installation
pip list | grep bridgelink

# Reinstall
pip install -e .

# Check PATH
echo $PATH

# Add ~/.local/bin to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

### "API key validation failed"

```bash
# Check API key format
echo $NB_API_KEY
# Should start with: Nb-kNGB.

# Test validation endpoint
curl -X POST https://dev.api.nativebridge.io/v1/bore/validate-api-key \
  -H "Content-Type: application/json" \
  -d "{\"api_key\": \"$NB_API_KEY\"}"
```

### "bore not installed"

```bash
# Check if bore exists
which bore

# Install manually
bridgelink install --bore-only

# Or download directly
curl -L https://github.com/himanshkukreja/nativebridge-bore-tunnel/releases/download/v0.6.1-nativebridge/bore-0.6.0-nativebridge-macos-arm64 -o bore
chmod +x bore
sudo mv bore /usr/local/bin/
```

### "ADB not found"

```bash
# Check if ADB exists
which adb

# Install via bridgelink
bridgelink install --adb-only

# Or install manually
# macOS
brew install android-platform-tools

# Linux
sudo apt-get install android-tools-adb
```

### "Could not connect to bore server"

```bash
# Test bore server connection
nc -zv 3.6.53.225 7835

# Should show: Connection succeeded

# If fails, check:
# 1. Server is running on EC2
# 2. Security group allows port 7835
# 3. Internet connection is working
```

---

## Testing Checklist

Before releasing, verify:

- [ ] Installation works: `pip install -e .`
- [ ] CLI accessible: `bridgelink --version`
- [ ] Help works: `bridgelink --help`
- [ ] bore installs: `bridgelink install --bore-only`
- [ ] ADB installs: `bridgelink install --adb-only`
- [ ] API key validates: Test with real key
- [ ] Device adds: `bridgelink devices add <serial>`
- [ ] Device lists: `bridgelink devices list`
- [ ] Daemon status: `bridgelink daemon status`
- [ ] Logs visible: `bridgelink daemon logs <serial>`
- [ ] Deactivate works: `bridgelink devices deactivate <serial>`
- [ ] Remove works: `bridgelink devices remove <serial>`
- [ ] Config shows: `bridgelink config show`
- [ ] Setup wizard: `bridgelink setup`
- [ ] Build succeeds: `python -m build`
- [ ] Package validates: `twine check dist/*`
- [ ] Wheel installs: Test in fresh venv
- [ ] All platforms: Test on macOS, Linux, Windows (if possible)

---

## Performance Testing

### Measure Tunnel Startup Time

```bash
time bridgelink devices add SERIAL123
```

### Monitor Resource Usage

```bash
# CPU and memory
top -p $(pgrep -f bore)

# Or with ps
ps aux | grep bore
```

### Test Multiple Devices

```bash
# Add 5 devices simultaneously
for i in {1..5}; do
  bridgelink devices add SERIAL$i &
done
wait

# Check all running
bridgelink daemon status
```

---

## Cleanup After Testing

```bash
# Deactivate all devices
bridgelink devices list --format json | \
  jq -r '.[].device_serial' | \
  xargs -I {} bridgelink devices deactivate {}

# Or remove all
bridgelink devices list --format json | \
  jq -r '.[].device_serial' | \
  xargs -I {} bridgelink devices remove {}

# Reset all data
bridgelink config reset

# Clean build artifacts
rm -rf build/ dist/ *.egg-info

# Deactivate venv
deactivate
```

---

## Next Steps

After local testing succeeds:

1. ✅ Verify all commands work
2. ✅ Test on different platforms (if available)
3. ✅ Fix any bugs found
4. 📦 Build package: `python -m build`
5. 🧪 Upload to TestPyPI (optional)
6. 🚀 Release to PyPI

---

## Resources

- **Quick Start**: [QUICK_START.md](QUICK_START.md)
- **PyPI Release**: [PYPI_RELEASE.md](PYPI_RELEASE.md)
- **GitHub Actions**: [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)
- **Complete Guide**: [FINAL_SUMMARY_AND_NEXT_STEPS.md](FINAL_SUMMARY_AND_NEXT_STEPS.md)

---

**Happy Testing!** 🧪
