# Fast Video Upload Workflow

This guide describes the faster method for uploading training data to RunPod by uploading compressed videos instead of extracted frames.

## Why Use This Method?

### Upload Time Comparison
- **Traditional method**: Upload 150 JPEG files (~400MB) → 3 minutes
- **Fast method**: Upload 2 MP4 files (~40MB) → 1-2 minutes
- **Speed improvement**: ? faster!

### When to Use Each Method

**Use Fast Video Upload when:**
- You have slow home internet (< 50 Mbps upload)
- You're creating multiple datasets
- You want the simplest workflow
- RunPod instance has good CPU

**Use Traditional Method when:**
- You need precise control over frame extraction
- You want to review images before upload
- RunPod instance has limited CPU
- You're debugging dataset issues

## Fast Workflow Steps

### 1. Record Videos
```bash
python3 capture_videos_only.py
```
This creates:
- `hand_video.mp4` (20 seconds, ~20MB)
- `not_hand_video.mp4` (20 seconds, ~20MB)

### 2. Upload Videos to RunPod
```bash
./upload_videos.sh
```
You'll be prompted for:
- RunPod IP address
- RunPod SSH port

The script will:
- Create `/workspace/videos/` directory
- Upload both MP4 files with compression
- Show progress and time estimate

### 3. Extract Frames and Train on RunPod

SSH into your RunPod instance:
```bash
ssh -p [PORT] -i ~/.ssh/id_ed25519 root@[IP]
```

Run the extraction and training script:
```bash
# First time: download the script
curl -O https://raw.githubusercontent.com/12mv2/finetune-workshop/main/runpod_extract_and_train.sh
chmod +x runpod_extract_and_train.sh

# Run extraction and training
./runpod_extract_and_train.sh
```

The script will:
1. Extract frames at 5 fps (100 per video)
2. Split 80/20 for train/validation
3. Ask if you want to append or replace existing data
4. Start training automatically (optional)

### 4. Download Trained Model
```bash
# Check latest training run number
ssh -p [PORT] -i ~/.ssh/id_ed25519 root@[IP] "ls /workspace/runs/classify/"

# Download (update train number!)
scp -P [PORT] -i ~/.ssh/id_ed25519 root@[IP]:/workspace/runs/classify/train4/weights/best.pt ./
```

## Complete Example

```bash
# Local machine
python3 capture_videos_only.py
./upload_videos.sh
# Enter: 65.123.45.67 (your IP)
# Enter: 12345 (your port)

# RunPod (via SSH)
ssh -p 12345 -i ~/.ssh/id_ed25519 root@65.123.45.67
./runpod_extract_and_train.sh
# Choose: 2 (append to existing)
# Choose: y (start training)

# Local machine (after training)
scp -P 12345 -i ~/.ssh/id_ed25519 root@65.123.45.67:/workspace/runs/classify/train4/weights/best.pt ./best_v2.pt
python3 live_demo.py --weights best_v2.pt
```

## Bandwidth Savings

### Traditional Method
- 200 images × 2MB average = 400MB upload
- Time on 10 Mbps upload: ~5-6 minutes
- Time on 50 Mbps upload: ~1-2 minutes

### Fast Video Method
- 2 videos × 20MB = 40MB upload
- Time on 10 Mbps upload: ~30-40 seconds
- Time on 50 Mbps upload: ~6-8 seconds

## Tips for Best Results

1. **Record quality videos**:
   - Good lighting
   - Stable camera
   - Clear hand movements
   - Varied backgrounds for "no hands"

2. **Multiple datasets**:
   - The append feature makes it easy to add variety
   - Record in different locations/lighting
   - Vary clothing and positions

3. **RunPod efficiency**:
   - Frame extraction on RunPod uses datacenter CPU (fast)
   - No need to download/re-upload for iterations
   - Can process multiple video sets quickly

## Troubleshooting

### "rsync not found"
The script will fall back to `scp` automatically.

### "Connection refused"
- Check IP and port are correct
- Ensure RunPod instance is running
- Verify SSH key is added to RunPod

### "ffmpeg not found" on RunPod
The script will install it automatically, but you can also:
```bash
apt update && apt install -y ffmpeg
```

### Frame extraction seems slow
- Normal: ~10-20 seconds per video
- RunPod CPU is still faster than upload time saved

## Advanced Options

### Custom frame rate
Edit `runpod_extract_and_train.sh` and change:
```bash
ffmpeg -i video.mp4 -vf fps=5 ...  # Change 5 to desired fps
```

### Different video formats
The scripts work with any video format ffmpeg supports:
- MP4 (default, recommended)
- MOV, AVI, MKV (will work)
- WebM (smaller files, same quality)

### Batch processing
Upload multiple video pairs and process them:
```bash
# Upload multiple sets
scp -P [PORT] hand_video_*.mp4 not_hand_video_*.mp4 root@[IP]:/workspace/videos/

# Process each pair
for i in 1 2 3; do
    ./process_video_pair.sh $i
done
```