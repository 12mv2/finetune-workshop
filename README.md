# Quick Object Classification Workshop: Halloween Hand

> ## 💻 Platform-Specific Instructions
> - **Windows Users** → [**Click here for Windows instructions**](WINDOWS_README.md) 🪟
> - **macOS/Linux Users** → Continue reading below 🍎🐧

This repository provides the materials for a 15-minute workshop on fine‑tuning **Ultralytics YOLOv8** for image classification.  The goal is to train a binary classifier that detects whether a hand is visible in an image and then build a fun live demo that reacts when the hand appears.

## 🚀 Quick Start Cheat Sheet

### Complete Workflow (Tested, 15 min total)

```bash
# 1. LOCAL: Install dependencies & create dataset
pip install -r requirements.txt
python3 capture_and_prepare.py  # Records videos & extracts ~300 images

# 2. RUNPOD: Setup account, create RTX A5000 pod with network storage

# 3. LOCAL: Upload dataset 
scp -r -P [PORT] -i ~/.ssh/id_ed25519 hand_cls root@[IP]:/workspace/

# 4. RUNPOD: Train (keep command on one line!)
yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 batch=32 device=0

# 5. LOCAL: Download model
scp -P [PORT] -i ~/.ssh/id_ed25519 root@[IP]:/workspace/hand_cls/runs/classify/train/weights/best.pt ./

# 6. LOCAL: Test your model
python3 live_demo.py --weights best.pt
```

### Option B: Fast Video Upload (Experimental, 10 min)

```bash
# 1. LOCAL: Record videos only
python3 capture_videos_only.py

# 2. LOCAL: Upload videos (40MB vs 400MB!)
./upload_videos.sh

# 3. RUNPOD: Extract & train
./runpod_extract_and_train.sh

# 4-5. Same as above
```

**💡 When in doubt, use Option A (traditional) - it always works!

## ✅ Tested Workshop Flow

This workshop has been fully tested end-to-end. Here's what we'll do:

1. **Local Setup** (5 min)
   - Install dependencies: `pip install -r requirements.txt`
   - Create dataset with video capture: `python3 capture_and_prepare.py` 
   - Records 2x20 second videos → extracts ~300 images automatically
   - Much faster than manual photos and gives better results!

2. **RunPod GPU Setup** (15 min)
   - Add SSH key to RunPod settings
   - Create RTX A5000 pod with PyTorch 2.4 + CUDA 12.4
   - Connect via SSH (accept fingerprint prompt)
   - Install tmux: `apt update && apt install -y tmux`

3. **Upload & Train** (2-5 min with fast method!)
   - **Option A - Fast Video Upload (Recommended)**: 
     - Upload 2 videos: `./upload_videos.sh` (40MB in 1-2 min)
     - Extract & train on RunPod: `./runpod_extract_and_train.sh`
   - **Option B - Traditional**: 
     - Upload 200+ images: `scp -r -P [port] hand_cls root@[ip]:/workspace/` (400MB in 10-15 min)
   - Training completes in <1 minute on RTX A5000

4. **Download & Demo** (2 min)
   - Download model: `scp -P [port] root@[ip]:/workspace/runs/classify/train*/weights/best.pt ./`
   - Run demo: `python3 live_demo.py --weights best.pt`
   - Webcam opens with MPS acceleration on Mac

## Objectives

* **Fine‑tune a pretrained model.**  We will start from the `yolov8n‑cls.pt` weights (pretrained on ImageNet) and fine‑tune only the classifier head to distinguish two classes: `hand` and `not_hand`.
* **Prepare a simple dataset.**  You will capture ~100 photos on your phone, organise them into a folder structure and split them into training/validation sets.  No bounding boxes or keypoints are needed—class names are inferred from folder names.
* **Train and evaluate.**  We will train the classifier using a GPU pod on RunPod, monitor accuracy, and explore the outputs.
* **Live demo.**  Finally we will run a webcam loop locally on your Mac; when the `hand` class is detected, messages appear on screen. Get 100% confidence to unlock the special ghost overlay!

## Getting Started

### Local Preparation (on your Mac)

1. **Clone this repository**:
   ```bash
   git clone https://github.com/[your-username]/halloween-hand-workshop.git
   cd halloween-hand-workshop
   ```

2. **Install dependencies locally** (for dataset prep and demo):
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare your dataset** (see Dataset Preparation below)

### RunPod Training

1. **Create a RunPod GPU pod** using the PyTorch 2.4 + CUDA 12.4 template (see [RunPod Setup Guide](docs/runpod_setup.md))

2. **Connect via SSH** and start a tmux session:
   ```bash
   ssh root@[pod-host]
   tmux new -s train
   ```

3. **Transfer your dataset** from your local machine:
   ```bash
   # From your LOCAL terminal
   rsync -avh hand_cls/ root@[pod-host]:/workspace/hand_cls/
   ```

4. **Run training** - The pretrained `yolov8n‑cls.pt` model will download automatically from Hugging Face:
   ```bash
   cd /workspace
   yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 imgsz=224 batch=32 device=0 freeze=10
   ```

## Dataset Preparation

### Option A: Manual Photo Collection
Capture 50–100 images with your phone:

* **`hand`** — 25–50 photos of your 3D‑printed Halloween hand (or any hand) from different angles, distances and lighting conditions.
* **`not_hand`** — 25–50 photos of anything else (room backgrounds, household objects, your face, etc.).  These examples teach the model what *not* to classify as a hand.

Create the following folder structure relative to the repository root:

```
hand_cls/
  train/
    hand/
    not_hand/
  val/
    hand/
    not_hand/
```

Place ~80 % of your images in `train` and ~20 % in `val`.  The folder names are the class labels—there is no need for annotation files.

> **Tip:** If you don’t have enough images, augment them by applying rotations, flips and colour jitter.  Data augmentation is built into YOLOv8’s classifier.

For more guidance on collecting and organising your photos, see **[`data_prep.md`](data_prep.md)**.

Use the provided script to create the folder structure:
```bash
python create_dataset_structure.py
# Then manually copy your photos into the appropriate folders
```

### Option B: Video Capture (Recommended for Workshops)
Use our automated video capture tool to create a dataset in 2 minutes:

```bash
python3 capture_and_prepare.py
```

This tool will:
1. Record 20 seconds of video with your hands visible
2. Record 20 seconds of video without hands (background only)
3. Extract frames at 5 fps to create ~300 images total (~150 per class)
4. Automatically split 80/20 for training/validation

**Requirements for video capture:**
- Working webcam
- ffmpeg installed (`brew install ffmpeg` on macOS)
- Good lighting for best results

The video capture method ensures consistent lighting and camera settings, which can lead to better model performance in workshop environments.

### Improving Model Accuracy

If your model is detecting false positives (e.g., 95% confidence when no hands are visible):

1. **Add more varied training data**:
   ```bash
   python3 capture_videos_only.py  # Record with different poses/positions
   ./upload_videos.sh               # Fast upload
   ./runpod_extract_and_train.sh   # Choose option 2 (append)
   ```

2. **Tips for better "no hands" videos**:
   - Include body positions that trigger false positives
   - Vary distance from camera
   - Different clothing (especially sleeves)
   - Multiple backgrounds

3. **Retrain with expanded dataset** (now 400+ images)
   - The model learns to distinguish hands from body positions
   - Typically achieves near-perfect accuracy after 2-3 rounds

### Model Versioning Tips
- Name your models meaningfully: `best_200imgs.pt`, `best_400imgs.pt`, `best_final.pt`
- Keep track of what each version fixed (e.g., "v2 fixed sleeve false positives")
- Test each version before deleting RunPod pod to avoid re-training

## Training on RunPod

From the project root on your RunPod instance, run the following command.  Adjust `--epochs` to fit within your workshop time (10–15 epochs typically train in under 10 minutes on a RTX A5000 GPU with video capture data):

```bash
# Train a YOLOv8 classifier on your dataset.
yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 batch=32 device=0
```

During training you’ll see logs showing training and validation accuracy.  YOLOv8 saves results in the `runs/classify/train` folder.  The **best weights** (based on validation accuracy) can be found at `runs/classify/train/weights/best.pt`.

To evaluate your model after training:

```bash
# Evaluate the trained classifier on the validation set
yolo classify val model=/workspace/runs/classify/train/weights/best.pt data=/workspace/hand_cls
```

## Live Demo

After training on RunPod, download your trained model to your local machine and run the demo.

### Download the Model from RunPod

From your local terminal:
```bash
# Download the trained model
scp root@[pod-host]:/workspace/runs/classify/train/weights/best.pt ./
```

### Run the Demo Locally

The demo script [`live_demo.py`](live_demo.py) runs on your local Mac using MPS acceleration.  It opens your webcam, feeds each frame to the trained model and shows detection results:

```bash
python live_demo.py --weights best.pt --imgsz 224
```

**Special Features:**
- Shows "Hand detected!" with confidence percentage
- At 100% confidence: Special "PERFECT DETECTION!" message with ghost overlay
- Confidence text turns gold when perfect
- Ghost overlay appears (if `assets/ghost.png` exists)

**Options:**
- `--no-overlay` - Disable ghost overlay, use text only
- `--perfect-threshold 95.0` - Lower threshold for special effects (default: 99.9)

The script will automatically detect and use Apple Silicon GPU (MPS) if available.  Press `q` to quit the demo.

## Workshop Agenda (Suggested Timing)

| Time      | Activity                                                        |
|-----------|-----------------------------------------------------------------|
| 0:00–0:10 | Introduction: transfer learning and pretrained models           |
| 0:10–0:25 | Dataset preparation: folder structure and data collection       |
| 0:25–0:45 | Environment setup: RunPod pod, install dependencies, clone repo |
| 0:45–1:05 | Training: run the `yolo classify train` command                 |
| 1:05–1:20 | Evaluation: inspect metrics, run `yolo classify val`            |
| 1:20–1:30 | Live demo: run `live_demo.py` and overlay the spooky message    |

## Known Issues & Solutions (From Testing)

### Video Capture & Dataset Creation
- **ModuleNotFoundError: ffmpeg** → Wrong package! Use `pip install ffmpeg-python` (not `pip install ffmpeg`)
- **ffmpeg not found** → Install with `brew install ffmpeg` on macOS
- **Multiple Python versions** → Check with `which python3` and ensure you're using the same Python for pip install and running scripts
- **pyenv issues** → Try using `/usr/local/bin/python3` instead of `python3`
- **PATH issues** → Add Homebrew to PATH: `export PATH="/opt/homebrew/bin:$PATH"`

### SSH & Connection
- **"authenticity can't be established"** → Type `yes` (normal first-time connection)
- **Connection refused** → You're using example values! Get YOUR actual IP and port from RunPod dashboard
- **tmux not found** → Run `apt update && apt install -y tmux`
- **Wrong terminal confusion** → Upload from LOCAL Mac, train on RunPod

### File Transfer
- **rsync fails** → Use scp with port: `scp -r -P [port] hand_cls root@[ip]:/workspace/`
- **"subsystem request failed"** → Use the direct IP connection (second SSH option)
- **scp syntax error** → Keep entire command on ONE line, no line breaks

### RunPod Setup
- **yolo: command not found** → Install ultralytics first: `pip install ultralytics`
- **Can't find model after training** → Check output for exact path (e.g., runs/classify/train3 not train)
- **First training run** → Path is just `train` (no number), subsequent runs are train2, train3, etc.
- **Script 404 errors** → If GitHub scripts give 404, create them locally or use traditional workflow

### Training
- **"Data argument missing"** → Keep entire YOLO command on ONE line (no line breaks)
- **CUDA out of memory** → Use `batch=16` or `batch=8`
- **Training completes in seconds** → This is normal with RTX A5000! Video capture data trains very efficiently

### General Tips
- Keep both terminals open (local + RunPod SSH)
- RunPod shows internal IP (172.x.x.x) - ignore it, use the SSH connection info
- Training on ~300 images from video capture takes ~10 seconds on RTX A5000!
- **STOP YOUR POD** when done to avoid charges!

### Which Terminal to Use
- **LOCAL terminal**: Upload datasets, download models, run demos
- **RUNPOD terminal**: Install packages (`pip install ultralytics`), run training
- Common mistake: Running upload commands in RunPod terminal (won't work!)

### Workflow Decision Guide
- **Fast upload (videos)**: Best when you have slow internet or want quick iteration
- **Traditional (images)**: Best when scripts fail or you want proven reliability
- Both methods give identical results - choose based on your situation

## Quick Start Scripts

- **`capture_and_prepare.py`** - Record videos and extract frames locally
- **`capture_videos_only.py`** - Record videos for fast upload workflow
- **`upload_videos.sh`** - Fast upload script (2 videos instead of 200 images)
- **`runpod_extract_and_train.sh`** - Extract frames and train on RunPod
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - One-page command reference

## Additional Resources

- **[Windows Instructions](WINDOWS_README.md)** - Complete guide for Windows users
- **[Windows Setup Guide](docs/windows_setup.md)** - Detailed Windows environment setup
- **[Fast Video Upload Workflow](docs/fast_workflow.md)** - Upload videos instead of images (5-10x faster!)
- **[Workshop Slides](docs/workshop_slides.md)** - Introduction presentation
- **[RunPod Setup Guide](docs/runpod_setup.md)** - Detailed GPU setup instructions
- **[RunPod Quick Setup](docs/runpod_quick_setup.md)** - One-page setup reference
- **[RunPod Troubleshooting](docs/runpod_setup_troubleshooting.md)** - Real-world issues and solutions
- **[Video Capture Troubleshooting](docs/video_capture_troubleshooting.md)** - Fix video capture and ffmpeg issues
- **[Troubleshooting Guide](docs/troubleshooting.md)** - Common issues and solutions
- **[Next Steps](docs/next_steps.md)** - Continue learning after the workshop

Enjoy your spooky classification workshop! 🎃
