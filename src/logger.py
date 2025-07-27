"""
Logging functionality for auto-stream.
Handles log file generation and management.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class AutoStreamLogger:
    """Handles logging for the auto-stream application."""
    
    def __init__(self, log_dir: str = "logs", log_level: int = logging.INFO):
        """Initialize the logger.
        
        Args:
            log_dir: Directory to store log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_dir = Path(log_dir)
        self.log_level = log_level
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Set up the logger with file and console handlers."""
        # Create logs directory if it doesn't exist
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('auto_stream')
        self.logger.setLevel(self.log_level)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.log_dir / f"auto_stream_{timestamp}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"Logger initialized. Log file: {log_file}")
    
    def info(self, message: str) -> None:
        """Log an info message."""
        if self.logger:
            self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log a warning message."""
        if self.logger:
            self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log an error message."""
        if self.logger:
            self.logger.error(message)
    
    def debug(self, message: str) -> None:
        """Log a debug message."""
        if self.logger:
            self.logger.debug(message)
    
    def critical(self, message: str) -> None:
        """Log a critical message."""
        if self.logger:
            self.logger.critical(message)
    
    def log_stream_start(self, game_name: str, stream_url: str) -> None:
        """Log stream start event."""
        self.info(f"Stream started - Game: {game_name}, URL: {stream_url}")
    
    def log_stream_stop(self, game_name: str, duration: str) -> None:
        """Log stream stop event."""
        self.info(f"Stream stopped - Game: {game_name}, Duration: {duration}")
    
    def log_game_detected(self, game_name: str) -> None:
        """Log game detection event."""
        self.info(f"Game detected: {game_name}")
    
    def log_game_stopped(self, game_name: str) -> None:
        """Log game stop event."""
        self.info(f"Game stopped: {game_name}")
    
    def log_ffmpeg_command(self, command: list) -> None:
        """Log the FFmpeg command being executed."""
        self.debug(f"FFmpeg command: {' '.join(command)}")
    
    def log_error(self, error: Exception, context: str = "") -> None:
        """Log an error with context."""
        error_msg = f"Error in {context}: {str(error)}" if context else str(error)
        self.error(error_msg)
    
    def get_log_files(self) -> list:
        """Get list of log files in the log directory."""
        if not self.log_dir.exists():
            return []
        
        log_files = []
        for file in self.log_dir.glob("auto_stream_*.log"):
            log_files.append({
                'name': file.name,
                'size': file.stat().st_size,
                'modified': datetime.fromtimestamp(file.stat().st_mtime)
            })
        
        return sorted(log_files, key=lambda x: x['modified'], reverse=True)
    
    def cleanup_old_logs(self, keep_days: int = 7) -> int:
        """Clean up log files older than specified days.
        
        Args:
            keep_days: Number of days to keep log files
            
        Returns:
            Number of files deleted
        """
        if not self.log_dir.exists():
            return 0
        
        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        deleted_count = 0
        
        for file in self.log_dir.glob("auto_stream_*.log"):
            if file.stat().st_mtime < cutoff_time:
                try:
                    file.unlink()
                    deleted_count += 1
                    self.info(f"Deleted old log file: {file.name}")
                except Exception as e:
                    self.error(f"Failed to delete log file {file.name}: {e}")
        
        return deleted_count 