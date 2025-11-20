"""
Bore tunnel binary installer
Handles downloading and installing the correct bore binary for the platform
"""

import os
import platform
import subprocess
import urllib.request
from pathlib import Path


class BoreInstaller:
    """Installs bore tunnel binary for the current platform"""

    VERSION = "0.6.0-nativebridge"
    RELEASE_TAG = "v0.6.1-nativebridge"
    REPO = "himanshkukreja/nativebridge-bore-tunnel"
    BASE_URL = f"https://github.com/{REPO}/releases/download/{RELEASE_TAG}"

    def __init__(self):
        self.platform = self._detect_platform()
        self.bore_path = self._get_install_path()

    def _detect_platform(self):
        """Detect the current platform and architecture"""
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == "darwin":  # macOS
            if machine in ("arm64", "aarch64"):
                return "macos-arm64"
            else:
                return "macos-x64"

        elif system == "linux":
            if machine in ("x86_64", "amd64"):
                return "linux-x64"
            else:
                raise Exception(f"Unsupported Linux architecture: {machine}")

        elif system == "windows":
            return "windows-x64"

        else:
            raise Exception(f"Unsupported operating system: {system}")

    def _get_install_path(self):
        """Get the installation path for bore binary"""
        if platform.system().lower() == "windows":
            # Windows: Install to user's AppData
            app_data = Path(os.getenv('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local')))
            bin_dir = app_data / "bridgelink" / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            return bin_dir / "bore.exe"
        else:
            # Unix-like: Try /usr/local/bin first, fallback to ~/.local/bin
            if os.access('/usr/local/bin', os.W_OK):
                return Path('/usr/local/bin/bore')
            else:
                local_bin = Path.home() / '.local' / 'bin'
                local_bin.mkdir(parents=True, exist_ok=True)
                return local_bin / 'bore'

    def get_platform_binary_name(self):
        """Get the binary filename for the current platform"""
        if self.platform == "windows-x64":
            return f"bore-{self.VERSION}-windows-x64.exe"
        else:
            return f"bore-{self.VERSION}-{self.platform}"

    def is_installed(self):
        """Check if bore is already installed"""
        if self.bore_path.exists():
            return True

        # Also check if it's in PATH
        try:
            subprocess.run(['bore', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_version(self):
        """Get the installed bore version"""
        try:
            result = subprocess.run(
                [str(self.bore_path), '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"

    def download(self, url, destination):
        """Download a file with progress indication"""
        try:
            # Create a simple progress callback
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
        """Install bore binary"""
        binary_name = self.get_platform_binary_name()
        download_url = f"{self.BASE_URL}/{binary_name}"

        print(f"  Platform: {self.platform}")
        print(f"  Binary: {binary_name}")
        print(f"  URL: {download_url}")
        print(f"  Installing to: {self.bore_path}")
        print()

        # Download to temporary location first
        temp_path = self.bore_path.parent / f"{self.bore_path.name}.tmp"

        try:
            self.download(download_url, temp_path)

            # Make executable (Unix-like systems)
            if platform.system().lower() != "windows":
                os.chmod(temp_path, 0o755)

            # Move to final location
            if self.bore_path.exists():
                self.bore_path.unlink()

            temp_path.rename(self.bore_path)

            # Verify installation
            if not self.is_installed():
                raise Exception("Installation verification failed")

            # Auto-configure PATH for ~/.local/bin
            if str(self.bore_path).startswith(str(Path.home() / '.local')):
                self._configure_path()
                print()
                print("✅ bore installed and PATH configured successfully!")
                print()

        except Exception as e:
            # Cleanup on failure
            if temp_path.exists():
                temp_path.unlink()
            raise e

    def _configure_path(self):
        """Automatically configure PATH to include ~/.local/bin"""
        local_bin = str(Path.home() / '.local' / 'bin')

        # Detect shell and add to appropriate config file
        shell = os.environ.get('SHELL', '').lower()

        if 'zsh' in shell:
            rc_file = Path.home() / '.zshrc'
        elif 'bash' in shell:
            rc_file = Path.home() / '.bashrc'
        else:
            # Try to detect from common files
            if (Path.home() / '.zshrc').exists():
                rc_file = Path.home() / '.zshrc'
            elif (Path.home() / '.bashrc').exists():
                rc_file = Path.home() / '.bashrc'
            else:
                # Fallback to .profile
                rc_file = Path.home() / '.profile'

        path_export = f'export PATH="$HOME/.local/bin:$PATH"'

        # Check if PATH is already configured
        if rc_file.exists():
            content = rc_file.read_text()
            if '.local/bin' in content and 'PATH' in content:
                print(f"  PATH already configured in {rc_file.name}")
                return

        # Add PATH export to rc file
        try:
            with open(rc_file, 'a') as f:
                f.write(f'\n# Added by BridgeLink installer\n')
                f.write(f'{path_export}\n')
            print(f"  Added to PATH in {rc_file.name}")

            # Also export for current session
            os.environ['PATH'] = f"{local_bin}:{os.environ.get('PATH', '')}"
            print(f"  PATH updated for current session")

            print()
            print("  To apply immediately in new terminals, run:")
            print(f"  source {rc_file}")

        except Exception as e:
            print(f"  ⚠️  Could not auto-configure PATH: {e}")
            print(f"  Please manually add to your shell config:")
            print(f"  echo '{path_export}' >> {rc_file}")

    def get_bore_command(self):
        """Get the bore command to use (path or 'bore' if in PATH)"""
        # Check if bore is in PATH
        try:
            result = subprocess.run(['bore', '--version'], capture_output=True)
            if result.returncode == 0:
                return 'bore'
        except FileNotFoundError:
            pass

        # Use the full path
        return str(self.bore_path)
