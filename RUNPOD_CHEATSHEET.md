# RunPod Training Cheat Sheet

Quick reference for training hand detection models on RunPod GPU instances.

---

## RunPod Connection Info

**Your Current Instance:**
- IP: `69.30.85.172`
- Port: `22199`
- SSH Key: `~/.ssh/id_ed25519`

**SSH Connection:**
```bash
ssh root@69.30.85.172 -p 22199 -i ~/.ssh/id_ed25519
```

**First Time Setup (on RunPod):**
```bash
# Verify GPU is available
nvidia-smi
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Install ultralytics (required for YOLO)
pip install ultralytics

# Create workspace directory (if it doesn't exist)
mkdir -p /workspace
cd /workspace
```

---

## Option 1: Local Webcam Capture

**Step 1: Capture and Extract (Local)**
```bash
# Records 2x20 second videos, extracts frames automatically
python3 capture_and_prepare.py
```

**Step 2: Upload Dataset from Local**
```bash
scp -r -P 22199 -i ~/.ssh/id_ed25519 hand_cls root@69.30.85.172:/workspace/
```

**Step 3: Train on RunPod**
```bash
cd /workspace
yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 batch=32 device=0
```

**Step 4: Download Model (Local)**
```bash
# Model path varies - check training output for exact path
scp -P 22199 -i ~/.ssh/id_ed25519 root@69.30.85.172:/workspace/runs/classify/train/weights/best.pt ./best_trained.pt
```

**Step 5: Test Model (Local)**
```bash
python3 live_demo.py --weights best_trained.pt
```

---

## Option 2: iPhone Video Import

**Step 1: Transfer Videos from iPhone**
- Use AirDrop to send videos to Mac
- Or connect via USB and use Image Capture app
- Videos appear in Downloads folder

**Step 2: Convert and Prepare (Local)**
```bash
# Convert iPhone .mov to .mp4
ffmpeg -i hand.mov hand_video.mp4
ffmpeg -i not_hand.mov not_hand_video.mp4

# Extract frames to dataset (creates hand_cls folder)
python3 extract_frames_to_dataset.py
```

**Options when extracting:**
- Option 1: Replace existing images (start fresh)
- Option 2: Append to existing dataset (add more variety)

**Step 3: Upload Dataset**
```bash
scp -r -P 22199 -i ~/.ssh/id_ed25519 hand_cls root@69.30.85.172:/workspace/
```

**Step 4: Train on RunPod**
```bash
cd /workspace
yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 batch=32 device=0
```

**Step 5: Download Model (Local)**
```bash
# Check training output for exact path (could be /workspace/runs/ or /root/runs/)
scp -P 22199 -i ~/.ssh/id_ed25519 root@69.30.85.172:/root/runs/classify/train/weights/best.pt ./best_iphone.pt
```

**Step 6: Test Model (Local)**
```bash
python3 live_demo.py --weights best_iphone.pt
```

---

## Common Model Paths

Training saves models to different locations:

**First training run:**
- `/workspace/runs/classify/train/weights/best.pt`
- `/root/runs/classify/train/weights/best.pt`

**Subsequent runs:**
- `/workspace/runs/classify/train2/weights/best.pt`
- `/workspace/runs/classify/train3/weights/best.pt`

**Tip:** Check the training output for "Results saved to:" message

---

## Video Recording Tips

**For "hand" videos:**
- Show hands clearly in various positions
- Different angles and distances
- Move hands around naturally
- 20 seconds recommended

**For "not_hand" videos:**
- NO hands visible at all
- Include body positions that might trigger false positives
- Different distances from camera
- Various backgrounds and lighting
- Different clothing (especially sleeves)
- 20-40 seconds recommended

**Balance:** Try to keep similar number of frames for both classes

---

## Improving Model Accuracy

If you get false positives (detects hands when none present):

1. **Record more "not_hand" videos** showing problematic positions
2. **Convert and append:**
   ```bash
   ffmpeg -i new_not_hand.mov not_hand_video.mp4
   python3 extract_frames_to_dataset.py
   # Choose option 2: Append to existing
   ```
3. **Re-upload and retrain**
4. **Name models meaningfully:**
   ```bash
   # Download with descriptive names
   scp ... best.pt ./best_v1_200imgs.pt
   scp ... best.pt ./best_v2_400imgs.pt
   scp ... best.pt ./best_final.pt
   ```

---

## File Structure

**Local:**
```
finetune-workshop/
├── hand_video.mp4           # Recorded/converted video
├── not_hand_video.mp4       # Recorded/converted video
├── hand_cls/                # Dataset folder (upload this)
│   ├── train/
│   │   ├── hand/           # ~80% of hand frames
│   │   └── not_hand/       # ~80% of not_hand frames
│   └── val/
│       ├── hand/           # ~20% of hand frames
│       └── not_hand/       # ~20% of not_hand frames
└── best_trained.pt          # Downloaded model
```

**RunPod:**
```
/workspace/
├── hand_cls/               # Uploaded dataset
└── runs/classify/train/   # Training results
    └── weights/
        └── best.pt        # Trained model
```

---

## Troubleshooting

**Upload fails:**
- Check RunPod pod is running
- Verify IP and port from RunPod dashboard
- Use `-P` (capital P) for port with scp

**Training fails:**
- Install ultralytics: `pip install ultralytics`
- Keep command on ONE line (no line breaks)
- Check dataset uploaded to `/workspace/hand_cls/`

**Model path not found:**
- Check training output for exact path
- Could be `/workspace/runs/` or `/root/runs/`
- Could be `train`, `train2`, `train3` etc.

**Video conversion fails:**
- Install ffmpeg: `brew install ffmpeg`
- Check video file exists: `ls -la *.mov`

---

## Cost Reminder

**RTX A5000: ~$0.25/hour**

**STOP YOUR POD when done!**
```
RunPod Dashboard → Your Pod → Stop/Terminate
```

---

## Quick Commands Reference

```bash
# Check what's in current directory
ls -la

# Check dataset structure
tree hand_cls -L 2

# Count images in dataset
find hand_cls -name "*.jpg" | wc -l

# Monitor RunPod GPU usage
watch -n 1 nvidia-smi

# Test local camera
python3 live_demo.py --weights best_trained.pt
```
# ultra light cheat sheet:

python3 -m venv workshop-env
source workshop-env/bin/activate
pip install -r requirements.txt
python3 capture_and_prepare.py
find hand_cls -name "*.jpg" | wc -l
ssh root@69.30.85.32 -p 22041 -i ~/.ssh/id_ed25519
pip install ultralytics (inside RunPod pod)
scp -r -P 22041 -i ~/.ssh/id_ed25519 hand_cls root@69.30.85.32:/workspace/
cd /workspace && yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 batch=32 device=0
scp -P 22041 -i ~/.ssh/id_ed25519 "root@69.30.85.32:/workspace/runs/classify/train*/weights/best.pt" ./
python3 [live_demo.py](http://_vscodecontentref_/0) --weights best.pt
deactivate (when finished)