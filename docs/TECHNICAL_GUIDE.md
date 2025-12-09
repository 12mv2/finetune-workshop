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

## Model Files

### Pretrained Backbones (auto-downloaded)

| File | Size | Description |
|------|------|-------------|
| `yolov8n-cls.pt` | ~5MB | Nano classifier, pretrained on ImageNet (1000 classes) |
| `yolov8m-cls.pt` | ~32MB | Medium classifier, pretrained on ImageNet (1000 classes) |

These download automatically from Ultralytics when you run `yolo classify train model=yolov8n-cls.pt ...` and the file doesn't exist locally.

### Fine-Tuned Output

| File | Location | Description |
|------|----------|-------------|
| `best.pt` | `runs/classify/train/weights/` | Best checkpoint (highest val accuracy) |
| `last.pt` | `runs/classify/train/weights/` | Final epoch checkpoint |

Subsequent runs save to `train2/`, `train3/`, etc.

### Fine-Tuning Flow

```
yolov8n-cls.pt (pretrained, 1000 classes, ~5MB)
        ↓
   Fine-tune on hand_cls/ (your data)
        ↓
best.pt (fine-tuned, 2 classes, ~5MB)
```

The pretrained model is not modified. Fine-tuning creates a new model file.

## Scripts

| Script | Purpose |
|--------|---------|
| `capture_and_prepare.py` | Main workflow: record videos + extract frames (use this) |
| `capture_dataset_videos.py` | Record 2x20s webcam videos |
| `extract_frames_to_dataset.py` | Extract frames at 5fps, split 80/20 |
| `create_dataset_structure.py` | Create hand_cls/ folder structure |
| `live_demo.py` | Production demo with Halloween theming |
| `debug_demo.py` | Diagnostic demo showing all class confidences |

## Multi-Class Classification

### Dataset Structure

For training with multiple object classes (e.g., hand, hammer, orange_ball):

```
multi_cls/
├── train/
│   ├── hand/           # Class 1 images
│   ├── hammer/         # Class 2 images
│   ├── orange_ball/    # Class 3 images
│   ├── ...
│   └── background/     # Negative samples
└── val/
    ├── hand/
    ├── hammer/
    ├── orange_ball/
    ├── ...
    └── background/
```

### Building Multi-Class Dataset

Use `build_multiclass_dataset.py` to merge binary classifiers into a single multi-class dataset:

```bash
python3 build_multiclass_dataset.py --undersample-background 150 --output multi_cls_v2
```

**Key parameters:**
- `--undersample-background N` - Limit background class to N samples (prevents imbalance)
- `--output DIR` - Output directory name (default: multi_cls)

**The script:**
1. Merges positive samples from binary datasets into separate class folders
2. Combines all negative samples into a single background class
3. Applies undersampling to balance the background class

### Training Multi-Class Model

```bash
yolo classify train model=yolov8n-cls.pt data=multi_cls_v2 epochs=50 imgsz=640 device=0,1,2,3
```

**Key differences from binary:**
- More epochs needed (50 vs 15) due to increased complexity
- Use `device=0,1,2,3` to leverage multiple GPUs
- Larger datasets require more training time

### Validated Results

**YOLOv8n-cls on 7-class dataset (1,390 train / 465 val images):**
- Final accuracy: 94.9% (top-1), 99.4% (top-5)
- Training time: ~2 hours on 4x RTX 5090
- Model size: ~3MB (same as binary)
- Per-class accuracy: 98-100%

**Class balance recommendations:**
- Undersample background to ~150 images for datasets with <200 images per class
- Remove ambiguous samples before training
- Merge duplicate classes (e.g., orange2 → orange_ball)

### Model Selection

| Model | Parameters | Accuracy | Inference (Xavier NX) | Recommended For |
|-------|-----------|----------|---------------------|----------------|
| YOLOv8n-cls | 3M | 94.9% | ~15-20ms | Edge devices (Xavier NX, Raspberry Pi) |
| YOLOv8m-cls | 9.7M | ~95.4% | ~45-60ms | Desktop/server applications |

**For Xavier NX deployment:** Use nano model - only 0.5% accuracy loss with 3x faster inference.

## Resources

Docs: https://docs.ultralytics.com/usage/cfg
GitHub: https://github.com/ultralytics/ultralytics