"""
ADB (Android Debug Bridge) installer
Handles downloading and installing ADB platform tools
"""

import os
import sys
import platform
import subprocess
import urllib.request
import zipfile
import tarfile
from pathlib import Path


class ADBInstaller:
    """Installs ADB platform tools for the current platform"""

    # Google's official platform-tools download URLs
    PLATFORM_TOOLS_URLS = {
        "darwin": "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip",
        "linux": "https://dl.google.com/android/repository/platform-tools-latest-linux.zip",
        "windows": "https://dl.google.com/android/repository/platform-tools-latest-windows.zip",
    }

    def __init__(self):
        self.platform = self._detect_platform()
        self.install_dir = self._get_install_dir()
        self.adb_path = self._get_adb_path()

    def _detect_platform(self):
        """Detect the current platform"""
        system = platform.system().lower()

        if system == "darwin":
            return "darwin"
        elif system == "linux":
            return "linux"
        elif system == "windows":
            return "windows"
        else:
            raise Exception(f"Unsupported operating system: {system}")

    def _get_install_dir(self):
        """Get the installation directory for ADB"""
        if platform.system().lower() == "windows":
            # Windows: Install to AppData\Local\bridgelink\platform-tools
            app_data = Path(os.getenv('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local')))
            install_dir = app_data / "bridgelink" / "platform-tools"
        else:
            # Unix-like: Install to ~/.local/share/bridgelink/platform-tools
            local_share = Path.home() / '.local' / 'share' / 'bridgelink' / 'platform-tools'
            install_dir = local_share

        install_dir.mkdir(parents=True, exist_ok=True)
        return install_dir

    def _get_adb_path(self):
        """Get the path to the adb binary"""
        if platform.system().lower() == "windows":
            return self.install_dir / "adb.exe"
        else:
            return self.install_dir / "adb"

    def is_installed(self):
        """Check if ADB is already installed"""
        # Check if our installed version exists
        if self.adb_path.exists():
            return True

        # Also check if it's in PATH
        try:
            subprocess.run(['adb', 'version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_version(self):
        """Get the installed ADB version"""
        try:
            # Try our installed version first
            adb_cmd = str(self.adb_path) if self.adb_path.exists() else 'adb'

            result = subprocess.run(
                [adb_cmd, 'version'],
                capture_output=True,
                text=True,
                check=True
            )

            # Extract version from output
            # Example: "Android Debug Bridge version 1.0.41"
            lines = result.stdout.strip().split('\n')
            if lines:
                return lines[0].strip()

            return "unknown"
        except Exception:
            return "unknown"

    def download(self, url, destination):
        """Download a file with progress indication"""
        try:
            def progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                if total_size > 0:
                    percent = min(100, downloaded * 100 / total_size)
                    print(f"\r  Downloading: {percent:.1f}%", end='', flush=True)

            urllib.request.urlretrieve(url, destination, reporthook=progress)
            print()  # New line after progress
        except Exception as e:
            raise Exception(f"Download failed: {e}")

    def install(self):
        """Install ADB platform tools"""
        download_url = self.PLATFORM_TOOLS_URLS[self.platform]

        print(f"  Platform: {self.platform}")
        print(f"  URL: {download_url}")
        print(f"  Installing to: {self.install_dir}")
        print()

        # Download to temporary location
        temp_dir = Path.home() / '.bridgelink' / 'tmp'
        temp_dir.mkdir(parents=True, exist_ok=True)

        archive_path = temp_dir / f"platform-tools.zip"

        try:
            # Download
            self.download(download_url, archive_path)

            # Extract
            print("  Extracting...")

            # Remove old installation
            if self.install_dir.exists():
                import shutil
                shutil.rmtree(self.install_dir)
                self.install_dir.mkdir(parents=True)

            # Extract the zip
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                # Extract all files
                zip_ref.extractall(temp_dir)

            # Move platform-tools directory to install location
            import shutil
            extracted_dir = temp_dir / "platform-tools"
            shutil.move(str(extracted_dir), str(self.install_dir.parent))

            # Make binaries executable (Unix-like systems)
            if platform.system().lower() != "windows":
                for binary in self.install_dir.glob('*'):
                    if binary.is_file() and not binary.suffix:
                        os.chmod(binary, 0o755)

            # Verify installation
            if not self.is_installed():
                raise Exception("Installation verification failed")

            # Add to PATH reminder
            print()
            print(f"✅ ADB installed successfully to: {self.install_dir}")
            print()
            print("⚠️  Note: Add ADB to your PATH to use it from anywhere:")

            if platform.system().lower() == "windows":
                print(f"   set PATH=%PATH%;{self.install_dir}")
            else:
                print(f"   export PATH=\"{self.install_dir}:$PATH\"")
                print()
                print("   To make it permanent, add to your shell profile:")
                print(f"   echo 'export PATH=\"{self.install_dir}:$PATH\"' >> ~/.zshrc")
                print("   source ~/.zshrc")

        except Exception as e:
            raise e
        finally:
            # Cleanup
            if archive_path.exists():
                archive_path.unlink()

    def get_adb_command(self):
        """Get the adb command to use (path or 'adb' if in PATH)"""
        # Check if adb is in PATH
        try:
            result = subprocess.run(['adb', 'version'], capture_output=True)
            if result.returncode == 0:
                return 'adb'
        except FileNotFoundError:
            pass

        # Use the full path
        return str(self.adb_path)

    def add_to_path_instructions(self):
        """Print instructions to add ADB to PATH"""
        if platform.system().lower() == "windows":
            return f"set PATH=%PATH%;{self.install_dir}"
        else:
            return f"export PATH=\"{self.install_dir}:$PATH\""
