"""
Game detection for auto-stream.
Monitors running processes to detect when specified games are launched.
"""

import platform
import threading
import time
from typing import Callable, Dict, List, Optional

import psutil


class GameDetector:
    """Detects when specified games are running."""

    def __init__(self, game_executables: List[str], check_interval: int = 10):
        self.game_executables = [exe.lower() for exe in game_executables]
        self.check_interval = check_interval
        self.is_monitoring = False
        self.monitoring_thread = None
        self.callbacks = {"game_started": [], "game_stopped": []}
        self.currently_running_games = set()

    def add_callback(self, event: str, callback: Callable):
        """Add callback for game events."""
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def remove_callback(self, event: str, callback: Callable):
        """Remove callback for game events."""
        if event in self.callbacks and callback in self.callbacks[event]:
            self.callbacks[event].remove(callback)

    def _trigger_callbacks(self, event: str, game_name: str, process_info: Dict = None):
        """Trigger all callbacks for an event."""
        for callback in self.callbacks.get(event, []):
            try:
                if process_info:
                    callback(game_name, process_info)
                else:
                    callback(game_name)
            except Exception as e:
                print(f"Error in callback for {event}: {e}")

    def get_running_processes(self) -> List[Dict]:
        """Get list of currently running processes."""
        processes = []
        try:
            for proc in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
                try:
                    proc_info = proc.info
                    if proc_info["name"]:
                        processes.append(
                            {
                                "pid": proc_info["pid"],
                                "name": proc_info["name"],
                                "exe": proc_info.get("exe", ""),
                                "cmdline": proc_info.get("cmdline", []),
                            }
                        )
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    continue
        except Exception as e:
            print(f"Error getting processes: {e}")

        return processes

    def find_running_games(self) -> Dict[str, Dict]:
        """Find currently running games from the watchlist."""
        running_games = {}
        processes = self.get_running_processes()

        for process in processes:
            process_name = process["name"].lower()

            # Check if this process matches any of our target games
            for target_game in self.game_executables:
                if target_game in process_name:
                    # Use the original case for the key
                    original_name = next(
                        (
                            exe
                            for exe in self.game_executables
                            if exe.lower() == target_game
                        ),
                        target_game,
                    )

                    running_games[original_name] = {
                        "process": process,
                        "window_title": self._get_window_title(process),
                    }
                    break

        return running_games

    def _get_window_title(self, process_info: Dict) -> Optional[str]:
        """Get window title for a process (Windows-specific for now)."""
        if platform.system() != "Windows":
            return None

        try:
            import win32gui
            import win32process

            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if pid == process_info["pid"]:
                        title = win32gui.GetWindowText(hwnd)
                        if title.strip():
                            windows.append(title)
                return True

            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)

            # Return the first non-empty title
            return windows[0] if windows else None

        except ImportError:
            # win32gui not available, return process name
            return process_info.get("name", "Unknown")
        except Exception as e:
            print(f"Error getting window title: {e}")
            return process_info.get("name", "Unknown")

    def is_game_running(self, game_executable: str) -> bool:
        """Check if a specific game is currently running."""
        running_games = self.find_running_games()
        return game_executable.lower() in [
            game.lower() for game in running_games.keys()
        ]

    def get_game_window_title(self, game_executable: str) -> Optional[str]:
        """Get the window title for a running game."""
        running_games = self.find_running_games()

        for game_name, game_info in running_games.items():
            if game_name.lower() == game_executable.lower():
                return game_info.get("window_title")

        return None

    def _monitoring_loop(self):
        """Main monitoring loop that runs in a separate thread."""
        print("Game monitoring started...")

        while self.is_monitoring:
            try:
                current_games = set(self.find_running_games().keys())

                # Check for newly started games
                new_games = current_games - self.currently_running_games
                for game in new_games:
                    print(f"Game started: {game}")
                    game_info = self.find_running_games().get(game, {})
                    self._trigger_callbacks("game_started", game, game_info)

                # Check for stopped games
                stopped_games = self.currently_running_games - current_games
                for game in stopped_games:
                    print(f"Game stopped: {game}")
                    self._trigger_callbacks("game_stopped", game)

                self.currently_running_games = current_games

            except Exception as e:
                print(f"Error in monitoring loop: {e}")

            # Wait for next check
            time.sleep(self.check_interval)

        print("Game monitoring stopped.")

    def start_monitoring(self):
        """Start monitoring for games in a separate thread."""
        if self.is_monitoring:
            print("Monitoring is already running.")
            return

        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitoring_thread.start()

    def stop_monitoring(self):
        """Stop monitoring for games."""
        if not self.is_monitoring:
            return

        self.is_monitoring = False

        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)

    def update_game_list(self, game_executables: List[str]):
        """Update the list of games to monitor."""
        self.game_executables = [exe.lower() for exe in game_executables]
        print(f"Updated game list: {self.game_executables}")

    def get_all_game_processes(self) -> List[Dict]:
        """Get all processes that might be games (for UI selection)."""
        processes = self.get_running_processes()

        # Filter for processes that might be games
        game_like_processes = []

        for process in processes:
            name = process["name"].lower()
            exe_path = process.get("exe", "").lower()

            # Skip system processes and common applications
            skip_patterns = [
                "system",
                "registry",
                "winlogon",
                "csrss",
                "smss",
                "lsass",
                "services",
                "spoolsv",
                "explorer",
                "dwm",
                "taskhost",
                "chrome",
                "firefox",
                "notepad",
                "cmd",
                "powershell",
                "python",
                "java",
                "node",
                "code",
                "discord",
                "steam",
                "origin",
                "uplay",
                "epicgames",
                "battle.net",
            ]

            # Include if it's an .exe and not in skip patterns
            if (
                name.endswith(".exe")
                and not any(pattern in name for pattern in skip_patterns)
                and not any(pattern in exe_path for pattern in skip_patterns)
            ):
                game_like_processes.append(process)

        return game_like_processes
