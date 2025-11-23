#!/bin/bash
# Build script for BridgeLink packages
# This script builds packages for PyPI, Homebrew, and Debian

set -e

VERSION="0.2.0"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=============================================="
echo "  Building BridgeLink v${VERSION} Packages"
echo "=============================================="
echo ""

cd "$PROJECT_DIR"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build PyPI package
echo ""
echo "Building PyPI package..."
python3 setup.py sdist bdist_wheel
echo "PyPI packages built in dist/"

# Calculate SHA256 for Homebrew
echo ""
echo "Calculating SHA256 for Homebrew formula..."
SDIST_FILE="dist/bridgelink-${VERSION}.tar.gz"
if [ -f "$SDIST_FILE" ]; then
    SHA256=$(shasum -a 256 "$SDIST_FILE" | awk '{print $1}')
    echo "SHA256: $SHA256"

    # Update Homebrew formula with SHA256
    sed -i.bak "s/PLACEHOLDER_SHA256/$SHA256/" packaging/homebrew/bridgelink.rb
    rm -f packaging/homebrew/bridgelink.rb.bak
    echo "Updated Homebrew formula with SHA256"
fi

# Build Debian package (if on Linux with dpkg-buildpackage)
if command -v dpkg-buildpackage &> /dev/null; then
    echo ""
    echo "Building Debian package..."

    # Copy debian files to project root
    cp -r packaging/debian .

    # Build the package
    dpkg-buildpackage -us -uc -b

    # Clean up
    rm -rf debian/

    echo "Debian package built"
else
    echo ""
    echo "Skipping Debian package build (dpkg-buildpackage not found)"
    echo "To build Debian package, run on a Debian/Ubuntu system"
fi

echo ""
echo "=============================================="
echo "  Build Complete!"
echo "=============================================="
echo ""
echo "Packages created:"
echo "  - PyPI: dist/bridgelink-${VERSION}.tar.gz"
echo "  - PyPI: dist/bridgelink-${VERSION}-py3-none-any.whl"
echo ""
echo "Next steps:"
echo "  1. Upload to PyPI: twine upload dist/*"
echo "  2. Update Homebrew tap with packaging/homebrew/bridgelink.rb"
echo "  3. Upload Debian package to your PPA"
echo ""
