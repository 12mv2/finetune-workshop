# YOLO Training Command

yolo classify train model=yolov8n-cls.pt data=hand_cls epochs=15

## Command Structure

yolo                    - CLI tool from ultralytics package (.venv/bin/yolo)
classify                - TASK: image classification (vs detect, segment, pose, obb)
train                   - MODE: train model (vs predict, val, export, benchmark, track)
model=yolov8n-cls.pt    - Pretrained model backbone (auto-downloads from Ultralytics if missing)
data=hand_cls           - Dataset directory (must have train/ and val/ subdirectories)
epochs=15               - Number of complete passes through training data

## The Stack

┌─────────────────────────────────┐
│  yolo CLI (Ultralytics)         │ ← You run commands here
├─────────────────────────────────┤
│  Ultralytics Python Library     │ ← Wraps PyTorch with easy API
├─────────────────────────────────┤
│  PyTorch                        │ ← Tensor operations & backprop
├─────────────────────────────────┤
│  CUDA (GPU) / CPU               │ ← Hardware acceleration layer
└─────────────────────────────────┘

## What Happens During Training

1. Model Architecture (nc=1000 → nc=2)
   - YOLOv8n pretrained on ImageNet (1000 classes)
   - Final layer replaced to match your 2 classes (hand/not_hand)
   - This is transfer learning: reuse learned features, adapt output

2. Transfer Learning (156/158 items transferred)
   - 156 pretrained layers: edge detectors, shapes, patterns (frozen or fine-tuned)
   - 2 new layers: final classification head (trained from scratch)
   - You're NOT training from zero - you're adapting existing knowledge

3. Dataset
   - 150 train images / 38 val images across 2 classes
   - Small dataset viable because pretrained model already knows "what objects look like"
   - More data = better accuracy, but transfer learning works with less

4. Auto-Optimizer Selection
   - YOLO picked AdamW (adaptive learning rate optimizer)
   - Learning rate: 0.000714 (auto-calculated based on dataset size)
   - Momentum: 0.9 (helps avoid local minima)
   - You didn't manually tune hyperparameters - YOLO does it

5. Hardware
   - CPU training: ~6.5 sec/batch (slow, only for testing)
   - GPU training (RunPod): ~100x faster (~0.06 sec/batch)
   - Production training requires GPU to be practical

## Resources

Docs: https://docs.ultralytics.com/usage/cfg
GitHub: https://github.com/ultralytics/ultralytics