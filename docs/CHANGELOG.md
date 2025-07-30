# Changelog

## [2.0.0] - 2024-01-XX

### 🎉 Complete Rewrite
This is a complete rewrite of Auto-Stream with a modular architecture and many new features.

### ✨ New Features
- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **JSON Configuration**: Easy-to-edit configuration file instead of environment variables
- **Automatic FFmpeg Download**: Downloads FFmpeg automatically on Windows
- **Cross-Platform Support**: Works on both Windows and Linux
- **Rich Discord Integration**: Discord bot with rich embeds and notifications
- **Multiple Streaming Platforms**: Support for YouTube Live and Twitch
- **Quality Options**: Configurable streaming quality (480p, 720p, 1080p)
- **Window Capture**: Capture specific game windows on Windows
- **Portable Builds**: Self-contained executable with build system
- **Better Error Handling**: Comprehensive error handling and user feedback
- **Configuration Validation**: Validates settings before starting
- **Stream Duration Tracking**: Tracks and reports stream duration
- **Test Mode**: Test streaming setup without full stream

### 🔧 Technical Improvements
- **Type Hints**: Full type annotation for better code quality
- **Async Discord Integration**: Proper async Discord bot implementation
- **Threading**: Background monitoring with proper threading
- **Process Management**: Better FFmpeg process management
- **Configuration System**: Robust configuration with defaults and validation
- **Logging**: Better error reporting and status messages
- **Build System**: PyInstaller integration for executable builds

### 📦 New Components
- `src/config.py` - Configuration management system
- `src/game_detector.py` - Game detection and monitoring
- `src/ffmpeg_manager.py` - FFmpeg download and command generation
- `src/discord_notifier.py` - Discord bot integration
- `src/stream_service.py` - Main streaming orchestration
- `build.py` - Build system for creating executables
- `setup.py` - Python package setup

### 🗑️ Removed
- Environment variable configuration (replaced with JSON)
- Hardcoded FFmpeg paths (now auto-detected/downloaded)
- Simple process monitoring (replaced with rich callback system)

### 📋 Dependencies
- `psutil>=5.9.0` - Process monitoring
- `requests>=2.28.0` - HTTP requests for FFmpeg download
- `discord.py>=2.3.0` - Discord bot integration
- `pywin32>=306` - Windows-specific features (Windows only)

### 🔄 Migration from v1.x
1. Remove old `.env` file
2. Run the new version to generate `config.json`
3. Edit `config.json` with your settings
4. Game executables are now in a list format
5. Discord uses bot tokens instead of webhooks

---

## [1.0.0] - Previous Version

### Features
- Basic game detection using environment variables
- YouTube streaming with FFmpeg
- Simple Discord webhook notifications
- Windows-only support
- Manual FFmpeg installation required 