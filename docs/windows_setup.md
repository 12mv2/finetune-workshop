# Detailed Windows Setup Guide

This guide provides step-by-step instructions for setting up the Halloween Hand workshop on Windows.

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Python Installation](#python-installation)
3. [FFmpeg Installation](#ffmpeg-installation)
4. [Git Setup](#git-setup)
5. [SSH Key Setup](#ssh-key-setup)
6. [Environment Verification](#environment-verification)
7. [Common Issues](#common-issues)

## System Requirements

- Windows 10 or 11 (64-bit)
- 8GB RAM minimum (16GB recommended)
- Webcam (built-in or USB)
- Internet connection for RunPod
- ~2GB free disk space

## Python Installation

### Method 1: Official Python (Recommended)

1. **Download Python**
   - Visit [python.org/downloads](https://python.org/downloads)
   - Download Python 3.9 or later (avoid 3.12 if packages have compatibility issues)

2. **Install Python**
   - Run the installer
   - ✅ **CHECK** "Add Python to PATH" (critical!)
   - Click "Install Now"
   - If you missed adding to PATH:
     ```
     Windows + X → System → Advanced System Settings
     → Environment Variables → Path → Edit
     → New → Add: C:\Users\[YourName]\AppData\Local\Programs\Python\Python39
     → New → Add: C:\Users\[YourName]\AppData\Local\Programs\Python\Python39\Scripts
     ```

3. **Verify Installation**
   ```powershell
   python --version
   pip --version
   ```

### Method 2: Anaconda (Easier for Beginners)

1. **Download Anaconda**
   - Visit [anaconda.com/download](https://www.anaconda.com/download)
   - Get the 64-bit installer

2. **Install Anaconda**
   - Run installer with default settings
   - Don't add to PATH (use Anaconda Prompt instead)

3. **Use Anaconda Prompt**
   - Start Menu → Anaconda3 → Anaconda Prompt
   - All Python commands run here

## FFmpeg Installation

### Method 1: Manual Installation (Recommended)

1. **Download FFmpeg**
   - Visit [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/)
   - Download "release full" build
   - Or direct link: [ffmpeg-release-full.7z](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z)

2. **Extract Files**
   - Extract to `C:\ffmpeg` (create this folder)
   - You should have `C:\ffmpeg\bin\ffmpeg.exe`

3. **Add to System PATH**
   ```
   1. Windows + X → System
   2. Advanced system settings
   3. Environment Variables
   4. Under "System variables", find "Path"
   5. Edit → New → Add: C:\ffmpeg\bin
   6. OK on all windows
   ```

4. **Verify Installation**
   - Open NEW PowerShell window
   ```powershell
   ffmpeg -version
   ```

### Method 2: Using Chocolatey

1. **Install Chocolatey** (Admin PowerShell)
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force
   [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
   iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

2. **Install FFmpeg**
   ```powershell
   choco install ffmpeg
   ```

### Method 3: Using Scoop

1. **Install Scoop** (Regular PowerShell)
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   irm get.scoop.sh | iex
   ```

2. **Install FFmpeg**
   ```powershell
   scoop install ffmpeg
   ```

## Git Setup

### Installing Git for Windows

1. **Download Git**
   - Visit [git-scm.com/download/win](https://git-scm.com/download/win)
   - Download 64-bit installer

2. **Install Git**
   - Run installer
   - Keep all default options
   - This installs Git Bash (recommended terminal)

3. **Configure Git**
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

## SSH Key Setup

### Generate SSH Key

1. **Open Git Bash** (not PowerShell)

2. **Generate Key**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```
   - Press Enter for default location
   - Enter passphrase (optional but recommended)

3. **View Public Key**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

4. **Copy Key** 
   - Select all text
   - Right-click to copy (in Git Bash)

### Add to RunPod

1. Log into RunPod
2. Go to Settings → SSH Keys
3. Click "Add SSH Key"
4. Paste your public key
5. Give it a name (e.g., "Windows Laptop")

## Environment Verification

### Check All Components

Create a test script `check_setup.py`:

```python
import sys
import subprocess
import cv2
import torch

print("Python version:", sys.version)
print("Python path:", sys.executable)

# Check pip
try:
    import pip
    print("✓ pip is installed")
except ImportError:
    print("✗ pip not found")

# Check ffmpeg
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ ffmpeg is installed")
    else:
        print("✗ ffmpeg not working")
except FileNotFoundError:
    print("✗ ffmpeg not found in PATH")

# Check camera
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("✓ Camera detected")
    cap.release()
else:
    print("✗ Camera not detected")

# Check PyTorch
print(f"PyTorch version: {torch.__version__}")
if torch.cuda.is_available():
    print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
else:
    print("✗ No CUDA (CPU only)")
```

Run it:
```powershell
python check_setup.py
```

## Common Issues

### PowerShell Execution Policy

If scripts are blocked:
```powershell
# Allow scripts for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Long Path Support

Enable long paths (Admin PowerShell):
```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### Terminal Recommendations

1. **Windows Terminal** (Best)
   - Install from Microsoft Store
   - Better Unicode support
   - Multiple tabs
   - Better colors

2. **Git Bash** (Good for Unix commands)
   - Included with Git
   - Understands Unix paths
   - Built-in SSH client

3. **PowerShell** (Default)
   - Works but syntax differences
   - Use PowerShell 7+ if possible

### Python Virtual Environments

Recommended to avoid conflicts:
```powershell
# Create virtual environment
python -m venv workshop_env

# Activate it
.\workshop_env\Scripts\Activate.ps1  # PowerShell
# or
workshop_env\Scripts\activate.bat    # Command Prompt
# or
source workshop_env/Scripts/activate  # Git Bash

# Install packages in virtual environment
pip install -r requirements.txt
```

### Firewall and Antivirus

- Windows Defender may block Python scripts
- Add exclusion for project folder:
  ```
  Windows Security → Virus & threat protection
  → Manage settings → Add or remove exclusions
  → Add folder → Select project folder
  ```

### GPU Support (NVIDIA Only)

1. Install NVIDIA drivers
2. Install CUDA Toolkit (optional, PyTorch includes it)
3. Verify with:
   ```python
   import torch
   print(torch.cuda.is_available())
   ```

## Quick Fixes

| Problem | Solution |
|---------|----------|
| `python` not recognized | Use `py` or full path `C:\Python39\python.exe` |
| `pip` not recognized | Use `python -m pip` |
| Can't install packages | Run as administrator |
| SSL certificate error | `pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org` |
| Camera won't open | Try indices 0, 1, 2 in `VideoCapture()` |
| Access denied | Check Windows Security camera permissions |

## Next Steps

Once everything is verified:
1. Continue with the [Windows README](../WINDOWS_README.md)
2. Run `python capture_and_prepare.py` to create your dataset
3. Follow the workshop flow

## Getting Help

- Windows-specific issues: Check error messages carefully
- Path issues: Use forward slashes in Python (`C:/Users/...`)
- Permission issues: Try running as administrator
- Still stuck? The error message usually hints at the solution!