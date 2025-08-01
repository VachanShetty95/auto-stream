# 🎮 Auto-Stream

**Simple CLI tool to automatically stream games to YouTube when you start playing.**


## ✨ Features

- 🎯 **Simple Game Detection** – Monitors for specified game executable
- 📺 **YouTube Streaming** – Direct streaming to YouTube Live
- 🤖 **Discord Notifications** – Optional Discord bot integration
- 🔧 **Environment Config** – Simple `.env` file configuration
- 🖥️ **Cross-Platform** – Works on Windows and Linux
- ⚡ **Lightweight** – Minimal dependencies, clean code

---

## 🚀 Quick Start

### 1. Clone and Install
```bash
git clone https://github.com/VachanShetty95/auto-stream.git
cd auto-stream
pip install -r requirements.txt
```

### 2. Configure
```bash
# Copy example configuration
cp .env.example .env

# Edit with your settings
nano .env
```

### 3. Run
```bash
# Start monitoring
python main.py

# Test mode (30 seconds)
python main.py --test

```

---

## ⚙️ Configuration

Edit `.env` with your settings:

```bash
# Required
YOUTUBE_STREAM_KEY=your-youtube-stream-key-here
GAME_EXECUTABLE=your-game.exe

# Optional
YOUTUBE_STREAM_URL=rtmp://a.rtmp.youtube.com/live2
CHECK_INTERVAL=10
STREAM_QUALITY=720p
STREAM_FRAMERATE=30
STREAM_BITRATE=3000k

# Discord (optional)
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_CHANNEL_ID=123456789012345678
DISCORD_MESSAGE=🎮 {game_name} stream is now live!

# System
FFMPEG_PATH=
AUTO_START=true
```
---

## 🎮 How It Works

1. **Monitors** for your specified game executable
2. **Detects** when the game starts running
3. **Captures** your screen using FFmpeg
4. **Streams** directly to YouTube Live
5. **Notifies** Discord (if configured)
6. **Stops** when game closes

---

## 🔧 Platform Notes

### Windows
- Uses `gdigrab` for screen capture
- FFmpeg auto-download available
- Supports window-specific capture

### Linux
- **X11**: Uses `x11grab` for screen capture
- **Wayland**: Limited screen capture (test patterns)
- Install FFmpeg: `sudo apt install ffmpeg`

### Mixed Environments
Auto-detects if you have both Wayland and X11 available and uses the best option.

---

## 📋 Requirements

- Python 3.8+
- FFmpeg (auto-installed on Windows)
- YouTube channel with streaming enabled
- Valid YouTube stream key

---

## 📜 License

MIT License - Feel free to modify and distribute!

---

**Happy Streaming! 🎮✨**

