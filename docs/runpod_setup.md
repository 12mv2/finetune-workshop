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
3. Select **"RunPod Pytorch 2.0.1"** (or latest version)
   - This includes CUDA, Python 3.10+, and Jupyter

## Step 4: Configure Resources

- **Container Disk**: 20 GB (default is fine)
- **Volume Disk**: 0 GB (we don't need persistent storage)
- **Ports**: Leave default

## Step 5: Deploy Pod

1. Click **"Deploy On-Demand Pod"**
2. Wait 1-2 minutes for pod to initialize
3. You'll see status change from "Creating" → "Running"

## Step 6: Connect to Your Pod

### Option A: Web Terminal (Easiest)
1. Click **"Connect"** button
2. Select **"Connect to Web Terminal"**
3. You now have a browser-based terminal!

### Option B: SSH Connection
1. Click **"Connect"** → **"Connect via SSH"**
2. Copy the SSH command
3. Open your local terminal and paste:
```bash
ssh root@[your-pod-ip] -p [port] -i ~/.ssh/id_rsa
```

### Option C: Jupyter Lab
1. Click **"Connect"** → **"Connect to Jupyter Lab"**
2. Great for running the notebook interactively

## Step 7: Initial Setup

Once connected, run these commands:

```bash
# Update pip
pip install --upgrade pip

# Clone the workshop repository
git clone https://github.com/[your-username]/halloween-hand-workshop.git
cd halloween-hand-workshop

# Install dependencies
pip install -r requirements.txt

# Verify GPU is available
python -c "import torch; print(f'GPU Available: {torch.cuda.is_available()}')"
```

## Step 8: Transfer Your Dataset

### Option A: Using SCP (from your local machine)
```bash
# From your LOCAL terminal (not RunPod)
scp -P [port] -r hand_cls root@[your-pod-ip]:~/halloween-hand-workshop/
```

### Option B: Using rsync (better for large files)
```bash
# From your LOCAL terminal
rsync -avz -e "ssh -p [port]" hand_cls/ root@[your-pod-ip]:~/halloween-hand-workshop/hand_cls/
```

### Option C: Upload to Google Drive
1. Upload your `hand_cls` folder to Google Drive
2. In RunPod terminal:
```bash
pip install gdown
# Get the file ID from your Google Drive share link
gdown --folder https://drive.google.com/drive/folders/[your-folder-id]
```

## Step 9: Verify Setup

Run this checklist:

```bash
# Check you're in the right directory
pwd  # Should show: /root/halloween-hand-workshop

# Check dataset structure
ls hand_cls/train/  # Should show: hand_prop not_hand
ls hand_cls/val/    # Should show: hand_prop not_hand

# Count images
find hand_cls -name "*.jpg" -o -name "*.png" | wc -l

# Test YOLOv8 import
python -c "from ultralytics import YOLO; print('YOLOv8 ready!')"
```

## Step 10: Start Training!

You're ready to train:

```bash
# Run the training script
bash train.sh

# Or run directly:
yolo classify train data=hand_cls model=yolov8n-cls.pt epochs=15 imgsz=224 device=0
```

## Monitoring Training

- Training progress appears in real-time
- Results saved to `runs/classify/train/`
- Best weights at `runs/classify/train/weights/best.pt`

## Downloading Results

After training, download your model:

```bash
# From your LOCAL terminal
scp -P [port] root@[your-pod-ip]:~/halloween-hand-workshop/runs/classify/train/weights/best.pt ./
```

## Stopping Your Pod

**IMPORTANT**: Don't forget to stop your pod when done!

1. Go to RunPod dashboard
2. Find your pod
3. Click **"Stop"** or **"Terminate"**
4. Confirm the action

**Tip**: "Stop" keeps your data but still charges storage. "Terminate" deletes everything and stops all charges.

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