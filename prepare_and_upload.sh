#!/bin/bash
# Local script to prepare dataset and upload to RunPod
# Run this on your LOCAL machine (Mac)

set -e

echo "=== Dataset Preparation and Upload Script ==="

# Check if dataset exists
if [ ! -d "hand_cls" ]; then
    echo "Dataset directory 'hand_cls' not found!"
    echo "Creating dataset structure..."
    python3 create_dataset_structure.py
    echo ""
    echo "Please add your images to the folders and run this script again."
    exit 1
fi

# Check dataset
echo "=== Checking Dataset ==="
python3 create_dataset_structure.py check

# Get RunPod host
echo -e "\n=== RunPod Connection ==="
read -p "Enter your RunPod hostname or IP (from SSH command): " RUNPOD_HOST

# Confirm upload
echo -e "\nWill upload dataset to: root@$RUNPOD_HOST:/workspace/hand_cls/"
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Upload cancelled."
    exit 1
fi

# Upload dataset
echo -e "\n=== Uploading Dataset ==="
rsync -avh --progress hand_cls/ root@$RUNPOD_HOST:/workspace/hand_cls/

echo -e "\n=== Upload Complete! ==="
echo "Next steps on RunPod:"
echo "1. SSH into your pod: ssh root@$RUNPOD_HOST"
echo "2. Run training: bash runpod_train.sh"
echo ""
echo "Or run training directly:"
echo "cd /workspace && yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 imgsz=224 batch=32 device=0 freeze=10"