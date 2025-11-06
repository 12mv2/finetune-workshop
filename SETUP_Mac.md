# Finetune Workshop (Mac Setup)

Get from zero to a working hand-detection classifier. Every step tested and verified.

⚠️ **Cost Alert**: Need $10 minimum for RunPod • RTX A5000 ≈ $0.25/hour • **STOP THE POD WHEN DONE**

---

## Prerequisites

- **Be in the correct project folder before running commands.**  
  Example:
  ```sh
  cd finetune-workshop
  ```
- **Python 3.8+ recommended** (check with `python3 --version`)
- Use a Python virtual environment to avoid conflicts:
  - Recommended: `python3 -m venv venv && source venv/bin/activate`
  - Or use `uv` if installed (manages venvs automatically)
- Upgrade `pip`:
  ```sh
  python3 -m pip install --upgrade pip
  ```

---

## Step 1: Setup Python Environment & Install Dependencies

If you have `uv`, run:
```sh
uv pip install -r requirements.txt
```

Otherwise:
```sh
pip install -r requirements.txt
```

> If you see version conflicts, note them and continue.

---

## Step 2: Create Dataset

Capture and prepare a small dataset:
```sh
python3 capture_and_prepare.py
```

This will:
- Open your webcam with instructions
- Record ~20 s with hands visible, then ~20 s without
- Extract ~300 images
- Create `hand_cls/train/` and `hand_cls/val/` folders

Verify:
```sh
find hand_cls -name "*.jpg" | wc -l
# Expect ~300
```

---

## Step 3: SSH Key Setup (macOS)

Check for an existing key:
```sh
ls -la ~/.ssh/
```

If none, create one:
```sh
ssh-keygen -t ed25519 -C "your-email@example.com"
# Press Enter for default path (~/.ssh/id_ed25519)
# Optionally set a simple passphrase (mlvisions)
```

Fix permissions:
```sh
chmod 600 ~/.ssh/id_ed25519
```

Copy your **public** key:
```sh
pbcopy < ~/.ssh/id_ed25519.pub
```

> Never share your **private** key. Only the **public** key is added to RunPod.

---

## Step 4: RunPod Account Setup

### Create Account
1. Go to runpod.io  
2. Sign up and verify email

### Add Funding
1. Billing → **Add Credit** ($10+)

### Add SSH Key
1. Settings → **SSH Keys** → **Add SSH Key**
2. Name: `Workshop Key`
3. Key: paste your public key
4. Save

---

## Step 5: Create GPU Pod 

### Configure Storage
1. **Add network volume**
2. **Size**: 10–20 GB
3. **Mount path**: `/workspace`
4. **Name**: `workshop-storage`

### Create Pod
1. **+ Deploy** → **Pods**
2. GPU: **RTX A5000** (24 GB)
3. Template: **PyTorch 2.4.0** (2.4 tested, 2.8 may work fine)
4. *(Optional)* Uncheck **Jupyter notebooks**

### Deploy
1. **Expose TCP port 22** so you get a **Public IP** and mapped **<PORT>**  
   *(You’ll see these later under “Direct TCP Ports.”)*
2. **Container Disk**: 50 GB (if available)
3. Click **Deploy Pod** and wait ~30 s

---

## Step 6: Connect to Pod

Use **SSH over exposed TCP** so `scp/sftp` work.

**Template**
```sh
ssh root@<PUBLIC_IP> -p <PORT> -i ~/.ssh/id_ed25519
```

**Example**
```sh
ssh root@69.30.85.208 -p 22055 -i ~/.ssh/id_ed25519
```

**Optional QoL**
```sh
ssh -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30 \
    root@<PUBLIC_IP> -p <PORT> -i ~/.ssh/id_ed25519
```

Accept the fingerprint (`yes`) and enter your key passphrase.

Verify environment:
```sh
nvidia-smi
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
ls -la /workspace
```

> If any command fails, confirm you used **exposed TCP** and not `ssh.runpod.io`.

---

## Step 7: Upload Dataset (macOS `scp`)

From your **local Mac**:

- from the directory that contains the hand class folder `hand_cls/`, or use and anbsolute path
  
```sh
scp -r -P <PORT> -i ~/.ssh/id_ed25519 hand_cls root@<PUBLIC_IP>:/workspace/
```

Notes:
- Replace `<PUBLIC_IP>` and `<PORT>` with the **Direct TCP** values shown on the pod
- `-P` is uppercase on macOS
- Do **not** include the angle brackets in the command
- Run from the directory that contains `hand_cls/`
- Result on pod: `/workspace/hand_cls/...
- Workspace directory does not exist in the runpod instace, it is created when the scp command is used

> Upload is ~1 minute for ~300 images.

---

## Step 8: Train Model (on the pod)

Install deps on the pod:
```sh
python3 -m pip install --upgrade pip
python3 -m pip install ultralytics
# or:
# python3 -m pip install -r /workspace/requirements.txt
```

Train:
```sh
cd /workspace
yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 batch=32 device=0
# if 'yolo' not found:
# python3 -m ultralytics classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 batch=32 device=0
```

Expected:
- ~240 train, ~60 val images (≈300 total)
- train images are used to train, val are used to validate / check how well the model is learning
- High accuracy on this simple dataset

Weights/Model:
```
/workspace/hand_cls/runs/classify/train/weights/best.pt
```
-best Model (checkpoint) from the 15 epochs

---

## Step 9: Download Trained Model (macOS `scp`)

From your **local Mac**:
```sh
scp -P <PORT> -i ~/.ssh/id_ed25519   root@<PUBLIC_IP>:/workspace/hand_cls/runs/classify/train/weights/best.pt   ./best_trained.pt
```

Notes:
- Use the **Direct TCP** `<PUBLIC_IP>` and `<PORT>`
- Do not include the angle brackets
- best.pt is renamed best_trained.pt
- saved to the directory you run the scp command 

---

## Step 10: Test Your Model (Local)

Run locally:
```sh
python3 live_demo.py --weights best_trained.pt
```

You should see:
- Webcam preview
- Real-time hand detection
- Green text for lower confidence, red for higher
- Press `q` to quit
- need to run the live_demo.py from directory where best_trained.pt lives, or provide the full path to best_trained.pt

🎉 You trained and ran a finetuned classifier.

---

## 🛑 Stop Your Pod

RunPod dashboard → Stop or Terminate → Confirm  
> Pods charge by the minute while running.

---

## Workshop Summary

**Result:** High accuracy on a small, simple dataset

### You built
- ✅ A custom webcam dataset  
- ✅ A cloud GPU training pipeline  
- ✅ A real-time demo using your model  
- ✅ End-to-end ML workflow from data → training → inference
- ✅ PyTorch framework (engine) with Ultralytics (library), used for both training and inference.

### Artifacts
- `hand_cls/` — dataset (few hundred images)  
- `best_trained.pt` — trained classifier (~3 MB)

---

## Troubleshooting

### Python version mismatch (local)
- Check `python3 --version` and `which python3`
- Use a venv (`venv` or `uv`) to isolate deps

### SSH key permissions (local)
```sh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

### `scp` issues
- Use **exposed TCP**: `root@<PUBLIC_IP>` with `-P <PORT>`
- `-P` must be uppercase on macOS
- Example:
  ```sh
  scp -r -P <PORT> -i ~/.ssh/id_ed25519 hand_cls root@<PUBLIC_IP>:/workspace/
  ```
- **Bastion `ssh.runpod.io` does not support `scp/sftp`**

### Camera issues (local)
- macOS: System Settings → Privacy & Security → **Camera**
- Close other apps using the camera
- Restart your terminal or Mac if needed

---
