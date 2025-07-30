#!/usr/bin/env python3
"""
Debug script to test streaming components individually.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import EnvConfig
from src.ffmpeg_manager import FFmpegManager


def test_ffmpeg_installation():
    """Test if FFmpeg is installed and working."""
    print("🔧 Testing FFmpeg Installation...")

    # Test system FFmpeg first
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print("✅ System FFmpeg found")
            print(f"   Version: {result.stdout.split()[2]}")
            return True
    except:
        pass

    # Test bundled FFmpeg
    ffmpeg_manager = FFmpegManager()
    if ffmpeg_manager.is_installed():
        print("✅ Bundled FFmpeg found")
        return True

    print("❌ FFmpeg not found!")
    print("💡 Install FFmpeg:")
    if platform.system() == "Windows":
        print("   - Download from https://ffmpeg.org/download.html")
        print("   - Add to PATH")
    else:
        print("   - sudo apt install ffmpeg  # Ubuntu/Debian")
        print("   - sudo pacman -S ffmpeg   # Arch")
        print("   - brew install ffmpeg     # macOS")

    return False


def test_screen_capture():
    """Test screen capture capabilities."""
    print("\n📺 Testing Screen Capture...")

    system = platform.system()
    print(f"   Platform: {system}")

    if system == "Linux":
        session = os.environ.get("XDG_SESSION_TYPE", "unknown")
        display = os.environ.get("DISPLAY", "none")
        print(f"   Session: {session}")
        print(f"   Display: {display}")

        if session == "wayland" and not display:
            print("⚠️  Wayland without X11 - screen capture will be limited")
            print("💡 Consider using X11 session for better compatibility")
        elif session == "wayland" and display:
            print("🔄 Mixed environment - will try X11 capture")
        else:
            print("✅ X11 environment - screen capture should work")

    # Test basic FFmpeg screen capture
    try:
        if system == "Windows":
            test_cmd = [
                "ffmpeg",
                "-f",
                "gdigrab",
                "-t",
                "1",
                "-i",
                "desktop",
                "-f",
                "null",
                "-",
            ]
        else:
            display = os.environ.get("DISPLAY", ":0.0")
            test_cmd = [
                "ffmpeg",
                "-f",
                "x11grab",
                "-t",
                "1",
                "-i",
                display,
                "-f",
                "null",
                "-",
            ]

        print(f"   Testing: {' '.join(test_cmd[:6])}...")
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✅ Screen capture test passed")
            return True
        else:
            print("❌ Screen capture test failed")
            print(f"   Error: {result.stderr[:200]}...")
            return False

    except Exception as e:
        print(f"❌ Screen capture test error: {e}")
        return False


def test_youtube_connection():
    """Test YouTube RTMP connection."""
    print("\n📡 Testing YouTube Connection...")

    # Load config
    if not Path(".env").exists():
        print("❌ No .env file found!")
        print("💡 Copy .env.example to .env and configure it")
        return False

    config = EnvConfig()
    errors = config.validate()
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   • {error}")
        return False

    print(f"   Stream URL: {config.youtube_stream_url}")
    print(f"   Stream Key: {config.youtube_stream_key[:8]}...")

    # Test RTMP connection with test pattern
    try:
        test_cmd = [
            "ffmpeg",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=640x480:rate=1",  # Very low settings for test
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=1000:sample_rate=48000",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-tune",
            "zerolatency",
            "-pix_fmt",
            "yuv420p",
            "-s",
            "640x480",
            "-r",
            "1",
            "-c:a",
            "aac",
            "-b:a",
            "64k",
            "-t",
            "3",  # Only 3 seconds
            "-f",
            "flv",
            f"{config.youtube_stream_url}/{config.youtube_stream_key}",
        ]

        print("   Testing RTMP connection (3 seconds)...")
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            print("✅ YouTube RTMP connection successful")
            return True
        else:
            print("❌ YouTube RTMP connection failed")
            print(f"   Error: {result.stderr[-300:]}")  # Last 300 chars of error

            # Check for common errors
            error_text = result.stderr.lower()
            if "connection refused" in error_text:
                print("💡 Connection refused - check your stream key")
            elif "authentication failed" in error_text:
                print("💡 Authentication failed - verify your stream key")
            elif "not found" in error_text:
                print(
                    "💡 Stream not found - make sure streaming is enabled on your YouTube channel"
                )

            return False

    except Exception as e:
        print(f"❌ RTMP test error: {e}")
        return False


def test_full_stream_command():
    """Test the full streaming command."""
    print("\n🎮 Testing Full Stream Command...")

    config = EnvConfig()
    ffmpeg_manager = FFmpegManager()

    # Generate the actual stream command
    try:
        stream_cmd = ffmpeg_manager.generate_stream_command(
            stream_url=config.youtube_stream_url,
            stream_key=config.youtube_stream_key,
            game_title=None,  # Full desktop capture
            quality=config.stream_quality,
            framerate=config.stream_framerate,
            bitrate=config.stream_bitrate,
        )

        print("   Generated command:")
        print(f"   {' '.join(stream_cmd[:10])}... (truncated)")

        # Test command for 5 seconds
        print("   Testing full stream (5 seconds)...")
        test_cmd = stream_cmd[:-1] + ["-t", "5"] + [stream_cmd[-1]]

        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            print("✅ Full stream test successful!")
            print("🎉 Your streaming setup should work!")
            return True
        else:
            print("❌ Full stream test failed")
            print(f"   Error: {result.stderr[-500:]}")
            return False

    except Exception as e:
        print(f"❌ Full stream test error: {e}")
        return False


def main():
    """Run all diagnostic tests."""
    print("🔍 Auto-Stream Diagnostic Tool")
    print("=" * 40)

    # Load environment
    from dotenv import load_dotenv

    if Path(".env").exists():
        load_dotenv(".env")
        print("✅ Loaded .env configuration")
    else:
        print("⚠️  No .env file found - using defaults")

    print()

    # Run tests
    tests = [
        ("FFmpeg Installation", test_ffmpeg_installation),
        ("Screen Capture", test_screen_capture),
        ("YouTube Connection", test_youtube_connection),
        ("Full Stream Test", test_full_stream_command),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print("\n🛑 Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 40)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 40)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    passed = sum(results.values())
    total = len(results)

    print(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed - streaming should work!")
    else:
        print("🔧 Fix the failing tests above to enable streaming")


if __name__ == "__main__":
    main()
