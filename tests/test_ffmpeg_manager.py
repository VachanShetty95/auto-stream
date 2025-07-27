"""
Tests for FFmpeg manager functionality.
"""

import platform
import subprocess
from typing import TYPE_CHECKING
import pytest
from unittest.mock import Mock, patch

from src.ffmpeg_manager import FFmpegManager

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from pytest_mock.plugin import MockerFixture


class TestFFmpegManager:
    """Test cases for FFmpegManager class."""

    def test_init_default_path(self) -> None:
        """Test FFmpegManager initialization with default path."""
        manager = FFmpegManager()
        
        if platform.system() == "Windows":
            assert manager.ffmpeg_name == "ffmpeg.exe"
        else:
            assert manager.ffmpeg_name == "ffmpeg"
        
        assert manager.install_dir.exists()

    def test_init_custom_path(self) -> None:
        """Test FFmpegManager initialization with custom path."""
        custom_path = "./test_custom_path"
        manager = FFmpegManager(install_dir=custom_path)
        
        # The path gets resolved, so we check that it contains the expected part
        assert "test_custom_path" in str(manager.install_dir)

    @patch('subprocess.run')
    def test_is_installed_true(self, mock_run: Mock) -> None:
        """Test is_installed returns True when FFmpeg is available."""
        mock_run.return_value.returncode = 0
        
        manager = FFmpegManager()
        manager.ffmpeg_path = Mock()
        manager.ffmpeg_path.exists.return_value = True
        
        assert manager.is_installed() is True

    @patch('subprocess.run')
    def test_is_installed_false(self, mock_run: Mock) -> None:
        """Test is_installed returns False when FFmpeg is not available."""
        mock_run.side_effect = FileNotFoundError()
        
        manager = FFmpegManager()
        manager.ffmpeg_path = Mock()
        manager.ffmpeg_path.exists.return_value = False
        
        assert manager.is_installed() is False

    @patch('shutil.which')
    def test_get_system_ffmpeg_found(self, mock_which: Mock) -> None:
        """Test get_system_ffmpeg when FFmpeg is found in PATH."""
        mock_which.return_value = "/usr/bin/ffmpeg"
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            manager = FFmpegManager()
            result = manager.get_system_ffmpeg()
            
            assert result == "/usr/bin/ffmpeg"

    @patch('shutil.which')
    def test_get_system_ffmpeg_not_found(self, mock_which: Mock) -> None:
        """Test get_system_ffmpeg when FFmpeg is not found in PATH."""
        mock_which.return_value = None
        
        manager = FFmpegManager()
        result = manager.get_system_ffmpeg()
        
        assert result is None

    @patch('platform.system')
    def test_generate_stream_command_windows(self, mock_system: Mock) -> None:
        """Test generate_stream_command for Windows platform."""
        mock_system.return_value = "Windows"
        
        with patch.object(FFmpegManager, 'ensure_ffmpeg') as mock_ensure:
            mock_ensure.return_value = "ffmpeg.exe"
            
            manager = FFmpegManager()
            cmd = manager.generate_stream_command(
                stream_url="rtmp://a.rtmp.youtube.com/live2",
                stream_key="test-key",
                quality="1080p",
                framerate=30
            )
            
            # Verify the command structure matches the working command
            assert cmd[0] == "ffmpeg.exe"
            assert "-f" in cmd
            assert "gdigrab" in cmd
            assert "-framerate" in cmd
            assert "30" in cmd
            assert "-video_size" in cmd
            assert "1920x1080" in cmd
            assert "-i" in cmd
            assert "desktop" in cmd
            assert "dshow" in cmd
            assert "audio=\"Stereo Mix (Realtek(R) Audio)\"" in cmd
            assert "-c:v" in cmd
            assert "libx264" in cmd
            assert "-preset" in cmd
            assert "veryfast" in cmd
            assert "-pix_fmt" in cmd
            assert "yuv420p" in cmd
            assert "-g" in cmd
            assert "60" in cmd
            assert "-keyint_min" in cmd
            assert "-c:a" in cmd
            assert "aac" in cmd
            assert "-b:a" in cmd
            assert "128k" in cmd
            assert "-ar" in cmd
            assert "44100" in cmd
            assert "-f" in cmd
            assert "flv" in cmd
            assert "rtmp://a.rtmp.youtube.com/live2/test-key" in cmd

    @patch('platform.system')
    def test_generate_stream_command_linux(self, mock_system: Mock) -> None:
        """Test generate_stream_command for Linux platform."""
        mock_system.return_value = "Linux"
        
        with patch.object(FFmpegManager, 'ensure_ffmpeg') as mock_ensure:
            mock_ensure.return_value = "ffmpeg"
            
            with patch.dict('os.environ', {'DISPLAY': ':0.0', 'XDG_SESSION_TYPE': 'x11'}):
                manager = FFmpegManager()
                cmd = manager.generate_stream_command(
                    stream_url="rtmp://a.rtmp.youtube.com/live2",
                    stream_key="test-key",
                    quality="720p",
                    framerate=30
                )
                
                # Verify the command structure for Linux
                assert cmd[0] == "ffmpeg"
                assert "-f" in cmd
                assert "x11grab" in cmd
                assert "-framerate" in cmd
                assert "30" in cmd
                assert "-i" in cmd
                assert ":0.0" in cmd
                assert "-c:v" in cmd
                assert "libx264" in cmd
                assert "-preset" in cmd
                assert "veryfast" in cmd
                assert "-pix_fmt" in cmd
                assert "yuv420p" in cmd
                assert "-g" in cmd
                assert "60" in cmd
                assert "-keyint_min" in cmd
                assert "-f" in cmd
                assert "flv" in cmd
                assert "rtmp://a.rtmp.youtube.com/live2/test-key" in cmd

    def test_generate_stream_command_quality_settings(self) -> None:
        """Test generate_stream_command with different quality settings."""
        with patch('platform.system', return_value="Windows"):
            with patch.object(FFmpegManager, 'ensure_ffmpeg') as mock_ensure:
                mock_ensure.return_value = "ffmpeg.exe"
                
                manager = FFmpegManager()
                
                # Test 480p
                cmd_480p = manager.generate_stream_command(
                    stream_url="rtmp://test.com",
                    stream_key="key",
                    quality="480p"
                )
                assert "854x480" in " ".join(cmd_480p)
                
                # Test 720p
                cmd_720p = manager.generate_stream_command(
                    stream_url="rtmp://test.com",
                    stream_key="key",
                    quality="720p"
                )
                assert "1280x720" in " ".join(cmd_720p)
                
                # Test 1080p
                cmd_1080p = manager.generate_stream_command(
                    stream_url="rtmp://test.com",
                    stream_key="key",
                    quality="1080p"
                )
                assert "1920x1080" in " ".join(cmd_1080p)

    @patch('subprocess.run')
    def test_test_stream_command_success(self, mock_run: Mock) -> None:
        """Test test_stream_command when command succeeds."""
        mock_run.return_value.returncode = 0
        
        manager = FFmpegManager()
        cmd = ["ffmpeg", "-version"]
        
        result = manager.test_stream_command(cmd, duration=5)
        assert result is True

    @patch('subprocess.run')
    def test_test_stream_command_failure(self, mock_run: Mock) -> None:
        """Test test_stream_command when command fails."""
        mock_run.return_value.returncode = 1
        
        manager = FFmpegManager()
        cmd = ["ffmpeg", "-invalid"]
        
        result = manager.test_stream_command(cmd, duration=5)
        assert result is False

    @patch('subprocess.run')
    def test_test_stream_command_timeout(self, mock_run: Mock) -> None:
        """Test test_stream_command when command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("ffmpeg", 5)
        
        manager = FFmpegManager()
        cmd = ["ffmpeg", "-version"]
        
        result = manager.test_stream_command(cmd, duration=5)
        assert result is False 