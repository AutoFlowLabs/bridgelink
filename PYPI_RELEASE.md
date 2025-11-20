## Publishing BridgeLink to PyPI

This guide covers the complete process of releasing BridgeLink to PyPI so users can install it with `pip install bridgelink`.

### Prerequisites

1. **PyPI Account**: Create account at https://pypi.org/account/register/
2. **PyPI API Token**: Generate at https://pypi.org/manage/account/token/
3. **Test PyPI Account** (optional): Create at https://test.pypi.org/account/register/

### One-Time Setup

#### 1. Install Publishing Tools

```bash
pip install --upgrade build twine
```

#### 2. Configure PyPI Credentials

Create `~/.pypirc`:

```bash
cat > ~/.pypirc << 'EOF'
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc... (your PyPI API token)

[testpypi]
username = __token__
password = pypi-AgENdGVzdC5weXBpLm9yZw... (your TestPyPI API token)
EOF

chmod 600 ~/.pypirc
```

---

## Release Process

### Step 1: Prepare the Release

#### 1.1 Update Version Number

Edit `bridgelink/__init__.py`:

```python
__version__ = "0.1.0"  # Update version
```

Edit `setup.py`:

```python
setup(
    name="bridgelink",
    version="0.1.0",  # Update version
    ...
)
```

Version scheme:
- `0.1.0` - Initial release
- `0.1.1` - Bug fix
- `0.2.0` - New features
- `1.0.0` - Stable release

#### 1.2 Update CHANGELOG

Create/update `CHANGELOG.md`:

```markdown
# Changelog

## [0.1.0] - 2024-11-20

### Added
- Initial release
- Device management (`add`, `list`, `deactivate`, `remove`)
- Automatic bore tunnel binary installation
- Background tunnel management
- NativeBridge API integration

### Fixed
- None

### Changed
- None
```

#### 1.3 Update README.md

Ensure README.md has:
- Clear description
- Installation instructions
- Quick start guide
- Examples
- Requirements
- License

#### 1.4 Verify setup.py

Check all fields in `setup.py`:

```python
setup(
    name="bridgelink",
    version="0.1.0",
    author="NativeBridge",
    author_email="support@nativebridge.io",
    description="CLI tool to expose Android devices remotely via NativeBridge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nativebridge/bridgelink",
    packages=find_packages(),
    classifiers=[...],
    python_requires=">=3.8",
    install_requires=[...],
    entry_points={...},
    keywords="android adb testing remote-devices nativebridge tunnel",
    project_urls={...},
)
```

---

### Step 2: Test Locally

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Install locally and test
pip install -e .
bridgelink --version
bridgelink --help

# Run all tests
pytest tests/

# Test on a fresh virtual environment
python3 -m venv test_env
source test_env/bin/activate
pip install .
bridgelink --version
deactivate
rm -rf test_env
```

---

### Step 3: Build the Package

```bash
# Navigate to project directory
cd /Users/himanshukukreja/autoflow/bridgelink

# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build source distribution and wheel
python -m build

# This creates:
# - dist/bridgelink-0.1.0-py3-none-any.whl (wheel)
# - dist/bridgelink-0.1.0.tar.gz (source distribution)
```

#### Verify Built Packages

```bash
# Check the created files
ls -lh dist/

# Output should show:
# -rw-r--r-- bridgelink-0.1.0-py3-none-any.whl
# -rw-r--r-- bridgelink-0.1.0.tar.gz

# Inspect the wheel contents
unzip -l dist/bridgelink-0.1.0-py3-none-any.whl

# Should include:
# - bridgelink/ directory with all Python files
# - bridgelink-0.1.0.dist-info/ metadata
```

---

### Step 4: Test Upload to TestPyPI (Recommended)

Before publishing to real PyPI, test on TestPyPI:

#### 4.1 Upload to TestPyPI

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Or with explicit credentials:
python -m twine upload --repository testpypi \
  --username __token__ \
  --password pypi-AgENdGVzdC5weXBpLm9yZw... \
  dist/*
```

#### 4.2 Test Installation from TestPyPI

```bash
# Create fresh virtual environment
python3 -m venv test_install
source test_install/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  bridgelink

# The --extra-index-url is needed because dependencies
# (click, requests, etc.) are on regular PyPI, not TestPyPI

# Test it works
bridgelink --version
bridgelink --help

# Clean up
deactivate
rm -rf test_install
```

---

### Step 5: Publish to PyPI

Once testing is complete, publish to real PyPI:

```bash
# Upload to PyPI
python -m twine upload dist/*

# Or with explicit credentials:
python -m twine upload \
  --username __token__ \
  --password pypi-AgEIcHlwaS5vcmc... \
  dist/*

# Output:
# Uploading distributions to https://upload.pypi.org/legacy/
# Uploading bridgelink-0.1.0-py3-none-any.whl
# 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Uploading bridgelink-0.1.0.tar.gz
# 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# View at:
# https://pypi.org/project/bridgelink/0.1.0/
```

---

### Step 6: Verify Publication

#### 6.1 Check PyPI Page

Visit: https://pypi.org/project/bridgelink/

Verify:
- ✅ Description renders correctly
- ✅ Version is correct
- ✅ Installation command is shown
- ✅ Links work (documentation, repository, etc.)
- ✅ Classifiers are correct

#### 6.2 Test Installation

```bash
# Fresh virtual environment
python3 -m venv verify_install
source verify_install/bin/activate

# Install from PyPI
pip install bridgelink

# Verify
bridgelink --version
bridgelink --help

# Clean up
deactivate
rm -rf verify_install
```

---

### Step 7: Create GitHub Release

#### 7.1 Tag the Release

```bash
# Create git tag
git tag -a v0.1.0 -m "Release version 0.1.0"

# Push tag to GitHub
git push origin v0.1.0
```

#### 7.2 Create GitHub Release

1. Go to https://github.com/nativebridge/bridgelink/releases
2. Click "Draft a new release"
3. Select tag: `v0.1.0`
4. Release title: `BridgeLink v0.1.0`
5. Description: Copy from CHANGELOG.md
6. Attach files:
   - `dist/bridgelink-0.1.0-py3-none-any.whl`
   - `dist/bridgelink-0.1.0.tar.gz`
7. Click "Publish release"

---

## Updating an Existing Package

### Patch Release (0.1.0 → 0.1.1)

For bug fixes:

```bash
# 1. Update version
# Edit bridgelink/__init__.py and setup.py: version = "0.1.1"

# 2. Update CHANGELOG.md

# 3. Commit changes
git add .
git commit -m "Bump version to 0.1.1"

# 4. Build
rm -rf build/ dist/ *.egg-info
python -m build

# 5. Upload
python -m twine upload dist/*

# 6. Tag and push
git tag -a v0.1.1 -m "Release version 0.1.1"
git push origin v0.1.1
```

### Minor Release (0.1.0 → 0.2.0)

For new features:

```bash
# Same as above, but version = "0.2.0"
```

### Major Release (0.2.0 → 1.0.0)

For breaking changes or stable release:

```bash
# Same as above, but version = "1.0.0"
```

---

## Automation with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: python -m twine upload dist/*
```

Setup:
1. Go to repository Settings → Secrets
2. Add secret: `PYPI_API_TOKEN` with your PyPI token
3. Create release on GitHub → Package automatically publishes

---

## Troubleshooting

### Error: "File already exists"

```bash
# You cannot re-upload the same version
# Increment version number and rebuild
```

### Error: "Invalid distribution file"

```bash
# Clean and rebuild
rm -rf build/ dist/ *.egg-info
python -m build
```

### Error: "403 Forbidden"

```bash
# Check your PyPI token
# Regenerate token if needed
# Update ~/.pypirc
```

### Error: "Long description rendering failed"

```bash
# Test README rendering locally
pip install readme-renderer
python -m readme_renderer README.md

# Fix any markdown issues
# Rebuild and upload
```

---

## Best Practices

### 1. Semantic Versioning

- `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes

### 2. Always Test on TestPyPI First

- Avoid mistakes on production PyPI
- Can delete packages from TestPyPI

### 3. Maintain CHANGELOG

- Document all changes
- Makes it easy for users to track updates

### 4. Use Tags

- Tag every release: `git tag v0.1.0`
- Makes it easy to roll back

### 5. Pin Dependencies

```python
# Instead of:
install_requires=['requests']

# Use:
install_requires=['requests>=2.28.0,<3.0.0']
```

### 6. Include License

```python
# setup.py
setup(
    ...
    license='MIT',
)
```

Add `LICENSE` file to repository.

---

## Post-Release Checklist

- ✅ Package visible on PyPI
- ✅ Installation works: `pip install bridgelink`
- ✅ Documentation updated
- ✅ GitHub release created
- ✅ CHANGELOG updated
- ✅ Announcement made (Twitter, blog, etc.)
- ✅ Version bumped for next development cycle

---

## Resources

- PyPI: https://pypi.org/
- TestPyPI: https://test.pypi.org/
- Python Packaging Guide: https://packaging.python.org/
- Twine documentation: https://twine.readthedocs.io/
- Setuptools documentation: https://setuptools.pypa.io/
