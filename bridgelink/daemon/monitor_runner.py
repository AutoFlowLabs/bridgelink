"""
Monitor Runner - Background process that monitors device health
This runs as a separate background process
"""

import sys
import os
import signal
import argparse
from pathlib import Path

# Ensure bridgelink module is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bridgelink.daemon.device_health_monitor import DeviceHealthMonitor


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\nReceived shutdown signal, stopping monitor...")
    sys.exit(0)


def main():
    """Main entry point for monitor daemon"""
    parser = argparse.ArgumentParser(description='BridgeLink Health Monitor Daemon')
    parser.add_argument('--api-key', required=True, help='NativeBridge API key')
    parser.add_argument('--interval', type=int, default=5, help='Poll interval in seconds')
    args = parser.parse_args()

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Create and start monitor
    try:
        monitor = DeviceHealthMonitor(poll_interval=args.interval, api_key=args.api_key)
        print(f"Starting health monitor (interval: {args.interval}s)")
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nMonitor stopped")
    except Exception as e:
        print(f"Monitor error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
