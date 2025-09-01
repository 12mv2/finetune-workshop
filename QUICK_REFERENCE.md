# Halloween Hand Workshop - Quick Reference

## Pre-Workshop Setup
```bash
# 1. Add SSH key to RunPod settings
cat ~/.ssh/id_ed25519.pub
# Copy entire output to RunPod Settings → SSH Keys

# 2. Clone repository
git clone https://github.com/12mv2/finetune-workshop.git
cd finetune-workshop

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create dataset structure
python3 create_dataset_structure.py
# Add your images to hand_cls/train and hand_cls/val folders
```

## RunPod Setup (Workshop Day)

### Create Pod
- GPU: **RTX A5000**
- Template: **PyTorch 2.4 + CUDA 12.4**
- SSH: **Enabled**
- Disk: **40-60 GB**

### Connect
```bash
# Use first connection option from RunPod
ssh [pod-id]@ssh.runpod.io -i ~/.ssh/id_ed25519
# Type 'yes' when prompted

# Install tmux
apt update && apt install -y tmux
tmux new -s workshop

# Run setup
curl -O https://raw.githubusercontent.com/12mv2/finetune-workshop/main/runpod_setup.sh
bash runpod_setup.sh
```

## Upload Dataset (FROM LOCAL TERMINAL)
```bash
# Open NEW terminal on your Mac
cd finetune-workshop

# Use the SECOND SSH option (with port)
scp -r -P [PORT] -i ~/.ssh/id_ed25519 hand_cls root@[IP]:/workspace/
```

## Train Model (ON RUNPOD)
```bash
cd /workspace

yolo classify train \
  model=yolov8n-cls.pt \
  data=/workspace/hand_cls \
  epochs=15 \
  imgsz=224 \
  batch=16 \
  device=0
```

## Download Model (FROM LOCAL TERMINAL)
```bash
# Find your model path first
ssh [pod-id]@ssh.runpod.io -i ~/.ssh/id_ed25519 "ls /workspace/runs/classify/*/weights/"

# Download it
scp -P [PORT] -i ~/.ssh/id_ed25519 root@[IP]:/workspace/runs/classify/train/weights/best.pt ./
```

## Run Demo (LOCAL)
```bash
python3 live_demo.py --weights best.pt
# Press 'q' to quit
```

## IMPORTANT: Stop Your Pod!
Go to RunPod dashboard → Stop or Terminate pod

## Common Fixes

| Problem | Solution |
|---------|----------|
| rsync error | Use scp instead |
| tmux not found | `apt update && apt install -y tmux` |
| Gradient error | Remove freeze=10, use batch=16 |
| Wrong terminal | Uploads from LOCAL, training on RUNPOD |
| Can't connect | Use second SSH option with port |

## Terminal Management
- **Terminal 1**: Local Mac (for uploads/downloads)
- **Terminal 2**: RunPod SSH (for training)
- **tmux commands**: 
  - Detach: `Ctrl+b, d`
  - Reattach: `tmux attach -t workshop`