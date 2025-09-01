# Quick Object Classification Workshop: Halloween Hand

This repository provides the materials for a 1.5‑hour workshop on fine‑tuning **Ultralytics YOLOv8** for image classification.  The goal is to train a binary classifier that detects whether a 3D‑printed Halloween hand is visible in an image and then build a fun live demo that reacts when the hand appears.

## Objectives

* **Fine‑tune a pretrained model.**  We will start from the `yolov8n‑cls.pt` weights (pretrained on ImageNet) and fine‑tune only the classifier head to distinguish two classes: `hand` and `not_hand`.
* **Prepare a simple dataset.**  You will capture ~100 photos on your phone, organise them into a folder structure and split them into training/validation sets.  No bounding boxes or keypoints are needed—class names are inferred from folder names.
* **Train and evaluate.**  We will train the classifier using a GPU pod on RunPod, monitor accuracy, and explore the outputs.
* **Live demo.**  Finally we will run a webcam loop locally on your Mac; when the `hand` class is detected, a spooky overlay or message appears on the frame.

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

You can also use the provided script to create the folder structure:
```bash
python create_dataset_structure.py
```

## Training on RunPod

From the project root on your RunPod instance, run the following command.  Adjust `--epochs` to fit within your workshop time (10–15 epochs typically train in under 10 minutes on a T4 GPU):

```bash
# Train a YOLOv8 classifier on your dataset.
yolo classify train \
  data=/workspace/hand_cls \
  model=yolov8n-cls.pt \
  epochs=15 \
  imgsz=224 \
  batch=32 \
  device=0 \
  freeze=10
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

The demo script [`live_demo.py`](live_demo.py) runs on your local Mac using MPS acceleration.  It opens your webcam, feeds each frame to the trained model and overlays a spooky message when the `hand` class is detected:

```bash
python live_demo.py --weights best.pt --imgsz 224
```

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

## Notes

* If training is too slow, lower the number of epochs or freeze the backbone by passing `--freeze 24` (freezes the first 24 layers).
* If there are webcam issues, you can test the model by running `yolo classify predict` on a static image: `yolo classify predict model=runs/classify/train/weights/best.pt source=path/to/image.jpg`.
* This repository is intentionally lightweight to keep setup simple.  Feel free to extend it by adding notebooks, different models, or advanced augmentation pipelines.

## Quick Start Scripts

- **`prepare_and_upload.sh`** - Prepare and upload dataset to RunPod
- **`runpod_setup.sh`** - Initial setup on RunPod instance
- **`runpod_train.sh`** - Complete training script for RunPod

## Additional Resources

- **[Workshop Slides](docs/workshop_slides.md)** - Introduction presentation
- **[RunPod Setup Guide](docs/runpod_setup.md)** - Detailed GPU setup instructions
- **[RunPod Quick Setup](docs/runpod_quick_setup.md)** - One-page setup reference
- **[RunPod Troubleshooting](docs/runpod_setup_troubleshooting.md)** - Real-world issues and solutions
- **[Troubleshooting Guide](docs/troubleshooting.md)** - Common issues and solutions
- **[Next Steps](docs/next_steps.md)** - Continue learning after the workshop

Enjoy your spooky classification workshop! 🎃
