# BridgeLink Security Guide

## 🛡️ Security Overview

BridgeLink creates secure tunnels to your Android devices, but like any remote access tool, it requires proper security practices to keep your devices safe.

---

## ⚠️ CRITICAL SECURITY WARNING

### Tunnel URLs are SECRETS!

When you activate a device, BridgeLink displays a tunnel URL:

```bash
✅ SUCCESS
Device 1d752b81 is now active!
Connect from anywhere:
  adb connect bridgelink.nativebridge.io:35553

⚠️  SECURITY WARNING:
   Treat this tunnel URL as a SECRET!
   Anyone with this URL can connect to your device.
   Deactivate when not in use: bridgelink devices deactivate 1d752b81
```

**⚠️ IMPORTANT:** The tunnel URL `bridgelink.nativebridge.io:35553` is like a password - **anyone who has it can connect to your device!**

---

## 🔒 Security Best Practices

### 1. **Keep Tunnel URLs Private**

❌ **DON'T:**
- Share tunnel URLs in public channels (Slack, Discord, etc.)
- Commit tunnel URLs to git repositories
- Post tunnel URLs in screenshots or documentation
- Leave tunnel URLs in shared documents

✅ **DO:**
- Treat tunnel URLs like passwords
- Share only via secure channels if absolutely necessary
- Delete shared URLs after use
- Use environment variables for scripts

**Example - Secure Sharing:**
```bash
# Bad - visible in history/logs
adb connect bridgelink.nativebridge.io:35553

# Better - use environment variable
export DEVICE_URL="bridgelink.nativebridge.io:35553"
adb connect $DEVICE_URL

# Best - get URL dynamically from bridgelink
DEVICE_URL=$(bridgelink devices list --format json | jq -r '.[0].tunnel_url')
adb connect $DEVICE_URL
```

---

### 2. **Deactivate When Not in Use**

Always deactivate devices when you're done:

```bash
# When you're done testing
bridgelink devices deactivate 1d752b81
```

**Why this matters:**
- ✅ Closes the tunnel (URL becomes invalid)
- ✅ Saves server resources
- ✅ Reduces attack surface
- ✅ Prevents unauthorized access

**Best Practice - Use in Sessions:**
```bash
# Morning: Activate for work
bridgelink devices activate 1d752b81

# ... do your work ...

# Evening: Deactivate when done
bridgelink devices deactivate 1d752b81
```

---

### 3. **Monitor Active Tunnels**

Regularly check what tunnels are running:

```bash
# Check active tunnels
bridgelink daemon status

# Clean up dead tunnels
bridgelink daemon cleanup
```

**Look for:**
- ❌ Tunnels you don't recognize
- ❌ Devices that should be inactive
- ❌ Old/stale tunnel processes

---

### 4. **Protect Your API Key**

Your NativeBridge API key (`NB_API_KEY`) is also sensitive:

❌ **DON'T:**
- Commit to git repositories
- Share in public channels
- Hardcode in scripts

✅ **DO:**
- Store in environment variables
- Use `.env` files (add to `.gitignore`)
- Rotate periodically

**Example - Secure Storage:**
```bash
# ~/.bashrc or ~/.zshrc
export NB_API_KEY='Nb-kNGB.your-secret-key'

# Or use .env file (git ignored)
echo "NB_API_KEY='Nb-kNGB.your-secret-key'" > .env
source .env
```

---

### 5. **Use Device Authorization**

On your Android device:
- ✅ Enable screen lock
- ✅ Review USB debugging authorizations regularly
- ✅ Revoke unknown computer authorizations

**How to check authorizations:**
```
Settings → Developer Options → Revoke USB debugging authorizations
```

---

## 🚨 Security Scenarios

### Scenario 1: Tunnel URL Leaked

**If you accidentally share a tunnel URL:**

1. **Immediately deactivate the device:**
   ```bash
   bridgelink devices deactivate <device-serial>
   ```

2. **Verify tunnel is stopped:**
   ```bash
   bridgelink daemon status
   ```

3. **Reactivate with new URL:**
   ```bash
   bridgelink devices activate <device-serial>
   ```

**Result:** Old URL is invalidated, new URL is generated.

---

### Scenario 2: API Key Compromised

**If your API key is exposed:**

1. **Immediately revoke the key** in NativeBridge Dashboard:
   - Go to https://nativebridge.io/dashboard/api-keys
   - Delete the compromised key

2. **Generate a new API key**

3. **Update your environment:**
   ```bash
   export NB_API_KEY='Nb-kNGB.new-secret-key'
   ```

4. **Deactivate all devices:**
   ```bash
   bridgelink devices list
   bridgelink devices deactivate <device-1>
   bridgelink devices deactivate <device-2>
   ```

5. **Reactivate with new key**

---

### Scenario 3: Unauthorized Access Detected

**If you suspect unauthorized access:**

1. **Immediately deactivate all devices:**
   ```bash
   # Get all device serials
   bridgelink devices list

   # Deactivate each one
   bridgelink devices deactivate <serial-1>
   bridgelink devices deactivate <serial-2>
   ```

2. **Stop all tunnels:**
   ```bash
   bridgelink daemon cleanup
   ```

3. **Check device logs:**
   ```bash
   # On Android device
   adb logcat -d > device_logs.txt
   ```

4. **Review ADB authorizations:**
   - Settings → Developer Options → Revoke USB debugging authorizations

5. **Contact support:**
   - Email: support@nativebridge.io
   - Include: Timeline, suspected access, device serials

---

## 🔐 Security Features

### Built-in Security

BridgeLink includes several security features:

#### 1. **API Key Authentication**
- All API calls require valid NativeBridge API key
- Keys are validated server-side
- Invalid keys are rejected immediately

#### 2. **User Isolation**
- Each user only sees their own devices
- Devices are scoped to user accounts
- No cross-user access possible

#### 3. **Input Validation**
- Device serials validated via ADB before backend calls
- Prevents injection attacks
- Rejects invalid/malicious input

#### 4. **HTTPS Encryption**
- All API communication uses HTTPS
- Tunnel traffic is encrypted
- Man-in-the-middle protection

#### 5. **Tunnel Server Authentication**
- bore server validates API keys
- Only authorized users can create tunnels
- Tunnels are user-specific

---

## 📋 Security Checklist

### Daily Usage
- [ ] Activate devices only when needed
- [ ] Deactivate devices after use
- [ ] Don't share tunnel URLs
- [ ] Monitor active tunnels
- [ ] Review device list periodically

### Weekly
- [ ] Check for stale/inactive devices
- [ ] Clean up dead tunnels: `bridgelink daemon cleanup`
- [ ] Review ADB authorizations on devices
- [ ] Check for unknown connected devices

### Monthly
- [ ] Review and remove unused devices
- [ ] Rotate API keys (optional but recommended)
- [ ] Update BridgeLink to latest version
- [ ] Review security logs

---

## 🔍 Security Audit Commands

```bash
# 1. Check what devices are registered
bridgelink devices list

# 2. Check what tunnels are running
bridgelink daemon status

# 3. View tunnel logs
bridgelink daemon logs <device-serial>

# 4. Clean up dead processes
bridgelink daemon cleanup

# 5. Check ADB connections
adb devices

# 6. Check API key (ensure it's set securely)
echo $NB_API_KEY | head -c 20  # Should show Nb-kNGB.xxx
```

---

## 🚫 What BridgeLink CANNOT Protect Against

While BridgeLink provides security features, you must still:

❌ **Physical Security**
- Lock your computer when away
- Secure your Android devices
- Don't leave devices unattended

❌ **Leaked Credentials**
- Keep API keys secure
- Don't share tunnel URLs
- Use strong passwords

❌ **Compromised Devices**
- Keep Android OS updated
- Don't install untrusted apps
- Review app permissions

❌ **Network Security**
- Use secure WiFi networks
- Avoid public WiFi for sensitive work
- Use VPN if needed

---

## 📞 Security Support

### Reporting Security Issues

**Found a security vulnerability?**

**Email:** security@nativebridge.io

**Please include:**
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

**We commit to:**
- Respond within 24 hours
- Investigate and fix promptly
- Credit security researchers (with permission)

### Getting Security Help

**Need security assistance?**

**Email:** support@nativebridge.io

**Community:**
- Issues: https://github.com/AutoFlowLabs/bridgelink/issues
- Discussions: https://github.com/AutoFlowLabs/bridgelink/discussions

---

## 📚 Additional Resources

### Official Documentation
- [Main README](../README.md)
- [Command Reference](README.md)
- [Validation Flow](VALIDATION_FLOW.md)

### Security Best Practices
- [OWASP Mobile Security](https://owasp.org/www-project-mobile-security/)
- [Android Security Best Practices](https://developer.android.com/training/articles/security-tips)
- [ADB Security](https://developer.android.com/studio/command-line/adb#security)

---

## 🎯 Key Takeaways

1. **Tunnel URLs are SECRETS** - Treat like passwords
2. **Deactivate when not in use** - Close tunnels after work
3. **Monitor active tunnels** - Regular security audits
4. **Protect your API key** - Never commit or share
5. **Use device authorization** - Lock and monitor your devices

---

**Stay secure!** 🔒

**Last Updated:** 2025-01-20
**Version:** 1.0.0
