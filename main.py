import os
import subprocess
import time
import psutil

STREAM_KEY = os.getenv('YOUTUBE_STREAM_KEY')
STREAM_URL = os.getenv('YOUTUBE_STREAM_URL')
GAME_EXECUTABLE = os.getenv('GAME_EXECUTABLE_PATH') 

# Define FFmpeg command,Capture game window (Windows-specific)
FFMPEG_COMMAND = (
    f"ffmpeg -f gdigrab -framerate 30 -i title='{GAME_EXECUTABLE}' "  
    "-c:v libx264 -preset veryfast -maxrate 3000k -bufsize 6000k -pix_fmt yuv420p "
    f"-f flv {STREAM_URL}/{STREAM_KEY}"
)

# Function to check if the game is running
def is_game_running(executable_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and executable_name.lower() in proc.info['name'].lower():
            return True
    return False

# Function to start streaming
def start_stream():
    print("Starting stream...")
    return subprocess.Popen(FFMPEG_COMMAND, shell=True)


def main():
    print("Starting stream monitor...")
    streaming_process = None
    while True:
        if is_game_running(GAME_EXECUTABLE):
            if streaming_process is None:
                streaming_process = start_stream()
        else:
            if streaming_process:
                print("Stopping stream...")
                streaming_process.terminate()
                streaming_process = None
        time.sleep(10) 

if __name__ == "__main__":
    main()
