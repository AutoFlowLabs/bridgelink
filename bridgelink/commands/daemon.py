"""
Daemon management commands
"""

import click
from ..daemon.tunnel_manager import TunnelManager
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
@click.argument('device_serial')
def stop_tunnel(device_serial):
    """
    Stop a running tunnel for a device

    DEVICE_SERIAL: Serial number of the device
    """
    tunnel_manager = TunnelManager()

    # Check if tunnel exists
    tunnel = tunnel_manager.get_tunnel_info(device_serial)
    if not tunnel:
        click.echo(f"❌ No active tunnel found for device {device_serial}", err=True)
        return

    # Stop the tunnel
    if tunnel_manager.stop_tunnel(device_serial):
        click.echo(f"✅ Stopped tunnel for device {device_serial}")
        click.echo(f"   Tunnel URL was: {tunnel['url']}")
    else:
        click.echo(f"❌ Failed to stop tunnel for device {device_serial}", err=True)
