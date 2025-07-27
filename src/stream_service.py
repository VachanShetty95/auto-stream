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
from .logger import AutoStreamLogger


class StreamService:
    """Simple streaming service."""
    
    def __init__(self, config):
        self.config = config
        
        # Initialize logger
        self.logger = AutoStreamLogger()
        
        # Initialize components
        # Handle case where no game executable is configured (desktop-only mode)
        game_executables = [config.game_executable] if config.game_executable.strip() else []
        self.game_detector = GameDetector(game_executables, config.check_interval)
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
        self.logger.log_game_detected(game_name)
        print(f"Game detected: {game_name}")
        
        if not self.config.auto_start:
            self.logger.info("Auto-start disabled")
            print("Auto-start disabled")
            return
        
        if self.current_stream:
            self.logger.info("Already streaming, skipping new stream")
            print(f"Already streaming")
            return
        
        # Start streaming
        success = self.start_stream(game_name)
        if success:
            self.logger.info(f"Started streaming {game_name}")
            print(f"Started streaming {game_name}")
        else:
            self.logger.error(f"Failed to start stream for {game_name}")
            print(f"Failed to start stream")
    
    def _on_game_stopped(self, game_name: str):
        """Handle game stopped event."""
        self.logger.log_game_stopped(game_name)
        print(f"Game stopped: {game_name}")
        
        if self.current_stream:
            self.stop_stream()
    
    def start_stream(self, game_name: str) -> bool:
        """Start streaming."""
        try:
            # Get quality settings
            quality_settings = self.config.get_quality_settings()
            
            # Determine if we should use desktop capture or game-specific capture
            use_desktop = True  # Default to desktop capture
            game_title = None
            
            # If game_executable is set and not empty, try game-specific capture
            if self.config.game_executable and self.config.game_executable.strip():
                # Check if the game is actually running
                if self.game_detector.is_game_running(self.config.game_executable):
                    game_title = game_name
                    use_desktop = False  # Try game-specific capture
                    self.logger.info(f"Using game-specific capture for: {game_name}")
                else:
                    self.logger.info(f"Game {self.config.game_executable} not running, using desktop capture")
            else:
                self.logger.info("No game executable configured, using desktop capture")
            
            # Generate FFmpeg command
            stream_cmd = self.ffmpeg_manager.generate_stream_command(
                stream_url=self.config.youtube_stream_url,
                stream_key=self.config.youtube_stream_key,
                game_title=game_title,
                quality=self.config.stream_quality,
                framerate=self.config.stream_framerate,
                bitrate=self.config.stream_bitrate,
                use_desktop=use_desktop
            )
            
            # Log the FFmpeg command
            self.logger.log_ffmpeg_command(stream_cmd)
            
            print(f"Starting stream...")
            self.logger.info(f"Starting stream with {'desktop' if use_desktop else 'game-specific'} capture")
            
            # Start FFmpeg process
            self.logger.info(f"Starting FFmpeg process with command: {' '.join(stream_cmd)}")
            
            process = subprocess.Popen(
                stream_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Check if process started successfully
            if process.poll() is not None:
                # Process terminated immediately
                stdout, stderr = process.communicate()
                self.logger.error(f"FFmpeg process failed to start. Return code: {process.returncode}")
                self.logger.error(f"FFmpeg stdout: {stdout}")
                self.logger.error(f"FFmpeg stderr: {stderr}")
                print(f"FFmpeg failed to start. Check logs for details.")
                return False
            
            # Wait a moment to see if process starts successfully
            import time
            time.sleep(2)
            
            if process.poll() is not None:
                # Process terminated after a short time
                stdout, stderr = process.communicate()
                self.logger.error(f"FFmpeg process terminated. Return code: {process.returncode}")
                self.logger.error(f"FFmpeg stdout: {stdout}")
                self.logger.error(f"FFmpeg stderr: {stderr}")
                print(f"FFmpeg process terminated. Check logs for details.")
                return False
            
            self.logger.info(f"FFmpeg process started successfully (PID: {process.pid})")
            
            # Store stream info
            self.current_stream = {
                'process': process,
                'start_time': datetime.now(),
                'game_name': game_name,
                'capture_type': 'desktop' if use_desktop else 'game-specific'
            }
            
            # Log stream start
            stream_url = f"{self.config.youtube_stream_url}/{self.config.youtube_stream_key}"
            self.logger.log_stream_start(game_name, stream_url)
            
            # Send Discord notification
            if self.discord_notifier:
                self.discord_notifier.notify_stream_started(
                    game_name=game_name,
                    custom_message=self.config.discord_message
                )
            
            return True
            
        except Exception as e:
            self.logger.log_error(e, "start_stream")
            print(f"Stream error: {e}")
            return False
    
    def stop_stream(self) -> bool:
        """Stop streaming."""
        if not self.current_stream:
            return False
        
        try:
            process = self.current_stream['process']
            start_time = self.current_stream['start_time']
            game_name = self.current_stream['game_name']
            capture_type = self.current_stream.get('capture_type', 'unknown')
            
            self.logger.info(f"Stopping stream for {game_name} (capture: {capture_type})")
            
            # Terminate FFmpeg
            process.terminate()
            
            try:
                process.wait(timeout=5)
                self.logger.info("FFmpeg process terminated successfully")
            except subprocess.TimeoutExpired:
                self.logger.warning("FFmpeg process did not terminate, forcing kill")
                process.kill()
                process.wait()
            
            # Calculate duration
            duration = datetime.now() - start_time
            duration_str = self._format_duration(duration)
            
            # Log stream stop
            self.logger.log_stream_stop(game_name, duration_str)
            
            # Send Discord notification
            if self.discord_notifier:
                self.discord_notifier.notify_stream_stopped(
                    game_name=game_name,
                    duration=duration_str
                )
            
            print(f"Stream stopped (Duration: {duration_str})")
            self.current_stream = None
            return True
            
        except Exception as e:
            self.logger.log_error(e, "stop_stream")
            print(f"Stop error: {e}")
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
        
        self.logger.info("Starting Auto-Stream service")
        print("Starting Auto-Stream...")
        
        # Validate configuration
        errors = self.config.validate()
        if errors:
            self.logger.error(f"Configuration errors: {errors}")
            print("Configuration errors:")
            for error in errors:
                print(f"   • {error}")
            return
        
        # Ensure FFmpeg is available
        try:
            ffmpeg_path = self.ffmpeg_manager.ensure_ffmpeg()
            self.logger.info(f"FFmpeg found at: {ffmpeg_path}")
            print(f"FFmpeg: {ffmpeg_path}")
        except Exception as e:
            self.logger.log_error(e, "FFmpeg initialization")
            print(f"FFmpeg error: {e}")
            return
        
        # Start Discord bot if configured
        if self.discord_notifier:
            self.logger.info("Starting Discord bot")
            self.discord_notifier.start_bot()
            time.sleep(1)
        
        # Check if we're in desktop-only mode (no game executable configured)
        if not self.config.game_executable.strip():
            self.logger.info("No game executable configured - starting desktop-only streaming")
            print("No game executable configured - starting desktop-only streaming")
            
            # Start streaming immediately for desktop-only mode
            success = self.start_stream("Desktop")
            if success:
                self.is_running = True
                print("Desktop streaming started successfully!")
            else:
                self.logger.error("Failed to start desktop streaming")
                print("Failed to start desktop streaming")
                return
        else:
            # Start game monitoring
            self.logger.info(f"Starting game monitoring for: {self.config.game_executable}")
            self.game_detector.start_monitoring()
            self.is_running = True
            print(f"Monitoring '{self.config.game_executable}'")
    
    def check_stream_health(self) -> bool:
        """Check if the current stream is healthy."""
        if not self.current_stream:
            return False
        
        process = self.current_stream['process']
        
        # Check if process is still running
        if process.poll() is not None:
            # Process has terminated
            stdout, stderr = process.communicate()
            self.logger.error(f"FFmpeg process terminated unexpectedly. Return code: {process.returncode}")
            self.logger.error(f"FFmpeg stdout: {stdout}")
            self.logger.error(f"FFmpeg stderr: {stderr}")
            return False
        
        return True
    
    def stop_service(self):
        """Stop the streaming service."""
        if not self.is_running:
            return
        
        self.logger.info("Stopping Auto-Stream service")
        print("Stopping service...")
        
        # Stop active stream
        if self.current_stream:
            self.stop_stream()
        
        # Stop game monitoring
        self.logger.info("Stopping game monitoring")
        self.game_detector.stop_monitoring()
        
        # Stop Discord bot
        if self.discord_notifier:
            self.logger.info("Stopping Discord bot")
            self.discord_notifier.stop_bot()
        
        self.is_running = False
        self.logger.info("Auto-Stream service stopped")
        print("Service stopped") 