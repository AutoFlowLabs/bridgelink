"""
Device management commands
"""

import click
import sys
import os
import subprocess
import time
import json
from pathlib import Path
from tabulate import tabulate
from ..utils.api_client import APIClient
from ..utils.adb import ADBDeviceManager
from ..utils.bore_installer import BoreInstaller
from ..daemon.tunnel_manager import TunnelManager


@click.group(name='devices')
def devices():
    """Manage Android devices"""
    pass


@devices.command(name='add')
@click.argument('device_serials', nargs=-1, required=True)
@click.option('--api-key', envvar='NB_API_KEY', help='NativeBridge API key')
@click.pass_context
def add_device(ctx, device_serials, api_key):
    """
    Add one or more Android devices to NativeBridge

    \b
    DEVICE_SERIALS: One or more device serial numbers (space or comma separated)

    \b
    Examples:
      bridgelink devices add SERIAL123
      bridgelink devices add SERIAL1 SERIAL2 SERIAL3
      bridgelink devices add SERIAL1,SERIAL2,SERIAL3
    """
    if not api_key:
        click.echo("❌ Error: NativeBridge API key not provided", err=True)
        click.echo("\nSet API key:")
        click.echo("  export NB_API_KEY='your-api-key'")
        click.echo("\nGet your API key: https://nativebridge.io/dashboard/api-keys")
        sys.exit(1)

    # Parse device serials (handle comma separation)
    serials = []
    for serial in device_serials:
        serials.extend(serial.split(','))
    serials = [s.strip() for s in serials if s.strip()]

    if not serials:
        click.echo("❌ Error: No device serials provided", err=True)
        sys.exit(1)

    # Check if bore is installed
    bore_installer = BoreInstaller()
    if not bore_installer.is_installed():
        click.echo("❌ bore tunnel binary is not installed", err=True)
        click.echo("\nInstall it first:")
        click.echo("  bridgelink install")
        sys.exit(1)

    # Initialize API client
    try:
        api_client = APIClient(api_key=api_key)
        user_info = api_client.validate_api_key()
        click.echo(f"✅ Authenticated as: {user_info['user_email']}\n")
    except Exception as e:
        click.echo(f"❌ API key validation failed: {e}", err=True)
        sys.exit(1)

    # Get all connected ADB devices
    connected_devices = ADBDeviceManager.list_devices()

    if not connected_devices:
        click.echo("❌ No Android devices found via ADB", err=True)
        click.echo("\nMake sure:")
        click.echo("  1. Device is connected via USB")
        click.echo("  2. USB debugging is enabled")
        click.echo("  3. ADB is installed and in PATH")
        sys.exit(1)

    click.echo(f"Found {len(connected_devices)} connected device(s)\n")

    # Initialize tunnel manager
    tunnel_manager = TunnelManager()

    # Process each device
    success_count = 0
    for serial in serials:
        click.echo(f"{'='*60}")
        click.echo(f"Processing device: {serial}")
        click.echo(f"{'='*60}\n")

        # Check if device is connected
        if serial not in connected_devices:
            click.echo(f"❌ Device {serial} is not connected via ADB", err=True)
            click.echo(f"   Connected devices: {', '.join(connected_devices)}\n")
            continue

        try:
            # Get device information
            click.echo("📱 Fetching device information...")
            device_info = ADBDeviceManager.get_device_info(serial)

            if not device_info:
                click.echo(f"❌ Could not get device information for {serial}", err=True)
                continue

            device_details = {
                'brand': device_info.manufacturer,
                'model': device_info.model,
                'android_version': device_info.android_version,
                'sdk_version': device_info.api_level,
            }

            device_type = 'emulator' if 'emulator' in serial.lower() else 'physical'

            click.echo(f"   Model: {device_info.model}")
            click.echo(f"   Brand: {device_info.manufacturer}")
            click.echo(f"   Android: {device_info.android_version}")
            click.echo(f"   Type: {device_type}\n")

            # Check if device already exists in backend
            click.echo("🔍 Checking device status...")
            existing_device = api_client.get_device(serial)

            if existing_device:
                if existing_device['device_state'] == 'active':
                    click.echo(f"✅ Device {serial} is already active")
                    click.echo(f"   Tunnel URL: {existing_device['device_connection_url']}\n")
                    success_count += 1
                    continue
                else:
                    click.echo(f"   Device exists but is inactive. Reactivating...\n")

            # Setup ADB TCP mode and get port
            click.echo("🔧 Setting up ADB TCP mode...")
            adb_port = tunnel_manager.setup_adb_tcp(serial)

            if not adb_port:
                click.echo(f"❌ Failed to setup ADB TCP mode for {serial}", err=True)
                continue

            click.echo(f"   ADB TCP port: {adb_port}\n")

            # Create bore tunnel
            click.echo("🌉 Creating bore tunnel...")
            tunnel_info = tunnel_manager.create_tunnel(serial, adb_port, api_key)

            if not tunnel_info:
                click.echo(f"❌ Failed to create tunnel for {serial}", err=True)
                continue

            tunnel_url = tunnel_info['url']
            click.echo(f"   Tunnel URL: {tunnel_url}\n")

            # Register/update device in backend
            click.echo("☁️  Registering device in NativeBridge...")

            device_data = {
                'device_serial': serial,
                'device_type': device_type,
                'device_details': device_details,
                'tunnel_url': tunnel_url,
                'device_state': 'active',
            }

            result = api_client.add_device(device_data)
            click.echo(f"   ✅ Device registered successfully\n")

            click.echo(f"{'✅ SUCCESS'.center(60, '=')}")
            click.echo(f"Device {serial} is now active!")
            click.echo(f"Connect from anywhere:")
            click.echo(f"  adb connect {tunnel_url}\n")

            success_count += 1

        except KeyboardInterrupt:
            click.echo("\n\n⚠️  Operation cancelled by user")
            sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Error adding device {serial}: {e}", err=True)
            continue

    # Summary
    click.echo(f"\n{'='*60}")
    click.echo(f"Summary: {success_count}/{len(serials)} device(s) added successfully")
    click.echo(f"{'='*60}\n")

    if success_count > 0:
        click.echo("View your devices:")
        click.echo("  bridgelink devices list")


@devices.command(name='list')
@click.option('--api-key', envvar='NB_API_KEY', help='NativeBridge API key')
@click.option('--format', type=click.Choice(['table', 'json']), default='table',
              help='Output format')
def list_devices(api_key, format):
    """List all registered devices"""

    if not api_key:
        click.echo("❌ Error: NativeBridge API key not provided", err=True)
        sys.exit(1)

    try:
        api_client = APIClient(api_key=api_key)
        devices = api_client.list_devices()

        if not devices:
            click.echo("No devices registered yet.")
            click.echo("\nAdd a device:")
            click.echo("  bridgelink devices add <device-serial>")
            return

        if format == 'json':
            click.echo(json.dumps(devices, indent=2))
        else:
            # Table format
            headers = ['Serial', 'Model', 'Brand', 'Type', 'State', 'Tunnel URL']
            rows = []

            for device in devices:
                details = device.get('device_details', {})
                rows.append([
                    device.get('device_serial', 'N/A'),
                    details.get('model', 'N/A'),
                    details.get('brand', 'N/A'),
                    device.get('device_type', 'N/A'),
                    device.get('device_state', 'N/A'),
                    device.get('tunnel_url', 'N/A'),
                ])

            click.echo(f"\n{tabulate(rows, headers=headers, tablefmt='grid')}\n")
            click.echo(f"Total: {len(devices)} device(s)")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@devices.command(name='deactivate')
@click.argument('device_serial')
@click.option('--api-key', envvar='NB_API_KEY', help='NativeBridge API key')
def deactivate_device(device_serial, api_key):
    """
    Deactivate a device and stop its tunnel

    DEVICE_SERIAL: Serial number of the device to deactivate
    """

    if not api_key:
        click.echo("❌ Error: NativeBridge API key not provided", err=True)
        sys.exit(1)

    try:
        api_client = APIClient(api_key=api_key)

        # Get device info
        device = api_client.get_device(device_serial)

        if not device:
            click.echo(f"❌ Device {device_serial} not found", err=True)
            sys.exit(1)

        if device['device_state'] == 'inactive':
            click.echo(f"⚠️  Device {device_serial} is already inactive")
            return

        # Stop tunnel
        tunnel_manager = TunnelManager()
        stopped = tunnel_manager.stop_tunnel(device_serial)

        if stopped:
            click.echo(f"✅ Stopped tunnel for device {device_serial}")

        # Update device state in backend
        api_client.update_device_state(device_serial, 'inactive')

        click.echo(f"✅ Device {device_serial} deactivated successfully")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@devices.command(name='remove')
@click.argument('device_serial')
@click.option('--api-key', envvar='NB_API_KEY', help='NativeBridge API key')
@click.confirmation_option(prompt='Are you sure you want to remove this device?')
def remove_device(device_serial, api_key):
    """
    Remove a device completely

    DEVICE_SERIAL: Serial number of the device to remove
    """

    if not api_key:
        click.echo("❌ Error: NativeBridge API key not provided", err=True)
        sys.exit(1)

    try:
        api_client = APIClient(api_key=api_key)

        # Stop tunnel first
        tunnel_manager = TunnelManager()
        tunnel_manager.stop_tunnel(device_serial)

        # Delete from backend
        api_client.delete_device(device_serial)

        click.echo(f"✅ Device {device_serial} removed successfully")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
