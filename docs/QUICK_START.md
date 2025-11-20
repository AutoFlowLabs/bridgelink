# 🚀 BridgeLink - Quick Start Guide

## For End Users (After PyPI Release)

### Install
```bash
pip install bridgelink
```

### Setup
```bash
# Install dependencies (bore + ADB)
bridgelink install

# Set API key
export NB_API_KEY='Nb-kNGB.your-api-key'

# Run setup wizard (optional)
bridgelink setup
```

### Use
```bash
# Add device
bridgelink devices add <device-serial>

# List devices
bridgelink devices list

# Deactivate device
bridgelink devices deactivate <device-serial>

# View logs
bridgelink daemon logs <device-serial>
```

---

## For Testing Locally (Before Release)

### Install in Development Mode
```bash
cd /Users/himanshukukreja/autoflow/bridgelink
pip install -e .
```

### Test All Features
```bash
# Install dependencies
bridgelink install

# Set API key
export NB_API_KEY='Nb-kNGB.4ae4797e-1e8b-4ccb-a3fa-2ba7abdaa24d'

# Test device commands
bridgelink devices add 1d752b81
bridgelink devices list
bridgelink daemon status
bridgelink devices deactivate 1d752b81
```

---

## For Deploying Backend

### Deploy Backend Changes
```bash
cd /Users/himanshukukreja/autoflow/app-anywhere-backend

# Verify new files exist
ls -la routes/bridgelink_device_routes.py
ls -la services/bridgelink_device_service.py

# Deploy (your deployment method)
git add .
git commit -m "Add BridgeLink device management API"
git push

# Or restart server if running locally
# Your deployment process here
```

### Start bore Server on EC2
```bash
ssh ubuntu@3.6.53.225

# Start bore server with validation
bore server --api-validation-url https://dev.api.nativebridge.io/v1/bore/validate-api-key

# Or use systemd (see EC2_BORE_SERVER_SETUP.md)
```

---

## For Publishing to PyPI

### Build Package
```bash
cd /Users/himanshukukreja/autoflow/bridgelink

# Clean
rm -rf build/ dist/ *.egg-info

# Build
python -m build
```

### Publish
```bash
# To PyPI
python -m twine upload dist/*

# Or to TestPyPI first
python -m twine upload --repository testpypi dist/*
```

---

## Common Commands Reference

### Installation
```bash
bridgelink install                    # Install bore + ADB
bridgelink install --bore-only        # Install only bore
bridgelink install --adb-only         # Install only ADB
```

### Devices
```bash
bridgelink devices add SERIAL1 SERIAL2    # Add multiple devices
bridgelink devices add SERIAL1,SERIAL2    # Comma-separated
bridgelink devices list                   # Table format
bridgelink devices list --format json     # JSON format
bridgelink devices deactivate SERIAL      # Stop tunnel
bridgelink devices remove SERIAL          # Delete device
```

### Daemon
```bash
bridgelink daemon status                  # Show active tunnels
bridgelink daemon logs SERIAL             # View logs
bridgelink daemon logs SERIAL --follow    # Follow logs
bridgelink daemon cleanup                 # Clean dead tunnels
```

### Config
```bash
bridgelink config show                    # Show config
bridgelink config set-api-key 'KEY'       # Set API key
bridgelink config reset                   # Reset all data
```

### Help
```bash
bridgelink --help                         # General help
bridgelink --version                      # Version
bridgelink devices --help                 # Device help
bridgelink daemon --help                  # Daemon help
```

---

## File Locations

### Data
```bash
~/.bridgelink/tunnels.json                # Tunnel state
~/.bridgelink/tunnel_SERIAL.log           # Tunnel logs
```

### Binaries (macOS/Linux)
```bash
/usr/local/bin/bore                       # bore (if writable)
~/.local/bin/bore                         # bore (fallback)
~/.local/share/bridgelink/platform-tools/adb  # ADB
```

---

## Environment Variables

```bash
export NB_API_KEY='Nb-kNGB.xxx'           # Required
export NB_API_URL='https://dev.api.nativebridge.io'  # Optional
export BORE_SERVER='3.6.53.225'           # Optional
```

---

## Backend API Endpoints

```bash
# bore validation (public)
POST /v1/bore/validate-api-key

# Device management (requires X-Api-Key header)
POST   /v1/devices                        # Add device
GET    /v1/devices                        # List devices
GET    /v1/devices/{serial}               # Get device
PATCH  /v1/devices/{serial}/state         # Update state
DELETE /v1/devices/{serial}               # Delete device
```

---

## Troubleshooting

### API key validation failed
```bash
# Test validation endpoint
curl -X POST https://dev.api.nativebridge.io/v1/bore/validate-api-key \
  -H "Content-Type: application/json" \
  -d '{"api_key": "Nb-kNGB.xxx"}'
```

### bore server not reachable
```bash
# Test connection
nc -zv 3.6.53.225 7835
```

### ADB device not showing
```bash
# Check connected devices
adb devices

# Restart ADB
adb kill-server && adb start-server
```

### View bridgelink logs
```bash
# Tunnel logs
cat ~/.bridgelink/tunnel_SERIAL123.log

# Or use daemon command
bridgelink daemon logs SERIAL123 --follow
```

---

## Quick Testing Checklist

- [ ] Install: `pip install -e .`
- [ ] Install deps: `bridgelink install`
- [ ] Set API key: `export NB_API_KEY='...'`
- [ ] Add device: `bridgelink devices add SERIAL`
- [ ] List devices: `bridgelink devices list`
- [ ] Check status: `bridgelink daemon status`
- [ ] View logs: `bridgelink daemon logs SERIAL`
- [ ] Deactivate: `bridgelink devices deactivate SERIAL`
- [ ] Test remote: `adb connect TUNNEL_URL`

---

## Resources

- **Full Summary**: [FINAL_SUMMARY_AND_NEXT_STEPS.md](FINAL_SUMMARY_AND_NEXT_STEPS.md)
- **Testing Guide**: [TESTING_LOCALLY.md](TESTING_LOCALLY.md)
- **PyPI Guide**: [PYPI_RELEASE.md](PYPI_RELEASE.md)
- **Implementation**: [COMPLETE_IMPLEMENTATION_SUMMARY.md](COMPLETE_IMPLEMENTATION_SUMMARY.md)
