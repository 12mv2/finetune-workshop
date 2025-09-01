# Halloween Hand Classification Workshop
## Fine-tuning YOLOv8 with Hugging Face & RunPod

---

## Welcome! 👋

### Today's Mission
Transform a pretrained model into a custom Halloween hand detector in just 90 minutes!

### What You'll Learn
- Transfer learning fundamentals
- Cloud GPU training with RunPod
- Fine-tuning YOLOv8 classification
- Building a live webcam demo

---

## Why Transfer Learning? 🧠

### Training from Scratch
- ❌ Requires massive datasets (millions of images)
- ❌ Takes days/weeks of GPU time
- ❌ Costs $$$
- ❌ Needs deep ML expertise

### Transfer Learning
- ✅ Works with small datasets (50-100 images)
- ✅ Trains in minutes
- ✅ Affordable GPU usage
- ✅ Beginner-friendly

---

## The Magic of Pretrained Models 🪄

### ImageNet Pretraining
- 14 million images
- 1000 object classes
- Learned features: edges, shapes, textures

### Your Task
- Keep the learned features
- Replace the final layer
- Train on YOUR specific classes

---

## YOLO: You Only Look Once 🎯

### YOLOv8 Family
- **Detection**: Bounding boxes around objects
- **Segmentation**: Pixel-level masks
- **Classification**: What we're using today!

### Model Sizes
- `yolov8n-cls`: Nano (fastest, smallest)
- `yolov8s-cls`: Small
- `yolov8m-cls`: Medium
- `yolov8l-cls`: Large
- `yolov8x-cls`: Extra Large

---

## Hugging Face Hub 🤗

### What It Provides
- Pretrained model weights
- Easy model discovery
- Version control
- Community models

### Our Starting Point
```python
from ultralytics import YOLO
model = YOLO('yolov8n-cls.pt')
```

---

## RunPod: Cloud GPUs Made Easy ☁️

### Why RunPod?
- Pay per hour (as low as $0.20/hr)
- Pre-configured ML environments
- Easy file transfer
- No local GPU required

### Today's Setup
- RTX 3090 or A4000
- PyTorch pre-installed
- ~10 minutes training time

---

## Our Binary Classifier 🎃

### Two Classes
1. **hand_prop**: Your 3D-printed Halloween hand
2. **not_hand**: Everything else

### Dataset Structure
```
hand_cls/
  train/
    hand_prop/    (40 images)
    not_hand/     (40 images)
  val/
    hand_prop/    (10 images)
    not_hand/     (10 images)
```

---

## The Training Process 🏋️

### What Happens During Fine-tuning
1. Load pretrained weights
2. Freeze early layers (feature extraction)
3. Replace final layer (2 classes instead of 1000)
4. Train only the new layer
5. Optionally unfreeze and fine-tune all layers

### Our Command
```bash
yolo classify train \
  data=hand_cls \
  model=yolov8n-cls.pt \
  epochs=15 \
  imgsz=224
```

---

## Metrics to Watch 📊

### During Training
- **Loss**: Should decrease
- **Accuracy**: Should increase
- **Val Accuracy**: Most important!

### Overfitting Signs
- Training accuracy >> Validation accuracy
- Validation loss increasing

---

## Live Demo Architecture 🎬

### Pipeline
1. Capture webcam frame
2. Resize to 224x224
3. Run through model
4. Get class probabilities
5. If "hand_prop" > threshold → Show overlay!

### Performance
- ~30 FPS on modern laptop
- Real-time classification
- Low latency

---

## Let's Build! 🚀

### Timeline
1. **0-10 min**: This intro
2. **10-25 min**: Dataset preparation
3. **25-45 min**: RunPod setup
4. **45-65 min**: Training
5. **65-80 min**: Evaluation
6. **80-90 min**: Live demo!

---

## Tips for Success 💡

### Dataset Quality
- Diverse backgrounds
- Multiple angles
- Varied lighting
- Balanced classes

### If Things Go Wrong
- Check folder structure
- Verify image formats (jpg/png)
- Ensure GPU is available
- Ask for help!

---

## Questions Before We Start? 🤔

### Resources
- GitHub repo: [your-repo-url]
- RunPod docs: runpod.io/docs
- YOLOv8 docs: docs.ultralytics.com

### Let's make something spooky! 👻