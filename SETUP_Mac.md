# Complete Halloween Hand Detection Workshop (Mac Setup)

Get from zero to working AI hand detection in 15 minutes on your Mac. Every step tested and verified.

⚠️ **Cost Alert**: Need $10 minimum for RunPod • RTX A5000 = $0.25/hour • **STOP POD WHEN DONE!**

---

## Prerequisites

- **Make sure you are in the correct project folder before running commands.**  
  For example, if your project folder is named `finetune-workshop`, navigate into it with:  
  ```sh
  cd finetune-workshop
  ```
- **Python 3.8+ recommended** (check with `python3 --version`)
- Use a Python virtual environment to avoid conflicts:
  - Recommended: `python3 -m venv venv` then `source venv/bin/activate`
  - Or use `uv` if installed (`uv` is a tool that automatically manages virtual environments)
- Make sure `pip` is up to date:
  ```sh
  python3 -m pip install --upgrade pip
  ```

---

## Step 1: Setup Python Environment & Install Dependencies

If you have `uv` installed, run:

```sh
uv pip install -r requirements.txt
```

If not, activate your virtual environment or use your system Python and run:

```sh
pip install -r requirements.txt
```

**Should install without warnings.** If you see version conflicts, note them but continue.

---

## Step 2: Create Dataset

Run the dataset capture script:

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

```sh
find hand_cls -name "*.jpg" | wc -l
# Should show ~300 images
```

---

## Step 3: SSH Key Setup (Mac Specific)

**Check if you have SSH keys:**

```sh
ls -la ~/.ssh/
```

If you see `id_ed25519.pub` → Skip to copying your key

If no SSH keys exist, create one:

```sh
ssh-keygen -t ed25519 -C "your-email@example.com"
# Press Enter for default location (~/.ssh/id_ed25519)
# Use a simple passphrase like "runpod" (easier for workshop)
# Press Enter again to confirm passphrase
```

**Set correct file permissions on your private key file:**

```sh
chmod 600 ~/.ssh/id_ed25519
```

**Copy your public key to clipboard (Mac only):**

```sh
pbcopy < ~/.ssh/id_ed25519.pub
```

**WARNING:**  
- Your **private key (`~/.ssh/id_ed25519`) must never be shared**.  
- Only share the **public key** (copied above) when adding to RunPod.

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
5. **Key**: Paste your public key from Step 3 (email part optional)  
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

```sh
ssh [pod-id]@ssh.runpod.io -i ~/.ssh/id_ed25519
```

**Connect (keep entire command on ONE line):**

```sh
ssh your-pod-id@ssh.runpod.io -i ~/.ssh/id_ed25519
# Type 'yes' when asked about fingerprint
# Enter your passphrase when prompted
```

You should see the RunPod welcome message and get a root prompt.

**Test your setup:**

```sh
nvidia-smi
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
ls -la /workspace
```

All should work without errors.

---

## Step 7: Upload Dataset (Mac SCP Instructions)

**From your LOCAL terminal (Mac):**

Use this form of the `scp` command to upload your dataset folder:

```sh
scp -r -P 22 -i ~/.ssh/id_ed25519 hand_cls your-pod-id@ssh.runpod.io:/workspace/
```

- Replace `your-pod-id` with your actual pod ID from RunPod dashboard (e.g., `20egall4xozk4a-6441145b`)  
- Replace `22` with the actual SSH port if different (default is 22)  
- Do **NOT** include brackets `[]` in your command  
- The `-r` flag copies directories recursively  
- The `-i` flag specifies your private key  

**This uploads ~300 images and takes about 1 minute.**

---

## Step 8: Train Model

Back in your RunPod terminal:

```sh
cd /workspace
yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 batch=32 device=0
```

**CRITICAL:** Keep entire command on ONE line or YOLO will ignore your parameters.

You should see:

- "found ~240 images in 2 classes" for training  
- "found ~60 images in 2 classes" for validation  
- Final accuracy: 100% (or very close)  

Model saved to: `/workspace/hand_cls/runs/classify/train/weights/best.pt`

---

## Step 9: Download Trained Model (Mac SCP)

From your LOCAL terminal (Mac), download your trained model with:

```sh
scp -P 22 -i ~/.ssh/id_ed25519 your-pod-id@ssh.runpod.io:/workspace/hand_cls/runs/classify/train/weights/best.pt ./best_trained.pt
```

- Replace `your-pod-id` and `22` with your actual pod ID and SSH port  
- Do **NOT** include brackets `[]` in your command  

Download takes less than 1 second (model is ~3MB).

---

## Step 10: Test Your Model (Immediate)

Run your newly trained model locally:

```sh
python3 live_demo.py --weights best_trained.pt
```

You should see:

- Webcam opens  
- Real-time hand detection  
- Green text (0-84% confidence): "Hand detected"  
- Red text (85%+ confidence): "HIGH CONFIDENCE HAND!"  
- Press 'q' to quit  

🎉 Congratulations! You've trained and deployed an ML model!

---

## 🛑 CRITICAL: Stop Your Pod!

**Go back to RunPod dashboard:**

1. Find your running pod  
2. Click **Stop** or **Terminate**  
3. Confirm termination  

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

### Python Version Mismatch

- Mac may have multiple Python versions (system Python, Homebrew Python, pyenv-managed Python)  
- Check `python3 --version` and `which python3` to confirm which Python is running  
- Use a virtual environment (`venv` or `uv`) to isolate dependencies and avoid conflicts  

### SSH Key Permissions Issue

- If you get permission errors connecting to RunPod:  
  ```bash
  chmod 600 ~/.ssh/id_ed25519
  chmod 644 ~/.ssh/id_ed25519.pub
  ```
- Ensure your private key is NOT world-readable  

### SCP Common Issues

- Make sure you replace placeholders (`your-pod-id`, `22`) with actual values from the RunPod dashboard  
- Do **NOT** include brackets `[]` in your commands  
- Use `-P` (uppercase) to specify port on macOS `scp`  
- Example correct command:  
  ```sh
  scp -r -P 22 -i ~/.ssh/id_ed25519 hand_cls your-pod-id@ssh.runpod.io:/workspace/
  ```
- If SCP fails, double-check SSH connection first with the `ssh` command  

### Camera Issues

- If webcam doesn't open in the dataset creation step or live demo:  
  - Check your Mac's camera permissions in System Preferences → Security & Privacy → Camera  
  - Try closing other apps that might be using the camera  
  - Restart your terminal or computer if needed  

---

**For detailed troubleshooting and advanced options, see [README.md](README.md)**