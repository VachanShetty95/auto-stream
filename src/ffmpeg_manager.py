"""
FFmpeg management for auto-stream.
Handles FFmpeg download, installation, and command generation.
"""

import os
import platform
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import List, Optional
import requests
from urllib.parse import urlparse


class FFmpegManager:
    """Manages FFmpeg installation and usage."""
    
    def __init__(self, install_dir: Optional[str] = None):
        if install_dir is None:
            # Default installation directory
            if platform.system() == "Windows":
                self.install_dir = Path.cwd() / "ffmpeg"
            else:
                self.install_dir = Path.home() / ".local" / "bin"
        else:
            self.install_dir = Path(install_dir)
        
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
        # FFmpeg executable name
        self.ffmpeg_name = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
        self.ffmpeg_path = self.install_dir / self.ffmpeg_name
    
    def is_installed(self) -> bool:
        """Check if FFmpeg is installed and working."""
        # Check if file exists
        if not self.ffmpeg_path.exists():
            return False
        
        # Check if it's executable and working
        try:
            result = subprocess.run(
                [str(self.ffmpeg_path), "-version"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
            return False
    
    def get_system_ffmpeg(self) -> Optional[str]:
        """Try to find FFmpeg in system PATH."""
        ffmpeg_cmd = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
        ffmpeg_path = shutil.which(ffmpeg_cmd)
        
        if ffmpeg_path:
            try:
                result = subprocess.run(
                    [ffmpeg_path, "-version"],
                    capture_output=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return ffmpeg_path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        return None
    
    def download_windows_ffmpeg(self, progress_callback=None) -> bool:
        """Download FFmpeg for Windows."""
        if platform.system() != "Windows":
            return False
        
        # FFmpeg download URL (using a reliable source)
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        
        try:
            print("Downloading FFmpeg...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Download to temporary file
            zip_path = self.install_dir / "ffmpeg.zip"
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
            
            print("Extracting FFmpeg...")
            
            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Find the ffmpeg.exe in the extracted files
                for file_info in zip_ref.filelist:
                    if file_info.filename.endswith('ffmpeg.exe'):
                        # Extract just the ffmpeg.exe file
                        with zip_ref.open(file_info) as source:
                            with open(self.ffmpeg_path, 'wb') as target:
                                shutil.copyfileobj(source, target)
                        break
            
            # Clean up
            zip_path.unlink()
            
            # Make executable (shouldn't be needed on Windows, but just in case)
            if self.ffmpeg_path.exists():
                os.chmod(self.ffmpeg_path, 0o755)
                print(f"FFmpeg installed to: {self.ffmpeg_path}")
                return True
            
        except Exception as e:
            print(f"Error downloading FFmpeg: {e}")
            if zip_path.exists():
                zip_path.unlink()
        
        return False
    
    def install_linux_instructions(self) -> str:
        """Return instructions for installing FFmpeg on Linux."""
        return """
FFmpeg installation on Linux:

Ubuntu/Debian:
    sudo apt update && sudo apt install ffmpeg

Fedora:
    sudo dnf install ffmpeg

Arch Linux:
    sudo pacman -S ffmpeg

Or download from: https://ffmpeg.org/download.html
"""
    
    def ensure_ffmpeg(self, progress_callback=None) -> str:
        """Ensure FFmpeg is available and return its path."""
        # Check if already installed locally
        if self.is_installed():
            return str(self.ffmpeg_path)
        
        # Check system PATH
        system_ffmpeg = self.get_system_ffmpeg()
        if system_ffmpeg:
            print(f"Using system FFmpeg: {system_ffmpeg}")
            return system_ffmpeg
        
        # Try to download (Windows only)
        if platform.system() == "Windows":
            if self.download_windows_ffmpeg(progress_callback):
                return str(self.ffmpeg_path)
            else:
                raise RuntimeError("Failed to download FFmpeg")
        else:
            # Linux - provide installation instructions
            raise RuntimeError(f"FFmpeg not found. {self.install_linux_instructions()}")
    
    def generate_stream_command(
        self,
        stream_url: str,
        stream_key: str,
        game_title: Optional[str] = None,
        quality: str = "720p",
        framerate: int = 30,
        bitrate: str = "3000k",
        use_desktop: bool = True
    ) -> List[str]:
        """Generate FFmpeg command for streaming.
        
        Args:
            stream_url: RTMP stream URL
            stream_key: Stream key for authentication
            game_title: Optional game window title (not used when use_desktop=True)
            quality: Stream quality (480p, 720p, 1080p)
            framerate: Video framerate
            bitrate: Video bitrate
            use_desktop: If True, capture entire desktop; if False, try to capture specific window
        """
        
        ffmpeg_path = self.ensure_ffmpeg()
        
        # Quality settings
        quality_settings = {
            "480p": {"width": 854, "height": 480, "bitrate": "1500k"},
            "720p": {"width": 1280, "height": 720, "bitrate": "3000k"},
            "1080p": {"width": 1920, "height": 1080, "bitrate": "6000k"}
        }
        
        settings = quality_settings.get(quality, quality_settings["720p"])
        if bitrate != "3000k":  # Override if custom bitrate provided
            settings["bitrate"] = bitrate
        
        # Base command
        cmd = [ffmpeg_path]
        
        # Input settings (platform-specific)
        if platform.system() == "Windows":
            # Use the working command structure
            if use_desktop or not game_title:
                # Desktop capture (default and most reliable)
                cmd.extend([
                    "-f", "gdigrab",
                    "-framerate", str(framerate),
                    "-video_size", f"{settings['width']}x{settings['height']}",
                    "-i", "desktop",
                    "-f", "dshow",
                    "-i", "audio=\"Stereo Mix (Realtek(R) Audio)\""
                ])
            else:
                # Window-specific capture (less reliable)
                cmd.extend([
                    "-f", "gdigrab",
                    "-framerate", str(framerate),
                    "-video_size", f"{settings['width']}x{settings['height']}",
                    "-i", f"title={game_title}",
                    "-f", "dshow",
                    "-i", "audio=\"Stereo Mix (Realtek(R) Audio)\""
                ])
        else:
            # Linux - detect display server and use appropriate capture
            import os
            session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
            display = os.environ.get('DISPLAY', '')
            
            # If we have a DISPLAY variable, prefer X11 capture even if session type says wayland
            if display and session_type == 'wayland':
                print(f"Detected mixed environment: session={session_type}, display={display}")
                print("Using X11 capture since DISPLAY is available")
                # Use X11 capture
                cmd.extend([
                    "-f", "x11grab",
                    "-framerate", str(framerate),
                    "-i", display
                ])
            elif session_type == 'wayland':
                # Wayland - try to use actual screen capture
                # First, try using pipewire screen capture (modern method)
                try:
                    import shutil
                    if shutil.which('wf-recorder'):
                        # Use wf-recorder with stdout output for FFmpeg
                        cmd.extend([
                            "-f", "pulse",
                            "-i", "default",
                            "-f", "video4linux2", 
                            "-i", "/dev/video0"  # This might work if pipewire creates a virtual camera
                        ])
                    else:
                        # Fallback to test pattern with warning
                        print("Wayland screen capture not available, using test pattern")
                        cmd.extend([
                            "-f", "lavfi",
                            "-i", "testsrc2=size=1280x720:rate=30",
                            "-f", "lavfi", 
                            "-i", "sine=frequency=1000:sample_rate=48000"
                        ])
                except:
                    # Fallback to test pattern
                    print("Screen capture failed, using test pattern")
                    cmd.extend([
                        "-f", "lavfi",
                        "-i", "testsrc2=size=1280x720:rate=30",
                        "-f", "lavfi", 
                        "-i", "sine=frequency=1000:sample_rate=48000"
                    ])
            else:
                # X11 capture
                display = os.environ.get('DISPLAY', ':0.0')
                cmd.extend([
                    "-f", "x11grab",
                    "-framerate", str(framerate),
                    "-i", display
                ])
        
        # Video encoding settings (using the working command structure)
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-g", "60",
            "-keyint_min", "60"
        ])
        
        # Audio settings (using the working command structure)
        if platform.system() == "Windows":
            cmd.extend([
                "-c:a", "aac",
                "-b:a", "128k",
                "-ar", "44100"
            ])
        
        # Output settings
        cmd.extend([
            "-f", "flv",
            f"{stream_url}/{stream_key}"
        ])
        
        return cmd
    
    def test_stream_command(self, cmd: List[str], duration: int = 10) -> bool:
        """Test the stream command for a short duration."""
        try:
            # Add duration limit for testing
            test_cmd = cmd[:-1] + ["-t", str(duration)] + [cmd[-1]]
            
            result = subprocess.run(
                test_cmd,
                capture_output=True,
                timeout=duration + 5
            )
            
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False 