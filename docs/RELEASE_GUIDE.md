# 🚀 GitHub Actions & Releases Guide

## How It Works

### Automatic Builds
Every time you push to `main` or `github-actions-build` branch:
1. **GitHub Actions automatically builds:**
   - `auto-stream.exe` (Windows)
   - `auto-stream` (Linux)
2. **Artifacts are available for 30 days** in the Actions tab

### Creating Releases with Executables

#### Method 1: GitHub Web Interface
1. Go to your repository on GitHub
2. Click **"Releases"** (right side of main page)
3. Click **"Create a new release"**
4. **Tag version:** `v1.0.0` (or any version)
5. **Title:** `Auto-Stream v1.0.0`
6. **Description:** What's new in this version
7. Click **"Publish release"**
8. **GitHub automatically attaches the executables!**

#### Method 2: Command Line
```bash
# Create and push a tag
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions will automatically create the release with executables
```

## What Users Get

When you create a release, users can download:

### Windows Package (`auto-stream-windows.zip`)
```
auto-stream-windows.zip
├── auto-stream.exe      # Ready to run!
├── .env.example        # Configuration template  
├── SETUP.txt           # Instructions
├── README.md           # Full docs
└── LICENSE             # License
```

### Linux Package (`auto-stream-linux.tar.gz`)
```
auto-stream-linux.tar.gz
├── auto-stream         # Ready to run!
├── .env.example        # Configuration template
├── SETUP.txt           # Instructions  
├── README.md           # Full docs
└── LICENSE             # License
```

## Where Users Find Your Executables

### Option 1: Releases Page
- Go to `https://github.com/yourusername/auto-stream/releases`
- Click **"Latest release"**
- Download the `.zip` (Windows) or `.tar.gz` (Linux)

### Option 2: Actions Artifacts (Development builds)
- Go to **Actions** tab
- Click on any successful build
- Download artifacts (requires GitHub login)

## Version Management

GitHub shows all your releases with:
- ✅ **Version numbers** (v1.0.0, v1.1.0, etc.)
- ✅ **Release dates**
- ✅ **Download counts**
- ✅ **Release notes**
- ✅ **Automatic executable attachments**

## Creating Your First Release

1. **Push your clean code:**
   ```bash
   git add .
   git commit -m "Ready for v1.0.0 release"
   git push origin github-actions-build
   ```

2. **Wait for Actions to complete** (check Actions tab)

3. **Create release:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

4. **Check Releases page** - your executables will be there automatically!

## 🎯 Answer to Your Question

> "Is there where the github shows versions of executable?"

**YES!** The **Releases** page shows:
- All versions of your executables
- Download links for each version  
- Download statistics
- Release notes for each version
- Both Windows `.exe` and Linux binaries

Perfect for distributing your gaming stream tool! 🎮 