#!/usr/bin/env python3
"""
BridgeLink - NativeBridge Device Connection Service
Exposes local ADB devices to the cloud testing platform
"""

import click
import subprocess
import time
import logging
import json
import os
import sys
import threading
import requests
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
import uuid
import signal
import psutil
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BridgeLink')

class DeviceStatus(Enum):
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    IDLE = "idle"

@dataclass
class DeviceInfo:
    serial: str
    model: str
    android_version: str
    sdk_version: str
    manufacturer: str
    product: str
    device_name: str

class NativeBridgeAPI:
    """API client for NativeBridge backend"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.nativebridge.io"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.session_id = str(uuid.uuid4())
    
    def validate_api_key(self) -> Dict:
        """Validate API key and get user info"""
        try:
            response = requests.get(
                f"{self.base_url}/v1/auth/validate",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API key validation failed: {e}")
            return None
    
    def register_device(self, device_info: DeviceInfo, proxy_url: str, local_port: int) -> Dict:
        """Register device with backend"""
        payload = {
            "session_id": self.session_id,
            "device": asdict(device_info),
            "proxy_url": proxy_url,
            "local_port": local_port,
            "status": DeviceStatus.CONNECTING.value,
            "connected_at": datetime.utcnow().isoformat(),
            "client_version": "1.0.0",
            "client_os": sys.platform
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/devices/register",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Device registration failed: {e}")
            return None
    
    def update_device_status(self, device_id: str, status: DeviceStatus, 
                            metadata: Dict = None) -> bool:
        """Update device status in backend"""
        payload = {
            "device_id": device_id,
            "status": status.value,
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        try:
            response = requests.patch(
                f"{self.base_url}/v1/devices/{device_id}/status",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Status update failed: {e}")
            return False
    
    def heartbeat(self, device_id: str, metrics: Dict = None) -> bool:
        """Send heartbeat to keep connection alive"""
        payload = {
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics or {}
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/devices/{device_id}/heartbeat",
                json=payload,
                headers=self.headers,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def unregister_device(self, device_id: str) -> bool:
        """Unregister device from backend"""
        try:
            response = requests.delete(
                f"{self.base_url}/v1/devices/{device_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Device unregistration failed: {e}")
            return False

class ADBDeviceManager:
    """Manages ADB device connections"""
    
    @staticmethod
    def list_devices() -> List[str]:
        """List all connected ADB devices"""
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                check=True
            )
            
            devices = []
            for line in result.stdout.strip().split('\n')[1:]:
                if '\t' in line:
                    serial, status = line.split('\t')
                    if status == 'device':
                        devices.append(serial)
            
            return devices
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list ADB devices: {e}")
            return []
    
    @staticmethod
    def get_device_info(serial: str) -> Optional[DeviceInfo]:
        """Get detailed device information"""
        try:
            def get_prop(prop):
                result = subprocess.run(
                    ["adb", "-s", serial, "shell", "getprop", prop],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout.strip()
            
            return DeviceInfo(
                serial=serial,
                model=get_prop("ro.product.model"),
                android_version=get_prop("ro.build.version.release"),
                sdk_version=get_prop("ro.build.version.sdk"),
                manufacturer=get_prop("ro.product.manufacturer"),
                product=get_prop("ro.product.name"),
                device_name=get_prop("ro.product.device")
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get device info: {e}")
            return None
    
    @staticmethod
    def setup_tcp_mode(serial: str, port: int = 5555) -> bool:
        """Enable TCP mode on device"""
        try:
            # Enable TCP mode
            subprocess.run(
                ["adb", "-s", serial, "tcpip", str(port)],
                capture_output=True,
                text=True,
                check=True
            )
            time.sleep(2)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to enable TCP mode: {e}")
            return False
    
    @staticmethod
    def setup_port_forward(serial: str, local_port: int, device_port: int = 5555) -> bool:
        """Setup port forwarding"""
        try:
            subprocess.run(
                ["adb", "-s", serial, "forward", f"tcp:{local_port}", f"tcp:{device_port}"],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to setup port forwarding: {e}")
            return False

class TunnelManager:
    """Manages tunnel connections (Cloudflare/ngrok)"""
    
    def __init__(self, tunnel_type: str = "cloudflare"):
        self.tunnel_type = tunnel_type
        self.tunnel_process = None
        self.tunnel_url = None
    
    def start_cloudflare_tunnel(self, port: int, device_id: str) -> Optional[str]:
        """Start Cloudflare tunnel"""
        try:
            # Use quick tunnel for simplicity (no config needed)
            process = subprocess.Popen(
                ["cloudflared", "tunnel", "--url", f"tcp://localhost:{port}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for tunnel URL
            for _ in range(30):  # Wait up to 30 seconds
                line = process.stderr.readline()
                if "trycloudflare.com" in line:
                    # Extract URL from output
                    import re
                    match = re.search(r'https://[^\s]+trycloudflare\.com', line)
                    if match:
                        self.tunnel_url = match.group(0).replace("https://", "tcp://")
                        self.tunnel_process = process
                        logger.info(f"Cloudflare tunnel established: {self.tunnel_url}")
                        return self.tunnel_url
                time.sleep(1)
            
            logger.error("Failed to get Cloudflare tunnel URL")
            process.terminate()
            return None
            
        except Exception as e:
            logger.error(f"Failed to start Cloudflare tunnel: {e}")
            return None
    
    def start_ngrok_tunnel(self, port: int) -> Optional[str]:
        """Start ngrok tunnel"""
        try:
            # Check if pyngrok is installed
            import pyngrok
            from pyngrok import ngrok
            
            # Set auth token if available
            auth_token = os.getenv("NGROK_AUTH_TOKEN")
            if auth_token:
                ngrok.set_auth_token(auth_token)
            
            # Start tunnel
            tunnel = ngrok.connect(port, "tcp")
            self.tunnel_url = tunnel.public_url
            logger.info(f"ngrok tunnel established: {self.tunnel_url}")
            return self.tunnel_url
            
        except ImportError:
            logger.error("pyngrok not installed. Run: pip install pyngrok")
            return None
        except Exception as e:
            logger.error(f"Failed to start ngrok tunnel: {e}")
            return None
    
    def start_tunnel(self, port: int, device_id: str) -> Optional[str]:
        """Start the configured tunnel type"""
        if self.tunnel_type == "cloudflare":
            return self.start_cloudflare_tunnel(port, device_id)
        elif self.tunnel_type == "ngrok":
            return self.start_ngrok_tunnel(port)
        else:
            logger.error(f"Unknown tunnel type: {self.tunnel_type}")
            return None
    
    def stop_tunnel(self):
        """Stop the tunnel"""
        if self.tunnel_process:
            self.tunnel_process.terminate()
            self.tunnel_process = None
        
        if self.tunnel_type == "ngrok":
            try:
                from pyngrok import ngrok
                ngrok.disconnect(self.tunnel_url)
            except:
                pass
        
        self.tunnel_url = None

class BridgeLink:
    """Main BridgeLink service"""
    
    def __init__(self, api_key: str, tunnel_type: str = "cloudflare"):
        self.api_key = api_key
        self.api_client = NativeBridgeAPI(api_key)
        self.tunnel_manager = TunnelManager(tunnel_type)
        self.adb_manager = ADBDeviceManager()
        
        self.device_id = None  # Backend device ID
        self.device_serial = None  # ADB serial
        self.local_port = None
        self.heartbeat_thread = None
        self.monitoring_thread = None
        self.running = False
        
        # Port allocation
        self.port_range = range(15555, 15600)
    
    def find_available_port(self) -> Optional[int]:
        """Find an available local port"""
        for port in self.port_range:
            try:
                import socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except:
                continue
        return None
    
    def heartbeat_worker(self):
        """Send periodic heartbeats to backend"""
        while self.running:
            if self.device_id:
                # Collect metrics
                metrics = {
                    "cpu_usage": psutil.cpu_percent(),
                    "memory_usage": psutil.virtual_memory().percent,
                    "uptime_seconds": int(time.time() - self.start_time)
                }
                
                # Send heartbeat
                if not self.api_client.heartbeat(self.device_id, metrics):
                    logger.warning("Heartbeat failed")
            
            time.sleep(30)  # Send heartbeat every 30 seconds
    
    def monitor_device(self):
        """Monitor device connection status"""
        while self.running:
            if self.device_serial:
                # Check if device is still connected
                devices = self.adb_manager.list_devices()
                if self.device_serial not in devices:
                    logger.error(f"Device {self.device_serial} disconnected")
                    self.api_client.update_device_status(
                        self.device_id, 
                        DeviceStatus.DISCONNECTED
                    )
                    self.stop()
                    break
            
            time.sleep(5)  # Check every 5 seconds
    
    def connect_device(self, device_serial: str) -> bool:
        """Connect to a specific device"""
        try:
            # Validate API key
            user_info = self.api_client.validate_api_key()
            if not user_info:
                logger.error("Invalid API key")
                return False
            
            logger.info(f"Authenticated as: {user_info.get('email', 'Unknown')}")
            
            # Get device info
            device_info = self.adb_manager.get_device_info(device_serial)
            if not device_info:
                logger.error("Failed to get device information")
                return False
            
            logger.info(f"Connecting to: {device_info.model} (Android {device_info.android_version})")
            
            # Find available port
            self.local_port = self.find_available_port()
            if not self.local_port:
                logger.error("No available ports")
                return False
            
            # Setup ADB TCP mode
            logger.info("Setting up TCP mode...")
            if not self.adb_manager.setup_tcp_mode(device_serial):
                return False
            
            # Setup port forwarding
            logger.info(f"Setting up port forwarding on port {self.local_port}...")
            if not self.adb_manager.setup_port_forward(device_serial, self.local_port):
                return False
            
            # Start tunnel
            logger.info("Starting tunnel...")
            tunnel_url = self.tunnel_manager.start_tunnel(self.local_port, device_serial)
            if not tunnel_url:
                logger.error("Failed to start tunnel")
                return False
            
            # Register device with backend
            logger.info("Registering device with NativeBridge...")
            registration = self.api_client.register_device(
                device_info, 
                tunnel_url, 
                self.local_port
            )
            
            if not registration:
                logger.error("Failed to register device")
                self.tunnel_manager.stop_tunnel()
                return False
            
            self.device_id = registration['device_id']
            self.device_serial = device_serial
            
            # Update status to connected
            self.api_client.update_device_status(
                self.device_id, 
                DeviceStatus.CONNECTED,
                {"tunnel_url": tunnel_url}
            )
            
            # Start monitoring
            self.running = True
            self.start_time = time.time()
            
            self.heartbeat_thread = threading.Thread(target=self.heartbeat_worker)
            self.heartbeat_thread.daemon = True
            self.heartbeat_thread.start()
            
            self.monitoring_thread = threading.Thread(target=self.monitor_device)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            
            logger.info(f"✅ Device successfully exposed!")
            logger.info(f"📱 Device ID: {self.device_id}")
            logger.info(f"🔗 Proxy URL: {tunnel_url}")
            logger.info(f"📝 To connect: adb connect {tunnel_url.replace('tcp://', '').replace('https://', '')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def stop(self):
        """Stop the service"""
        self.running = False
        
        # Update device status
        if self.device_id:
            self.api_client.update_device_status(
                self.device_id, 
                DeviceStatus.DISCONNECTED
            )
            self.api_client.unregister_device(self.device_id)
        
        # Stop tunnel
        self.tunnel_manager.stop_tunnel()
        
        # Clear port forwarding
        if self.device_serial and self.local_port:
            try:
                subprocess.run(
                    ["adb", "-s", self.device_serial, "forward", "--remove", f"tcp:{self.local_port}"],
                    capture_output=True,
                    check=False
                )
            except:
                pass
        
        logger.info("Service stopped")

class InteractiveDeviceSelector:
    """Interactive device selection UI"""
    
    @staticmethod
    def select_device(devices: List[str]) -> Optional[str]:
        """Interactive device selection"""
        if not devices:
            logger.error("No devices found")
            return None
        
        if len(devices) == 1:
            return devices[0]
        
        click.echo("\n📱 Available Devices:")
        click.echo("-" * 50)
        
        for idx, serial in enumerate(devices, 1):
            # Get device info
            info = ADBDeviceManager.get_device_info(serial)
            if info:
                click.echo(f"{idx}. {info.model} ({info.manufacturer})")
                click.echo(f"   Serial: {serial}")
                click.echo(f"   Android: {info.android_version} (SDK {info.sdk_version})")
            else:
                click.echo(f"{idx}. {serial}")
            click.echo()
        
        while True:
            try:
                choice = click.prompt("Select device number", type=int)
                if 1 <= choice <= len(devices):
                    return devices[choice - 1]
                else:
                    click.echo("Invalid choice. Please try again.")
            except:
                click.echo("Invalid input. Please enter a number.")

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """BridgeLink - NativeBridge Device Connection Service
    
    Expose your local Android devices to the cloud for remote testing.
    """
    pass

@cli.command()
@click.option('--device', '-d', help='Device serial number (optional)')
@click.option('--tunnel', '-t', 
              type=click.Choice(['cloudflare', 'ngrok']), 
              default='cloudflare',
              help='Tunnel provider to use')
@click.option('--api-key', '-k', 
              envvar='NATIVEBRIDGE_API_KEY',
              help='NativeBridge API key (or set NATIVEBRIDGE_API_KEY env var)')
def connect(device, tunnel, api_key):
    """Connect and expose an Android device"""
    
    # ASCII art banner
    click.echo("""
    ╔══════════════════════════════════════╗
    ║        🌉 BridgeLink v1.0.0         ║
    ║    NativeBridge Device Connector    ║
    ╚══════════════════════════════════════╝
    """)
    
    # Validate API key
    if not api_key:
        click.echo("❌ API key not found. Please provide via --api-key or NATIVEBRIDGE_API_KEY env var")
        click.echo("Get your API key from: https://dashboard.nativebridge.io/settings/api")
        return 1
    
    # List available devices
    devices = ADBDeviceManager.list_devices()
    if not devices:
        click.echo("❌ No ADB devices found. Please connect a device via USB and ensure ADB is enabled.")
        click.echo("\nTroubleshooting:")
        click.echo("1. Enable Developer Options on your Android device")
        click.echo("2. Enable USB Debugging in Developer Options")
        click.echo("3. Connect device via USB and authorize the computer")
        click.echo("4. Run 'adb devices' to verify connection")
        return 1
    
    # Select device
    if device:
        if device not in devices:
            click.echo(f"❌ Device {device} not found")
            return 1
        selected_device = device
    else:
        selected_device = InteractiveDeviceSelector.select_device(devices)
        if not selected_device:
            return 1
    
    # Create service instance
    service = BridgeLink(api_key, tunnel)
    
    # Setup signal handlers
    def signal_handler(sig, frame):
        click.echo("\n\n🛑 Shutting down...")
        service.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Connect device
    click.echo(f"\n🔄 Connecting device {selected_device}...")
    if not service.connect_device(selected_device):
        click.echo("❌ Failed to connect device")
        return 1
    
    # Keep running
    click.echo("\n✅ Device is now accessible remotely!")
    click.echo("Press Ctrl+C to disconnect and stop the service...")
    
    try:
        while service.running:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    service.stop()
    click.echo("\n👋 Service stopped. Device disconnected from cloud.")

@cli.command()
@click.option('--api-key', '-k', 
              envvar='NATIVEBRIDGE_API_KEY',
              help='NativeBridge API key')
def status(api_key):
    """Check service status and connected devices"""
    
    if not api_key:
        click.echo("❌ API key not found")
        return 1
    
    api_client = NativeBridgeAPI(api_key)
    
    # Validate API key and get status
    user_info = api_client.validate_api_key()
    if not user_info:
        click.echo("❌ Invalid API key")
        return 1
    
    click.echo(f"✅ Authenticated as: {user_info.get('email', 'Unknown')}")
    click.echo(f"📊 Account type: {user_info.get('plan', 'Free')}")
    click.echo(f"🔧 Active devices: {user_info.get('active_devices', 0)}/{user_info.get('device_limit', 'Unlimited')}")

@cli.command()
def install():
    """Install BridgeLink as a system service"""
    
    click.echo("📦 Installing BridgeLink service...")
    
    # Check for required dependencies
    dependencies = {
        'adb': 'Android Debug Bridge (ADB)',
        'cloudflared': 'Cloudflare Tunnel client'
    }
    
    missing = []
    for cmd, name in dependencies.items():
        if subprocess.run(['which', cmd], capture_output=True).returncode != 0:
            missing.append(name)
    
    if missing:
        click.echo("❌ Missing dependencies:")
        for dep in missing:
            click.echo(f"  - {dep}")
        click.echo("\nInstallation instructions:")
        click.echo("  - ADB: https://developer.android.com/studio/command-line/adb")
        click.echo("  - Cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/")
        return 1
    
    # Create config directory
    config_dir = Path.home() / '.bridgelink'
    config_dir.mkdir(exist_ok=True)
    
    # Save configuration
    config_file = config_dir / 'config.json'
    config = {
        'version': '1.0.0',
        'installed_at': datetime.now().isoformat()
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    click.echo(f"✅ Configuration saved to: {config_file}")
    click.echo("\n📝 Setup Instructions:")
    click.echo("1. Get your API key from: https://dashboard.nativebridge.io/settings/api")
    click.echo("2. Set environment variable: export NATIVEBRIDGE_API_KEY='your-api-key'")
    click.echo("3. Connect your Android device via USB")
    click.echo("4. Run: bridgelink connect")
    
    # Offer to add to PATH
    if click.confirm("\nAdd BridgeLink to PATH?"):
        # Create symlink
        symlink_path = Path('/usr/local/bin/bridgelink')
        current_path = Path(__file__).resolve()
        
        try:
            symlink_path.symlink_to(current_path)
            click.echo(f"✅ Added to PATH: {symlink_path}")
        except:
            click.echo("⚠️  Could not add to PATH. Run with sudo or add manually.")

if __name__ == '__main__':
    cli()