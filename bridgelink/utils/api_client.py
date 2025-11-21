"""
NativeBridge API Client
Handles all API communication with the NativeBridge backend
"""

import requests
import os
from typing import Optional, Dict, Any


class APIClient:
    """Client for NativeBridge API"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv('NB_API_KEY')
        self.base_url = base_url or os.getenv(
            'NB_API_URL',
            'https://dev.api.nativebridge.io'
        )

        if not self.api_key:
            raise ValueError(
                "API key not provided. Set NB_API_KEY environment variable "
                "or pass api_key parameter"
            )

    def _get_headers(self):
        """Get common headers for API requests"""
        return {
            'Content-Type': 'application/json',
            'X-Api-Key': self.api_key
        }

    def validate_api_key(self) -> Dict[str, Any]:
        """Validate the API key and get user information"""
        url = f"{self.base_url}/v1/bore/validate-api-key"
        response = requests.post(
            url,
            json={'api_key': self.api_key},
            timeout=10
        )

        if response.status_code != 200:
            raise Exception(f"API key validation failed: {response.text}")

        data = response.json()

        if not data.get('valid'):
            raise Exception(f"Invalid API key: {data.get('error', 'Unknown error')}")

        return data

    def add_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add or update a device in the backend

        Args:
            device_data: Dictionary containing device information
                - device_serial: str
                - device_type: str (emulator/physical)
                - device_details: dict (brand, model, etc.)
                - tunnel_url: str
                - device_state: str (active/inactive)
                - auto_activate: bool (optional) - auto-activate on reconnection

        Returns:
            API response data
        """
        url = f"{self.base_url}/v1/bridgelink/devices"
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=device_data,
            timeout=10
        )

        if response.status_code not in (200, 201):
            raise Exception(f"Failed to add device: {response.text}")

        return response.json()

    def update_device_state(self, device_serial: str, state: str) -> Dict[str, Any]:
        """
        Update device state (active/inactive)

        Args:
            device_serial: Device serial number
            state: New state (active/inactive)

        Returns:
            API response data
        """
        url = f"{self.base_url}/v1/bridgelink/devices/{device_serial}/state"
        response = requests.patch(
            url,
            headers=self._get_headers(),
            json={'state': state},
            timeout=10
        )

        if response.status_code != 200:
            raise Exception(f"Failed to update device state: {response.text}")

        return response.json()

    def get_device(self, device_serial: str) -> Optional[Dict[str, Any]]:
        """
        Get device information from backend

        Args:
            device_serial: Device serial number

        Returns:
            Device data or None if not found
        """
        url = f"{self.base_url}/v1/bridgelink/devices/{device_serial}"
        response = requests.get(
            url,
            headers=self._get_headers(),
            timeout=10
        )

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            raise Exception(f"Failed to get device: {response.text}")

        return response.json()

    def list_devices(self) -> list:
        """
        List all devices for the current user

        Returns:
            List of device data dictionaries
        """
        url = f"{self.base_url}/v1/bridgelink/devices"
        response = requests.get(
            url,
            headers=self._get_headers(),
            timeout=10
        )

        if response.status_code != 200:
            raise Exception(
                f"Failed to list devices (HTTP {response.status_code}): {response.text}"
            )

        data = response.json()

        # Debug logging if DEBUG env var is set
        if os.getenv('DEBUG'):
            print(f"DEBUG API Response: {data}")

        return data.get('devices', [])

    def delete_device(self, device_serial: str) -> Dict[str, Any]:
        """
        Delete a device from the backend

        Args:
            device_serial: Device serial number

        Returns:
            API response data
        """
        url = f"{self.base_url}/v1/bridgelink/devices/{device_serial}"
        response = requests.delete(
            url,
            headers=self._get_headers(),
            timeout=10
        )

        if response.status_code != 200:
            raise Exception(f"Failed to delete device: {response.text}")

        return response.json()

    def update_auto_activate(self, device_serial: str, auto_activate: bool) -> Dict[str, Any]:
        """
        Update auto-activate preference for a device

        Args:
            device_serial: Device serial number
            auto_activate: Enable/disable auto-activation

        Returns:
            API response data
        """
        url = f"{self.base_url}/v1/bridgelink/devices/{device_serial}/auto-activate"
        response = requests.patch(
            url,
            headers=self._get_headers(),
            json={'auto_activate': auto_activate},
            timeout=10
        )

        if response.status_code != 200:
            raise Exception(f"Failed to update auto-activate: {response.text}")

        return response.json()

    def get_auto_activate_devices(self) -> list:
        """
        Get all inactive devices with auto-activate enabled

        Returns:
            List of device data dictionaries
        """
        url = f"{self.base_url}/v1/bridgelink/devices/auto-activate/candidates"
        response = requests.get(
            url,
            headers=self._get_headers(),
            timeout=10
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get auto-activate devices: {response.text}")

        data = response.json()
        return data.get('devices', [])
