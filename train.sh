#!/bin/bash
# Training script for RunPod
# Usage: bash train.sh

set -e

echo "=== Environment Check ==="
python - <<'EOF'
import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
EOF

echo -e "\n=== NVIDIA GPU Info ==="
nvidia-smi | head -n 15

echo -e "\n=== Installing Dependencies ==="
pip install --upgrade pip
pip install ultralytics opencv-python

echo -e "\n=== Starting Training ==="
echo "Dataset path: /workspace/hand_cls"
echo "Epochs: ${EPOCHS:-15}"
echo "Batch size: ${BATCH_SIZE:-32}"

# Check dataset exists
if [ ! -d "/workspace/hand_cls" ]; then
    echo "ERROR: Dataset not found at /workspace/hand_cls"
    echo "Please upload your dataset first using:"
    echo "  rsync -avh hand_cls/ root@[pod-host]:/workspace/hand_cls/"
    exit 1
fi

# Count images
echo -e "\n=== Dataset Summary ==="
echo "Train images:"
find /workspace/hand_cls/train -name "*.jpg" -o -name "*.png" | wc -l
echo "Val images:"
find /workspace/hand_cls/val -name "*.jpg" -o -name "*.png" | wc -l

# Train the classifier
echo -e "\n=== Training YOLOv8 Classifier ==="
# Note: Removed freeze=10 due to gradient issues with small datasets
# Reduced default batch size from 32 to 16 for stability
yolo classify train \
  data=/workspace/hand_cls \
  model=yolov8n-cls.pt \
  epochs=${EPOCHS:-15} \
  imgsz=224 \
  batch=${BATCH_SIZE:-16} \
  device=0

echo -e "\n=== Training Complete ==="
echo "Best weights saved at: /workspace/runs/classify/train*/weights/best.pt"
