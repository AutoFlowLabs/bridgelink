# GitHub Actions CI/CD Setup

## Overview

BridgeLink uses GitHub Actions for automated testing, building, and publishing to PyPI. The workflows are triggered automatically on commits to the `production` branch.

## Workflows

### 1. **release.yml** - Automatic PyPI Release

**Trigger:** Push to `production` branch

**What it does:**
1. ✅ **Tests** - Runs tests on multiple OS and Python versions
2. 🔨 **Builds** - Creates wheel and source distribution
3. 📦 **Publishes to TestPyPI** - Tests the upload process
4. 🧪 **Tests TestPyPI install** - Verifies TestPyPI package works
5. 🚀 **Publishes to PyPI** - Uploads to production PyPI
6. 🏷️ **Creates GitHub Release** - Automatic release with artifacts
7. 📢 **Notifies** - Success notification

**Jobs:**
- `test` - Multi-platform testing (Ubuntu, macOS, Windows)
- `build` - Package building and validation
- `publish-testpypi` - TestPyPI upload
- `test-testpypi-install` - Installation verification
- `publish-pypi` - PyPI upload
- `create-release` - GitHub release creation
- `notify` - Success notification

### 2. **test.yml** - Testing on PRs and Commits

**Trigger:** Push/PR to `main`, `develop`, or `production` branches

**What it does:**
1. 🔍 **Linting** - Code quality checks (flake8, black, isort, mypy)
2. 🧪 **Tests** - Full test suite on multiple platforms
3. 📦 **Install tests** - Wheel and source distribution installation
4. 🖥️ **Platform tests** - Platform-specific detection tests
5. 🔒 **Security** - Safety and bandit scans

**Jobs:**
- `lint` - Code quality checks
- `test` - Multi-platform test suite
- `install-test` - Installation verification
- `platform-specific` - Platform detection tests
- `security` - Security scanning

### 3. **version-bump.yml** - Manual Version Bumping

**Trigger:** Manual workflow dispatch

**What it does:**
1. 📈 **Bumps version** - Increments version number (patch/minor/major)
2. 📝 **Updates CHANGELOG** - Adds changelog entry
3. 💾 **Commits changes** - Auto-commits version bump
4. 📋 **Summary** - Creates summary of changes

**Inputs:**
- `version_type` - patch, minor, or major
- `changelog_entry` - Optional changelog description

---

## Setup Instructions

### Step 1: Repository Setup

1. **Create GitHub repository** (if not exists):
   ```bash
   cd /Users/himanshukukreja/autoflow/bridgelink
   git init
   git remote add origin https://github.com/AutoFlowLabs/bridgelink.git
   ```

2. **Create production branch**:
   ```bash
   git checkout -b production
   git push -u origin production
   ```

### Step 2: Configure PyPI Trusted Publishing

#### For PyPI (Production)

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in:
   - **PyPI Project Name**: `bridgelink`
   - **Owner**: `nativebridge` (your GitHub org/username)
   - **Repository name**: `bridgelink`
   - **Workflow name**: `release.yml`
   - **Environment name**: `pypi`
4. Click "Add"

#### For TestPyPI (Testing)

1. Go to https://test.pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in:
   - **PyPI Project Name**: `bridgelink`
   - **Owner**: `nativebridge`
   - **Repository name**: `bridgelink`
   - **Workflow name**: `release.yml`
   - **Environment name**: `testpypi`
4. Click "Add"

### Step 3: Create GitHub Environments

1. Go to repository **Settings → Environments**
2. Create two environments:

#### Environment: `testpypi`
- **No protection rules needed**
- **No secrets needed** (using trusted publishing)

#### Environment: `pypi`
- **Protection rules** (optional):
  - Required reviewers (recommended for production)
  - Wait timer (optional)
- **No secrets needed** (using trusted publishing)

### Step 4: Verify Workflows

1. **Check workflows are present**:
   ```bash
   ls -la .github/workflows/
   # Should show:
   # - release.yml
   # - test.yml
   # - version-bump.yml
   ```

2. **Commit and push workflows**:
   ```bash
   git add .github/workflows/
   git commit -m "Add GitHub Actions workflows"
   git push origin production
   ```

---

## Usage

### Automatic Release (Recommended)

Just push to production branch:

```bash
# 1. Make your changes
git add .
git commit -m "Your changes"

# 2. Push to production branch
git push origin production

# 3. GitHub Actions automatically:
#    - Tests the code
#    - Builds the package
#    - Publishes to PyPI
#    - Creates GitHub release
```

### Manual Version Bump

Use the version bump workflow:

1. Go to **Actions → Version Bump**
2. Click **Run workflow**
3. Select:
   - **Branch**: `develop` or `main`
   - **Version type**: `patch`, `minor`, or `major`
   - **Changelog entry**: Optional description
4. Click **Run workflow**
5. Review the commit
6. Merge to `production` to trigger release

### Manual Release Trigger

If you need to manually trigger a release:

1. Go to **Actions → Build and Publish to PyPI**
2. Click **Run workflow**
3. Select **Branch**: `production`
4. Click **Run workflow**

---

## Workflow Details

### Release Workflow Steps

```
┌─────────────────────────────────────────────────────────────┐
│                    Push to production                        │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────▼──────────┐
         │   1. Run Tests       │
         │   - Ubuntu          │
         │   - macOS           │
         │   - Windows         │
         │   - Python 3.8-3.12 │
         └───────────┬──────────┘
                     │
         ┌───────────▼──────────┐
         │   2. Build Package   │
         │   - Build wheel      │
         │   - Build sdist      │
         │   - Check with twine │
         └───────────┬──────────┘
                     │
         ┌───────────▼──────────────────┐
         │   3. Publish to TestPyPI    │
         │   - Test upload             │
         │   - Skip if version exists  │
         └───────────┬──────────────────┘
                     │
         ┌───────────▼──────────────────┐
         │   4. Test TestPyPI Install  │
         │   - Install from TestPyPI   │
         │   - Verify CLI works        │
         └───────────┬──────────────────┘
                     │
         ┌───────────▼──────────────┐
         │   5. Publish to PyPI     │
         │   - Production upload    │
         └───────────┬──────────────┘
                     │
         ┌───────────▼──────────────┐
         │   6. Create Release      │
         │   - Create git tag       │
         │   - Create GitHub release│
         │   - Attach artifacts     │
         └───────────┬──────────────┘
                     │
         ┌───────────▼──────────────┐
         │   7. Notify Success      │
         │   - Show links           │
         └──────────────────────────┘
```

### Test Matrix

The test workflow runs on:

**Operating Systems:**
- Ubuntu Latest
- macOS Latest
- Windows Latest

**Python Versions:**
- 3.8
- 3.9
- 3.10
- 3.11
- 3.12

**Total combinations:** 15 test jobs

---

## Environment Variables

The workflows use these automatic variables:

- `${{ secrets.GITHUB_TOKEN }}` - Automatic GitHub token
- `${{ github.repository }}` - Repository name
- `${{ github.ref_name }}` - Branch name

**No secrets need to be configured** when using trusted publishing!

---

## Versioning Strategy

### Version Format

Follow **Semantic Versioning (SemVer)**:
```
MAJOR.MINOR.PATCH
```

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes

### Examples

```
0.1.0  → 0.1.1   (patch: bug fix)
0.1.1  → 0.2.0   (minor: new feature)
0.2.0  → 1.0.0   (major: breaking change)
```

### How to Bump Version

#### Method 1: Manual (in code)

Edit `bridgelink/__init__.py`:
```python
__version__ = "0.1.1"  # Increment version
```

Edit `setup.py`:
```python
setup(
    version="0.1.1",  # Same version
    ...
)
```

Commit and push to `production`.

#### Method 2: Automated (via workflow)

Use the **Version Bump** workflow:
1. Go to Actions → Version Bump
2. Select version type (patch/minor/major)
3. Add changelog entry
4. Run workflow
5. Review and merge to production

---

## Troubleshooting

### "Trusted publisher is not configured"

**Solution**: Configure trusted publishing on PyPI/TestPyPI (see Step 2 above)

### "Version already exists on PyPI"

**Solution**: Bump the version number. You cannot overwrite existing versions on PyPI.

```bash
# Bump version
# Edit bridgelink/__init__.py and setup.py
# Then commit and push
```

### "Tests failed"

**Solution**: Check the test logs in Actions tab. Fix the failing tests locally:

```bash
pip install pytest
pytest tests/ -v
```

### "Build failed"

**Solution**: Check build logs. Test locally:

```bash
python -m build
twine check dist/*
```

### "Environment not found"

**Solution**: Create the environment in repository settings (see Step 3 above)

---

## Best Practices

### 1. Always Test Locally First

```bash
# Run tests
pytest tests/ -v

# Build package
python -m build

# Check package
twine check dist/*

# Test install
pip install dist/*.whl
bridgelink --version
```

### 2. Use Feature Branches

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and push
git push origin feature/my-feature

# Create PR to main
# After review, merge to main
# Then merge main to production for release
```

### 3. Review TestPyPI First

Before production release, check TestPyPI:
```
https://test.pypi.org/project/bridgelink/
```

### 4. Update CHANGELOG

Always update CHANGELOG.md before releasing:

```markdown
## [0.1.1] - 2024-11-20

### Added
- New feature X

### Fixed
- Bug Y

### Changed
- Improvement Z
```

### 5. Tag Releases

GitHub Actions creates tags automatically, but you can also create manually:

```bash
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

---

## Monitoring Releases

### Check Workflow Status

- **Actions tab**: https://github.com/AutoFlowLabs/bridgelink/actions
- **Badges**: Add to README for status visibility

### Check Package Status

- **PyPI**: https://pypi.org/project/bridgelink/
- **TestPyPI**: https://test.pypi.org/project/bridgelink/
- **GitHub Releases**: https://github.com/AutoFlowLabs/bridgelink/releases

### Download Stats

View download statistics:
- PyPI Stats: https://pypistats.org/packages/bridgelink
- GitHub Traffic: Repository Insights → Traffic

---

## Adding Badges to README

Add these to your README.md:

```markdown
[![Tests](https://github.com/AutoFlowLabs/bridgelink/workflows/Tests/badge.svg)](https://github.com/AutoFlowLabs/bridgelink/actions?query=workflow%3ATests)
[![PyPI](https://img.shields.io/pypi/v/bridgelink.svg)](https://pypi.org/project/bridgelink/)
[![Python Versions](https://img.shields.io/pypi/pyversions/bridgelink.svg)](https://pypi.org/project/bridgelink/)
[![Downloads](https://pepy.tech/badge/bridgelink)](https://pepy.tech/project/bridgelink)
```

---

## Support

If you encounter issues with GitHub Actions:

1. Check the Actions logs
2. Review this documentation
3. Check GitHub Actions documentation: https://docs.github.com/en/actions
4. Contact support@nativebridge.io

---

## Quick Reference

```bash
# First-time setup
1. Configure trusted publishing on PyPI
2. Create GitHub environments (testpypi, pypi)
3. Push workflows to repository

# For each release
1. Make changes and commit
2. Push to production branch
3. GitHub Actions handles the rest!

# Manual version bump
1. Go to Actions → Version Bump
2. Select version type
3. Run workflow
4. Merge to production

# Check release status
https://github.com/AutoFlowLabs/bridgelink/actions
https://pypi.org/project/bridgelink/
```
