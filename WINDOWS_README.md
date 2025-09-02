# Quick Object Classification Workshop: Halloween Hand (Windows Edition)

This guide is specifically for **Windows users**. For macOS/Linux instructions, see the [main README](README.md).

## 🚀 Quick Start Cheat Sheet for Windows

### Prerequisites
1. Python 3.8+ installed (check with `python --version`)
2. Git for Windows installed
3. Working webcam
4. RunPod account with credits

### Fast Path: Video to Webcam Demo

```powershell
# 1. CREATE DATASET (2 min)
python capture_and_prepare.py  # Records videos & extracts images

# 2. UPLOAD TO RUNPOD (5-10 min)
# Use WinSCP or command line:
scp -r -P [PORT] hand_cls root@[IP]:/workspace/

# 3. ON RUNPOD: Install & train
pip install ultralytics
yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 batch=16

# 4. DOWNLOAD MODEL (PowerShell)
scp -P [PORT] root@[IP]:/workspace/runs/classify/train/weights/best.pt ./

# 5. TEST WITH WEBCAM
python live_demo.py --weights best.pt
```

## 📋 Windows-Specific Setup

### 1. Install Python

**Option A: Official Python**
1. Download from [python.org](https://python.org)
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify: Open PowerShell and run `python --version`

**Option B: Anaconda (Recommended for beginners)**
1. Download [Anaconda](https://www.anaconda.com/download)
2. Install with default settings
3. Use Anaconda Prompt for all commands

### 2. Install Git for Windows
1. Download from [git-scm.com](https://git-scm.com/download/win)
2. Install with default settings
3. This includes Git Bash (Unix-like terminal for Windows)

### 3. Install FFmpeg

**Option A: Manual Installation**
1. Download from [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to System PATH:
   - Windows + X → System → Advanced System Settings
   - Environment Variables → Path → Edit → New
   - Add `C:\ffmpeg\bin`
4. Restart PowerShell and verify: `ffmpeg -version`

**Option B: Using Chocolatey**
```powershell
# Install Chocolatey first (admin PowerShell)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install ffmpeg
choco install ffmpeg
```

### 4. Clone Repository
```powershell
cd C:\Users\YourName\Documents
git clone https://github.com/12mv2/finetune-workshop.git
cd finetune-workshop
```

### 5. Install Python Dependencies
```powershell
pip install -r requirements.txt
```

If you get "pip not recognized", try:
```powershell
python -m pip install -r requirements.txt
```

## 🎥 Dataset Creation

### Check Camera Access
Before starting, ensure no other apps are using your camera:
- Close Zoom, Teams, Discord, etc.
- Close Windows Camera app
- If issues persist, check Device Manager for camera drivers

### Create Dataset
```powershell
python capture_and_prepare.py
```

This will:
1. Open your webcam
2. Record 20 seconds with hands visible
3. Record 20 seconds without hands
4. Extract 200 images automatically

**Troubleshooting Camera Issues:**
- If camera doesn't open, try camera index 1 or 2:
  ```python
  # In capture_dataset_videos.py, change:
  cap = cv2.VideoCapture(1)  # or 2
  ```
- Check Windows Privacy Settings → Camera → Allow apps

## 🖥️ RunPod Setup

### 1. Generate SSH Key (if needed)
```powershell
# PowerShell or Git Bash
ssh-keygen -t ed25519 -C "your_email@example.com"

# View your public key
type C:\Users\YourName\.ssh\id_ed25519.pub
```

### 2. Add SSH Key to RunPod
1. Copy the entire public key output
2. Go to RunPod Settings → SSH Keys
3. Add your key BEFORE creating a pod

### 3. Connect to RunPod

**Option A: Git Bash (Recommended)**
```bash
ssh -p [PORT] root@[IP]
```

**Option B: PowerShell with OpenSSH**
```powershell
ssh -p [PORT] root@[IP]
```

**Option C: PuTTY**
1. Download PuTTY from [putty.org](https://www.putty.org)
2. Enter IP and Port
3. Connection → SSH → Auth → Browse to private key

## 📤 File Transfer Options

### Option A: Command Line (Git Bash)
```bash
# Upload dataset
scp -r -P [PORT] hand_cls root@[IP]:/workspace/

# Download model
scp -P [PORT] root@[IP]:/workspace/runs/classify/train/weights/best.pt ./
```

### Option B: WinSCP (GUI)
1. Download [WinSCP](https://winscp.net)
2. New Site → Enter IP, Port, Username (root)
3. Advanced → SSH → Authentication → Private key file
4. Drag and drop files

### Option C: Fast Video Upload
```powershell
# Only upload 2 video files (40MB vs 400MB)
python capture_videos_only.py
scp -P [PORT] hand_video.mp4 not_hand_video.mp4 root@[IP]:/workspace/
```

## 🚀 Training on RunPod

Same as macOS/Linux:
```bash
# Install packages
pip install ultralytics

# Train model
yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 batch=16
```

## 🎮 Running the Demo

### GPU Support
- **NVIDIA GPU**: CUDA will be auto-detected
- **No GPU**: Falls back to CPU (slower but works)
- **AMD/Intel GPU**: Not supported yet (use CPU)

### Run Demo
```powershell
python live_demo.py --weights best.pt
```

**Controls:**
- Press 'q' to quit
- Shows confidence percentage
- At 100% confidence: Special effects!

## 🔧 Windows-Specific Troubleshooting

### Python Issues
- **"python not recognized"**: Add Python to PATH or use full path
- **"pip not recognized"**: Use `python -m pip` instead
- **Multiple Python versions**: Use Python Launcher `py -3.9`

### Camera Problems
- **Camera not found**: Try different indices (0, 1, 2)
- **Black screen**: Check privacy settings
- **Access denied**: Run as administrator

### File Path Issues
- **Path too long**: Move project closer to C:\ drive
- **Permission denied**: Run PowerShell as administrator
- **Slash direction**: Python handles both / and \

### Antivirus Issues
- Windows Defender might block scripts
- Add project folder to exclusions
- Or temporarily disable real-time protection

### PowerShell Execution Policy
If scripts won't run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📚 Additional Windows Resources

- [Detailed Windows Setup Guide](docs/windows_setup.md)
- [WSL2 Alternative Setup](docs/wsl2_setup.md) (Run Linux on Windows)
- [Windows GPU Setup](docs/windows_cuda.md) (NVIDIA CUDA)

## 💡 Tips for Windows Users

1. **Use Git Bash** when possible - it understands Unix commands
2. **Install Windows Terminal** from Microsoft Store for better experience
3. **Consider WSL2** if you're comfortable with Linux
4. **Use Anaconda** for easier package management
5. **Keep paths short** - Windows has 260 character limit

## 🆘 Getting Help

If you encounter Windows-specific issues:
1. Check the [Windows Troubleshooting Guide](docs/windows_troubleshooting.md)
2. Try running as administrator
3. Verify all prerequisites are installed
4. Use Git Bash instead of PowerShell for Unix commands

Remember: The core functionality is the same as macOS/Linux, just the setup and commands differ slightly!

---
*Note: This workshop was primarily developed on macOS. Please report any Windows-specific issues to help us improve!*