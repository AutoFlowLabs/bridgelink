"""
Device Connection Monitor
Monitors ADB for newly connected devices and automatically activates devices with auto_activate enabled
"""

import os
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

from bridgelink.utils.adb import ADBDeviceManager
from bridgelink.utils.api_client import APIClient
from bridgelink.daemon.tunnel_manager import TunnelManager


class DeviceConnectionMonitor:
    """
    Monitors ADB for device connections and auto-activates devices with auto_activate preference
    - Polls ADB for connected devices
    - Detects newly connected devices
    - Checks if device has auto_activate enabled in backend
    - Automatically creates tunnel and activates device
    """

    def __init__(self, poll_interval: int = 1, api_key: str = None):
        """
        Initialize connection monitor

        Args:
            poll_interval: Seconds between connection checks (default: 1)
            api_key: NativeBridge API key (defaults to NB_API_KEY env var)
        """
        self.poll_interval = poll_interval
        self.tunnel_manager = TunnelManager()

        # Get API key from parameter or environment
        api_key = api_key or os.getenv('NB_API_KEY')
        if not api_key:
            raise ValueError("API key required. Set NB_API_KEY environment variable or pass api_key parameter.")

        self.api_client = APIClient(api_key=api_key)
        self.api_key = api_key
        self.state_file = Path.home() / '.bridgelink' / 'connection_monitor.json'
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._running = False
        self._previously_connected = set()  # Track previously seen devices

    def get_connected_devices(self) -> Set[str]:
        """
        Get set of currently connected device serials

        Returns:
            Set of device serial numbers
        """
        try:
            devices = ADBDeviceManager.list_devices()
            return set(devices)
        except Exception as e:
            print(f"Error getting connected devices: {e}")
            return set()

    def check_auto_activate_eligibility(self, device_serial: str) -> Dict:
        """
        Check if a device is eligible for auto-activation

        Args:
            device_serial: Device serial number

        Returns:
            Dict with eligibility info:
                {
                    'eligible': bool,
                    'device': dict or None,
                    'reason': str
                }
        """
        try:
            # Get device from backend
            device = self.api_client.get_device(device_serial)

            if not device:
                return {
                    'eligible': False,
                    'device': None,
                    'reason': 'Device not registered in NativeBridge'
                }

            # Check if auto_activate is enabled
            if not device.get('auto_activate', False):
                return {
                    'eligible': False,
                    'device': device,
                    'reason': 'Auto-activation not enabled for this device'
                }

            # Check if already active
            if device.get('device_state') == 'active':
                return {
                    'eligible': False,
                    'device': device,
                    'reason': 'Device is already active'
                }

            # Device is eligible for auto-activation
            return {
                'eligible': True,
                'device': device,
                'reason': 'Ready for auto-activation'
            }

        except Exception as e:
            print(f"Error checking auto-activate eligibility for {device_serial}: {e}")
            return {
                'eligible': False,
                'device': None,
                'reason': f'Error: {e}'
            }

    def auto_activate_device(self, device_serial: str, device_info: Dict) -> bool:
        """
        Automatically activate a device

        Args:
            device_serial: Device serial number
            device_info: Device information from backend

        Returns:
            True if activation succeeded, False otherwise
        """
        try:
            print(f"\n🔄 Auto-activating device: {device_serial}")

            # Get device type
            device_type = device_info.get('device_type', 'physical')

            # Setup ADB TCP mode
            print(f"   Setting up ADB TCP mode...")
            adb_port = self.tunnel_manager.setup_adb_tcp(device_serial)

            if not adb_port:
                print(f"   ❌ Failed to setup ADB TCP mode")
                return False

            print(f"   ADB TCP port: {adb_port}")

            # Create bore tunnel
            print(f"   Creating bore tunnel...")
            tunnel_info = self.tunnel_manager.create_tunnel(
                device_serial,
                adb_port,
                self.api_key,
                device_type
            )

            if not tunnel_info:
                print(f"   ❌ Failed to create tunnel")
                return False

            tunnel_url = tunnel_info['url']
            print(f"   Tunnel URL: {tunnel_url}")

            # Update device in backend
            print(f"   Updating device in NativeBridge...")

            device_data = {
                'device_serial': device_serial,
                'device_type': device_type,
                'device_details': device_info['device_details'],
                'tunnel_url': tunnel_url,
                'device_state': 'active',
                'auto_activate': True,  # Preserve auto-activate preference
            }

            self.api_client.add_device(device_data)

            print(f"✅ Device {device_serial} auto-activated successfully")
            print(f"   Connect with: adb connect {tunnel_url}\n")

            return True

        except Exception as e:
            print(f"❌ Error auto-activating device {device_serial}: {e}")
            return False

    def poll_once(self) -> Dict:
        """
        Perform one connection check cycle

        Returns:
            Dict with check results
        """
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "connected_devices": 0,
            "new_connections": 0,
            "auto_activated": 0,
            "skipped": 0,
            "errors": []
        }

        # Get currently connected devices
        current_devices = self.get_connected_devices()
        results["connected_devices"] = len(current_devices)

        # Find newly connected devices
        new_devices = current_devices - self._previously_connected

        if new_devices:
            print(f"\n🔌 Detected {len(new_devices)} newly connected device(s)")
            results["new_connections"] = len(new_devices)

            for device_serial in new_devices:
                try:
                    # Check if eligible for auto-activation
                    eligibility = self.check_auto_activate_eligibility(device_serial)

                    if eligibility['eligible']:
                        # Attempt auto-activation
                        success = self.auto_activate_device(
                            device_serial,
                            eligibility['device']
                        )

                        if success:
                            results["auto_activated"] += 1
                        else:
                            results["errors"].append(
                                f"Failed to auto-activate {device_serial}"
                            )
                    else:
                        print(f"   Skipping {device_serial}: {eligibility['reason']}")
                        results["skipped"] += 1

                except Exception as e:
                    error_msg = f"Error processing {device_serial}: {e}"
                    print(f"❌ {error_msg}")
                    results["errors"].append(error_msg)

        # Update previously connected devices
        self._previously_connected = current_devices

        return results

    def start_monitoring(self):
        """
        Start continuous monitoring loop
        """
        self._running = True
        print(f"🚀 Starting device connection monitor (poll interval: {self.poll_interval}s - fast reconnect detection)")
        print(f"   Watching for newly connected devices with auto-activate enabled")
        print(f"   Press Ctrl+C to stop\n")

        # Initialize with current devices
        self._previously_connected = self.get_connected_devices()
        print(f"📱 Currently connected: {len(self._previously_connected)} device(s)")

        try:
            while self._running:
                results = self.poll_once()

                # Wait for next poll
                if self._running:
                    time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping connection monitor...")
            self._running = False

    def stop_monitoring(self):
        """Stop monitoring loop"""
        self._running = False
