"""
Interactive setup wizard
"""

import click
import os
from ..utils.bore_installer import BoreInstaller
from ..utils.api_client import APIClient


def run_setup(api_key=None):
    """Interactive setup wizard for first-time users"""
    click.echo("\n" + "="*60)
    click.echo("  🌉 BridgeLink Setup Wizard")
    click.echo("="*60 + "\n")

    # Step 1: Check/Set API Key
    click.echo("Step 1: NativeBridge API Key")
    click.echo("-" * 30)

    if not api_key:
        api_key = os.getenv('NB_API_KEY')

    if api_key:
        click.echo(f"✅ API key found: {api_key[:10]}...")

        # Validate API key
        try:
            client = APIClient(api_key=api_key)
            user_info = client.validate_api_key()
            click.echo(f"✅ Authenticated as: {user_info['user_email']}")
        except Exception as e:
            click.echo(f"❌ API key validation failed: {e}", err=True)
            api_key = None

    if not api_key:
        click.echo("\n📝 Get your API key from:")
        click.echo("   https://nativebridge.io/dashboard/api-keys\n")

        api_key = click.prompt("Enter your API key", type=str)

        # Validate the entered key
        try:
            client = APIClient(api_key=api_key)
            user_info = client.validate_api_key()
            click.echo(f"\n✅ Authenticated as: {user_info['user_email']}")
        except Exception as e:
            click.echo(f"\n❌ API key validation failed: {e}", err=True)
            click.echo("\nSetup aborted. Please check your API key and try again.")
            return

        # Save API key
        click.echo("\n💾 To save your API key permanently, add this to your shell profile:")
        click.echo(f"\n   export NB_API_KEY='{api_key}'")
        click.echo("\nFor zsh:")
        click.echo(f"   echo \"export NB_API_KEY='{api_key}'\" >> ~/.zshrc")
        click.echo("   source ~/.zshrc")
        click.echo("\nFor bash:")
        click.echo(f"   echo \"export NB_API_KEY='{api_key}'\" >> ~/.bashrc")
        click.echo("   source ~/.bashrc")

    click.echo()

    # Step 2: Install bore binary
    click.echo("\nStep 2: bore Tunnel Binary")
    click.echo("-" * 30)

    installer = BoreInstaller()

    if installer.is_installed():
        click.echo(f"✅ bore is already installed at: {installer.bore_path}")
        click.echo(f"   Version: {installer.get_version()}")
    else:
        click.echo("📥 Installing bore tunnel binary...")

        try:
            installer.install()
            click.echo(f"✅ bore installed successfully at: {installer.bore_path}")
            click.echo(f"   Version: {installer.get_version()}")
        except Exception as e:
            click.echo(f"❌ Installation failed: {e}", err=True)
            click.echo("\nYou can install it manually later with:")
            click.echo("  bridgelink install")

    click.echo()

    # Step 3: Check ADB
    click.echo("\nStep 3: Android Debug Bridge (ADB)")
    click.echo("-" * 30)

    import subprocess

    try:
        result = subprocess.run(['adb', 'version'], capture_output=True, text=True, check=True)
        click.echo("✅ ADB is installed")
        version_line = result.stdout.split('\n')[0]
        click.echo(f"   {version_line}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        click.echo("❌ ADB is not installed or not in PATH")
        click.echo("\nInstall ADB:")
        click.echo("  macOS:   brew install android-platform-tools")
        click.echo("  Linux:   sudo apt-get install android-tools-adb")
        click.echo("  Windows: Download from https://developer.android.com/studio/releases/platform-tools")

    click.echo()

    # Step 4: Summary
    click.echo("\n" + "="*60)
    click.echo("  ✅ Setup Complete!")
    click.echo("="*60 + "\n")

    click.echo("Next steps:")
    click.echo("  1. Connect your Android device via USB")
    click.echo("  2. Enable USB debugging on the device")
    click.echo("  3. Run: bridgelink devices add <device-serial>")
    click.echo("\nTo see connected devices:")
    click.echo("  adb devices\n")

    click.echo("For help:")
    click.echo("  bridgelink --help")
    click.echo("  bridgelink devices --help\n")

    click.echo("Documentation:")
    click.echo("  https://docs.nativebridge.io/bridgelink\n")
