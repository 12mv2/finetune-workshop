# Hand Classification Workshop (Linux Setup)

Train a hand-detection classifier end-to-end using YOLOv8 and cloud GPUs.

⚠️ **Cost**: $10 minimum for RunPod • RTX A5000 ≈ $0.25/hour • **STOP THE POD WHEN DONE**

---

## Prerequisites

```bash
# Check Python version (3.8+ required)
python3 --version

# Clone repo and navigate
cd ~/projects/finetune-workshop
```

---

## Setup

### 1. System Dependencies

```bash
# Install ffmpeg (required for video processing)
sudo apt-get update
sudo apt-get install -y ffmpeg

# Optional: Fix Qt warnings for OpenCV
sudo apt-get install -y libxcb-xinerama0
```

### 2. Python Environment & Dependencies

```bash
# Using uv (recommended - fast and reliable)
uv sync

# Or standard pip with venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. Create Dataset

```bash
# Capture videos and extract frames
# IMPORTANT: Let each video record for the full 20 seconds for best results
# Don't press ESC - wait for automatic completion
python3 capture_and_prepare.py

# Verify dataset (expect ~200 images if recorded full 20s each)
find hand_cls -name "*.jpg" | wc -l
```

### 4. SSH Key Setup

```bash
# Check for existing key
ls -la ~/.ssh/

# Generate if needed
ssh-keygen -t ed25519 -C "your-email@example.com"
chmod 600 ~/.ssh/id_ed25519

# Copy public key to add to RunPod
cat ~/.ssh/id_ed25519.pub
```

### 5. RunPod Setup

1. Create account at [runpod.io](https://runpod.io) and add $10+ credit
2. Settings → SSH Keys → Add your public key
3. Deploy Pod:
   - GPU: **RTX A5000** (24GB)
   - Template: **PyTorch 2.4.0**
   - Expose TCP port 22 (for SSH/SCP access)
   - Container Disk: 50GB
   - Optional: Add network volume (10-20GB, mount: `/workspace`)

### 6. Connect to Pod

```bash
# Get PUBLIC_IP and PORT from RunPod dashboard under "Direct TCP Ports"
ssh root@<PUBLIC_IP> -p <PORT> -i ~/.ssh/id_ed25519

# Verify GPU
nvidia-smi
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

### 7. Upload Dataset

From your **local terminal**:

```bash
scp -r -P <PORT> -i ~/.ssh/id_ed25519 hand_cls root@<PUBLIC_IP>:/workspace/
```

### 8. Train on RunPod

In the **RunPod SSH session**:

```bash
# Install dependencies
pip install ultralytics

# Optional: Use tmux for persistent session
tmux new -s training

# Train (keep on one line!)
cd /workspace
yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 batch=32 device=0

# Detach from tmux: Ctrl+b, d
# Reattach later: tmux attach -t training
```

Expected output:
- ~240 train, ~60 val images
- High accuracy on simple dataset
- Weights: `/workspace/runs/classify/train/weights/best.pt`

### 9. Download Trained Model

From your **local terminal**:

```bash
scp -P <PORT> -i ~/.ssh/id_ed25519 \
  root@<PUBLIC_IP>:/workspace/runs/classify/train/weights/best.pt \
  ./best_trained.pt
```

### 10. Test Locally

```bash
python3 live_demo.py --weights best_trained.pt
```

- Webcam opens with real-time detection
- Green/red confidence indicators
- Press `q` to quit

### 11. Stop Your Pod

RunPod Dashboard → Stop/Terminate → Confirm

---

## Troubleshooting

**SSH connection fails:**
- Use Direct TCP connection (not bastion `ssh.runpod.io`)
- Check IP/port in RunPod dashboard
- Verify key permissions: `chmod 600 ~/.ssh/id_ed25519`

**Upload/download fails:**
- Use `-P` (uppercase) for port with `scp`
- Run from directory containing `hand_cls/`
- Bastion does not support `scp` - use Direct TCP

**Training fails:**
- Install ultralytics: `pip install ultralytics`
- Keep YOLO command on ONE line
- Check dataset: `ls /workspace/hand_cls/`

**Model path not found:**
- Check training output for exact path
- Could be `/workspace/runs/` or `/root/runs/`
- Sequential runs: `train`, `train2`, `train3`, etc.

**Camera issues:**
- Check permissions: `ls /dev/video*`
- Close other apps using camera
- Install opencv dependencies if needed
- Qt warnings: Install `libxcb-xinerama0`

**ffmpeg not found:**
- Install system package: `sudo apt-get install ffmpeg`
- Python package `ffmpeg-python` is different from system `ffmpeg`

---

## Quick Reference

### Complete Workflow

```bash
# LOCAL: Install system dependencies
sudo apt-get update
sudo apt-get install -y ffmpeg libxcb-xinerama0

# LOCAL: Setup and create dataset
cd ~/projects/finetune-workshop
source .venv/bin/activate  # or: uv sync

# Record full 20 seconds for each video (don't press ESC early!)
python3 capture_and_prepare.py
find hand_cls -name "*.jpg" | wc -l  # ~200 for full recording, min ~100 works

# LOCAL: Connect to RunPod
ssh root@<PUBLIC_IP> -p <PORT> -i ~/.ssh/id_ed25519

# RUNPOD: Start persistent session
tmux new -s training

# LOCAL: Upload dataset (new terminal)
scp -P <PORT> -r hand_cls root@<PUBLIC_IP>:/workspace/

# RUNPOD: Train
yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 batch=32 device=0

# RUNPOD: Detach from tmux
# Press: Ctrl+b, d

# LOCAL: Download trained model
scp -P <PORT> root@<PUBLIC_IP>:/workspace/runs/classify/train/weights/best.pt ./best_trained.pt

# LOCAL: Run demo
python3 live_demo.py --weights best_trained.pt

# RUNPOD DASHBOARD: Stop pod
```

### Useful Commands

```bash
# Check dataset structure
tree hand_cls -L 3

# Monitor GPU usage on RunPod
watch -n 1 nvidia-smi

# Reattach to tmux session
tmux attach -t training

# List all tmux sessions
tmux ls

# Count training images
find /workspace/hand_cls/train -name "*.jpg" | wc -l
```

### Model Paths

First run: `/workspace/runs/classify/train/weights/best.pt`
Subsequent: `/workspace/runs/classify/train2/weights/best.pt`, `train3/`, etc.

Check training output for "Results saved to:" message.

---

## What You Built

- ✅ Custom webcam dataset (~300 images)
- ✅ Cloud GPU training pipeline
- ✅ Real-time inference demo
- ✅ End-to-end ML workflow: data → training → inference

**Artifacts:**
- `hand_cls/` — dataset
- `best_trained.pt` — trained classifier (~3MB)
