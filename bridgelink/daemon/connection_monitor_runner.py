"""
Connection Monitor Runner
Entry point for running the connection monitor as a background daemon
"""

import sys
import signal
import argparse
from bridgelink.daemon.connection_monitor import DeviceConnectionMonitor


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n\nReceived shutdown signal, stopping...")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description='BridgeLink Connection Monitor Daemon')
    parser.add_argument('--api-key', required=True, help='NativeBridge API key')
    parser.add_argument('--interval', type=int, default=5, help='Poll interval in seconds')

    args = parser.parse_args()

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Create and start monitor
    monitor = DeviceConnectionMonitor(
        poll_interval=args.interval,
        api_key=args.api_key
    )

    monitor.start_monitoring()


if __name__ == '__main__':
    main()
