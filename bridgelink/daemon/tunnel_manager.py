"""
Tunnel Manager - Manages bore tunnel processes
"""

import os
import subprocess
import time
import re
import json
import signal
import psutil
from pathlib import Path
from typing import Optional, Dict, List
from ..utils.bore_installer import BoreInstaller


class TunnelManager:
    """Manages bore tunnel processes for devices"""

    def __init__(self):
        self.state_dir = Path.home() / '.bridgelink'
        self.state_dir.mkdir(exist_ok=True)
        self.tunnels_file = self.state_dir / 'tunnels.json'
        self.bore_server = os.getenv('BORE_SERVER', 'bridgelink.nativebridge.io')
        self.bore_installer = BoreInstaller()

    def _load_tunnels(self) -> Dict:
        """Load tunnel state from file"""
        if not self.tunnels_file.exists():
            return {}

        try:
            with open(self.tunnels_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_tunnels(self, tunnels: Dict):
        """Save tunnel state to file"""
        try:
            with open(self.tunnels_file, 'w') as f:
                json.dump(tunnels, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save tunnel state: {e}")

    def setup_adb_tcp(self, device_serial: str) -> Optional[int]:
        """
        Setup ADB TCP mode for a device

        Returns:
            Port number if successful, None otherwise
        """
        try:
            # Enable TCP mode on device
            result = subprocess.run(
                ['adb', '-s', device_serial, 'tcpip', '5555'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return None

            time.sleep(3)

            # Find available port
            port = self._find_available_port(5555)

            if not port:
                return None

            # Setup port forwarding
            result = subprocess.run(
                ['adb', '-s', device_serial, 'forward', f'tcp:{port}', 'tcp:5555'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return None

            return port

        except Exception as e:
            print(f"Error setting up ADB TCP: {e}")
            return None

    def _find_available_port(self, start_port: int = 5555, max_attempts: int = 10) -> Optional[int]:
        """Find an available port"""
        import socket

        for port in range(start_port, start_port + max_attempts):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()

                if result != 0:  # Port is available
                    return port
            except Exception:
                continue

        return None

    def create_tunnel(self, device_serial: str, local_port: int, api_key: str, device_type: str = "physical") -> Optional[Dict]:
        """
        Create a bore tunnel for a device

        Args:
            device_serial: Device serial number
            local_port: Local ADB port
            api_key: NativeBridge API key
            device_type: Device type (physical/emulator) for health monitoring

        Returns:
            Dictionary with tunnel info (url, pid) or None if failed
        """
        try:
            bore_cmd = self.bore_installer.get_bore_command()

            # Log file for this tunnel
            log_file = self.state_dir / f'tunnel_{device_serial}.log'

            # Start bore process
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    [
                        bore_cmd,
                        'local',
                        str(local_port),
                        '--to',
                        self.bore_server,
                        '--api-key',
                        api_key
                    ],
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True,
                    start_new_session=True  # Detach from parent
                )

            # Wait for tunnel to establish and get the URL
            tunnel_url = None
            max_wait = 30

            for i in range(max_wait):
                # Check if process died
                if process.poll() is not None:
                    with open(log_file, 'r') as f:
                        error_log = f.read()
                    raise Exception(f"bore process exited: {error_log}")

                # Read log file
                try:
                    with open(log_file, 'r') as f:
                        output = f.read()

                    # Look for tunnel URL patterns
                    # Pattern: "listening at host:port"
                    match = re.search(r'listening at ([^\s]+):(\d+)', output)
                    if match:
                        host = match.group(1)
                        port = match.group(2)

                        # Use the configured bore server hostname if available
                        if host in ('0.0.0.0', 'localhost'):
                            tunnel_url = f"{self.bore_server}:{port}"
                        else:
                            tunnel_url = f"{host}:{port}"
                        break

                    # Alternative pattern: just host:port
                    match = re.search(r'([0-9.]+):(\d+)', output)
                    if match:
                        port = match.group(2)
                        tunnel_url = f"{self.bore_server}:{port}"
                        break

                except Exception:
                    pass

                time.sleep(1)

            if not tunnel_url:
                process.terminate()
                raise Exception("Could not determine tunnel URL")

            # Save tunnel state
            tunnels = self._load_tunnels()
            tunnels[device_serial] = {
                'pid': process.pid,
                'url': tunnel_url,
                'local_port': local_port,
                'log_file': str(log_file),
                'started_at': time.time(),
                'device_type': device_type  # Store for health monitoring
            }
            self._save_tunnels(tunnels)

            return {
                'url': tunnel_url,
                'pid': process.pid,
                'log_file': str(log_file)
            }

        except Exception as e:
            raise Exception(f"Failed to create tunnel: {e}")

    def stop_tunnel(self, device_serial: str) -> bool:
        """
        Stop a tunnel for a device

        Args:
            device_serial: Device serial number

        Returns:
            True if stopped successfully, False otherwise
        """
        tunnels = self._load_tunnels()

        if device_serial not in tunnels:
            return False

        tunnel = tunnels[device_serial]
        pid = tunnel['pid']

        try:
            # Try to kill the process
            try:
                process = psutil.Process(pid)
                process.terminate()
                process.wait(timeout=5)
            except psutil.NoSuchProcess:
                pass  # Process already dead
            except psutil.TimeoutExpired:
                # Force kill
                try:
                    process.kill()
                except Exception:
                    pass

            # Remove from state
            del tunnels[device_serial]
            self._save_tunnels(tunnels)

            return True

        except Exception as e:
            print(f"Error stopping tunnel: {e}")
            return False

    def list_active_tunnels(self) -> List[Dict]:
        """List all active tunnels"""
        tunnels = self._load_tunnels()
        active = []

        for serial, tunnel in list(tunnels.items()):
            pid = tunnel['pid']

            # Check if process is still running
            try:
                process = psutil.Process(pid)
                if process.is_running():
                    active.append({
                        'device_serial': serial,
                        **tunnel
                    })
                else:
                    # Process died, remove from state
                    del tunnels[serial]
            except psutil.NoSuchProcess:
                # Process doesn't exist, remove from state
                del tunnels[serial]

        # Save cleaned up state
        self._save_tunnels(tunnels)

        return active

    def get_tunnel_info(self, device_serial: str) -> Optional[Dict]:
        """Get tunnel information for a device"""
        tunnels = self._load_tunnels()
        return tunnels.get(device_serial)

    def cleanup_dead_tunnels(self):
        """Clean up tunnels for processes that are no longer running"""
        tunnels = self._load_tunnels()
        updated = False

        for serial in list(tunnels.keys()):
            tunnel = tunnels[serial]
            pid = tunnel['pid']

            try:
                process = psutil.Process(pid)
                if not process.is_running():
                    del tunnels[serial]
                    updated = True
            except psutil.NoSuchProcess:
                del tunnels[serial]
                updated = True

        if updated:
            self._save_tunnels(tunnels)
