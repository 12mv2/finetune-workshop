# Halloween Hand Workshop: Fine-tuning Ultralytics YOLOv8 for Hand Classification

Welcome to the Halloween Hand Workshop! This project guides you through fine-tuning a pretrained Ultralytics YOLOv8 classifier to detect whether a hand is visible in an image. You'll capture your own dataset, train a binary classifier on a GPU pod in the cloud, and run a fun live demo on your local machine.

---

## Workshop Roadmap

This workshop is designed to be completed in about 15 minutes with a GPU pod. The high-level workflow is:

1. **Local Preparation**  
   Capture videos or photos and prepare your dataset locally.

2. **RunPod Setup**  
   Create and connect to a GPU pod with PyTorch and CUDA installed.

3. **Upload & Train**  
   Transfer your dataset to the pod and run training using YOLOv8.

4. **Download & Test**  
   Download the trained model and run the live demo on your local machine.

---

## Setup Guides

For detailed platform-specific setup and commands, please refer to the following guides:

- [Mac Setup Guide](SETUP_Mac.md)  
- [Windows Setup Guide](SETUP_Windows.md)

These guides include instructions for installing dependencies, SSH configuration, and file transfers.

---

## Quick Start Overview

1. **Local Preparation**  
   - Install dependencies  
   - Capture videos or photos to create your dataset  
   - Prepare dataset folder structure

2. **RunPod Setup**  
   - Create a GPU pod (e.g., RTX A5000) with PyTorch 2.4 + CUDA 12.4  
   - Connect via SSH and install any necessary packages

3. **Upload & Train**  
   - Transfer your dataset to the pod  
   - Run YOLOv8 classification training with the pretrained model

4. **Download & Test**  
   - Download the best weights from the pod  
   - Run the live demo locally to see hand detection in action

---

## Troubleshooting

For common issues and solutions, please consult the troubleshooting sections in the platform setup guides:

- [Mac Troubleshooting](SETUP_Mac.md#troubleshooting)  
- [Windows Troubleshooting](SETUP_Windows.md#troubleshooting)

---

## Workshop Objectives

- **Fine-tune a pretrained YOLOv8 classifier** to distinguish between `hand` and `not_hand`.  
- **Prepare a simple dataset** by capturing images or videos, organizing them into labeled folders, and splitting into training and validation sets.  
- **Train and evaluate** the model on a GPU pod, monitoring accuracy and outputs.  
- **Run a live demo** locally that uses your webcam to detect hands and display interactive messages.

---

## Dataset Preparation

You can prepare your dataset in two main ways:

- **Manual Photo Collection:** Capture 50–100 photos split into `hand` and `not_hand` folders, organized into `train` and `val` sets.  
- **Video Capture (Recommended):** Use the provided script to record short videos with and without hands, extract frames, and automatically split into training and validation sets.

Refer to the dataset preparation section in the setup guides for detailed instructions.

---

## Training on RunPod

Train the classifier on your dataset with the pretrained `yolov8n-cls.pt` model. Training runs efficiently on an RTX A5000 GPU and usually completes in under 10 minutes.

Example training command:

```sh
yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 batch=32 device=0
```

After training, the best model weights will be saved in the `runs/classify/train/weights` folder.

---

## Live Demo

Run the live demo locally to test your trained model. The demo opens your webcam, performs real-time classification, and displays messages when a hand is detected.

Example command:

```sh
python live_demo.py --weights best.pt --imgsz 224
```

Features include confidence display, special effects at high confidence, and optional ghost overlays.

---

Enjoy the workshop and happy fine-tuning! 🎃
