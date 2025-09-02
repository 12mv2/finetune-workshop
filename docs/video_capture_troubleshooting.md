# Video Capture Troubleshooting Guide

This guide covers common issues when using the video capture tools for dataset creation.

## Python Environment Issues

### ModuleNotFoundError: No module named 'ffmpeg'
**Problem**: You get this error even after installing ffmpeg with brew.

**Solution**: You need the Python package, not just the command-line tool:
```bash
# Wrong package:
pip install ffmpeg  # DON'T use this

# Correct package:
pip install ffmpeg-python  # USE THIS
```

### Multiple Python Versions
**Problem**: Package installed but still getting ModuleNotFoundError.

**Cause**: You have multiple Python installations (pyenv, system, homebrew).

**Solution**:
1. Check which Python you're using:
   ```bash
   which python3
   python3 --version
   ```

2. Install packages for the correct Python:
   ```bash
   # If using /usr/local/bin/python3
   /usr/local/bin/pip3 install ffmpeg-python
   
   # If using pyenv
   pyenv shell 3.11.6  # or your version
   pip install ffmpeg-python
   ```

3. Run scripts with the same Python:
   ```bash
   /usr/local/bin/python3 capture_and_prepare.py
   ```

## FFmpeg Installation

### ffmpeg: command not found
**Problem**: Python finds ffmpeg-python but can't find the ffmpeg binary.

**Solution**:
1. Install ffmpeg:
   ```bash
   brew install ffmpeg
   ```

2. Add to PATH if needed:
   ```bash
   export PATH="/opt/homebrew/bin:$PATH"
   ```

3. Verify installation:
   ```bash
   which ffmpeg
   ffmpeg -version
   ```

## Video Capture Issues

### Camera Not Found
**Problem**: Script can't access webcam.

**Solution**:
1. Grant camera permissions (macOS):
   - System Settings → Privacy & Security → Camera
   - Allow Terminal/iTerm access

2. Check camera is not in use:
   - Close Zoom, Teams, etc.
   - Restart if needed

### Poor Video Quality
**Problem**: Extracted images are blurry or dark.

**Solution**:
1. Ensure good lighting
2. Keep camera steady
3. Clean camera lens
4. Position yourself at appropriate distance

## Frame Extraction Issues

### Wrong Number of Frames
**Problem**: Not getting exactly 100 frames per video.

**Possible Causes**:
- Video recording was interrupted
- Frame extraction failed

**Solution**:
1. Check video files:
   ```bash
   ffmpeg -i hand_video.mp4 2>&1 | grep Duration
   ffmpeg -i not_hand_video.mp4 2>&1 | grep Duration
   ```
   Should show ~20 seconds each.

2. Re-run extraction:
   ```bash
   python3 extract_frames_to_dataset.py
   ```

### Images in Wrong Folders
**Problem**: Hand images mixed with not_hand images.

**Solution**:
1. Clear the dataset:
   ```bash
   rm -rf hand_cls/train/* hand_cls/val/*
   ```

2. Re-run extraction:
   ```bash
   python3 extract_frames_to_dataset.py
   ```

## Performance Tips

### Fast Dataset Creation
The video capture method is optimized for workshops:
- 2 minutes total time (vs 30+ for manual photos)
- Consistent lighting and camera settings
- Perfect 50/50 class balance
- Automatic 80/20 train/val split

### Better Model Performance
Video capture often gives better results because:
- Consistent camera angle and distance
- Same lighting conditions
- Natural hand movement variations
- No accidental similar backgrounds in different classes

## Common Mistakes to Avoid

1. **Installing wrong package**: Use `ffmpeg-python`, not `ffmpeg`
2. **Mixing Python environments**: Use the same Python for install and run
3. **Line breaks in commands**: Keep scp commands on one line
4. **Not checking video files**: Verify 20-second duration before extraction
5. **Skipping preparation phase**: The 2-second warning helps position correctly

## Need More Help?

If you're still having issues:
1. Check the main [README.md](../README.md) troubleshooting section
2. Verify all requirements are installed: `pip list | grep -E "ffmpeg|opencv"`
3. Try the manual photo collection method as a fallback