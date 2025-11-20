#!/usr/bin/env python3
"""
BridgeLink CLI - Main command-line interface
"""

import click
import sys
import os
from pathlib import Path
from . import __version__
from .commands import device, daemon, config
from .utils.bore_installer import BoreInstaller
from .utils.api_client import APIClient


@click.group()
@click.version_option(version=__version__, prog_name="bridgelink")
@click.pass_context
def main(ctx):
    """
    BridgeLink - Expose Android devices remotely via NativeBridge

    A CLI tool to expose your local Android devices to the cloud,
    making them accessible from anywhere with secure tunneling.

    \b
    Quick Start:
      1. Get API key: https://nativebridge.io/dashboard/api-keys
      2. Set API key: export NB_API_KEY='your-key'
      3. Add device:   bridgelink add-device <device-serial>
      4. View devices:  bridgelink list

    \b
    Need Help?
      Documentation: https://docs.nativebridge.io/bridgelink
      Support:       support@nativebridge.io
    """
    ctx.ensure_object(dict)

    # Store API key in context
    api_key = os.getenv('NB_API_KEY')
    ctx.obj['API_KEY'] = api_key


@main.command()
@click.option('--bore-only', is_flag=True, help='Install only bore binary')
@click.option('--adb-only', is_flag=True, help='Install only ADB')
def install(bore_only, adb_only):
    """
    Install required tools (bore tunnel binary and ADB).

    By default, installs both bore and ADB.
    Use --bore-only or --adb-only to install individual tools.
    """
    from .utils.adb_installer import ADBInstaller

    # Determine what to install
    install_bore = not adb_only
    install_adb = not bore_only

    click.echo("🔧 Installing BridgeLink dependencies...\n")

    # Install bore
    if install_bore:
        click.echo("="*60)
        click.echo("  Installing bore Tunnel Binary")
        click.echo("="*60 + "\n")

        bore_installer = BoreInstaller()

        if bore_installer.is_installed():
            click.echo(f"✅ bore is already installed at: {bore_installer.bore_path}")
            click.echo(f"   Version: {bore_installer.get_version()}")

            if not click.confirm("\nDo you want to reinstall bore?"):
                pass
            else:
                try:
                    bore_installer.install()
                    click.echo(f"\n✅ bore reinstalled successfully")
                except Exception as e:
                    click.echo(f"\n❌ bore installation failed: {e}", err=True)
        else:
            try:
                bore_installer.install()
                click.echo(f"\n✅ bore installed successfully at: {bore_installer.bore_path}")
                click.echo(f"   Version: {bore_installer.get_version()}")
            except Exception as e:
                click.echo(f"\n❌ bore installation failed: {e}", err=True)

        click.echo()

    # Install ADB
    if install_adb:
        click.echo("="*60)
        click.echo("  Installing Android Debug Bridge (ADB)")
        click.echo("="*60 + "\n")

        adb_installer = ADBInstaller()

        if adb_installer.is_installed():
            click.echo(f"✅ ADB is already installed")
            click.echo(f"   Version: {adb_installer.get_version()}")

            if not click.confirm("\nDo you want to reinstall ADB?"):
                pass
            else:
                try:
                    adb_installer.install()
                    click.echo(f"\n✅ ADB reinstalled successfully")
                    click.echo(f"   Version: {adb_installer.get_version()}")
                except Exception as e:
                    click.echo(f"\n❌ ADB installation failed: {e}", err=True)
        else:
            try:
                adb_installer.install()
                click.echo(f"\n✅ ADB installed successfully")
                click.echo(f"   Version: {adb_installer.get_version()}")
            except Exception as e:
                click.echo(f"\n❌ ADB installation failed: {e}", err=True)

        click.echo()

    # Summary
    click.echo("="*60)
    click.echo("  Installation Complete!")
    click.echo("="*60 + "\n")

    click.echo("Next steps:")
    click.echo("  1. Set your NativeBridge API key:")
    click.echo("     export NB_API_KEY='your-api-key'")
    click.echo("  2. Run setup wizard:")
    click.echo("     bridgelink setup")
    click.echo("  3. Add a device:")
    click.echo("     bridgelink devices add <device-serial>\n")


@main.command()
@click.pass_context
def setup(ctx):
    """Interactive setup wizard for first-time users."""
    from .commands.setup import run_setup
    run_setup(ctx.obj.get('API_KEY'))


# Register command groups
main.add_command(device.devices)
main.add_command(daemon.daemon)
main.add_command(config.config)


if __name__ == '__main__':
    main()
