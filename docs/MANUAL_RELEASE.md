# Manual Release Guide for BridgeLink

This guide covers manual release steps for Homebrew (macOS) and PPA (Ubuntu/Debian) after the automated PyPI release completes.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Release Overview](#release-overview)
3. [Homebrew Release (macOS)](#homebrew-release-macos)
4. [PPA Release (Ubuntu/Debian)](#ppa-release-ubuntudebian)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### For Homebrew
- macOS with Homebrew installed
- Git access to `AutoFlowLabs/homebrew-tap` repository
- PyPI release must be completed first

### For PPA
- Ubuntu/Debian server (or VM)
- GPG key registered with Launchpad
- Launchpad account with PPA created
- Required packages: `devscripts`, `debhelper`, `dh-python`, `python3-all`, `dput`

---

## Release Overview

After pushing to `production` branch, GitHub Actions automatically:
1. Runs tests
2. Builds package
3. Publishes to PyPI
4. Creates GitHub Release

**Manual steps required after PyPI release:**
- Update Homebrew formula (macOS)
- Build and upload to PPA (Ubuntu)

---

## Homebrew Release (macOS)

### Step 1: Get the SHA256 Hash

After PyPI release, get the SHA256 of the new tarball:

```bash
# Replace VERSION with actual version (e.g., 0.2.1)
VERSION="0.2.1"
curl -sL "https://files.pythonhosted.org/packages/source/b/bridgelink/bridgelink-${VERSION}.tar.gz" | shasum -a 256
```

Save the hash output (e.g., `abc123def456...`).

### Step 2: Clone the Homebrew Tap

```bash
git clone https://github.com/AutoFlowLabs/homebrew-tap.git
cd homebrew-tap
```

### Step 3: Update the Formula

Edit `Formula/bridgelink.rb`:

```bash
# Open in editor
nano Formula/bridgelink.rb
# Or use any editor: code, vim, etc.
```

Update these two lines:

```ruby
url "https://files.pythonhosted.org/packages/source/b/bridgelink/bridgelink-VERSION.tar.gz"
sha256 "YOUR_SHA256_HASH_HERE"
```

**Example:**
```ruby
url "https://files.pythonhosted.org/packages/source/b/bridgelink/bridgelink-0.2.1.tar.gz"
sha256 "abc123def456789..."
```

### Step 4: Commit and Push

```bash
git add Formula/bridgelink.rb
git commit -m "Update bridgelink to v${VERSION}"
git push origin main
```

### Step 5: Test Installation

```bash
# Update Homebrew
brew update

# If tap not added yet
brew tap AutoFlowLabs/tap

# Install/Upgrade
brew upgrade bridgelink || brew install bridgelink

# Verify
bridgelink --version
```

### Homebrew Quick Reference

```bash
# Full one-liner after getting SHA256
VERSION="0.2.1"
SHA256="your-sha256-here"

cd ~/homebrew-tap
sed -i '' "s|url \".*\"|url \"https://files.pythonhosted.org/packages/source/b/bridgelink/bridgelink-${VERSION}.tar.gz\"|" Formula/bridgelink.rb
sed -i '' "s|sha256 \".*\"|sha256 \"${SHA256}\"|" Formula/bridgelink.rb
git add Formula/bridgelink.rb && git commit -m "Update bridgelink to v${VERSION}" && git push
```

---

## PPA Release (Ubuntu/Debian)

### Step 1: SSH to Your Ubuntu Server

```bash
ssh user@your-server
```

### Step 2: Update the Repository

```bash
cd ~/bridgelink
git pull origin production
```

### Step 3: Install Build Dependencies (First Time Only)

```bash
sudo apt-get update
sudo apt-get install -y devscripts debhelper dh-python python3-all python3-setuptools python3-tabulate python3-click python3-requests python3-psutil gnupg dput
```

### Step 4: Prepare Debian Directory

```bash
cd ~/bridgelink

# Copy debian directory to project root
cp -r packaging/debian .

# Remove compat file (if exists) - compat is specified in control file
rm -f debian/compat
```

### Step 5: Update debian/changelog

```bash
# Get version from setup.py
VERSION=$(python3 -c "from bridgelink import __version__; print(__version__)")

# Create changelog entry
cat > debian/changelog << EOF
bridgelink (${VERSION}-1) jammy; urgency=medium

  * Release version ${VERSION}
  * See https://github.com/AutoFlowLabs/bridgelink/releases for details

 -- NativeBridge <support@nativebridge.io>  $(date -R)
EOF
```

### Step 6: Create Original Tarball

```bash
VERSION=$(python3 -c "from bridgelink import __version__; print(__version__)")

cd ..
tar -czvf bridgelink_${VERSION}.orig.tar.gz \
  --exclude='bridgelink/.git' \
  --exclude='bridgelink/venv' \
  --exclude='bridgelink/dist' \
  --exclude='bridgelink/build' \
  --exclude='bridgelink/*.egg-info' \
  --exclude='bridgelink/__pycache__' \
  bridgelink

cd bridgelink
```

### Step 7: Build Signed Source Package

```bash
# Get your GPG key ID
gpg --list-secret-keys --keyid-format=long
# Look for line like: sec   rsa4096/84EA3861DC96F4D1 2024-11-23 [SC]
# Your key ID is: 84EA3861DC96F4D1

# Build source package (replace with your key ID)
debuild -S -sa -k84EA3861DC96F4D1 -p"gpg --batch --pinentry-mode loopback"
```

### Step 8: Upload to PPA

```bash
VERSION=$(python3 -c "from bridgelink import __version__; print(__version__)")

# Upload to PPA
dput ppa:himanshukukreja/bridgelink ../bridgelink_${VERSION}-1_source.changes
```

### Step 9: Monitor Build

1. Check email for acceptance/rejection from Launchpad
2. Monitor build status at: https://launchpad.net/~himanshukukreja/+archive/ubuntu/bridgelink
3. Build typically takes 10-30 minutes

### Step 10: Test Installation (After Build Completes)

```bash
# On a fresh Ubuntu machine or VM
sudo add-apt-repository ppa:himanshukukreja/bridgelink
sudo apt update
sudo apt install bridgelink

# Verify
bridgelink --version
```

### PPA Quick Reference Script

Save this as `release_ppa.sh` on your server:

```bash
#!/bin/bash
set -e

cd ~/bridgelink
git pull origin production

# Get version
VERSION=$(python3 -c "from bridgelink import __version__; print(__version__)")
echo "Releasing version: ${VERSION}"

# Setup debian
cp -r packaging/debian .
rm -f debian/compat

# Update changelog
cat > debian/changelog << EOF
bridgelink (${VERSION}-1) jammy; urgency=medium

  * Release version ${VERSION}

 -- NativeBridge <support@nativebridge.io>  $(date -R)
EOF

# Create tarball
cd ..
tar -czvf bridgelink_${VERSION}.orig.tar.gz \
  --exclude='bridgelink/.git' \
  --exclude='bridgelink/venv' \
  --exclude='bridgelink/dist' \
  --exclude='bridgelink/build' \
  --exclude='bridgelink/*.egg-info' \
  bridgelink
cd bridgelink

# Build (replace YOUR_KEY_ID with your actual GPG key ID)
debuild -S -sa -kYOUR_KEY_ID -p"gpg --batch --pinentry-mode loopback"

# Upload
dput ppa:himanshukukreja/bridgelink ../bridgelink_${VERSION}-1_source.changes

echo "Done! Check https://launchpad.net/~himanshukukreja/+archive/ubuntu/bridgelink"
```

Make it executable:
```bash
chmod +x release_ppa.sh
```

---

## Troubleshooting

### Homebrew Issues

**"SHA256 mismatch"**
- Wait a few minutes after PyPI release for CDN propagation
- Re-download and recalculate SHA256

**"No available formula"**
```bash
brew tap AutoFlowLabs/tap
brew update
```

**"android-platform-tools" dependency error**
- This is now a cask, not a formula
- Install separately: `brew install --cask android-platform-tools`

### PPA Issues

**"GPG key not found"**
```bash
# List your keys
gpg --list-secret-keys --keyid-format=long

# If no keys, generate one
gpg --batch --pinentry-mode loopback --gen-key <<EOF
%echo Generating GPG key
Key-Type: RSA
Key-Length: 4096
Name-Real: Your Name
Name-Email: your-email@example.com
Expire-Date: 0
%no-protection
%commit
EOF

# Upload to keyserver
gpg --send-keys --keyserver keyserver.ubuntu.com YOUR_KEY_ID
```

**"Operation cancelled" during GPG**
```bash
# Configure GPG for headless use
mkdir -p ~/.gnupg
echo "allow-loopback-pinentry" >> ~/.gnupg/gpg-agent.conf
gpgconf --kill gpg-agent
```

**"Unmet build dependencies"**
```bash
sudo apt-get install -y debhelper dh-python python3-all python3-tabulate
```

**"debhelper compat level specified twice"**
```bash
rm debian/compat
```

**"unrepresentable changes to source"**
```bash
# Use native format
echo "3.0 (native)" > debian/source/format
```

**"Can't open .changes file"**
- Make sure you're in the right directory
- Run `debuild` first to create the file
- Check parent directory: `ls -la ../bridgelink*.changes`

**Launchpad rejects upload**
- Check email for specific error
- Common issues: invalid GPG signature, version already exists, bad changelog format

### General Tips

1. Always pull latest changes before releasing
2. Ensure version is updated in `setup.py` and `bridgelink/__init__.py`
3. PyPI release must complete before Homebrew/PPA releases
4. Keep your GPG key secure and backed up

---

## Release Checklist

### Before Release
- [ ] Update version in `setup.py`
- [ ] Update version in `bridgelink/__init__.py`
- [ ] Update `CHANGELOG.md`
- [ ] Commit and push to `main`
- [ ] Merge to `production` branch

### After PyPI Release (Automated)
- [ ] Verify PyPI: https://pypi.org/project/bridgelink/
- [ ] Verify GitHub Release created

### Manual Steps
- [ ] **Homebrew**: Update formula with new SHA256
- [ ] **PPA**: Build and upload source package
- [ ] Verify Homebrew: `brew upgrade bridgelink`
- [ ] Verify PPA: Check Launchpad build status

---

## Links

- **PyPI**: https://pypi.org/project/bridgelink/
- **GitHub**: https://github.com/AutoFlowLabs/bridgelink
- **Homebrew Tap**: https://github.com/AutoFlowLabs/homebrew-tap
- **PPA**: https://launchpad.net/~himanshukukreja/+archive/ubuntu/bridgelink
