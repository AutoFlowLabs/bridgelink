# BridgeLink Documentation Structure

All documentation has been organized into the `docs/` folder for better organization.

---

## 📁 File Structure

```
bridgelink/
├── README.md                          # Main README (root level only)
├── LICENSE                            # MIT License
├── setup.py                           # Package configuration
├── requirements.txt                   # Dependencies
├── .gitignore                         # Git ignore rules
├── .bumpversion.cfg                   # Version bump configuration
│
├── bridgelink/                        # Main Python package
│   ├── __init__.py
│   ├── cli.py
│   ├── commands/
│   │   ├── device.py                 # Device management commands
│   │   ├── daemon.py                 # Daemon management commands
│   │   ├── config.py
│   │   └── setup.py
│   ├── daemon/
│   │   └── tunnel_manager.py         # Tunnel process management
│   └── utils/
│       ├── adb.py                    # ADB device manager
│       ├── adb_installer.py          # ADB installer
│       ├── bore_installer.py         # bore installer
│       └── api_client.py             # Backend API client
│
├── .github/workflows/                 # CI/CD pipelines
│   ├── release.yml                   # PyPI release automation
│   ├── test.yml                      # Testing pipeline
│   └── version-bump.yml              # Version management
│
└── docs/                              # 📚 All Documentation
    ├── README.md                      # Documentation index & command reference
    ├── CHANGELOG.md                   # Version history
    ├── QUICK_START.md                 # Quick reference
    ├── LOCAL_TESTING_GUIDE.md         # Local testing instructions
    ├── PYPI_RELEASE.md                # PyPI release guide
    ├── GITHUB_ACTIONS_SETUP.md        # CI/CD setup
    ├── COMPLETE_IMPLEMENTATION_SUMMARY.md  # Technical overview
    ├── PROJECT_STATUS.md              # Current status
    ├── FINAL_SUMMARY_AND_NEXT_STEPS.md     # Summary & next steps
    ├── CICD_COMPLETE_SUMMARY.md       # CI/CD overview
    └── VALIDATION_FLOW.md             # Security & validation docs
```

---

## 📖 Documentation Guide

### For Users

**Start here:**
1. [Main README](README.md) - Overview and quick start
2. [docs/README.md](docs/README.md) - Complete command reference
3. [docs/QUICK_START.md](docs/QUICK_START.md) - Quick command reference

**For detailed usage:**
- [docs/LOCAL_TESTING_GUIDE.md](docs/LOCAL_TESTING_GUIDE.md) - Test before deploying

### For Developers

**Implementation details:**
- [docs/COMPLETE_IMPLEMENTATION_SUMMARY.md](docs/COMPLETE_IMPLEMENTATION_SUMMARY.md) - Full technical overview
- [docs/VALIDATION_FLOW.md](docs/VALIDATION_FLOW.md) - Security and validation
- [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) - Current status

**Deployment:**
- [docs/PYPI_RELEASE.md](docs/PYPI_RELEASE.md) - Publishing to PyPI
- [docs/GITHUB_ACTIONS_SETUP.md](docs/GITHUB_ACTIONS_SETUP.md) - CI/CD setup
- [docs/CICD_COMPLETE_SUMMARY.md](docs/CICD_COMPLETE_SUMMARY.md) - CI/CD overview

### For Contributors

**Getting started:**
1. [LICENSE](LICENSE) - MIT License terms
2. [docs/CHANGELOG.md](docs/CHANGELOG.md) - Version history
3. [docs/FINAL_SUMMARY_AND_NEXT_STEPS.md](docs/FINAL_SUMMARY_AND_NEXT_STEPS.md) - What's next

---

## 📝 Documentation Principles

### 1. **Root Level**
- **Only README.md** at root level
- Quick overview and getting started
- Links to detailed docs in `docs/`

### 2. **docs/ Folder**
- **All other documentation** lives here
- Organized by purpose (user guides, technical docs, deployment)
- Each file has a specific purpose

### 3. **Navigation**
- Root README links to `docs/README.md`
- `docs/README.md` is the main documentation index
- All docs cross-reference each other

---

## 🔗 Quick Links

| Document | Purpose | Audience |
|----------|---------|----------|
| [README.md](README.md) | Quick start & overview | Everyone |
| [docs/README.md](docs/README.md) | Complete command reference | Users |
| [docs/QUICK_START.md](docs/QUICK_START.md) | Quick commands | Users |
| [docs/LOCAL_TESTING_GUIDE.md](docs/LOCAL_TESTING_GUIDE.md) | Testing guide | Developers |
| [docs/VALIDATION_FLOW.md](docs/VALIDATION_FLOW.md) | Security details | Developers |
| [docs/PYPI_RELEASE.md](docs/PYPI_RELEASE.md) | Release process | Maintainers |
| [docs/COMPLETE_IMPLEMENTATION_SUMMARY.md](docs/COMPLETE_IMPLEMENTATION_SUMMARY.md) | Technical details | Developers |

---

## ✅ Benefits of This Structure

### Organization
- ✅ Clean root directory (only README.md)
- ✅ All docs in one place (`docs/`)
- ✅ Easy to navigate and maintain

### Discoverability
- ✅ Main README points to detailed docs
- ✅ Documentation index in `docs/README.md`
- ✅ Cross-references between documents

### Maintenance
- ✅ Easy to add new documentation
- ✅ Clear separation of concerns
- ✅ Version control friendly

### User Experience
- ✅ Quick start at root level
- ✅ Detailed docs when needed
- ✅ Multiple entry points

---

## 🔄 Updating Documentation

### Adding New Documentation

1. Create file in `docs/` folder
2. Add link to `docs/README.md` index
3. Cross-reference from relevant docs
4. Update this structure doc if needed

### File Naming Convention

- Use `UPPERCASE_WITH_UNDERSCORES.md` for consistency
- Be descriptive: `LOCAL_TESTING_GUIDE.md` not `TESTING.md`
- Group related docs: `CICD_*.md`, `*_SUMMARY.md`

---

Made with ❤️ by the [NativeBridge](https://nativebridge.io) team
