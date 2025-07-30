#!/usr/bin/env python3
"""
Auto-Stream: Automatic game streaming to YouTube.
Simple CLI version that uses .env configuration.
"""

import argparse
import os
import signal
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import EnvConfig
from src.logger import AutoStreamLogger
from src.stream_service import StreamService


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\nShutting down Auto-Stream...")
    if "service" in globals():
        service.logger.info("Received shutdown signal, stopping service")
        service.stop_service()
    sys.exit(0)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Auto-Stream: Automatic game streaming"
    )
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    parser.add_argument("--game", type=str, help="Override game executable name")
    parser.add_argument("--key", type=str, help="Override YouTube stream key")
    args = parser.parse_args()

    # Load environment variables first
    env_path = Path(".env")
    if not env_path.exists():
        print("No .env file found!")
        print("Copy .env.example to .env and configure your settings")
        return 1

    load_dotenv(env_path)

    # Create configuration from environment
    config = EnvConfig()

    # Initialize logger with config
    logger = AutoStreamLogger(config=config)

    print("Auto-Stream v2.0 - CLI Edition")
    print("=" * 40)

    logger.info("Loaded .env configuration")

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Apply CLI overrides
        if args.game:
            config.game_executable = args.game
            logger.info(f"CLI override: Game = {args.game}")
            print(f"Override: Game = {args.game}")

        if args.key:
            config.youtube_stream_key = args.key
            logger.info(f"CLI override: Stream key = {args.key[:8]}...")
            print(f"Override: Stream key = {args.key[:8]}...")

        # Validate configuration
        errors = config.validate()
        if errors:
            logger.error(f"Configuration errors: {errors}")
            print("Configuration errors:")
            for error in errors:
                print(f"   • {error}")
            return 1

        logger.info("Configuration loaded successfully")
        print("Configuration loaded successfully")

        # Show configuration details
        if config.game_executable.strip():
            print(f"Game: {config.game_executable}")
        else:
            print("Game: Desktop-only mode (no game executable configured)")

        print(f"Platform: YouTube")
        print(f"Quality: {config.stream_quality}")

        # Initialize and start service
        global service
        service = StreamService(config)

        if args.test:
            logger.info("Running in test mode (30 seconds)")
            print("\nRunning in test mode (30 seconds)...")
            service.start_service()

            if service.is_running:
                logger.info("Test mode: Service started successfully")
                print("Service started - monitoring for 30 seconds...")
                time.sleep(30)
                service.stop_service()
                logger.info("Test mode: Test completed successfully")
                print("Test completed!")
            else:
                logger.error("Test mode: Service failed to start")
                print("Service failed to start")
                return 1
        else:
            logger.info("Starting Auto-Stream service in normal mode")
            print("\nStarting Auto-Stream service...")
            service.start_service()

            if not service.is_running:
                logger.error("Failed to start service")
                print("Failed to start service")
                return 1

            logger.info("Service running successfully")
            print("Service running! Press Ctrl+C to stop.")

            if config.game_executable.strip():
                print(
                    f"Monitoring for '{config.game_executable}' every {config.check_interval}s"
                )
            else:
                print("Desktop streaming active - no game monitoring")

            # Keep running until interrupted
            try:
                while service.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

        return 0

    except Exception as e:
        logger.log_error(e, "main")
        print(f"Error: {e}")
        return 1

    finally:
        if "service" in locals():
            service.stop_service()


if __name__ == "__main__":
    sys.exit(main())
