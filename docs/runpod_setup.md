# RunPod Setup Guide

This guide walks you through setting up a GPU pod on RunPod for the workshop.

## Prerequisites

- RunPod account (sign up at [runpod.io](https://runpod.io))
- Credit added to your account ($5-10 is plenty for the workshop)
- Your dataset prepared locally

## Step 1: Create a New Pod

1. Log into RunPod and click **"+ Deploy"**
2. Select **"Pods"** → **"GPU Pod"**

## Step 2: Choose Your GPU

### Recommended GPUs (sorted by cost):
- **RTX 3090** (~$0.20-0.30/hr) - Best value for this workshop
- **RTX A4000** (~$0.25-0.35/hr) - Good alternative
- **RTX 4090** (~$0.40-0.50/hr) - Faster but overkill
- **T4** (~$0.15-0.20/hr) - Budget option, slightly slower

**Tip**: Check "Community Cloud" for cheaper options!

## Step 3: Select Template

1. Click **"Change Template"**
2. Search for **"PyTorch"**
3. Select **"PyTorch 2.4 + CUDA 12.4"** template
   - Full name: `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`
   - This includes CUDA, Python 3.11, and Jupyter

## Step 4: Configure Resources

- **Container Disk**: 20 GB (default is fine)
- **Volume Disk**: 20 GB (recommended for persistent storage)
- **Expose SSH Port**: Check "Expose SSH" or ensure port 22 is exposed
- **Skip Jupyter**: We'll use SSH for this workshop

## Step 5: Deploy Pod

1. Click **"Deploy On-Demand Pod"**
2. Wait 1-2 minutes for pod to initialize
3. You'll see status change from "Creating" → "Running"

## Step 6: Connect to Your Pod via SSH

1. Click **"Connect"** → **"Connect via SSH"**
2. Copy the SSH command (it will look like: `ssh root@[pod-ip-or-host]`)
3. Open your local terminal and paste the command

**First-time connection:**
```bash
# Connect to your pod
ssh root@[pod-ip-or-host]

# Start a persistent session (recommended)
tmux new -s train
```

**Why tmux?** It keeps your training running even if your SSH connection drops. To reconnect:
```bash
ssh root@[pod-ip-or-host]
tmux attach -t train
```

## Step 7: Initial Setup

Once connected, run these commands:

```bash
# Quick environment check
python - <<'EOF'
import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
EOF

# Check GPU details
nvidia-smi | head -n 10

# Install dependencies
pip install --upgrade pip
pip install ultralytics opencv-python

# Verify installation
yolo version
```

## Step 8: Transfer Your Dataset

From your LOCAL terminal (where you prepared the dataset):

### Using rsync (Recommended)
```bash
# Navigate to parent of hand_cls folder
cd /path/to/your/dataset/parent

# Sync the dataset (replace [pod-host] with your RunPod hostname)
rsync -avh hand_cls/ root@[pod-host]:/workspace/hand_cls/
```

### Using scp (Alternative)
```bash
# Copy the entire folder
scp -r hand_cls/ root@[pod-host]:/workspace/hand_cls/
```

**Note**: RunPod typically uses standard SSH port 22, so no `-P` flag needed unless specified otherwise.

## Step 9: Verify Setup

Run this checklist:

```bash
# Check dataset location
ls -la /workspace/hand_cls/
# Should show: train/ val/

# Check dataset structure
ls /workspace/hand_cls/train/  # Should show: hand not_hand
ls /workspace/hand_cls/val/    # Should show: hand not_hand

# Count images
find /workspace/hand_cls -name "*.jpg" -o -name "*.png" | wc -l

# Test YOLOv8 with correct data path
yolo classify train data=/workspace/hand_cls epochs=1 device=0
# This will download yolov8n-cls.pt from Hugging Face and verify setup
```

## Step 10: Start Training!

You're ready to train:

```bash
cd /workspace

# Full training command
yolo classify train \
  model=yolov8n-cls.pt \
  data=/workspace/hand_cls \
  epochs=15 \
  imgsz=224 \
  batch=32 \
  device=0 \
  freeze=10

# Training progress appears in real-time
# Results saved to runs/classify/train*/
```

## Monitoring Training

- Training progress appears in real-time
- Results saved to `runs/classify/train/`
- Best weights at `runs/classify/train/weights/best.pt`

## Downloading Results

After training completes, download your model to your local Mac:

```bash
# First, find the exact path on RunPod
ssh root@[pod-host] "ls /workspace/runs/classify/*/weights/best.pt"

# From your LOCAL terminal, download the model
scp root@[pod-host]:/workspace/runs/classify/train/weights/best.pt ./

# Verify download
ls -lh best.pt  # Should be ~5-10MB
```

## Stopping Your Pod

**IMPORTANT**: Don't forget to stop your pod when done!

1. Go to RunPod dashboard
2. Find your pod
3. Click **"Stop"** or **"Terminate"**
4. Confirm the action

**Tip**: "Stop" keeps your data but still charges storage. "Terminate" deletes everything and stops all charges.

## tmux Quick Reference

Essential tmux commands for managing your training session:

```bash
# Start new session
tmux new -s train

# Detach from session (training continues)
Ctrl+b, then d

# List sessions
tmux ls

# Reattach to session
tmux attach -t train

# Kill session (if needed)
tmux kill-session -t train
```

## Troubleshooting

### "CUDA out of memory"
- Reduce batch size: `batch=16` or `batch=8`
- Use smaller image size: `imgsz=128`

### "Connection refused"
- Check pod is "Running" status
- Try Web Terminal instead of SSH
- Verify your SSH key is added to RunPod

### "Module not found"
- Make sure you ran `pip install -r requirements.txt`
- Try `pip install ultralytics --upgrade`

### Slow training
- Verify GPU with: `nvidia-smi`
- Check no other processes: `ps aux | grep python`
- Consider upgrading to faster GPU

## Cost Optimization Tips

1. **Use Spot Instances**: 50-80% cheaper but can be interrupted
2. **Stop immediately after training**: Don't leave running
3. **Download results quickly**: Then terminate pod
4. **Test locally first**: Ensure dataset is ready before starting pod

## Workshop Day Checklist

- [ ] RunPod account created and funded
- [ ] Dataset prepared and ready to upload
- [ ] Know which GPU to select
- [ ] Practiced file transfer method
- [ ] Bookmark this guide!

Happy training! 🎃