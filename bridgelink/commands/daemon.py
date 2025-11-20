"""
Daemon management commands
"""

import click
from ..daemon.tunnel_manager import TunnelManager
from ..daemon.background_monitor import get_daemon_instance
from tabulate import tabulate


@click.group(name='daemon')
def daemon():
    """Manage BridgeLink daemon and background tunnels"""
    pass


@daemon.command(name='status')
def status():
    """Show status of running tunnels"""
    tunnel_manager = TunnelManager()
    active_tunnels = tunnel_manager.list_active_tunnels()

    if not active_tunnels:
        click.echo("No active tunnels running.")
        return

    headers = ['Device Serial', 'Tunnel URL', 'Local Port', 'PID', 'Started At']
    rows = []

    for tunnel in active_tunnels:
        import datetime
        started = datetime.datetime.fromtimestamp(tunnel['started_at'])
        started_str = started.strftime('%Y-%m-%d %H:%M:%S')

        rows.append([
            tunnel['device_serial'],
            tunnel['url'],
            tunnel['local_port'],
            tunnel['pid'],
            started_str
        ])

    click.echo(f"\n{tabulate(rows, headers=headers, tablefmt='grid')}\n")
    click.echo(f"Total active tunnels: {len(active_tunnels)}")


@daemon.command(name='logs')
@click.argument('device_serial')
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
@click.option('--lines', '-n', default=50, help='Number of lines to show')
def logs(device_serial, follow, lines):
    """View tunnel logs for a device"""
    tunnel_manager = TunnelManager()
    tunnel = tunnel_manager.get_tunnel_info(device_serial)

    if not tunnel:
        click.echo(f"❌ No active tunnel found for device {device_serial}", err=True)
        return

    log_file = tunnel['log_file']

    if follow:
        import subprocess
        subprocess.run(['tail', '-f', log_file])
    else:
        import subprocess
        result = subprocess.run(
            ['tail', f'-n{lines}', log_file],
            capture_output=True,
            text=True
        )
        click.echo(result.stdout)


@daemon.command(name='cleanup')
def cleanup():
    """Clean up dead tunnel processes"""
    tunnel_manager = TunnelManager()
    tunnel_manager.cleanup_dead_tunnels()
    click.echo("✅ Cleaned up dead tunnels")


@daemon.command(name='stop')
@click.argument('device_serial', required=False)
@click.option('--all', is_flag=True, help='Stop all running tunnels')
def stop_tunnel(device_serial, all):
    """
    Stop running tunnel(s)

    DEVICE_SERIAL: Serial number of the device (optional if --all is used)

    \b
    Examples:
      bridgelink daemon stop 1d752b81        # Stop specific tunnel
      bridgelink daemon stop --all           # Stop all tunnels
      bridgelink daemon stop                 # Stop all tunnels (prompts for confirmation)
    """
    tunnel_manager = TunnelManager()

    # If no serial provided and --all not explicitly set, prompt user
    if not device_serial and not all:
        if click.confirm("⚠️  No device specified. Stop ALL running tunnels?", default=False):
            all = True
        else:
            click.echo("Operation cancelled.")
            return

    # Stop all tunnels
    if all or not device_serial:
        active_tunnels = tunnel_manager.list_active_tunnels()

        if not active_tunnels:
            click.echo("No active tunnels running.")
            return

        click.echo(f"Found {len(active_tunnels)} active tunnel(s)\n")

        success_count = 0
        for tunnel in active_tunnels:
            serial = tunnel['device_serial']
            tunnel_url = tunnel['url']

            click.echo(f"Stopping tunnel for device: {serial}")
            click.echo(f"  Tunnel URL: {tunnel_url}")

            if tunnel_manager.stop_tunnel(serial):
                click.echo(f"  ✅ Stopped successfully\n")
                success_count += 1
            else:
                click.echo(f"  ❌ Failed to stop\n", err=True)

        click.echo(f"{'='*60}")
        click.echo(f"Stopped {success_count}/{len(active_tunnels)} tunnel(s) successfully")
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

    # Stop single tunnel
    # Check if tunnel exists
    tunnel = tunnel_manager.get_tunnel_info(device_serial)
    if not tunnel:
        click.echo(f"❌ No active tunnel found for device {device_serial}", err=True)
        return

    # Stop the tunnel
    if tunnel_manager.stop_tunnel(device_serial):
        click.echo(f"✅ Stopped tunnel for device {device_serial}")
        click.echo(f"   Tunnel URL was: {tunnel['url']}")

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
    else:
        click.echo(f"❌ Failed to stop tunnel for device {device_serial}", err=True)


