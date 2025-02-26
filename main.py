import os
import subprocess
import sys
import time

import psutil

STREAM_KEY = os.getenv("YOUTUBE_STREAM_KEY")
STREAM_URL = os.getenv("YOUTUBE_STREAM_URL")
GAME_EXECUTABLE = os.getenv("GAME_EXECUTABLE_PATH")


if not all([STREAM_KEY, STREAM_URL, GAME_EXECUTABLE]):
    print(
        "Error: Missing environment variables. Please set YOUTUBE_STREAM_KEY, YOUTUBE_STREAM_URL, and GAME_EXECUTABLE_PATH."
    )
    sys.exit(1)


FFMPEG_PATH = os.path.join(os.path.dirname(__file__), "ffmpeg", "ffmpeg.exe")

if not os.path.exists(FFMPEG_PATH):
    print(
        f"Error: FFmpeg not found at {FFMPEG_PATH}. Ensure ffmpeg.exe is in the correct directory."
    )
    sys.exit(1)


FFMPEG_COMMAND = [
    FFMPEG_PATH,
    "-f",
    "gdigrab",
    "-framerate",
    "30",
    "-i",
    f"title={GAME_EXECUTABLE}",
    "-c:v",
    "libx264",
    "-preset",
    "veryfast",
    "-maxrate",
    "3000k",
    "-bufsize",
    "6000k",
    "-pix_fmt",
    "yuv420p",
    "-f",
    "flv",
    f"{STREAM_URL}/{STREAM_KEY}",
]


def is_game_running(executable_name):
    try:
        for proc in psutil.process_iter(["name"]):
            if (
                proc.info["name"]
                and executable_name.lower() in proc.info["name"].lower()
            ):
                return True
    except Exception as e:
        print(f"Error checking game process: {e}")
    return False


def start_stream():
    try:
        print("Starting stream...")
        return subprocess.Popen(
            FFMPEG_COMMAND,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
        )
    except Exception as e:
        print(f"Error starting stream: {e}")
        return None


def main():
    print("Starting stream monitor...")
    streaming_process = None
    try:
        while True:
            if is_game_running(GAME_EXECUTABLE):
                if streaming_process is None:
                    streaming_process = start_stream()
            else:
                if streaming_process:
                    print("Stopping stream...")
                    streaming_process.terminate()
                    streaming_process.wait()
                    streaming_process = None
            time.sleep(10)
    except KeyboardInterrupt:
        print("Exiting...")
        if streaming_process:
            streaming_process.terminate()
            streaming_process.wait()


if __name__ == "__main__":
    main()
