# Audio Device Setup Guide

## Windows Audio Device Configuration

The auto-stream application needs to capture audio from your system. On Windows, this requires configuring the correct audio device name.

### Step 1: Find Your Audio Devices

Run the audio device finder utility:

```bash
python tools/find_audio_devices.py
```

This will list all available audio devices on your system.

### Step 2: Test Your Audio Device

Test a specific audio device:

```bash
python tools/find_audio_devices.py "Your Device Name"
```

### Step 3: Configure Your .env File

Add the working audio device to your `.env` file:

```env
AUDIO_DEVICE="Your Working Device Name"
```

### Common Audio Device Names

- `Stereo Mix (Realtek(R) Audio)` - Most common
- `Microphone (Realtek(R) Audio)` - Uses microphone
- `Speakers (Realtek(R) Audio)` - Uses speakers
- `What U Hear (Creative)` - Creative sound cards
- `Stereo Mix` - Generic stereo mix

### Troubleshooting

#### Issue: "Could not find audio only device"

**Solution 1: Enable Stereo Mix**
1. Right-click the speaker icon in taskbar
2. Select "Open Sound settings"
3. Click "Sound Control Panel"
4. Go to "Recording" tab
5. Right-click in empty space → "Show Disabled Devices"
6. Right-click "Stereo Mix" → "Enable"

**Solution 2: Use Different Device**
Try different audio devices from the list:
```env
AUDIO_DEVICE="Microphone (Realtek(R) Audio)"
```

**Solution 3: Stream Without Audio**
If no audio device works, the application will automatically fallback to video-only streaming.

### Testing Your Setup

1. **Test with working command first:**
   ```bash
   ffmpeg -f gdigrab -framerate 30 -video_size 1920x1080 -i desktop -f dshow -i audio="Your Device Name" -c:v libx264 -preset veryfast -pix_fmt yuv420p -g 60 -keyint_min 60 -c:a aac -b:a 128k -ar 44100 -f flv "rtmp://a.rtmp.youtube.com/live2/your-stream-key"
   ```

2. **If that works, your auto-stream should work too!**

### Notes

- The application will automatically try to stream without audio if the configured audio device fails
- Check the logs in `logs/` directory for detailed error messages
- Different Windows systems may have different audio device names
- Some systems may not have Stereo Mix enabled by default 