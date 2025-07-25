"""
Simplified streaming service for auto-stream.
"""

import subprocess
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from .game_detector import GameDetector
from .ffmpeg_manager import FFmpegManager
from .discord_notifier import DiscordNotifier


class StreamService:
    """Simple streaming service."""
    
    def __init__(self, config):
        self.config = config
        
        # Initialize components
        self.game_detector = GameDetector([config.game_executable], config.check_interval)
        self.ffmpeg_manager = FFmpegManager()
        
        # Discord notifier (optional)
        self.discord_notifier = None
        if config.discord_bot_token and config.discord_channel_id:
            self.discord_notifier = DiscordNotifier(
                config.discord_bot_token,
                config.discord_channel_id,
                ""  # guild_id not needed
            )
        
        # Streaming state
        self.current_stream = None
        self.is_running = False
        
        # Setup callbacks
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Set up callbacks for game events."""
        self.game_detector.add_callback('game_started', self._on_game_started)
        self.game_detector.add_callback('game_stopped', self._on_game_stopped)
    
    def _on_game_started(self, game_name: str, game_info: Dict):
        """Handle game started event."""
        print(f"🎮 Game detected: {game_name}")
        
        if not self.config.auto_start:
            print("Auto-start disabled")
            return
        
        if self.current_stream:
            print(f"Already streaming")
            return
        
        # Start streaming
        success = self.start_stream(game_name)
        if success:
            print(f"✅ Started streaming {game_name}")
        else:
            print(f"❌ Failed to start stream")
    
    def _on_game_stopped(self, game_name: str):
        """Handle game stopped event."""
        print(f"🛑 Game stopped: {game_name}")
        
        if self.current_stream:
            self.stop_stream()
    
    def start_stream(self, game_name: str) -> bool:
        """Start streaming."""
        try:
            # Get quality settings
            quality_settings = self.config.get_quality_settings()
            
            # Generate FFmpeg command
            stream_cmd = self.ffmpeg_manager.generate_stream_command(
                stream_url=self.config.youtube_stream_url,
                stream_key=self.config.youtube_stream_key,
                game_title=game_name,
                quality=self.config.stream_quality,
                framerate=self.config.stream_framerate,
                bitrate=self.config.stream_bitrate
            )
            
            print(f"📡 Starting stream...")
            
            # Start FFmpeg process
            process = subprocess.Popen(
                stream_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Store stream info
            self.current_stream = {
                'process': process,
                'start_time': datetime.now(),
                'game_name': game_name
            }
            
            # Send Discord notification
            if self.discord_notifier:
                self.discord_notifier.notify_stream_started(
                    game_name=game_name,
                    custom_message=self.config.discord_message
                )
            
            return True
            
        except Exception as e:
            print(f"❌ Stream error: {e}")
            return False
    
    def stop_stream(self) -> bool:
        """Stop streaming."""
        if not self.current_stream:
            return False
        
        try:
            process = self.current_stream['process']
            start_time = self.current_stream['start_time']
            game_name = self.current_stream['game_name']
            
            # Terminate FFmpeg
            process.terminate()
            
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            # Calculate duration
            duration = datetime.now() - start_time
            duration_str = self._format_duration(duration)
            
            # Send Discord notification
            if self.discord_notifier:
                self.discord_notifier.notify_stream_stopped(
                    game_name=game_name,
                    duration=duration_str
                )
            
            print(f"⏹️ Stream stopped (Duration: {duration_str})")
            self.current_stream = None
            return True
            
        except Exception as e:
            print(f"❌ Stop error: {e}")
            return False
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format duration as human-readable string."""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def start_service(self):
        """Start the streaming service."""
        if self.is_running:
            return
        
        print("🚀 Starting Auto-Stream...")
        
        # Validate configuration
        errors = self.config.validate()
        if errors:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"   • {error}")
            return
        
        # Ensure FFmpeg is available
        try:
            ffmpeg_path = self.ffmpeg_manager.ensure_ffmpeg()
            print(f"✅ FFmpeg: {ffmpeg_path}")
        except Exception as e:
            print(f"❌ FFmpeg error: {e}")
            return
        
        # Start Discord bot if configured
        if self.discord_notifier:
            self.discord_notifier.start_bot()
            time.sleep(1)
        
        # Start game monitoring
        self.game_detector.start_monitoring()
        self.is_running = True
        
        print(f"✅ Monitoring '{self.config.game_executable}'")
    
    def stop_service(self):
        """Stop the streaming service."""
        if not self.is_running:
            return
        
        print("🛑 Stopping service...")
        
        # Stop active stream
        if self.current_stream:
            self.stop_stream()
        
        # Stop game monitoring
        self.game_detector.stop_monitoring()
        
        # Stop Discord bot
        if self.discord_notifier:
            self.discord_notifier.stop_bot()
        
        self.is_running = False
        print("✅ Service stopped") 