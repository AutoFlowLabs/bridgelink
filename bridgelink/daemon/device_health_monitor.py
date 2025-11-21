"""
Device Health Monitor
Polls active devices to check connectivity and automatically deactivates disconnected devices
"""

import os
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

from bridgelink.utils.adb import ADBDeviceManager
from bridgelink.utils.api_client import APIClient
from bridgelink.daemon.tunnel_manager import TunnelManager


class DeviceHealthMonitor:
    """
    Monitors active BridgeLink devices and automatically handles disconnections
    - Polls ADB for device status
    - Detects offline/disconnected devices
    - Stops tunnels for disconnected devices
    - Updates device state in backend
    """

    def __init__(self, poll_interval: int = 1, api_key: str = None):
        """
        Initialize health monitor

        Args:
            poll_interval: Seconds between health checks (default: 1)
            api_key: NativeBridge API key (defaults to NB_API_KEY env var)
        """
        self.poll_interval = poll_interval
        self.tunnel_manager = TunnelManager()

        # Get API key from parameter or environment
        api_key = api_key or os.getenv('NB_API_KEY')
        if not api_key:
            raise ValueError("API key required. Set NB_API_KEY environment variable or pass api_key parameter.")

        self.api_client = APIClient(api_key=api_key)
        self.state_file = Path.home() / '.bridgelink' / 'health_monitor.json'
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._running = False

    def _load_state(self) -> Dict:
        """Load monitor state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_check": None, "monitored_devices": []}

    def _save_state(self, state: Dict):
        """Save monitor state to disk"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save monitor state: {e}")

    def get_adb_device_status(self, device_serial: str) -> str:
        """
        Get device status from ADB

        Returns:
            - "device" if connected and online
            - "offline" if connected but offline (emulators can be in this state)
            - "disconnected" if not found in ADB
        """
        try:
            # Get all ADB devices with their states
            result = subprocess.run(
                ['adb', 'devices', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return "disconnected"

            # Parse ADB output
            # Format: serial_number    state    product:... model:... device:...
            lines = result.stdout.strip().split('\n')[1:]  # Skip "List of devices attached"

            for line in lines:
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) < 2:
                    continue

                serial = parts[0]
                state = parts[1]

                if serial == device_serial:
                    # Return the actual ADB state: device, offline, unauthorized, etc.
                    return state

            # Device not found in ADB list
            return "disconnected"

        except Exception as e:
            print(f"Error checking device status: {e}")
            return "disconnected"

    def check_device_health(self, device_serial: str, device_type: str) -> Dict:
        """
        Check health of a single device

        Args:
            device_serial: Device serial number
            device_type: Device type (physical/emulator)

        Returns:
            Dict with status info
        """
        adb_status = self.get_adb_device_status(device_serial)

        health = {
            "serial": device_serial,
            "type": device_type,
            "adb_status": adb_status,
            "is_healthy": False,
            "action_required": None
        }

        if device_type == "physical":
            # Physical devices: only "device" state is healthy
            if adb_status == "device":
                health["is_healthy"] = True
            elif adb_status in ("offline", "unauthorized"):
                health["action_required"] = "deactivate"
                health["reason"] = f"Device is {adb_status}"
            else:  # disconnected
                health["action_required"] = "deactivate"
                health["reason"] = "Device disconnected"

        elif device_type == "emulator":
            # Emulators: both "device" and "offline" states are acceptable
            if adb_status in ("device", "offline"):
                health["is_healthy"] = True
            else:  # disconnected, unauthorized, etc.
                health["action_required"] = "deactivate"
                health["reason"] = "Emulator disconnected or unauthorized"

        return health

    def handle_unhealthy_device(self, device_serial: str, reason: str):
        """
        Handle an unhealthy device by stopping tunnel and deactivating

        Args:
            device_serial: Device serial number
            reason: Reason for deactivation
        """
        print(f"\n⚠️  Device {device_serial} is unhealthy: {reason}")

        # Stop tunnel
        tunnel_info = self.tunnel_manager.get_tunnel_info(device_serial)
        if tunnel_info:
            print(f"   Stopping tunnel...")
            self.tunnel_manager.stop_tunnel(device_serial)

        # Update backend state to inactive
        try:
            print(f"   Updating backend state to inactive...")
            self.api_client.update_device_state(device_serial, 'inactive')
            print(f"✅ Device {device_serial} deactivated successfully")
        except Exception as e:
            print(f"❌ Failed to update backend: {e}")

    def poll_once(self) -> Dict:
        """
        Perform one health check cycle

        Returns:
            Dict with check results
        """
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "checked": 0,
            "healthy": 0,
            "deactivated": 0,
            "errors": []
        }

        # Get all active tunnels
        active_tunnels = self.tunnel_manager.list_active_tunnels()

        if not active_tunnels:
            print("No active devices to monitor")
            return results

        print(f"\n🔍 Checking health of {len(active_tunnels)} active device(s)...")

        for tunnel in active_tunnels:
            device_serial = tunnel['device_serial']
            device_type = tunnel.get('device_type', 'physical')  # Default to physical

            results["checked"] += 1

            try:
                # Check device health
                health = self.check_device_health(device_serial, device_type)

                if health["is_healthy"]:
                    results["healthy"] += 1
                    print(f"✓ {device_serial}: OK ({health['adb_status']})")
                elif health["action_required"] == "deactivate":
                    # Device needs to be deactivated
                    self.handle_unhealthy_device(device_serial, health["reason"])
                    results["deactivated"] += 1

            except Exception as e:
                error_msg = f"Error checking {device_serial}: {e}"
                print(f"❌ {error_msg}")
                results["errors"].append(error_msg)

        return results

    def start_monitoring(self):
        """
        Start continuous monitoring loop
        """
        self._running = True
        print(f"🚀 Starting device health monitor (poll interval: {self.poll_interval}s - fast disconnect detection)")
        print(f"   Press Ctrl+C to stop")

        try:
            while self._running:
                results = self.poll_once()

                # Save state
                state = self._load_state()
                state["last_check"] = results["timestamp"]
                self._save_state(state)

                # Wait for next poll
                if self._running:
                    time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping health monitor...")
            self._running = False

    def stop_monitoring(self):
        """Stop monitoring loop"""
        self._running = False


# Singleton instance for background monitoring
_monitor_instance = None


def get_monitor_instance(poll_interval: int = 30) -> DeviceHealthMonitor:
    """Get or create monitor instance"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = DeviceHealthMonitor(poll_interval)
    return _monitor_instance
