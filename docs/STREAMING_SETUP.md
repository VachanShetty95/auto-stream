# 🎥 YouTube Streaming Setup Guide

## The Issue
Your `.env` file has placeholder values. You need real YouTube streaming credentials.

## 📺 Enable YouTube Streaming

### Step 1: Enable Live Streaming on YouTube
1. Go to [YouTube Studio](https://studio.youtube.com)
2. Click **"Go Live"** in the top right
3. If prompted, **verify your channel** with phone number
4. Wait 24 hours after verification (YouTube requirement)

### Step 2: Get Your Stream Key
1. In YouTube Studio, click **"Go Live"**
2. Choose **"Stream"** (not webcam)
3. **Copy your Stream Key** - it looks like: `abcd-1234-efgh-5678-ijkl`

### Step 3: Configure Your .env File
Edit your `.env` file:
```bash
# Replace this placeholder
YOUTUBE_STREAM_KEY=your_youtube_stream_key_here

# With your actual key  
YOUTUBE_STREAM_KEY=abcd-1234-efgh-5678-ijkl

# Set your game executable
GAME_EXECUTABLE=YourGame.exe
```

## 🧪 Test Without YouTube

If you want to test streaming without YouTube setup:
```bash
# Test with file output instead
python test_local_stream.py
```

## 🔍 Debug Your Setup

After setting real credentials:
```bash
python debug_stream.py
```

All tests should pass ✅

## ⚠️ Common Issues

### "Channel not verified"
- Verify your YouTube channel with phone number
- Wait 24 hours after verification

### "Stream key invalid"  
- Copy the key exactly (no spaces)
- Generate a new key in YouTube Studio

### "Streaming not enabled"
- Make sure you clicked "Go Live" at least once
- Some channels need to build up watch time first

## 🎮 Game Detection

Set your game's executable name:
```bash
GAME_EXECUTABLE=csgo.exe          # Counter-Strike
GAME_EXECUTABLE=RocketLeague.exe  # Rocket League  
GAME_EXECUTABLE=minecraft.exe     # Minecraft
```

The app will automatically start streaming when it detects your game running! 