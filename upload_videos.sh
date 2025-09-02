#!/bin/bash

# Fast video upload script for RunPod
# Uploads MP4 videos instead of extracted frames (5-10x faster)

echo "=== Fast Video Upload for RunPod ==="
echo "This uploads video files for extraction on RunPod (much faster!)"
echo ""

# Check if video files exist
if [ ! -f "hand_video.mp4" ] || [ ! -f "not_hand_video.mp4" ]; then
    echo "❌ Error: Video files not found!"
    echo "Please run: python3 capture_dataset_videos.py first"
    exit 1
fi

# Get file sizes
HAND_SIZE=$(ls -lh hand_video.mp4 | awk '{print $5}')
NOHAND_SIZE=$(ls -lh not_hand_video.mp4 | awk '{print $5}')
TOTAL_SIZE=$(du -ch hand_video.mp4 not_hand_video.mp4 | grep total | awk '{print $1}')

echo "📊 Files to upload:"
echo "  • hand_video.mp4 ($HAND_SIZE)"
echo "  • not_hand_video.mp4 ($NOHAND_SIZE)"
echo "  • Total: ~$TOTAL_SIZE (vs ~400MB for extracted frames)"
echo ""

# Get RunPod connection details
echo "Enter your RunPod connection details:"
echo "(Find these in your RunPod dashboard)"
echo ""
read -p "RunPod IP address: " RUNPOD_IP
read -p "RunPod SSH port: " RUNPOD_PORT

# Confirm details
echo ""
echo "📡 Uploading to: root@$RUNPOD_IP:$RUNPOD_PORT"
echo "Press Enter to continue or Ctrl+C to cancel..."
read

# Create videos directory on RunPod
echo ""
echo "Creating directory on RunPod..."
ssh -p $RUNPOD_PORT -i ~/.ssh/id_ed25519 root@$RUNPOD_IP "mkdir -p /workspace/videos"

# Upload videos with compression and progress
echo ""
echo "Uploading videos (this should take 1-2 minutes)..."
echo ""

# Use rsync for better progress and resume capability
if command -v rsync &> /dev/null; then
    rsync -avz --progress -e "ssh -p $RUNPOD_PORT -i ~/.ssh/id_ed25519" \
        hand_video.mp4 not_hand_video.mp4 \
        root@$RUNPOD_IP:/workspace/videos/
else
    # Fallback to scp if rsync not available
    scp -P $RUNPOD_PORT -i ~/.ssh/id_ed25519 \
        hand_video.mp4 not_hand_video.mp4 \
        root@$RUNPOD_IP:/workspace/videos/
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Upload complete!"
    echo ""
    echo "Next steps:"
    echo "1. SSH into RunPod: ssh -p $RUNPOD_PORT -i ~/.ssh/id_ed25519 root@$RUNPOD_IP"
    echo "2. Run: bash /workspace/runpod_extract_and_train.sh"
    echo ""
    echo "💡 Tip: Download the extraction script first:"
    echo "curl -O https://raw.githubusercontent.com/12mv2/finetune-workshop/main/runpod_extract_and_train.sh"
else
    echo ""
    echo "❌ Upload failed! Check your connection details and try again."
    exit 1
fi