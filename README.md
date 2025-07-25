# 🎮 Auto-Stream v2.0

**Simple CLI tool to automatically stream games to YouTube when you start playing.**

Clean, modular architecture with `.env` configuration. No complex JSON files, no GUI - just simple environment variables and CLI commands.

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

# Override settings
python main.py --game "myGame.exe" --key "your-stream-key"
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

## 🧪 Testing

```bash
# Test YouTube streaming
python tests/test_youtube.py
```

This will:
- Load your `.env` configuration
- Start monitoring for 30 seconds
- Show if streaming works
- Display any errors

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

## 🛠️ Troubleshooting

### Game Not Detected
```bash
# Check exact process name
ps aux | grep your-game

# Update .env with exact name
GAME_EXECUTABLE=exact-process-name
```

### Stream Not Starting
- Verify YouTube stream key is correct
- Check FFmpeg is installed: `ffmpeg -version`
- Test with: `python main.py --test`

### No Video (Audio Only)
- **Linux Wayland**: Switch to X11 session
- **Permissions**: Grant screen sharing permissions
- **Mixed Environment**: System should auto-detect

---

## 📁 Project Structure

```
auto-stream/
├── src/
│   ├── config.py          # Environment configuration
│   ├── stream_service.py  # Main streaming logic
│   ├── game_detector.py   # Process monitoring
│   ├── ffmpeg_manager.py  # FFmpeg integration
│   └── discord_notifier.py# Discord bot
├── tests/
│   └── test_youtube.py    # YouTube streaming test
├── .env.example           # Configuration template
├── main.py               # CLI entry point
└── requirements.txt      # Dependencies
```

---

## 🔄 What's New in v2.0

- **Simplified Architecture** – Clean, modular design
- **Environment Config** – No more complex JSON files
- **CLI Interface** – Simple command-line usage
- **Better Error Handling** – Clear error messages
- **Cross-Platform** – Windows and Linux support
- **Auto-Detection** – Smart display server detection

---

## 📜 License

MIT License - Feel free to modify and distribute!

---

**Happy Streaming! 🎮✨**

