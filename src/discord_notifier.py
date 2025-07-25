"""
Discord integration for auto-stream.
Handles Discord bot functionality and stream notifications.
"""

import asyncio
import threading
from typing import Optional, Dict, Any
import discord
from discord.ext import commands


class DiscordNotifier:
    """Handles Discord notifications for stream events."""
    
    def __init__(self, bot_token: str, channel_id: str, guild_id: str = ""):
        self.bot_token = bot_token
        self.channel_id = int(channel_id) if channel_id.isdigit() else None
        self.guild_id = int(guild_id) if guild_id.isdigit() else None
        
        # Create bot instance
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        
        # Bot state
        self.is_connected = False
        self.bot_thread = None
        self.loop = None
        
        # Setup bot events
        self._setup_bot_events()
    
    def _setup_bot_events(self):
        """Set up Discord bot event handlers."""
        
        @self.bot.event
        async def on_ready():
            print(f'Discord bot logged in as {self.bot.user}')
            self.is_connected = True
        
        @self.bot.event
        async def on_disconnect():
            print('Discord bot disconnected')
            self.is_connected = False
        
        @self.bot.event
        async def on_error(event, *args, **kwargs):
            print(f'Discord bot error in {event}: {args}')
    
    def start_bot(self):
        """Start the Discord bot in a separate thread."""
        if self.bot_thread and self.bot_thread.is_alive():
            print("Discord bot is already running.")
            return
        
        def run_bot():
            try:
                # Create new event loop for this thread
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                
                # Run the bot
                self.loop.run_until_complete(self.bot.start(self.bot_token))
            except Exception as e:
                print(f"Error running Discord bot: {e}")
                self.is_connected = False
        
        self.bot_thread = threading.Thread(target=run_bot, daemon=True)
        self.bot_thread.start()
        
        # Wait a bit for connection
        import time
        time.sleep(2)
    
    def stop_bot(self):
        """Stop the Discord bot."""
        if self.loop and not self.loop.is_closed():
            # Schedule bot close
            asyncio.run_coroutine_threadsafe(self.bot.close(), self.loop)
        
        if self.bot_thread and self.bot_thread.is_alive():
            self.bot_thread.join(timeout=5)
        
        self.is_connected = False
    
    def send_message_sync(self, message: str, embed: Optional[discord.Embed] = None) -> bool:
        """Send a message synchronously."""
        if not self.is_connected or not self.loop:
            print("Discord bot is not connected.")
            return False
        
        if not self.channel_id:
            print("No Discord channel ID configured.")
            return False
        
        async def send_message():
            try:
                channel = self.bot.get_channel(self.channel_id)
                if not channel:
                    print(f"Could not find channel with ID: {self.channel_id}")
                    return False
                
                if embed:
                    await channel.send(message, embed=embed)
                else:
                    await channel.send(message)
                
                return True
            except Exception as e:
                print(f"Error sending Discord message: {e}")
                return False
        
        try:
            # Schedule the coroutine to run in the bot's event loop
            future = asyncio.run_coroutine_threadsafe(send_message(), self.loop)
            return future.result(timeout=10)
        except Exception as e:
            print(f"Error scheduling Discord message: {e}")
            return False
    
    def notify_stream_started(
        self, 
        game_name: str, 
        stream_url: str = "", 
        custom_message: str = "",
        additional_info: Dict[str, Any] = None
    ) -> bool:
        """Send notification when stream starts."""
        
        if custom_message:
            message = custom_message.format(
                game_name=game_name,
                stream_url=stream_url
            )
        else:
            message = f"🎮 **{game_name}** stream is now live!"
            if stream_url:
                message += f"\n🔗 {stream_url}"
        
        # Create embed for richer notification
        embed = discord.Embed(
            title="🔴 Stream Started",
            description=f"Now streaming **{game_name}**",
            color=0x00ff00  # Green
        )
        
        if stream_url:
            embed.add_field(name="Stream URL", value=stream_url, inline=False)
        
        if additional_info:
            for key, value in additional_info.items():
                embed.add_field(name=key.title(), value=str(value), inline=True)
        
        embed.set_footer(text="Auto-Stream Bot")
        
        return self.send_message_sync(message, embed)
    
    def notify_stream_stopped(self, game_name: str, duration: str = "") -> bool:
        """Send notification when stream stops."""
        
        message = f"⏹️ **{game_name}** stream has ended."
        if duration:
            message += f"\n⏱️ Duration: {duration}"
        
        # Create embed
        embed = discord.Embed(
            title="⏹️ Stream Ended",
            description=f"**{game_name}** stream has stopped",
            color=0xff0000  # Red
        )
        
        if duration:
            embed.add_field(name="Duration", value=duration, inline=True)
        
        embed.set_footer(text="Auto-Stream Bot")
        
        return self.send_message_sync(message, embed)
    
    def test_connection(self) -> bool:
        """Test the Discord connection by sending a test message."""
        if not self.is_connected:
            return False
        
        test_message = "🧪 Auto-Stream bot test message"
        return self.send_message_sync(test_message)
    
    def get_channel_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the configured channel."""
        if not self.is_connected or not self.channel_id:
            return None
        
        async def get_info():
            try:
                channel = self.bot.get_channel(self.channel_id)
                if not channel:
                    return None
                
                return {
                    'name': channel.name,
                    'id': channel.id,
                    'guild': channel.guild.name if hasattr(channel, 'guild') else 'DM',
                    'type': str(channel.type)
                }
            except Exception as e:
                print(f"Error getting channel info: {e}")
                return None
        
        try:
            future = asyncio.run_coroutine_threadsafe(get_info(), self.loop)
            return future.result(timeout=5)
        except Exception as e:
            print(f"Error getting channel info: {e}")
            return None
    
    def update_config(self, bot_token: str, channel_id: str, guild_id: str = ""):
        """Update Discord configuration."""
        # Stop current bot if running
        if self.is_connected:
            self.stop_bot()
        
        # Update configuration
        self.bot_token = bot_token
        self.channel_id = int(channel_id) if channel_id.isdigit() else None
        self.guild_id = int(guild_id) if guild_id.isdigit() else None
        
        # Restart if we had a valid configuration
        if self.bot_token and self.channel_id:
            self.start_bot() 