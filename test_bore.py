#!/usr/bin/env python3
"""
BridgeLink with Self-Hosted bore Server - API Key Authentication
"""

import sys
import os
import time
import subprocess
import re
import socket
import threading
from main import ADBDeviceManager

class SelfHostedBoreTest:
    """Test with self-hosted bore server with API key authentication"""

    def __init__(self, api_key=None):
        # Your self-hosted bore server configuration
        # Using EC2 IP directly until DNS is configured
        self.bore_server = "bridgelink.nativebridge.io"
        self.bore_server_display = "bridgelink.nativebridge.io (3.6.53.225)"

        # Get API key from environment or parameter
        self.api_key = api_key or os.getenv('NB_API_KEY')

        if not self.api_key:
            print("❌ Error: NativeBridge API key not provided!")
            print("\nPlease provide API key via:")
            print("  1. Environment variable: export NB_API_KEY='your-api-key'")
            print("  2. Command line argument: python test_bore.py --api-key 'your-api-key'")
            print("\nGet your API key from: https://nativebridge.io/dashboard/api-keys")
            sys.exit(1)

        self.device_serial = None
        self.adb_port = None
        self.bore_process = None
        self.tunnel_url = None
        self.output_lines = []

    def print_header(self, text):
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60)

    def print_step(self, step_num, text):
        print(f"\n[STEP {step_num}] {text}")

    def find_available_port(self, start_port=5555, max_attempts=10):
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + max_attempts):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()

                if result != 0:  # Port is available
                    return port
            except:
                continue
        return None

    def select_device(self):
        """Select an Android device"""
        self.print_step(1, "Detecting Android Devices")

        devices = ADBDeviceManager.list_devices()

        if not devices:
            print("❌ No devices found!")
            return False

        print(f"✅ Found {len(devices)} device(s)")

        for idx, serial in enumerate(devices, 1):
            info = ADBDeviceManager.get_device_info(serial)
            if info:
                print(f"\n  {idx}. {info.model} ({info.manufacturer})")
                print(f"     Serial: {serial}")
                print(f"     Android: {info.android_version}")

        if len(devices) == 1:
            self.device_serial = devices[0]
            print(f"\n✅ Auto-selected: {self.device_serial}")
        else:
            while True:
                try:
                    choice = int(input("\nSelect device number: "))
                    if 1 <= choice <= len(devices):
                        self.device_serial = devices[choice - 1]
                        break
                except ValueError:
                    pass

        return True

    def setup_adb_connection(self):
        """Setup ADB connection"""
        self.print_step(2, "Setting up ADB TCP Mode")

        print(f"Enabling TCP mode on device {self.device_serial}...")

        result = subprocess.run(
            ["adb", "-s", self.device_serial, "tcpip", "5555"],
            capture_output=True,
            text=True,
            timeout=10
        )

        print(f"Output: {result.stdout.strip()}")

        if result.returncode != 0:
            print(f"❌ Failed: {result.stderr}")
            return False

        print("✅ TCP mode enabled")
        time.sleep(3)

        self.print_step(3, "Finding Available Local Port")

        self.adb_port = self.find_available_port(5555)
        if not self.adb_port:
            print("❌ No available ports")
            return False

        print(f"✅ Found available port: {self.adb_port}")

        self.print_step(4, "Setting up Port Forwarding")

        print(f"Forwarding localhost:{self.adb_port} → device:5555")

        result = subprocess.run(
            ["adb", "-s", self.device_serial, "forward", f"tcp:{self.adb_port}", "tcp:5555"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            print(f"❌ Failed")
            return False

        print("✅ Port forwarding established")
        time.sleep(2)

        self.print_step(5, "Connecting via ADB")

        result = subprocess.run(
            ["adb", "connect", f"localhost:{self.adb_port}"],
            capture_output=True,
            text=True,
            timeout=10
        )

        print(f"Output: {result.stdout.strip()}")
        print("✅ Connected")

        return True

    def read_output_thread(self, pipe, output_list):
        """Thread to read output from bore process"""
        try:
            for line in iter(pipe.readline, ''):
                if line:
                    output_list.append(line)
        except:
            pass

    def start_bore_tunnel(self):
        """Start bore tunnel with API key authentication"""
        self.print_step(6, "Starting bore Tunnel")

        print(f"Connecting to: {self.bore_server_display}")
        print(f"Local port: {self.adb_port}")
        print(f"Using API key: {self.api_key[:10]}...")
        print("")

        # Start bore with API key authentication
        self.bore_process = subprocess.Popen(
            [
                "bore",
                "local",
                str(self.adb_port),
                "--to",
                self.bore_server,
                "--api-key",
                self.api_key
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # Read output in separate threads
        stdout_lines = []
        stderr_lines = []

        stdout_thread = threading.Thread(
            target=self.read_output_thread,
            args=(self.bore_process.stdout, stdout_lines)
        )
        stderr_thread = threading.Thread(
            target=self.read_output_thread,
            args=(self.bore_process.stderr, stderr_lines)
        )

        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()

        print("⏳ Waiting for tunnel to establish...")
        print("")

        tunnel_url = None
        max_wait = 30  # 30 seconds

        for i in range(max_wait):
            # Check if process died
            if self.bore_process.poll() is not None:
                print("\n❌ bore process exited")
                print("STDOUT:", ''.join(stdout_lines))
                print("STDERR:", ''.join(stderr_lines))
                return False

            # Check all output lines (both stdout and stderr)
            all_lines = stdout_lines + stderr_lines

            for line in all_lines:
                line_stripped = line.strip()

                if line_stripped:
                    print(f"  {line_stripped}")

                    # Pattern 1: "listening at host:port"
                    match = re.search(r'listening at ([^\s]+):(\d+)', line_stripped)
                    if match:
                        host = match.group(1)
                        port = match.group(2)
                        tunnel_url = f"{host}:{port}"
                        break

                    # Pattern 2: Just the host:port
                    match = re.search(r'([0-9.]+):(\d+)', line_stripped)
                    if match and not tunnel_url:
                        host = match.group(1)
                        port = match.group(2)
                        if host == self.bore_server or host == "0.0.0.0":
                            tunnel_url = f"{self.bore_server}:{port}"

            if tunnel_url:
                print(f"\n✅ Tunnel URL found: {tunnel_url}")
                break

            time.sleep(1)

        if not tunnel_url:
            print("\n⚠️  Could not parse tunnel URL from output")
            print("\nAll output captured:")
            print("STDOUT:", ''.join(stdout_lines))
            print("STDERR:", ''.join(stderr_lines))
            print("\n💡 The tunnel might still be working!")
            print("   Check your EC2 logs for the assigned port")

            # Ask user for port
            try:
                port = input("\nEnter port from EC2 logs (or press Enter to exit): ")
                if port.strip():
                    tunnel_url = f"{self.bore_server}:{port.strip()}"
                    print(f"✅ Using manual URL: {tunnel_url}")
                else:
                    return False
            except:
                return False

        self.tunnel_url = tunnel_url
        return True

    def display_connection_info(self):
        """Display connection information"""
        self.print_step(7, "Connection Information")

        print("\n" + "━"*60)
        print("📱 DEVICE")
        print("━"*60)

        info = ADBDeviceManager.get_device_info(self.device_serial)
        if info:
            print(f"{info.model} - {info.manufacturer}")
            print(f"Android {info.android_version}")

        print("\n" + "━"*60)
        print("🌐 TUNNEL")
        print("━"*60)
        print(f"Local:  localhost:{self.adb_port}")
        print(f"Remote: {self.tunnel_url}")
        print(f"Server: {self.bore_server_display}")

        print("\n" + "━"*60)
        print("🔗 CONNECT FROM ANYWHERE")
        print("━"*60)
        print(f"\n  adb connect {self.tunnel_url}")
        print(f"  adb shell")

    def test_connection(self):
        """Test the connection"""
        self.print_step(8, "Testing Connection")

        time.sleep(2)

        try:
            result = subprocess.run(
                ["adb", "connect", self.tunnel_url],
                capture_output=True,
                text=True,
                timeout=15
            )

            print(f"Output: {result.stdout.strip()}")

            if "connected" in result.stdout.lower():
                print("✅ Connection successful!")

                result = subprocess.run(
                    ["adb", "-s", self.tunnel_url, "shell", "echo", "test"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    print("✅ Device responds!")
                    print("\n🎉 TUNNEL IS WORKING!")
                    return True

            print("⚠️  Try manually: adb connect " + self.tunnel_url)
            return False

        except Exception as e:
            print(f"Error: {e}")
            return False

    def keep_alive(self):
        """Keep tunnel alive"""
        print("\n" + "="*60)
        print("  ✅ TUNNEL ACTIVE")
        print("="*60)
        print(f"\n🌐 URL: {self.tunnel_url}")
        print("\nPress Ctrl+C to stop...")
        print("")

        try:
            while True:
                if self.bore_process.poll() is not None:
                    print("\n⚠️  bore exited")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping...")

    def cleanup(self):
        """Cleanup"""
        print("\n[CLEANUP]")

        if self.bore_process:
            print("  Stopping tunnel...")
            self.bore_process.terminate()
            try:
                self.bore_process.wait(timeout=5)
            except:
                self.bore_process.kill()

        if self.adb_port:
            subprocess.run(["adb", "disconnect", f"localhost:{self.adb_port}"],
                         capture_output=True)

        subprocess.run(["adb", "forward", "--remove-all"], capture_output=True)

        if self.device_serial:
            subprocess.run(["adb", "-s", self.device_serial, "usb"],
                         capture_output=True)

        print("✅ Done")

    def run(self):
        """Run test"""
        print("\n" + "🌉 BridgeLink Test".center(60, "="))
        print(f"Server: {self.bore_server_display}")
        print("="*60)

        try:
            if not self.select_device():
                return 1
            if not self.setup_adb_connection():
                return 1
            if not self.start_bore_tunnel():
                return 1

            self.display_connection_info()

            test = input("\n\nTest connection? (y/n): ")
            if test.lower() == 'y':
                self.test_connection()

            self.keep_alive()
            return 0

        except KeyboardInterrupt:
            return 0
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return 1
        finally:
            self.cleanup()

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='BridgeLink - Expose Android devices with NativeBridge',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using environment variable
  export NB_API_KEY='Nb-kNGB.xxx-xxx-xxx'
  python test_bore.py

  # Using command line argument
  python test_bore.py --api-key 'Nb-kNGB.xxx-xxx-xxx'

Get your API key from: https://nativebridge.io/dashboard/api-keys
        """
    )

    parser.add_argument(
        '--api-key',
        type=str,
        help='NativeBridge API key (or set NB_API_KEY environment variable)'
    )

    args = parser.parse_args()

    tester = SelfHostedBoreTest(api_key=args.api_key)
    return tester.run()

if __name__ == '__main__':
    sys.exit(main())
