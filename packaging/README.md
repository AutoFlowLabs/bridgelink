# BridgeLink Packaging Guide

This guide explains how to build and distribute BridgeLink packages for different platforms.

## 📦 Distribution Methods

BridgeLink is available via three distribution channels:

| Method | Platform | Command |
|--------|----------|---------|
| Homebrew | macOS | `brew install AutoFlowLabs/tap/bridgelink` |
| APT | Debian/Ubuntu | `apt install bridgelink` |
| PyPI | All platforms | `pip install bridgelink` |

---

## 🍺 Homebrew (macOS)

### Prerequisites

1. A GitHub repository for the Homebrew tap (e.g., `AutoFlowLabs/homebrew-tap`)
2. PyPI package published first (Homebrew downloads from PyPI)

### Setup Homebrew Tap

1. **Create the tap repository:**
   ```bash
   # Create a new repo named "homebrew-tap" under AutoFlowLabs
   # GitHub URL: https://github.com/AutoFlowLabs/homebrew-tap
   ```

2. **Copy the formula:**
   ```bash
   # Copy the formula to the tap repository
   cp packaging/homebrew/bridgelink.rb /path/to/homebrew-tap/Formula/
   ```

3. **Update SHA256 hash:**

   After publishing to PyPI, get the SHA256:
   ```bash
   # Download the tarball and calculate SHA256
   curl -sL https://files.pythonhosted.org/packages/source/b/bridgelink/bridgelink-0.2.0.tar.gz | shasum -a 256
   ```

   Update the `sha256` line in `bridgelink.rb`.

4. **Commit and push:**
   ```bash
   cd /path/to/homebrew-tap
   git add Formula/bridgelink.rb
   git commit -m "Add bridgelink formula v0.2.0"
   git push origin main
   ```

### User Installation

```bash
# First time: Add the tap
brew tap AutoFlowLabs/tap

# Install
brew install bridgelink

# Or in one command
brew install AutoFlowLabs/tap/bridgelink
```

### Updating the Formula

When releasing a new version:

1. Update `url` with new version number
2. Update `sha256` with new hash
3. Push changes to homebrew-tap repository

---

## 🐧 APT (Debian/Ubuntu)

### Prerequisites

1. A Launchpad account (https://launchpad.net)
2. GPG key for signing packages
3. PPA created on Launchpad

### Setup PPA

1. **Create a PPA on Launchpad:**
   - Go to https://launchpad.net/~himanshukukreja
   - Create a PPA named `bridgelink`
   - PPA URL will be: `ppa:himanshukukreja/bridgelink`

2. **Set up GPG key:**
   ```bash
   # Generate GPG key if not exists
   gpg --gen-key

   # Export and upload to Ubuntu keyserver
   gpg --send-keys --keyserver keyserver.ubuntu.com YOUR_KEY_ID
   ```

3. **Configure dput for uploads:**

   Create `~/.dput.cf`:
   ```ini
   [bridgelink-ppa]
   fqdn = ppa.launchpad.net
   method = ftp
   incoming = ~himanshukukreja/bridgelink/ubuntu/
   login = anonymous
   allow_unsigned_uploads = 0
   ```

### Building the Debian Package

1. **Prepare the source:**
   ```bash
   cd /path/to/bridgelink

   # Copy debian directory
   cp -r packaging/debian .

   # Create source tarball
   tar -czvf ../bridgelink_0.2.0.orig.tar.gz --exclude=debian --exclude=.git .
   ```

2. **Build source package:**
   ```bash
   # Build source package for PPA
   debuild -S -sa

   # This creates:
   # - bridgelink_0.2.0-1.dsc
   # - bridgelink_0.2.0-1.debian.tar.xz
   # - bridgelink_0.2.0-1_source.changes
   ```

3. **Upload to PPA:**
   ```bash
   dput bridgelink-ppa ../bridgelink_0.2.0-1_source.changes
   ```

4. **Wait for build:**

   Launchpad will build the package for different Ubuntu versions.
   Check status at: https://launchpad.net/~himanshukukreja/+archive/ubuntu/bridgelink

### User Installation

```bash
# Add repository
sudo add-apt-repository ppa:himanshukukreja/bridgelink
sudo apt update

# Install
sudo apt install bridgelink
```

### Alternative: Local .deb Package

For direct distribution without PPA:

```bash
# Build binary package locally
cd /path/to/bridgelink
cp -r packaging/debian .
dpkg-buildpackage -us -uc -b

# Install locally
sudo dpkg -i ../bridgelink_0.2.0-1_all.deb
sudo apt-get install -f  # Fix dependencies
```

---

## 🐍 PyPI

### Prerequisites

1. PyPI account (https://pypi.org)
2. `twine` installed: `pip install twine`

### Building and Publishing

```bash
cd /path/to/bridgelink

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build packages
python3 setup.py sdist bdist_wheel

# Upload to PyPI
twine upload dist/*
```

### User Installation

```bash
pip install bridgelink
```

---

## 🔨 Build Script

Use the provided build script to build all packages:

```bash
./packaging/build_packages.sh
```

This script:
1. Builds PyPI packages (sdist and wheel)
2. Calculates SHA256 for Homebrew formula
3. Updates the Homebrew formula automatically
4. Builds Debian package (if on Linux)

---

## 🔐 GitHub Secrets (Required for CI/CD)

To enable automatic releases via GitHub Actions, configure these secrets in your repository:

### Required Secrets

| Secret | Description | How to Get |
|--------|-------------|------------|
| `GPG_PRIVATE_KEY` | GPG private key for signing PPA packages | `gpg --armor --export-secret-keys YOUR_KEY_ID` |
| `GPG_PASSPHRASE` | Passphrase for the GPG key | The passphrase you set when creating the key |
| `HOMEBREW_TAP_TOKEN` | GitHub PAT with write access to homebrew-tap repo | GitHub Settings → Developer Settings → PAT |

### Setting Up GPG Key for PPA

1. **Export your GPG private key:**
   ```bash
   # On your server where you created the GPG key
   gpg --armor --export-secret-keys YOUR_KEY_ID
   ```

2. **Add to GitHub Secrets:**
   - Go to your repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `GPG_PRIVATE_KEY`
   - Value: Paste the entire output (including BEGIN/END lines)

3. **Add GPG passphrase:**
   - Name: `GPG_PASSPHRASE`
   - Value: Your GPG key passphrase (leave empty if no passphrase)

### Setting Up Homebrew Tap Token

1. **Create a Personal Access Token:**
   - Go to GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
   - Generate new token with `repo` scope
   - Copy the token

2. **Add to GitHub Secrets:**
   - Name: `HOMEBREW_TAP_TOKEN`
   - Value: The PAT you created

---

## 📋 Release Checklist

### Before Release

- [ ] Update version in `setup.py`
- [ ] Update version in `bridgelink/__init__.py`
- [ ] Update `CHANGELOG.md`
- [ ] Run tests
- [ ] Commit all changes

### Automatic Release (Recommended)

Simply push to the `production` branch - GitHub Actions will automatically:

1. Run tests on multiple platforms
2. Build and publish to PyPI
3. Build Debian package
4. Upload to PPA (`ppa:himanshukukreja/bridgelink`)
5. Update Homebrew tap
6. Create GitHub Release with all artifacts

```bash
git checkout production
git merge main
git push origin production
```

### Manual Release Steps

If you prefer manual releases:

1. **Tag the release:**
   ```bash
   git tag -a v0.2.0 -m "Version 0.2.0"
   git push origin v0.2.0
   ```

2. **Build and publish to PyPI:**
   ```bash
   ./packaging/build_packages.sh
   twine upload dist/*
   ```

3. **Update Homebrew tap:**
   ```bash
   # Update SHA256 in formula
   # Push to homebrew-tap repository
   ```

4. **Upload to PPA:**
   ```bash
   # Build and upload Debian source package
   debuild -S -sa
   dput bridgelink-ppa ../bridgelink_0.2.0-1_source.changes
   ```

5. **Create GitHub Release:**
   - Go to GitHub releases
   - Create release from tag
   - Attach dist/* files
   - Copy changelog notes

---

## 🗂️ Directory Structure

```
packaging/
├── README.md              # This file
├── build_packages.sh      # Build script for all packages
├── homebrew/
│   └── bridgelink.rb      # Homebrew formula
└── debian/
    ├── changelog          # Debian changelog
    ├── compat             # Debian compat version
    ├── control            # Package metadata
    ├── copyright          # License information
    ├── postinst           # Post-installation script
    └── rules              # Build rules
```

---

## 🆘 Troubleshooting

### Homebrew Issues

**"No available formula with the name bridgelink"**
```bash
# Make sure tap is added
brew tap AutoFlowLabs/tap
brew update
```

**"SHA256 mismatch"**
```bash
# Formula SHA256 doesn't match PyPI. Update the formula.
```

### APT Issues

**"Package not found"**
```bash
# Make sure PPA is added
sudo add-apt-repository ppa:himanshukukreja/bridgelink
sudo apt update
```

**"Dependencies not satisfiable"**
```bash
# Install missing dependencies
sudo apt-get install -f
```

### PyPI Issues

**"Permission denied"**
```bash
# Use --user flag or virtual environment
pip install --user bridgelink
```

---

## 📚 References

- [Homebrew Formula Cookbook](https://docs.brew.sh/Formula-Cookbook)
- [Debian Packaging Tutorial](https://www.debian.org/doc/manuals/maint-guide/)
- [Launchpad PPA Guide](https://help.launchpad.net/Packaging/PPA)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
