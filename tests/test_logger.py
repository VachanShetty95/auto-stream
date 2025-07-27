"""
Tests for the logging functionality.
"""

import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING
import pytest

from src.logger import AutoStreamLogger

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from pytest_mock.plugin import MockerFixture


class TestAutoStreamLogger:
    """Test cases for AutoStreamLogger class."""

    def test_init_creates_log_directory(self) -> None:
        """Test that logger creates log directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = AutoStreamLogger(log_dir=temp_dir)
            
            # Check that log directory exists
            assert Path(temp_dir).exists()
            assert Path(temp_dir).is_dir()

    def test_log_levels(self) -> None:
        """Test all log levels work correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = AutoStreamLogger(log_dir=temp_dir)
            
            # Test all log levels
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")
            
            # Check that log file was created
            log_files = list(Path(temp_dir).glob("auto_stream_*.log"))
            assert len(log_files) == 1

    def test_log_stream_events(self) -> None:
        """Test stream event logging methods."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = AutoStreamLogger(log_dir=temp_dir)
            
            # Test stream event logging
            logger.log_stream_start("test_game", "rtmp://test.com/key")
            logger.log_stream_stop("test_game", "1h 30m")
            logger.log_game_detected("test_game")
            logger.log_game_stopped("test_game")
            
            # Check that log file was created
            log_files = list(Path(temp_dir).glob("auto_stream_*.log"))
            assert len(log_files) == 1

    def test_log_ffmpeg_command(self) -> None:
        """Test FFmpeg command logging."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = AutoStreamLogger(log_dir=temp_dir)
            
            # Test FFmpeg command logging
            test_command = ["ffmpeg", "-f", "gdigrab", "-i", "desktop"]
            logger.log_ffmpeg_command(test_command)
            
            # Check that log file was created
            log_files = list(Path(temp_dir).glob("auto_stream_*.log"))
            assert len(log_files) == 1

    def test_log_error_with_context(self) -> None:
        """Test error logging with context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = AutoStreamLogger(log_dir=temp_dir)
            
            # Test error logging
            test_error = ValueError("Test error")
            logger.log_error(test_error, "test_context")
            
            # Check that log file was created
            log_files = list(Path(temp_dir).glob("auto_stream_*.log"))
            assert len(log_files) == 1

    def test_get_log_files(self) -> None:
        """Test getting list of log files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = AutoStreamLogger(log_dir=temp_dir)
            
            # Create some test log files
            log_dir = Path(temp_dir)
            (log_dir / "auto_stream_20240101_120000.log").touch()
            (log_dir / "auto_stream_20240101_130000.log").touch()
            
            # Get log files
            log_files = logger.get_log_files()
            
            # Should have 3 files (2 created + 1 from logger init)
            assert len(log_files) == 3
            
            # Check that files are sorted by modification time (newest first)
            assert log_files[0]['name'] == "auto_stream_20240101_130000.log"

    def test_cleanup_old_logs(self) -> None:
        """Test cleanup of old log files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = AutoStreamLogger(log_dir=temp_dir)
            
            # Create some test log files
            log_dir = Path(temp_dir)
            old_file = log_dir / "auto_stream_20240101_120000.log"
            old_file.touch()
            
            # Set modification time to 10 days ago
            import time
            old_time = time.time() - (10 * 24 * 60 * 60)
            os.utime(old_file, (old_time, old_time))
            
            # Clean up old logs (keep 7 days)
            deleted_count = logger.cleanup_old_logs(keep_days=7)
            
            # Should have deleted 1 file
            assert deleted_count == 1
            assert not old_file.exists() 