"""
Simple configuration management using environment variables.
"""

import os
from typing import List


class EnvConfig:
    """Simple configuration from environment variables."""
    
    def __init__(self):
        # YouTube streaming
        self.youtube_stream_key = os.getenv('YOUTUBE_STREAM_KEY', '')
        self.youtube_stream_url = os.getenv('YOUTUBE_STREAM_URL', 'rtmp://a.rtmp.youtube.com/live2')
        
        # Game detection (optional - can be empty for desktop-only streaming)
        self.game_executable = os.getenv('GAME_EXECUTABLE', '')
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '10'))
        
        # Stream quality
        self.stream_quality = os.getenv('STREAM_QUALITY', '720p')
        self.stream_framerate = int(os.getenv('STREAM_FRAMERATE', '30'))
        self.stream_bitrate = os.getenv('STREAM_BITRATE', '3000k')
        
        # Discord (optional)
        self.discord_bot_token = os.getenv('DISCORD_BOT_TOKEN', '')
        self.discord_channel_id = os.getenv('DISCORD_CHANNEL_ID', '')
        self.discord_message = os.getenv('DISCORD_MESSAGE', '{game_name} stream is now live!')
        
        # System
        self.ffmpeg_path = os.getenv('FFMPEG_PATH', '')
        self.auto_start = os.getenv('AUTO_START', 'true').lower() == 'true'
        
        # Audio device (Windows only)
        self.audio_device = os.getenv('AUDIO_DEVICE', 'Stereo Mix (Realtek(R) Audio)')
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.youtube_stream_key.strip():
            errors.append("YOUTUBE_STREAM_KEY is required")
        
        if not self.youtube_stream_url.strip():
            errors.append("YOUTUBE_STREAM_URL is required")
        
        # GAME_EXECUTABLE is now optional - can be empty for desktop-only streaming
        # if not self.game_executable.strip():
        #     errors.append("GAME_EXECUTABLE is required")
        
        if self.check_interval < 1:
            errors.append("CHECK_INTERVAL must be at least 1 second")
        
        if self.stream_quality not in ['480p', '720p', '1080p']:
            errors.append("STREAM_QUALITY must be 480p, 720p, or 1080p")
        
        if self.stream_framerate < 1 or self.stream_framerate > 60:
            errors.append("STREAM_FRAMERATE must be between 1 and 60")
        
        return errors
    
    def get_quality_settings(self):
        """Get quality settings for the configured quality."""
        quality_settings = {
            "480p": {"width": 854, "height": 480, "bitrate": "1500k"},
            "720p": {"width": 1280, "height": 720, "bitrate": "3000k"},
            "1080p": {"width": 1920, "height": 1080, "bitrate": "6000k"}
        }
        
        settings = quality_settings.get(self.stream_quality, quality_settings["720p"])
        
        # Override bitrate if custom one is provided
        if self.stream_bitrate != "3000k":
            settings["bitrate"] = self.stream_bitrate
        
        return settings


# Keep the old classes for backward compatibility but mark as deprecated
class ConfigManager:
    """Deprecated: Use EnvConfig instead."""
    
    def __init__(self, config_path=None):
        print("⚠️  ConfigManager is deprecated. Use EnvConfig instead.")
        self.config = EnvConfig()
    
    def validate(self):
        return self.config.validate()


# For backward compatibility
class AppConfig:
    """Deprecated: Use EnvConfig instead."""
    pass


class StreamConfig:
    """Deprecated: Use EnvConfig instead.""" 
    pass


class DiscordConfig:
    """Deprecated: Use EnvConfig instead."""
    pass


class GameConfig:
    """Deprecated: Use EnvConfig instead."""
    pass 