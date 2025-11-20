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
from ..daemon.background_monitor import get_daemon_instance


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
                'sdk_version': device_info.sdk_version,
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
                    click.echo(f"   Tunnel URL: {existing_device['tunnel_url']}\n")
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
            tunnel_info = tunnel_manager.create_tunnel(serial, adb_port, api_key, device_type)

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

            # Auto-start background health monitor
            daemon = get_daemon_instance()
            if not daemon.is_running():
                click.echo("🔍 Starting background health monitor...")
                if daemon.start(api_key):
                    click.echo("   ✅ Health monitor started\n")
                else:
                    click.echo("   ⚠️  Could not start health monitor (device will still work)\n")

            click.echo(f"{'✅ SUCCESS'.center(60, '=')}")
            click.echo(f"Device {serial} is now active!")
            click.echo(f"Connect from anywhere:")
            click.echo(f"  adb connect {tunnel_url}")
            click.echo(f"\n💡 Health monitoring is active - disconnected devices will be auto-deactivated")
            click.echo(f"\n⚠️  SECURITY WARNING:")
            click.echo(f"   Treat this tunnel URL as a SECRET!")
            click.echo(f"   Anyone with this URL can connect to your device.")
            click.echo(f"   Deactivate when not in use: bridgelink devices deactivate {serial}\n")

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

        # Debug: show raw response
        if os.getenv('DEBUG'):
            click.echo(f"DEBUG: API returned {len(devices)} devices")
            click.echo(f"DEBUG: Response: {devices}")

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
                state = device.get('device_state', 'N/A')
                tunnel_url = device.get('tunnel_url', 'N/A')

                # Format state with visual indicator
                if state == 'active':
                    state_display = '✓ active'
                elif state == 'inactive':
                    state_display = '○ inactive'
                else:
                    state_display = state

                # Format tunnel URL based on state
                if state == 'inactive' and tunnel_url != 'N/A':
                    tunnel_display = f"(last: {tunnel_url})"
                else:
                    tunnel_display = tunnel_url if tunnel_url != 'N/A' else '-'

                rows.append([
                    device.get('device_serial', 'N/A'),
                    details.get('model', 'N/A'),
                    details.get('brand', 'N/A'),
                    device.get('device_type', 'N/A'),
                    state_display,
                    tunnel_display,
                ])

            click.echo(f"\n{tabulate(rows, headers=headers, tablefmt='grid')}\n")
            click.echo(f"Total: {len(devices)} device(s)")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@devices.command(name='deactivate')
@click.argument('device_serial', required=False)
@click.option('--api-key', envvar='NB_API_KEY', help='NativeBridge API key')
@click.option('--all', is_flag=True, help='Deactivate all active devices')
def deactivate_device(device_serial, api_key, all):
    """
    Deactivate device(s) and stop tunnel(s)

    DEVICE_SERIAL: Serial number of the device to deactivate (optional if --all is used)

    \b
    Examples:
      bridgelink devices deactivate 1d752b81        # Deactivate specific device
      bridgelink devices deactivate --all           # Deactivate all devices
      bridgelink devices deactivate                 # Deactivate all devices (prompts for confirmation)
    """

    if not api_key:
        click.echo("❌ Error: NativeBridge API key not provided", err=True)
        sys.exit(1)

    try:
        api_client = APIClient(api_key=api_key)
        tunnel_manager = TunnelManager()

        # If no serial provided and --all not explicitly set, prompt user
        if not device_serial and not all:
            if click.confirm("⚠️  No device specified. Deactivate ALL active devices?", default=False):
                all = True
            else:
                click.echo("Operation cancelled.")
                return

        # Deactivate all devices
        if all or not device_serial:
            devices = api_client.list_devices()

            if not devices:
                click.echo("No devices registered.")
                return

            active_devices = [d for d in devices if d.get('device_state') == 'active']

            if not active_devices:
                click.echo("No active devices to deactivate.")
                return

            click.echo(f"Found {len(active_devices)} active device(s)\n")

            success_count = 0
            for device in active_devices:
                serial = device['device_serial']
                click.echo(f"Deactivating device: {serial}")

                try:
                    # Stop tunnel
                    stopped = tunnel_manager.stop_tunnel(serial)
                    if stopped:
                        click.echo(f"  ✅ Stopped tunnel")

                    # Update device state in backend
                    api_client.update_device_state(serial, 'inactive')
                    click.echo(f"  ✅ Updated backend state\n")

                    success_count += 1

                except Exception as e:
                    click.echo(f"  ❌ Error: {e}\n", err=True)
                    continue

            click.echo(f"{'='*60}")
            click.echo(f"Deactivated {success_count}/{len(active_devices)} device(s) successfully")
            click.echo(f"{'='*60}")

            # Stop health monitor daemon if no devices remain active
            remaining_active = tunnel_manager.list_active_tunnels()
            if not remaining_active:
                daemon = get_daemon_instance()
                if daemon.is_running():
                    click.echo("\n🔍 No active devices remaining, stopping health monitor...")
                    if daemon.stop():
                        click.echo("   ✅ Health monitor stopped")
                    else:
                        click.echo("   ⚠️  Could not stop health monitor")

            return

        # Deactivate single device
        # Get device info
        device = api_client.get_device(device_serial)

        if not device:
            click.echo(f"❌ Device {device_serial} not found", err=True)
            sys.exit(1)

        if device['device_state'] == 'inactive':
            click.echo(f"⚠️  Device {device_serial} is already inactive")
            return

        # Stop tunnel
        stopped = tunnel_manager.stop_tunnel(device_serial)

        if stopped:
            click.echo(f"✅ Stopped tunnel for device {device_serial}")

        # Update device state in backend
        api_client.update_device_state(device_serial, 'inactive')

        click.echo(f"✅ Device {device_serial} deactivated successfully")

        # Stop health monitor daemon if no devices remain active
        remaining_active = tunnel_manager.list_active_tunnels()
        if not remaining_active:
            daemon = get_daemon_instance()
            if daemon.is_running():
                click.echo("\n🔍 No active devices remaining, stopping health monitor...")
                if daemon.stop():
                    click.echo("   ✅ Health monitor stopped")
                else:
                    click.echo("   ⚠️  Could not stop health monitor")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@devices.command(name='activate')
@click.argument('device_serial')
@click.option('--api-key', envvar='NB_API_KEY', help='NativeBridge API key')
def activate_device(device_serial, api_key):
    """
    Activate an existing device that is registered in NativeBridge

    DEVICE_SERIAL: Serial number of the device to activate
    """

    if not api_key:
        click.echo("❌ Error: NativeBridge API key not provided", err=True)
        click.echo("\nSet API key:")
        click.echo("  export NB_API_KEY='your-api-key'")
        sys.exit(1)

    # Validate device via ADB first (before any backend calls)
    click.echo("🔍 Validating device via ADB...")
    connected_devices = ADBDeviceManager.list_devices()

    if not connected_devices:
        click.echo("❌ No Android devices found via ADB", err=True)
        click.echo("\nMake sure:")
        click.echo("  1. Device is connected via USB")
        click.echo("  2. USB debugging is enabled")
        click.echo("  3. ADB is installed and in PATH")
        sys.exit(1)

    if device_serial not in connected_devices:
        click.echo(f"❌ Device '{device_serial}' is not a valid connected device", err=True)
        click.echo(f"\nConnected devices: {', '.join(connected_devices)}")
        click.echo("\nMake sure:")
        click.echo("  1. Device serial is correct")
        click.echo("  2. Device is connected via USB")
        click.echo("  3. Run 'adb devices' to verify")
        sys.exit(1)

    click.echo(f"✅ Device {device_serial} is connected via ADB\n")

    # Initialize API client
    try:
        api_client = APIClient(api_key=api_key)
        user_info = api_client.validate_api_key()
        click.echo(f"✅ Authenticated as: {user_info['user_email']}\n")
    except Exception as e:
        click.echo(f"❌ API key validation failed: {e}", err=True)
        sys.exit(1)

    # Check if device exists in backend
    try:
        click.echo("🔍 Checking device registration in NativeBridge...")
        existing_device = api_client.get_device(device_serial)

        if not existing_device:
            click.echo(f"❌ Device {device_serial} is not registered in NativeBridge\n")

            # Ask if user wants to register the device
            if click.confirm("Would you like to register/add this device now?"):
                click.echo("\n📝 Registering new device...\n")
                # Use the add_device command logic
                ctx = click.get_current_context()
                ctx.invoke(add_device, device_serials=(device_serial,), api_key=api_key)
            else:
                click.echo("\nTo register this device later, run:")
                click.echo(f"  bridgelink devices add {device_serial}")
            return

        # Check if already active
        if existing_device['device_state'] == 'active':
            click.echo(f"✅ Device {device_serial} is already active")
            click.echo(f"   Tunnel URL: {existing_device['tunnel_url']}\n")
            click.echo("To deactivate, run:")
            click.echo(f"  bridgelink devices deactivate {device_serial}")
            return

        # Device exists but is inactive - reactivate it
        click.echo(f"📱 Device {device_serial} found (currently inactive)")
        click.echo(f"   Model: {existing_device['device_details'].get('model', 'N/A')}")
        click.echo(f"   Brand: {existing_device['device_details'].get('brand', 'N/A')}")
        click.echo(f"   Last tunnel: {existing_device.get('tunnel_url', 'N/A')}\n")

        # Initialize tunnel manager
        tunnel_manager = TunnelManager()

        # Setup ADB TCP mode and get port
        click.echo("🔧 Setting up ADB TCP mode...")
        adb_port = tunnel_manager.setup_adb_tcp(device_serial)

        if not adb_port:
            click.echo(f"❌ Failed to setup ADB TCP mode for {device_serial}", err=True)
            sys.exit(1)

        click.echo(f"   ADB TCP port: {adb_port}\n")

        # Get device type for health monitoring
        device_type = existing_device['device_type']

        # Create bore tunnel
        click.echo("🌉 Creating bore tunnel...")
        tunnel_info = tunnel_manager.create_tunnel(device_serial, adb_port, api_key, device_type)

        if not tunnel_info:
            click.echo(f"❌ Failed to create tunnel for {device_serial}", err=True)
            sys.exit(1)

        tunnel_url = tunnel_info['url']
        click.echo(f"   Tunnel URL: {tunnel_url}\n")

        # Update device in backend
        click.echo("☁️  Updating device in NativeBridge...")

        device_data = {
            'device_serial': device_serial,
            'device_type': device_type,
            'device_details': existing_device['device_details'],
            'tunnel_url': tunnel_url,
            'device_state': 'active',
        }

        result = api_client.add_device(device_data)
        click.echo(f"   ✅ Device activated successfully\n")

        # Auto-start background health monitor
        daemon = get_daemon_instance()
        if not daemon.is_running():
            click.echo("🔍 Starting background health monitor...")
            if daemon.start(api_key):
                click.echo("   ✅ Health monitor started\n")
            else:
                click.echo("   ⚠️  Could not start health monitor (device will still work)\n")

        click.echo(f"{'✅ SUCCESS'.center(60, '=')}")
        click.echo(f"Device {device_serial} is now active!")
        click.echo(f"Connect from anywhere:")
        click.echo(f"  adb connect {tunnel_url}")
        click.echo(f"\n💡 Health monitoring is active - disconnected devices will be auto-deactivated")
        click.echo(f"\n⚠️  SECURITY WARNING:")
        click.echo(f"   Treat this tunnel URL as a SECRET!")
        click.echo(f"   Anyone with this URL can connect to your device.")
        click.echo(f"   Deactivate when not in use: bridgelink devices deactivate {device_serial}\n")

    except Exception as e:
        click.echo(f"❌ Error activating device: {e}", err=True)
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
