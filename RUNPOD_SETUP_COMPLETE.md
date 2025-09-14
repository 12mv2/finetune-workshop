# RunPod Quick Setup - Cloud GPU Training

⚠️ **Need $10 minimum** • **RTX A5000 = $0.25/hour** • **STOP POD WHEN DONE!**

## 1. SSH Key Setup

Check existing keys:
```bash
ls -la ~/.ssh/
```

If no `id_ed25519.pub`, create one:
```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
# Press Enter 3 times (use defaults)
```

Get your public key:
```bash
cat ~/.ssh/id_ed25519.pub
```
**Copy entire output** (starts with `ssh-ed25519`)

## 2. RunPod Account

1. [runpod.io](https://runpod.io) → Sign Up
2. **Billing** → Add $10+ credit
3. **Settings** → **SSH Keys** → Add your public key

## 3. Create Pod

1. **+ Deploy** → **Pods**
2. Select **RTX A5000** (24GB VRAM)
3. Template: **PyTorch 2.4 + CUDA 12.4**
4. Enable **SSH** (port 22)
5. Container Disk: **50GB**
6. **Deploy Pod** → Wait 2-5 minutes

## 4. Connect

Copy SSH command from RunPod dashboard:
```bash
ssh root@ssh.runpod.io -p 12345
# Type 'yes' when prompted
```

Install tmux (optional):
```bash
apt update && apt install -y tmux
tmux new -s workshop
```

## 5. Test Setup

```bash
nvidia-smi
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
pip install ultralytics opencv-python
```

## 🛑 Stop Pod When Done!

RunPod dashboard → Find your pod → **Stop** → Confirm

---

**Next**: Upload dataset and train model