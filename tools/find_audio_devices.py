#!/usr/bin/env python3
"""
Utility to find available audio devices on Windows.
Helps users configure the correct AUDIO_DEVICE in their .env file.
"""

import platform
import subprocess
import sys


def find_audio_devices():
    """Find available audio devices using FFmpeg."""
    if platform.system() != "Windows":
        print("This utility is for Windows only.")
        return

    print("Finding available audio devices on Windows...")
    print("=" * 50)

    try:
        # Use FFmpeg to list audio devices
        cmd = ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"]

        print("Running: ffmpeg -list_devices true -f dshow -i dummy")
        print()

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("Available audio devices:")
            print("-" * 30)

            # Parse the output to find audio devices
            lines = result.stderr.split("\n")
            in_audio_section = False
            found_devices = []

            for line in lines:
                if "DirectShow audio devices" in line:
                    in_audio_section = True
                    print("📻 Audio Devices:")
                    continue
                elif "DirectShow video devices" in line:
                    in_audio_section = False
                    continue

                if in_audio_section and '"' in line:
                    # Extract device name
                    start = line.find('"') + 1
                    end = line.find('"', start)
                    if start > 0 and end > start:
                        device_name = line[start:end]
                        found_devices.append(device_name)
                        print(f"  • {device_name}")

            if not found_devices:
                print("  ❌ No audio devices found!")
                print()
                print("🔧 Troubleshooting:")
                print("  1. Check if Stereo Mix is enabled:")
                print("     - Right-click speaker icon → Open Sound settings")
                print("     - Click 'Sound Control Panel'")
                print("     - Go to 'Recording' tab")
                print("     - Right-click empty space → 'Show Disabled Devices'")
                print("     - Right-click 'Stereo Mix' → 'Enable'")
                print()
                print("  2. Try enabling other audio devices:")
                print("     - Look for 'Microphone', 'Speakers', etc.")
                print("     - Right-click → 'Enable'")
                print()
                print("  3. If no devices work, the app will stream without audio")
            else:
                print()
                print("💡 To use a device, add it to your .env file:")
                print('   AUDIO_DEVICE="Your Device Name Here"')
                print()
                print("🔍 Common audio devices (if not found above):")
                print("   • Stereo Mix (Realtek(R) Audio)")
                print("   • Microphone (Realtek(R) Audio)")
                print("   • Speakers (Realtek(R) Audio)")
                print("   • What U Hear (Creative)")
                print("   • Stereo Mix")

        else:
            print("❌ Failed to list audio devices")
            print(f"Error: {result.stderr}")

    except FileNotFoundError:
        print("❌ FFmpeg not found. Please install FFmpeg first.")
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_audio_device(device_name):
    """Test if a specific audio device works."""
    if platform.system() != "Windows":
        print("This utility is for Windows only.")
        return

    print(f"Testing audio device: {device_name}")
    print("=" * 40)

    try:
        # Test the audio device with a short duration
        cmd = [
            "ffmpeg",
            "-f",
            "dshow",
            "-i",
            f'audio="{device_name}"',
            "-t",
            "3",  # 3 seconds
            "-f",
            "null",
            "-",
        ]

        print(f"Running: {' '.join(cmd)}")
        print()

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✅ Audio device works!")
            print("You can use this device in your .env file:")
            print(f'AUDIO_DEVICE="{device_name}"')
        else:
            print("❌ Audio device failed")
            print(f"Error: {result.stderr}")

    except Exception as e:
        print(f"❌ Error testing device: {e}")


def main():
    """Main function."""
    if len(sys.argv) > 1:
        # Test specific device
        device_name = sys.argv[1]
        test_audio_device(device_name)
    else:
        # List all devices
        find_audio_devices()


if __name__ == "__main__":
    main()
