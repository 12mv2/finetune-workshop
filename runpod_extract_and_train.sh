#!/bin/bash

# RunPod-side script: Extract frames from videos and train model
# Run this ON RunPod after uploading videos

echo "=== RunPod Frame Extraction and Training ==="
echo "This script extracts frames from uploaded videos and trains the model"
echo ""

# Check if videos exist
if [ ! -f "/workspace/videos/hand_video.mp4" ] || [ ! -f "/workspace/videos/not_hand_video.mp4" ]; then
    echo "❌ Error: Video files not found in /workspace/videos/"
    echo "Please upload videos first using upload_videos.sh"
    exit 1
fi

# Check if ultralytics is installed
if ! python -c "import ultralytics" 2>/dev/null; then
    echo "📦 Installing ultralytics..."
    pip install ultralytics
fi

# Create dataset structure
echo "📁 Creating dataset structure..."
mkdir -p /workspace/hand_cls/train/hand
mkdir -p /workspace/hand_cls/train/not_hand
mkdir -p /workspace/hand_cls/val/hand
mkdir -p /workspace/hand_cls/val/not_hand

# Check if dataset already has images (for append mode)
EXISTING_HAND_TRAIN=$(find /workspace/hand_cls/train/hand -name "*.jpg" 2>/dev/null | wc -l)
EXISTING_NOTHAND_TRAIN=$(find /workspace/hand_cls/train/not_hand -name "*.jpg" 2>/dev/null | wc -l)

if [ $EXISTING_HAND_TRAIN -gt 0 ] || [ $EXISTING_NOTHAND_TRAIN -gt 0 ]; then
    echo ""
    echo "⚠️  Found existing images:"
    echo "   Hand training images: $EXISTING_HAND_TRAIN"
    echo "   Not-hand training images: $EXISTING_NOTHAND_TRAIN"
    echo ""
    echo "What would you like to do?"
    echo "1) Replace existing images (fresh start)"
    echo "2) Add to existing images (append)"
    echo "3) Cancel"
    read -p "Enter choice (1/2/3): " CHOICE
    
    case $CHOICE in
        1)
            echo "Clearing existing images..."
            rm -f /workspace/hand_cls/train/hand/*.jpg
            rm -f /workspace/hand_cls/train/not_hand/*.jpg
            rm -f /workspace/hand_cls/val/hand/*.jpg
            rm -f /workspace/hand_cls/val/not_hand/*.jpg
            START_NUM=1
            ;;
        2)
            echo "Adding to existing dataset..."
            # Find highest number in existing files
            LAST_HAND=$(ls /workspace/hand_cls/train/hand/*.jpg 2>/dev/null | sed 's/.*hand_//' | sed 's/.jpg//' | sort -n | tail -1)
            LAST_NOTHAND=$(ls /workspace/hand_cls/train/not_hand/*.jpg 2>/dev/null | sed 's/.*not_hand_//' | sed 's/.jpg//' | sort -n | tail -1)
            START_HAND=$((${LAST_HAND:-0} + 1))
            START_NOTHAND=$((${LAST_NOTHAND:-0} + 1))
            ;;
        3)
            echo "Cancelled."
            exit 0
            ;;
        *)
            echo "Invalid choice. Exiting."
            exit 1
            ;;
    esac
else
    START_NUM=1
    START_HAND=1
    START_NOTHAND=1
fi

# Extract frames at 5 fps (100 frames per 20-second video)
echo ""
echo "🎬 Extracting frames from hand_video.mp4..."
mkdir -p /tmp/hand_frames
ffmpeg -i /workspace/videos/hand_video.mp4 -vf fps=5 -q:v 2 /tmp/hand_frames/frame_%03d.jpg -loglevel error

HAND_FRAMES=$(ls /tmp/hand_frames/*.jpg | wc -l)
echo "✓ Extracted $HAND_FRAMES frames"

echo ""
echo "🎬 Extracting frames from not_hand_video.mp4..."
mkdir -p /tmp/nothand_frames
ffmpeg -i /workspace/videos/not_hand_video.mp4 -vf fps=5 -q:v 2 /tmp/nothand_frames/frame_%03d.jpg -loglevel error

NOTHAND_FRAMES=$(ls /tmp/nothand_frames/*.jpg | wc -l)
echo "✓ Extracted $NOTHAND_FRAMES frames"

# Split 80/20 for train/val
echo ""
echo "📊 Splitting dataset 80/20..."

# Hand images
TRAIN_COUNT=$((HAND_FRAMES * 80 / 100))
VAL_COUNT=$((HAND_FRAMES - TRAIN_COUNT))

echo "Hand images: $TRAIN_COUNT train, $VAL_COUNT val"

# Copy hand training images
COUNTER=1
for img in $(ls /tmp/hand_frames/*.jpg | head -$TRAIN_COUNT); do
    cp $img /workspace/hand_cls/train/hand/hand_$(printf "%03d" $((START_HAND + COUNTER - 1))).jpg
    ((COUNTER++))
done

# Copy hand validation images
COUNTER=1
for img in $(ls /tmp/hand_frames/*.jpg | tail -$VAL_COUNT); do
    cp $img /workspace/hand_cls/val/hand/hand_$(printf "%03d" $COUNTER).jpg
    ((COUNTER++))
done

# Not-hand images
TRAIN_COUNT=$((NOTHAND_FRAMES * 80 / 100))
VAL_COUNT=$((NOTHAND_FRAMES - TRAIN_COUNT))

echo "Not-hand images: $TRAIN_COUNT train, $VAL_COUNT val"

# Copy not-hand training images
COUNTER=1
for img in $(ls /tmp/nothand_frames/*.jpg | head -$TRAIN_COUNT); do
    cp $img /workspace/hand_cls/train/not_hand/not_hand_$(printf "%03d" $((START_NOTHAND + COUNTER - 1))).jpg
    ((COUNTER++))
done

# Copy not-hand validation images
COUNTER=1
for img in $(ls /tmp/nothand_frames/*.jpg | tail -$VAL_COUNT); do
    cp $img /workspace/hand_cls/val/not_hand/not_hand_$(printf "%03d" $COUNTER).jpg
    ((COUNTER++))
done

# Clean up temp directories
rm -rf /tmp/hand_frames /tmp/nothand_frames

# Show final dataset stats
echo ""
echo "✅ Dataset ready! Final counts:"
echo "Training:"
find /workspace/hand_cls/train -name "*.jpg" | wc -l | xargs echo "  Total images:"
find /workspace/hand_cls/train/hand -name "*.jpg" | wc -l | xargs echo "  Hand images:"
find /workspace/hand_cls/train/not_hand -name "*.jpg" | wc -l | xargs echo "  Not-hand images:"
echo "Validation:"
find /workspace/hand_cls/val -name "*.jpg" | wc -l | xargs echo "  Total images:"

# Ask if user wants to start training
echo ""
echo "🚀 Ready to train!"
read -p "Start training now? (y/n): " START_TRAINING

if [ "$START_TRAINING" = "y" ] || [ "$START_TRAINING" = "Y" ]; then
    echo ""
    echo "🏃 Starting training..."
    cd /workspace
    yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 batch=16
    
    echo ""
    echo "✅ Training complete!"
    echo ""
    echo "📥 Download your model with:"
    echo "scp -P [PORT] root@[IP]:/workspace/runs/classify/train*/weights/best.pt ./"
else
    echo ""
    echo "To train later, run:"
    echo "yolo classify train model=yolov8n-cls.pt data=/workspace/hand_cls epochs=15 batch=16"
fi