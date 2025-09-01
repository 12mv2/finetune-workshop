#!/bin/bash
# Training script for RunPod
# Usage: bash train.sh

set -e

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Train the classifier
# Assumes dataset is in ./hand_cls
# Adjust epochs and batch size as needed

yolo classify train \
  data=hand_cls \
  model=yolov8n-cls.pt \
  epochs=${EPOCHS:-15} \
  imgsz=224 \
  batch=${BATCH_SIZE:-32} \
  device=0
