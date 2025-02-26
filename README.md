# 🎮 auto-stream
Automatically initiate game streaming to YouTube upon launch and receive real-time Discord notifications when the stream goes live.

## 🚀 Features
✅ **Automatic Game Detection** – Starts streaming when a specified game is running.  
✅ **Seamless YouTube Streaming** – Uses FFmpeg to stream to YouTube Live.  
✅ **Real-Time Discord Notifications** – Notifies a Discord channel when the stream starts.  
✅ **Lightweight & Efficient** – No manual setup needed after installation.  

---

## 🛠️ Installation  

### 1️⃣ **Clone the Repository**  
```sh
git clone https://github.com/VachanShetty95/auto-stream.git
cd auto-stream
```

### 2️⃣ **Download FFmpeg** (Required for Windows)  
1. Download the **Windows FFmpeg build** from [here](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z).  
2. Extract it and copy `ffmpeg.exe` into the `ffmpeg/` directory inside this project.  
   ```
   auto-stream/
   ├── ffmpeg/
   │   ├── ffmpeg.exe  <-- Place it here
   ├── main.py
   ├── .env
   ├── requirements.txt
   └── README.md
   ```

### 3️⃣ **Install Dependencies**  
```sh
pip install -r requirements.txt
```

### 4️⃣ **Set Up Environment Variables**  
Create a `.env` file in the project directory and add:  
```ini
YOUTUBE_STREAM_KEY=your_youtube_stream_key_here
YOUTUBE_STREAM_URL=rtmp://a.rtmp.youtube.com/live2
GAME_EXECUTABLE_PATH=game_executable_name.exe
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
```

---

## 🎥 Usage  

Simply run:  
```sh
python main.py
```
- The script will monitor for your game process (`GAME_EXECUTABLE_PATH`).  
- Once detected, it will **automatically start streaming** to YouTube.  
- A **Discord notification** will be sent when streaming begins.  
- When the game closes, streaming stops automatically.  

---

## 🛠️ Building an Executable (Windows)  
To run the script without Python installed, you can package it into an executable:  
```sh
pyinstaller --onefile --hidden-import dotenv main.py
```
This will create a standalone `main.exe` in the `dist/` folder.

---

## ⚠️ Troubleshooting  

### ❌ **FFmpeg Not Found?**  
Ensure `ffmpeg.exe` is correctly placed in the `ffmpeg/` directory.  

### ❌ **Game Not Detected?**  
- Double-check the `GAME_EXECUTABLE_PATH` in `.env` (it should match the process name).  
- Open Task Manager and verify the game's actual executable name.  

### ❌ **Stream Not Starting?**  
- Ensure your **YouTube stream key** is correct in `.env`.  
- Test FFmpeg manually:  
  ```sh
  ffmpeg -f gdigrab -framerate 30 -i title="YourGameWindow" -f flv rtmp://a.rtmp.youtube.com/live2/YOUR_STREAM_KEY
  ```

---

## 📜 License  
MIT License – Feel free to modify and distribute!  

