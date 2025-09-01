#!/bin/bash
# Complete training script for RunPod
# Run this AFTER uploading your dataset to /workspace/hand_cls

set -e

echo "=== Halloween Hand Classification Training ==="
echo "Starting at: $(date)"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader)"

# Check dataset exists
if [ ! -d "/workspace/hand_cls" ]; then
    echo "ERROR: Dataset not found at /workspace/hand_cls"
    echo "Please upload your dataset first!"
    exit 1
fi

# Count images
echo -e "\n=== Dataset Summary ==="
echo "Training images:"
echo "  hand: $(find /workspace/hand_cls/train/hand -name "*.jpg" -o -name "*.png" | wc -l)"
echo "  not_hand: $(find /workspace/hand_cls/train/not_hand -name "*.jpg" -o -name "*.png" | wc -l)"
echo "Validation images:"
echo "  hand: $(find /workspace/hand_cls/val/hand -name "*.jpg" -o -name "*.png" | wc -l)"
echo "  not_hand: $(find /workspace/hand_cls/val/not_hand -name "*.jpg" -o -name "*.png" | wc -l)"

# Training
echo -e "\n=== Starting Training ==="
cd /workspace

yolo classify train \
  model=yolov8n-cls.pt \
  data=/workspace/hand_cls \
  epochs=15 \
  imgsz=224 \
  batch=32 \
  device=0 \
  freeze=10 \
  name=halloween_hand \
  exist_ok=True

echo -e "\n=== Training Complete! ==="
echo "Results saved to: /workspace/runs/classify/halloween_hand/"
echo ""
echo "To download your model, run this from your LOCAL terminal:"
echo "scp root@$(hostname -I | awk '{print $1}'):/workspace/runs/classify/halloween_hand/weights/best.pt ./"

# Optional: Run validation
echo -e "\n=== Running Validation ==="
yolo classify val \
  model=/workspace/runs/classify/halloween_hand/weights/best.pt \
  data=/workspace/hand_cls

echo -e "\n=== All Done! ==="
echo "Finished at: $(date)"