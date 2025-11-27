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
from ..daemon.background_connection_monitor import get_connection_daemon_instance


@click.group(name='devices')
def devices():
    """Manage Android devices"""
    pass


@devices.command(name='add')
@click.argument('device_serials', nargs=-1, required=True)
@click.option('--api-key', envvar='NB_API_KEY', help='NativeBridge API key')
@click.option('--auto-activate', is_flag=True, default=False,
              help='Auto-activate device when reconnected (after disconnect)')
@click.option('--wifi', is_flag=True, default=False,
              help='Connect device via WiFi (device must be USB-connected first to enable WiFi mode)')
@click.pass_context
def add_device(ctx, device_serials, api_key, auto_activate, wifi):
    """
    Add one or more Android devices to NativeBridge

    \b
    DEVICE_SERIALS: One or more device serial numbers (space or comma separated)

    \b
    Examples:
      bridgelink devices add SERIAL123
      bridgelink devices add SERIAL1 SERIAL2 SERIAL3 --auto-activate
      bridgelink devices add SERIAL1,SERIAL2,SERIAL3
      bridgelink devices add SERIAL123 --wifi  # Enable WiFi connection

    \b
    WiFi Connection:
      When --wifi is enabled, the device will be set up for wireless ADB connection.
      The device must be initially connected via USB. The setup process will:
      1. Enable TCP/IP mode on the device
      2. Get the device's WiFi IP address
      3. Connect via WiFi
      4. Create tunnel using WiFi connection
      After setup, you can disconnect the USB cable and the device will remain
      accessible via BridgeLink using WiFi.

    \b
    Auto-Activate Feature:
      When --auto-activate is enabled, the device will automatically
      reactivate (create tunnel and update backend) when reconnected
      after being disconnected. This eliminates the need to manually
      run 'bridgelink devices add' or 'activate' again.
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
        click.echo(click.style("✅ Authenticated as: ", fg='green', bold=True) +
                   click.style(user_info['user_email'], fg='yellow', bold=True) + "\n")
    except Exception as e:
        click.echo(click.style(f"❌ API key validation failed: {e}", fg='red', bold=True), err=True)
        sys.exit(1)

    # Get all connected ADB devices
    if wifi:
        # For WiFi mode, we need USB devices first
        connected_devices = ADBDeviceManager.list_usb_devices()

        if not connected_devices:
            click.echo("❌ No USB-connected Android devices found", err=True)
            click.echo("\nFor WiFi setup, you must:")
            click.echo("  1. Connect device via USB first")
            click.echo("  2. Ensure USB debugging is enabled")
            click.echo("  3. Both device and computer must be on the same WiFi network")
            click.echo("\nAfter WiFi setup completes, you can disconnect the USB cable.")
            sys.exit(1)

        click.echo(f"Found {len(connected_devices)} USB-connected device(s)\n")
    else:
        # Normal mode - get all devices (USB + WiFi)
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
        click.echo(click.style(f"{'='*60}", fg='cyan'))
        click.echo(click.style(f"Processing device: ", fg='cyan', bold=True) +
                   click.style(serial, fg='magenta', bold=True))
        click.echo(click.style(f"{'='*60}", fg='cyan') + "\n")

        # Check if device is connected
        if serial not in connected_devices:
            click.echo(f"❌ Device {serial} is not connected via ADB", err=True)
            click.echo(f"   Connected devices: {', '.join(connected_devices)}\n")
            continue

        # WiFi setup if requested
        wifi_serial = None
        if wifi:
            click.echo(click.style("📡 Setting up WiFi connection...", fg='blue', bold=True))

            # Step 1: Enable TCP/IP mode on device
            click.echo(click.style("   Step 1/3: Enabling TCP/IP mode on device...", fg='blue'))
            if not ADBDeviceManager.enable_tcpip_mode(serial):
                click.echo(click.style(f"❌ Failed to enable TCP/IP mode on device {serial}", fg='red', bold=True), err=True)
                click.echo(click.style("   Make sure the device is connected via USB and authorized.\n", fg='yellow'))
                continue

            click.echo(click.style("   ✓ TCP/IP mode enabled on port 5555", fg='green'))

            # Step 2: Get device IP address
            click.echo(click.style("   Step 2/3: Getting device IP address...", fg='blue'))
            device_ip = ADBDeviceManager.get_device_ip_address(serial)

            if not device_ip:
                click.echo(click.style(f"❌ Could not get IP address for device {serial}", fg='red', bold=True), err=True)
                click.echo(click.style("   Make sure:", fg='yellow'))
                click.echo(click.style("     1. Device is connected to WiFi", fg='yellow'))
                click.echo(click.style("     2. Device and computer are on the same network", fg='yellow'))
                click.echo(click.style("     3. WiFi is enabled on the device\n", fg='yellow'))
                continue

            click.echo(click.style(f"   ✓ Device IP address: ", fg='green') +
                       click.style(device_ip, fg='cyan', bold=True))

            # Step 3: Connect via WiFi
            click.echo(click.style("   Step 3/3: Connecting to device via WiFi...", fg='blue'))
            if not ADBDeviceManager.connect_wifi(device_ip):
                click.echo(click.style(f"❌ Failed to connect to device via WiFi", fg='red', bold=True), err=True)
                click.echo(click.style(f"   Try manually: adb connect {device_ip}:5555\n", fg='yellow'))
                continue

            click.echo(click.style(f"   ✓ Connected via WiFi: ", fg='green') +
                       click.style(f"{device_ip}:5555", fg='cyan', bold=True))
            click.echo(click.style(f"\n💡 You can now disconnect the USB cable!", fg='yellow', bold=True))
            click.echo(click.style(f"   The device will remain connected via WiFi.\n", fg='yellow'))

            # Use WiFi address for the rest of the setup
            wifi_serial = f"{device_ip}:5555"
            serial = wifi_serial  # Update serial to use WiFi connection

        try:
            # Get device information
            click.echo(click.style("📱 Fetching device information...", fg='blue', bold=True))
            device_info = ADBDeviceManager.get_device_info(serial)

            if not device_info:
                click.echo(click.style(f"❌ Could not get device information for {serial}", fg='red', bold=True), err=True)
                continue

            # Determine connection mode
            connection_mode = 'WiFi' if ADBDeviceManager.is_wifi_connection(serial) else 'USB'

            device_details = {
                'brand': device_info.manufacturer,  # Backend expects 'brand'
                'model': device_info.model,
                'android_version': device_info.android_version,  # Backend expects 'android_version'
                'sdk_version': device_info.sdk_version,
                'manufacturer': device_info.manufacturer,
                'os_version': device_info.android_version,
                'sdk': device_info.sdk_version,
                'security_patch': device_info.security_patch,
                'cpu': device_info.cpu,
                'ram_gb': device_info.ram_gb,
                'storage_gb': device_info.storage_gb,
                'resolution': device_info.resolution,
                'density_dpi': device_info.density_dpi,
                'connection_mode': connection_mode,
            }

            device_type = 'emulator' if 'emulator' in serial.lower() else 'physical'

            click.echo(click.style("   Model: ", fg='white') +
                       click.style(device_info.model, fg='cyan', bold=True))
            click.echo(click.style("   Manufacturer: ", fg='white') +
                       click.style(device_info.manufacturer, fg='cyan', bold=True))
            click.echo(click.style("   Android: ", fg='white') +
                       click.style(f"{device_info.android_version}", fg='green', bold=True) +
                       click.style(f" (SDK {device_info.sdk_version})", fg='green'))
            if device_info.ram_gb:
                click.echo(click.style("   RAM: ", fg='white') +
                           click.style(f"{device_info.ram_gb} GB", fg='magenta', bold=True))
            if device_info.storage_gb:
                click.echo(click.style("   Storage: ", fg='white') +
                           click.style(f"{device_info.storage_gb} GB", fg='magenta', bold=True))
            if device_info.resolution:
                click.echo(click.style("   Resolution: ", fg='white') +
                           click.style(device_info.resolution, fg='yellow', bold=True))
            click.echo(click.style("   Type: ", fg='white') +
                       click.style(device_type, fg='blue', bold=True) + "\n")

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
            click.echo("🔧 Setting up ADB port forwarding...")
            is_wifi_conn = ADBDeviceManager.is_wifi_connection(serial)
            adb_port = tunnel_manager.setup_adb_tcp(serial, is_wifi=is_wifi_conn)

            if not adb_port:
                click.echo(f"❌ Failed to setup ADB port forwarding for {serial}", err=True)
                continue

            click.echo(f"   Local ADB port: {adb_port}\n")

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
                'auto_activate': auto_activate,
            }

            result = api_client.add_device(device_data)
            click.echo(f"   ✅ Device registered successfully")
            if auto_activate:
                click.echo(f"   🔄 Auto-activation ENABLED - device will auto-reconnect when plugged back in\n")
            else:
                click.echo()

            # Auto-start background health monitor
            daemon = get_daemon_instance()
            if not daemon.is_running():
                click.echo("🔍 Starting background health monitor...")
                if daemon.start(api_key):
                    click.echo("   ✅ Health monitor started")
                else:
                    click.echo("   ⚠️  Could not start health monitor (device will still work)")

            # Auto-start connection monitor if auto_activate is enabled
            if auto_activate:
                connection_daemon = get_connection_daemon_instance()
                if not connection_daemon.is_running():
                    click.echo("🔌 Starting auto-activation connection monitor...")
                    if connection_daemon.start(api_key):
                        click.echo("   ✅ Connection monitor started\n")
                    else:
                        click.echo("   ⚠️  Could not start connection monitor\n")
                else:
                    click.echo("   Connection monitor already running\n")
            else:
                click.echo()

            click.echo(click.style(f"{'='*60}", fg='green', bold=True))
            click.echo(click.style("✅ SUCCESS", fg='green', bold=True).center(60 + 10))
            click.echo(click.style(f"{'='*60}", fg='green', bold=True))
            click.echo(click.style("Device ", fg='white') +
                       click.style(serial, fg='cyan', bold=True) +
                       click.style(" is now active!", fg='green', bold=True))
            click.echo(click.style("Connect from anywhere:", fg='yellow', bold=True))
            click.echo(click.style("  adb connect ", fg='white') +
                       click.style(tunnel_url, fg='magenta', bold=True))

            # Show dashboard URL
            dashboard_url = api_client.get_dashboard_url()
            click.echo(click.style("\n🌐 Manage device in NativeBridge Dashboard:", fg='blue', bold=True))
            click.echo(click.style("   ", fg='white') +
                       click.style(dashboard_url, fg='cyan', bold=True, underline=True))
            click.echo(click.style("   → View device status, start remote sessions, and control your device", fg='blue'))

            click.echo(click.style("\n💡 Health monitoring is active", fg='yellow', bold=True) +
                       click.style(" - disconnected devices will be auto-deactivated", fg='yellow'))
            if auto_activate:
                click.echo(click.style("🔄 Auto-activation ENABLED", fg='green', bold=True) +
                           click.style(" - device will auto-reconnect when plugged back in", fg='green'))
            click.echo(click.style("\n⚠️  SECURITY WARNING:", fg='yellow', bold=True))
            click.echo(click.style("   Treat this tunnel URL as a SECRET!", fg='yellow'))
            click.echo(click.style("   Anyone with this URL can connect to your device.", fg='yellow'))
            click.echo(click.style("   Deactivate when not in use: ", fg='yellow') +
                       click.style(f"bridgelink devices deactivate {serial}", fg='white', bold=True) + "\n")

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
            click.echo(click.style("No devices registered yet.", fg='yellow', bold=True))
            click.echo(click.style("\nAdd a device:", fg='cyan'))
            click.echo(click.style("  bridgelink devices add <device-serial>", fg='white', bold=True))
            return

        if format == 'json':
            click.echo(json.dumps(devices, indent=2))
        else:
            # Table format
            headers = ['#', 'Serial', 'Model', 'Brand', 'Type', 'Mode', 'State', 'Auto-Act', 'Tunnel URL']
            rows = []

            for idx, device in enumerate(devices, start=1):
                details = device.get('device_details', {})
                state = device.get('device_state', 'N/A')
                tunnel_url = device.get('tunnel_url', 'N/A')
                auto_activate = device.get('auto_activate', False)
                connection_mode = details.get('connection_mode', 'N/A')

                # Format state with visual indicator
                if state == 'active':
                    state_display = '✓ active'
                elif state == 'inactive':
                    state_display = '○ inactive'
                else:
                    state_display = state

                # Format auto-activate indicator
                auto_act_display = '🔄 ON' if auto_activate else '○ off'

                # Format tunnel URL based on state
                if state == 'inactive' and tunnel_url != 'N/A':
                    tunnel_display = f"(last: {tunnel_url})"
                else:
                    tunnel_display = tunnel_url if tunnel_url != 'N/A' else '-'

                rows.append([
                    idx,
                    device.get('device_serial', 'N/A'),
                    details.get('model', 'N/A'),
                    details.get('brand', 'N/A'),
                    device.get('device_type', 'N/A'),
                    connection_mode,
                    state_display,
                    auto_act_display,
                    tunnel_display,
                ])

            click.echo(f"\n{tabulate(rows, headers=headers, tablefmt='grid')}\n")
            click.echo(click.style("Total: ", fg='white') +
                       click.style(f"{len(devices)} device(s)", fg='cyan', bold=True))
            click.echo(click.style("\n💡 Mode: ", fg='yellow', bold=True) +
                       click.style("Connection mode (USB or WiFi)", fg='yellow'))
            click.echo(click.style("💡 Auto-Act: ", fg='yellow', bold=True) +
                       click.style("Auto-activation feature (device auto-reconnects when plugged back in)", fg='yellow'))

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
        click.echo(click.style("✅ Authenticated as: ", fg='green', bold=True) +
                   click.style(user_info['user_email'], fg='yellow', bold=True) + "\n")
    except Exception as e:
        click.echo(click.style(f"❌ API key validation failed: {e}", fg='red', bold=True), err=True)
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
        click.echo("🔧 Setting up ADB port forwarding...")
        is_wifi_conn = ADBDeviceManager.is_wifi_connection(device_serial)
        adb_port = tunnel_manager.setup_adb_tcp(device_serial, is_wifi=is_wifi_conn)

        if not adb_port:
            click.echo(f"❌ Failed to setup ADB port forwarding for {device_serial}", err=True)
            sys.exit(1)

        click.echo(f"   Local ADB port: {adb_port}\n")

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

        # Update connection mode in device details
        device_details = existing_device['device_details']
        device_details['connection_mode'] = 'WiFi' if ADBDeviceManager.is_wifi_connection(device_serial) else 'USB'

        device_data = {
            'device_serial': device_serial,
            'device_type': device_type,
            'device_details': device_details,
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

        # Show dashboard URL
        dashboard_url = api_client.get_dashboard_url()
        click.echo(f"\n🌐 Manage device in NativeBridge Dashboard:")
        click.echo(f"   {dashboard_url}")
        click.echo(f"   → View device status, start remote sessions, and control your device")

        click.echo(click.style("\n💡 Health monitoring is active", fg='yellow', bold=True) +
                   click.style(" - disconnected devices will be auto-deactivated", fg='yellow'))
        click.echo(click.style("\n⚠️  SECURITY WARNING:", fg='yellow', bold=True))
        click.echo(click.style("   Treat this tunnel URL as a SECRET!", fg='yellow'))
        click.echo(click.style("   Anyone with this URL can connect to your device.", fg='yellow'))
        click.echo(click.style("   Deactivate when not in use: ", fg='yellow') +
                   click.style(f"bridgelink devices deactivate {device_serial}", fg='white', bold=True) + "\n")

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


@devices.command(name='set-auto-activate')
@click.argument('device_serial')
@click.argument('enabled', type=click.Choice(['on', 'off'], case_sensitive=False))
@click.option('--api-key', envvar='NB_API_KEY', help='NativeBridge API key')
def set_auto_activate(device_serial, enabled, api_key):
    """
    Enable or disable auto-activation for a device

    DEVICE_SERIAL: Serial number of the device
    ENABLED: 'on' to enable, 'off' to disable

    \b
    Examples:
      bridgelink devices set-auto-activate SERIAL123 on
      bridgelink devices set-auto-activate SERIAL123 off

    \b
    When enabled, the device will automatically activate (create tunnel
    and update backend) when reconnected after being disconnected.
    """

    if not api_key:
        click.echo("❌ Error: NativeBridge API key not provided", err=True)
        sys.exit(1)

    try:
        api_client = APIClient(api_key=api_key)
        auto_activate = (enabled.lower() == 'on')

        # Check if device exists
        device = api_client.get_device(device_serial)
        if not device:
            click.echo(f"❌ Device {device_serial} not found", err=True)
            sys.exit(1)

        # Update auto-activate preference
        result = api_client.update_auto_activate(device_serial, auto_activate)

        action = "enabled" if auto_activate else "disabled"
        click.echo(f"✅ Auto-activation {action} for device {device_serial}")

        if auto_activate:
            # Start connection monitor if not running
            connection_daemon = get_connection_daemon_instance()
            if not connection_daemon.is_running():
                click.echo(f"\n🔌 Starting auto-activation connection monitor...")
                if connection_daemon.start(api_key):
                    click.echo(f"   ✅ Connection monitor started")
                else:
                    click.echo(f"   ⚠️  Could not start connection monitor")

            click.echo(f"\n💡 Device will automatically reconnect when plugged back in")
            click.echo(f"   No need to run 'bridgelink devices add' again!")
        else:
            click.echo(f"\n💡 Device will require manual activation:")
            click.echo(f"   bridgelink devices activate {device_serial}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
