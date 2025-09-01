# Troubleshooting Guide

Common issues and solutions for the Halloween Hand Classification Workshop.

## Table of Contents
- [Dataset Issues](#dataset-issues)
- [RunPod Problems](#runpod-problems)
- [Training Errors](#training-errors)
- [Demo Issues](#demo-issues)
- [Performance Problems](#performance-problems)

---

## Dataset Issues

### Error: "Dataset not found"
```
Dataset 'hand_cls' not found.
```

**Solution:**
1. Check you're in the correct directory:
   ```bash
   pwd  # Should show: /root/halloween-hand-workshop
   ```
2. Verify dataset structure:
   ```bash
   ls -la hand_cls/
   # Should show: train/ val/
   ```
3. If missing, re-upload your dataset

### Error: "No images found in data"
**Causes:**
- Wrong file extensions
- Incorrect folder structure
- Hidden files (starting with .)

**Solution:**
```bash
# Check for images
find hand_cls -name "*.jpg" -o -name "*.png" -o -name "*.jpeg"

# Remove hidden files
find hand_cls -name ".*" -delete

# Verify structure
tree hand_cls -d
```

### Imbalanced Classes Warning
**Symptom:** Model always predicts one class

**Solution:**
1. Check class balance:
   ```python
   import os
   for split in ['train', 'val']:
       for cls in ['hand_prop', 'not_hand']:
           path = f'hand_cls/{split}/{cls}'
           count = len(os.listdir(path))
           print(f"{split}/{cls}: {count} images")
   ```
2. Add more images to underrepresented class
3. Use class weights in training (advanced)

---

## RunPod Problems

### Cannot Connect to Pod
**Symptoms:**
- SSH connection refused
- Web terminal not loading

**Solutions:**
1. Check pod status is "Running"
2. Wait 2-3 minutes after starting
3. Try different connection method:
   - Web Terminal → SSH → Jupyter
4. Restart the pod

### GPU Not Available
```python
torch.cuda.is_available()  # Returns False
```

**Solutions:**
1. Check GPU allocation:
   ```bash
   nvidia-smi
   ```
2. Restart Python/Jupyter kernel
3. Verify PyTorch GPU version:
   ```python
   import torch
   print(torch.__version__)  # Should include +cu118 or similar
   ```
4. Reinstall PyTorch:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

### File Transfer Failing
**SCP Permission Denied:**
```bash
# Add -i flag with your SSH key
scp -i ~/.ssh/id_rsa -P [port] -r hand_cls root@[ip]:~/
```

**Large Files Timeout:**
- Use rsync instead:
  ```bash
  rsync -avz --progress -e "ssh -p [port]" hand_cls/ root@[ip]:~/hand_cls/
  ```
- Upload to cloud storage first (Google Drive, Dropbox)

---

## Training Errors

### CUDA Out of Memory
```
RuntimeError: CUDA out of memory
```

**Solutions (try in order):**
1. Reduce batch size:
   ```bash
   yolo classify train data=hand_cls model=yolov8n-cls.pt epochs=15 batch=16
   ```
2. Reduce image size:
   ```bash
   yolo classify train data=hand_cls model=yolov8n-cls.pt epochs=15 imgsz=128
   ```
3. Clear GPU memory:
   ```python
   import torch
   torch.cuda.empty_cache()
   ```
4. Kill other processes:
   ```bash
   pkill -f python
   ```

### Training Extremely Slow
**Causes:**
- CPU training instead of GPU
- Other processes using GPU
- Wrong device specified

**Solutions:**
1. Force GPU usage:
   ```bash
   yolo classify train data=hand_cls model=yolov8n-cls.pt device=0
   ```
2. Check GPU utilization:
   ```bash
   watch -n 1 nvidia-smi
   ```
3. Use smaller model for testing:
   ```bash
   # Test with 1 epoch first
   yolo classify train data=hand_cls model=yolov8n-cls.pt epochs=1
   ```

### Model Not Learning
**Symptoms:**
- Accuracy stays at 50%
- Loss not decreasing

**Solutions:**
1. Check learning rate:
   ```bash
   # Try higher learning rate
   yolo classify train data=hand_cls model=yolov8n-cls.pt lr0=0.01
   ```
2. Verify images are different between classes
3. Check for corrupted images:
   ```python
   from PIL import Image
   import os
   
   for root, dirs, files in os.walk('hand_cls'):
       for file in files:
           if file.endswith(('.jpg', '.png')):
               try:
                   img = Image.open(os.path.join(root, file))
                   img.verify()
               except:
                   print(f"Corrupted: {os.path.join(root, file)}")
   ```

---

## Demo Issues

### Webcam Not Found
```
RuntimeError: Could not open webcam
```

**Solutions:**
1. List available cameras:
   ```python
   import cv2
   for i in range(10):
       cap = cv2.VideoCapture(i)
       if cap.isOpened():
           print(f"Camera {i} available")
           cap.release()
   ```
2. Try different camera index:
   ```bash
   python live_demo.py --weights best.pt --camera 1
   ```
3. Check camera permissions (macOS):
   - System Preferences → Security & Privacy → Camera

### Low FPS / Laggy Demo
**Solutions:**
1. Reduce inference size:
   ```bash
   python live_demo.py --weights best.pt --imgsz 128
   ```
2. Skip frames:
   ```python
   # Process every 3rd frame
   if frame_count % 3 == 0:
       # run inference
   ```
3. Use threading for camera capture

### Overlay Not Showing
**Solutions:**
1. Check overlay path:
   ```bash
   ls assets/ghost.png
   ```
2. Run without overlay to test:
   ```bash
   python live_demo.py --weights best.pt --no-overlay
   ```
3. Verify PNG has transparency:
   ```python
   import cv2
   img = cv2.imread('assets/ghost.png', cv2.IMREAD_UNCHANGED)
   print(f"Channels: {img.shape[2]}")  # Should be 4 for RGBA
   ```

---

## Performance Problems

### Poor Classification Accuracy
**Solutions:**
1. Collect more diverse data
2. Train for more epochs:
   ```bash
   yolo classify train data=hand_cls model=yolov8n-cls.pt epochs=30
   ```
3. Try data augmentation:
   ```bash
   yolo classify train data=hand_cls model=yolov8n-cls.pt augment=True
   ```
4. Use larger model:
   ```bash
   yolo classify train data=hand_cls model=yolov8s-cls.pt
   ```

### Model Overfitting
**Symptoms:**
- Train accuracy >> Val accuracy
- Val loss increasing

**Solutions:**
1. Add more training data
2. Increase augmentation
3. Add dropout:
   ```bash
   yolo classify train data=hand_cls model=yolov8n-cls.pt dropout=0.2
   ```
4. Stop training early

---

## Quick Fixes Checklist

When something goes wrong, try these in order:

1. **Restart kernel/terminal**
2. **Check you're in the right directory**
3. **Verify GPU with `nvidia-smi`**
4. **Clear GPU cache**
5. **Reduce batch size**
6. **Check file permissions**
7. **Look at error message carefully**
8. **Google the exact error**
9. **Ask for help!**

---

## Getting Help

### During Workshop
- Ask the instructor
- Check workshop Slack/Discord
- Pair with another participant

### Online Resources
- [YOLOv8 Docs](https://docs.ultralytics.com)
- [RunPod Support](https://docs.runpod.io)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/yolov8)

### Debug Information to Collect
When asking for help, provide:
```bash
# System info
python --version
pip show ultralytics
nvidia-smi

# Dataset info
ls -la hand_cls/
find hand_cls -name "*.jpg" | wc -l

# Error message (full traceback)
# Your exact command
# What you've already tried
```

Remember: Every error is a learning opportunity! 🎃