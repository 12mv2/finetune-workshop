# RunPod Quick Setup Guide

## 1. Create Pod

1. Log into RunPod
2. Click **"+ Deploy"** → **"Pods"**
3. Select **RTX A5000** GPU (24GB VRAM)
4. Choose template: **PyTorch 2.4 + CUDA 12.4**
   - Or use image: `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`
5. Configure:
   - **Expose SSH**: ✓ (port 22)
   - **Container Disk**: 40-60 GB
   - **Network Volume**: 20 GB at `/workspace` (optional but recommended)
6. Click **"Deploy On-Demand Pod"**

## 2. Connect via SSH

```bash
# Copy SSH command from RunPod dashboard
ssh root@[pod-ip]

# Start tmux session (recommended)
tmux new -s workshop
```

## 3. Quick Setup

```bash
# Download and run setup script
curl -O https://raw.githubusercontent.com/12mv2/finetune-workshop/main/runpod_setup.sh
bash runpod_setup.sh
```

Or manually:
```bash
# Check GPU
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
nvidia-smi

# Install dependencies
pip install --upgrade pip
pip install ultralytics opencv-python
```

## 4. Upload Dataset

From your LOCAL terminal:
```bash
# Navigate to dataset parent directory
cd /path/to/your/dataset/parent

# Upload to RunPod
rsync -avh hand_cls/ root@[pod-ip]:/workspace/hand_cls/
```

## 5. Train Model

On RunPod:
```bash
cd /workspace

yolo classify train \
  model=yolov8n-cls.pt \
  data=/workspace/hand_cls \
  epochs=15 \
  imgsz=224 \
  batch=32 \
  device=0 \
  freeze=10
```

## 6. Download Results

From your LOCAL terminal:
```bash
# Download trained model
scp root@[pod-ip]:/workspace/runs/classify/train/weights/best.pt ./
```

## 7. Stop Pod

**IMPORTANT**: Stop your pod when done to avoid charges!

---

## Troubleshooting

### Connection Issues
- Ensure pod shows "Running" status
- Try reconnecting after 1-2 minutes
- Check RunPod dashboard for SSH command

### CUDA Not Available
- Verify you selected GPU template
- Restart pod if needed
- Check with: `nvidia-smi`

### Out of Memory
- Reduce batch size: `batch=16` or `batch=8`
- Use smaller image: `imgsz=128`

### tmux Commands
- Detach: `Ctrl+b, d`
- Reattach: `tmux attach -t workshop`
- List: `tmux ls`