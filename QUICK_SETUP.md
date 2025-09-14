# Complete Halloween Hand Detection Workshop

Get from zero to working AI hand detection in 15 minutes. Every step tested and verified.

⚠️ **Cost Alert**: Need $10 minimum for RunPod • RTX A5000 = $0.25/hour • **STOP POD WHEN DONE!**

---

## Step 1: Install Dependencies 

```bash
pip install -r requirements.txt
```

**Should install without warnings.** If you see version conflicts, note them but continue.

---

## Step 2: Create Dataset 

```bash
python3 capture_and_prepare.py
```

**This will:**
- Open your webcam with instructions
- Record 20 seconds with hands visible
- Record 20 seconds without hands
- Extract ~300 images automatically
- Create proper `hand_cls/train/` and `hand_cls/val/` folders

**Verify it worked:**
```bash
find hand_cls -name "*.jpg" | wc -l
# Should show ~300 images
```

---

## Step 3: SSH Key Setup 

**Check if you have SSH keys:**
```bash
ls -la ~/.ssh/
```

**If you see `id_ed25519.pub`** → Skip to getting your key

**If no SSH keys exist, create one:**
```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
# Press Enter for default location
# Use simple passphrase like "runpod" (easier for workshop)
# Press Enter again to confirm passphrase
```

**Get your public key:**
```bash
cat ~/.ssh/id_ed25519.pub
```

**Copy the entire output** (starts with `ssh-ed25519`) - you'll need this for RunPod.

---

## Step 4: RunPod Account Setup 

### Create Account
1. Go to [runpod.io](https://runpod.io)
2. **Sign Up** with email/password
3. Verify your email

### Add Funding
1. Go to **Billing** 
2. **Add Credit** → Add $10+ (minimum required)
3. Add credit card or PayPal

### Add SSH Key
1. Go to **Settings** (gear icon)
2. Click **SSH Keys**
3. Click **Add SSH Key**
4. **Name**: "Workshop Key"
5. **Key**: Paste your public key from Step 3 (email part is optional)
6. Click **Add Key**

---

## Step 5: Create GPU Pod 

### Configure Storage
1. Click **Add network volume** at top
2. **Size**: 10-20GB 
3. **Mount path**: `/workspace`
4. **Name**: "workshop-storage"

### Create Pod
1. Click **+ Deploy** → **Pods**
2. Select **RTX A5000** (24GB VRAM, ~$0.25/hour)
3. Template: **PyTorch 2.4.0** (more stable than newer versions)
4. **Uncheck Jupyter notebooks** (we don't need them)

### Deploy
1. Enable **SSH** (port 22)
2. **Container Disk**: 50GB (if available)
3. Click **Deploy Pod**
4. **Wait ~30 seconds** for provisioning

---

## Step 6: Connect to Pod 

**Copy SSH command from RunPod dashboard** (looks like):
```
ssh [pod-id]@ssh.runpod.io -i ~/.ssh/id_ed25519
```

**Connect (keep entire command on ONE line):**
```bash
ssh [your-pod-id]@ssh.runpod.io -i ~/.ssh/id_ed25519
# Type 'yes' when asked about fingerprint
# Enter your passphrase when prompted
```

**You should see the RunPod welcome message and get a root prompt.**

**Test your setup:**
```bash
nvidia-smi
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
ls -la /workspace
```

All should work without errors.

---

## Step 7: Upload Dataset 

**From your LOCAL terminal** (open new tab/window), upload your dataset.

**Use the SAME connection details from Step 6** (the SSH command that worked):

If your SSH command was:
```bash
ssh 20egall4xozk4a-6441145b@ssh.runpod.io -i ~/.ssh/id_ed25519
```
ssh 20egall4xozk4a-6441145b@ssh.runpod.io -i ~/.ssh/id_ed25519
Then your scp command is:
```bash
scp -r -i ~/.ssh/id_ed25519 hand_cls 20egall4xozk4a-6441145b@ssh.runpod.io:/workspace/
```

**Pattern: Replace `ssh` with `scp -r`, add source and destination**
- Keep the same user@host part
- Keep the same SSH key (`-i ~/.ssh/id_ed25519`)
- Add what to upload (`hand_cls`) and where (`:/workspace/`)

**This uploads ~300 images and takes 1 minute.**

---

## Step 8: Train Model 

**Back in your RunPod terminal:**

```bash
cd /workspace
yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 batch=32 device=0
```

**CRITICAL: Keep entire command on ONE line** or YOLO will ignore your parameters.

**You should see:**
- "found ~240 images in 2 classes" for training
- "found ~60 images in 2 classes" for validation  
- Final accuracy: 100% (or very close)

**Model saved to:** `/workspace/hand_cls/runs/classify/train/weights/best.pt`

---

## Step 9: Download Trained Model 

**From your LOCAL terminal:**

```bash
scp -P [port] -i ~/.ssh/id_ed25519 root@[ip-address]:/workspace/hand_cls/runs/classify/train/weights/best.pt ./best_trained.pt
```

**Use the exact port and IP from RunPod dashboard.**

**Download takes <1 second** (model is ~3MB).

---

## Step 10: Test Your Model (immediate)

**Run your newly trained model:**

```bash
python3 live_demo.py --weights best_trained.pt
```

**You should see:**
- Webcam opens
- Real-time hand detection
- Green text (0-84% confidence): "Hand detected"
- Red text (85%+ confidence): "HIGH CONFIDENCE HAND!"
- Press 'q' to quit

**🎉 Congratulations! You've trained and deployed an ML model!**

---

## 🛑 CRITICAL: Stop Your Pod!

**Go back to RunPod dashboard:**
1. Find your running pod
2. Click **Stop** or **Terminate**  
3. **Confirm termination**

**Pods charge by the minute while running!**

---

## Workshop Summary

**Result:** Custom AI hand detection model with 100% accuracy

### What You Built:
- ✅ Custom dataset from webcam video
- ✅ Cloud GPU training pipeline  
- ✅ Real-time hand detection system
- ✅ Complete ML workflow from data to deployment

### Files You Created:
- `hand_cls/` - Your training dataset (~600 images)
- `best_trained.pt` - Your custom AI model (3MB)
- Working webcam demo with your model

---

## Troubleshooting

### Command Issues
**Problem**: "data argument missing" or wrong dataset  
**Solution**: Keep entire command on ONE line (no line breaks)

### SSH Connection  
**Problem**: "Permission denied"  
**Solution**: Check SSH key added to RunPod settings

### Upload Fails
**Problem**: scp command error  
**Solution**: Get exact command from RunPod dashboard, keep on one line

### Training Too Fast
**Problem**: Trains in seconds but uses wrong dataset  
**Solution**: Check that command is on single line, verify dataset path

### Camera Issues
**Problem**: Webcam doesn't open  
**Solution**: Check camera permissions, try different browser/app first

---

**For detailed troubleshooting and advanced options, see [README.md](README.md)**