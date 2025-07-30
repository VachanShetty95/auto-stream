#!/usr/bin/env python3
"""
Simple YouTube streaming test using .env configuration.
"""

import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.config import EnvConfig
from src.stream_service import StreamService


def main():
    """Test YouTube streaming with .env configuration."""
    print("🧪 YouTube Streaming Test")
    print("=" * 30)
    print("This test uses your .env configuration")
    print()

    # Load environment variables
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print("❌ No .env file found!")
        print("📝 Create .env file with your YouTube stream key")
        return 1

    load_dotenv(env_path)

    try:
        # Create configuration
        config = EnvConfig()

        # Validate
        errors = config.validate()
        if errors:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"   • {error}")
            return 1

        print("✅ Configuration valid")
        print(f"🎮 Game: {config.game_executable}")
        print(f"🔑 Stream key: {config.youtube_stream_key[:8]}...")
        print(f"🎥 Quality: {config.stream_quality}")

        # Initialize service
        service = StreamService(config)

        print("\n🚀 Starting test (30 seconds)...")
        service.start_service()

        if not service.is_running:
            print("❌ Service failed to start")
            return 1

        print("✅ Service started")
        print(f"🔍 Monitoring for '{config.game_executable}'")
        print("📺 Check YouTube Studio: https://studio.youtube.com/")
        print("💡 Start your game to begin streaming!")

        # Run for 30 seconds
        for i in range(30):
            print(f"   {30 - i}s remaining...")
            time.sleep(1)

        print("\n🛑 Stopping test...")
        service.stop_service()
        print("✅ Test completed!")

        if service.current_stream:
            print("🎉 Stream was active during test!")
        else:
            print("💡 No stream detected - make sure your game is running")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
