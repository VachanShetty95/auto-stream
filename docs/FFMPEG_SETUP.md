# FFmpeg Setup Guide

## Automatic Installation

The auto-stream application automatically handles FFmpeg installation:

### Windows
- Automatically downloads and installs FFmpeg if not found
- Uses system FFmpeg if available in PATH
- Falls back to local installation in the project directory

### Linux
- Uses system package manager (apt, dnf, pacman)
- Provides installation instructions if not found
- No automatic download (security best practice)

## Manual Installation (if needed)

### Windows
1. Download from [FFmpeg official site](https://ffmpeg.org/download.html)
2. Extract and add to PATH, or
3. Set `FFMPEG_PATH` in your `.env` file

### Linux
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

## Verification

Test FFmpeg installation:
```bash
ffmpeg -version
```

The application will automatically detect and use the installed FFmpeg.
