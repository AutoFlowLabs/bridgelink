"""
Background Health Monitor Daemon
Automatically monitors active devices and deactivates disconnected ones
"""

import os
import sys
import time
import signal
import json
import subprocess
from pathlib import Path
from typing import Optional


class BackgroundMonitorDaemon:
    """
    Manages the background health monitoring daemon process
    """

    def __init__(self):
        self.state_dir = Path.home() / '.bridgelink'
        self.state_dir.mkdir(exist_ok=True)
        self.pid_file = self.state_dir / 'monitor.pid'
        self.log_file = self.state_dir / 'monitor.log'

    def is_running(self) -> bool:
        """Check if monitor daemon is running"""
        if not self.pid_file.exists():
            return False

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if process exists
            os.kill(pid, 0)  # Doesn't kill, just checks if process exists
            return True
        except (ProcessLookupError, ValueError, FileNotFoundError):
            # Process doesn't exist, clean up stale PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False

    def get_pid(self) -> Optional[int]:
        """Get PID of running monitor daemon"""
        if not self.pid_file.exists():
            return None

        try:
            with open(self.pid_file, 'r') as f:
                return int(f.read().strip())
        except (ValueError, FileNotFoundError):
            return None

    def start(self, api_key: str, poll_interval: int = 5) -> bool:
        """
        Start the background monitor daemon

        Args:
            api_key: NativeBridge API key for backend updates
            poll_interval: Seconds between health checks (default: 5)

        Returns:
            True if started successfully, False otherwise
        """
        # Check if already running
        if self.is_running():
            return True

        try:
            # Start daemon process
            # Use subprocess to run the monitor in background
            process = subprocess.Popen(
                [
                    sys.executable,
                    '-m',
                    'bridgelink.daemon.monitor_runner',
                    '--api-key', api_key,
                    '--interval', str(poll_interval)
                ],
                stdout=open(self.log_file, 'w'),
                stderr=subprocess.STDOUT,
                start_new_session=True,  # Detach from parent
                env={**os.environ, 'NB_API_KEY': api_key}
            )

            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))

            # Give it a moment to start
            time.sleep(1)

            # Verify it's still running
            if self.is_running():
                return True
            else:
                return False

        except Exception as e:
            print(f"Failed to start monitor daemon: {e}")
            return False

    def stop(self) -> bool:
        """
        Stop the background monitor daemon

        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.is_running():
            return True

        try:
            pid = self.get_pid()
            if pid:
                # Send SIGTERM for graceful shutdown
                os.kill(pid, signal.SIGTERM)

                # Wait for process to stop (max 5 seconds)
                for _ in range(50):
                    if not self.is_running():
                        break
                    time.sleep(0.1)

                # Force kill if still running
                if self.is_running():
                    os.kill(pid, signal.SIGKILL)
                    time.sleep(0.5)

            # Clean up PID file
            if self.pid_file.exists():
                self.pid_file.unlink()

            return True

        except Exception as e:
            print(f"Failed to stop monitor daemon: {e}")
            return False

    def ensure_running(self, api_key: str) -> bool:
        """
        Ensure monitor daemon is running, start if not

        Args:
            api_key: NativeBridge API key

        Returns:
            True if running (or started), False otherwise
        """
        if self.is_running():
            return True

        return self.start(api_key)

    def status(self) -> dict:
        """Get daemon status information"""
        is_running = self.is_running()
        pid = self.get_pid() if is_running else None

        status = {
            'running': is_running,
            'pid': pid,
            'log_file': str(self.log_file) if is_running else None
        }

        return status


# Singleton instance
_daemon_instance = None


def get_daemon_instance() -> BackgroundMonitorDaemon:
    """Get or create daemon instance"""
    global _daemon_instance
    if _daemon_instance is None:
        _daemon_instance = BackgroundMonitorDaemon()
    return _daemon_instance
