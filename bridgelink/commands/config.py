"""
Configuration management commands
"""

import click
import json
import os
from pathlib import Path


@click.group(name='config')
def config():
    """Manage BridgeLink configuration"""
    pass


@config.command(name='show')
def show_config():
    """Show current configuration"""
    config_data = {
        'api_key': os.getenv('NB_API_KEY', '(not set)'),
        'api_url': os.getenv('NB_API_URL', 'https://dev.api.nativebridge.io'),
        'bore_server': os.getenv('BORE_SERVER', '3.6.53.225'),
        'data_dir': str(Path.home() / '.bridgelink'),
    }

    click.echo("\nCurrent Configuration:")
    click.echo("="*60)
    for key, value in config_data.items():
        if key == 'api_key' and value != '(not set)':
            # Mask API key
            masked = value[:10] + '...' if len(value) > 10 else value
            click.echo(f"{key:20s}: {masked}")
        else:
            click.echo(f"{key:20s}: {value}")
    click.echo("="*60)


@config.command(name='set-api-key')
@click.argument('api_key')
def set_api_key(api_key):
    """Set NativeBridge API key"""
    # Validate API key format
    if not api_key.startswith('Nb-'):
        click.echo("⚠️  Warning: API key should start with 'Nb-'", err=True)

    click.echo("\nTo set API key permanently, add this to your shell profile:")
    click.echo(f"\nexport NB_API_KEY='{api_key}'")
    click.echo("\nFor bash/zsh:")
    click.echo(f"echo \"export NB_API_KEY='{api_key}'\" >> ~/.zshrc")
    click.echo("source ~/.zshrc")


@config.command(name='reset')
@click.confirmation_option(prompt='Are you sure you want to reset all data?')
def reset_config():
    """Reset BridgeLink data and configuration"""
    import shutil

    data_dir = Path.home() / '.bridgelink'

    if data_dir.exists():
        shutil.rmtree(data_dir)
        click.echo("✅ All data reset")
    else:
        click.echo("No data to reset")
