#!/bin/bash
# RunPod Setup Script for Halloween Hand Classification Workshop
# This script runs ON the RunPod instance after SSH connection

set -e

echo "=== RunPod Workshop Setup Script ==="
echo "Running on: $(hostname)"
echo "Date: $(date)"

# 1. Environment check
echo -e "\n=== Step 1: Environment Check ==="
python3 - <<'EOF'
import torch
print(f"Python: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
EOF

echo -e "\n=== GPU Information ==="
nvidia-smi | head -n 15

# 2. Install dependencies
echo -e "\n=== Step 2: Installing Dependencies ==="
pip install --upgrade pip
pip install ultralytics opencv-python

# 3. Verify installation
echo -e "\n=== Step 3: Verify Installation ==="
python3 -c "from ultralytics import YOLO; print('✓ YOLOv8 imported successfully')"
python3 -c "import cv2; print(f'✓ OpenCV {cv2.__version__} imported successfully')"

# 4. Create workspace directory
echo -e "\n=== Step 4: Setting up Workspace ==="
mkdir -p /workspace
cd /workspace

# 5. Show dataset upload instructions
echo -e "\n=== Step 5: Dataset Upload Instructions ==="
echo "Your RunPod instance is ready!"
echo ""
echo "Next steps:"
echo "1. From your LOCAL terminal, upload your dataset:"
echo "   rsync -avh hand_cls/ root@$(hostname -I | awk '{print $1}'):/workspace/hand_cls/"
echo ""
echo "2. Then run training:"
echo "   cd /workspace"
echo "   yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 imgsz=224 batch=32 device=0 freeze=10"
echo ""
echo "3. Download trained model:"
echo "   scp root@$(hostname -I | awk '{print $1}'):/workspace/runs/classify/train/weights/best.pt ./"

echo -e "\n=== Setup Complete! ==="