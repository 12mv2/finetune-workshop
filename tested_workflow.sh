#!/bin/bash
# Tested workflow script - exact commands that worked in our testing
# Run sections of this script as needed

echo "=== Halloween Hand Workshop - Tested Workflow ==="
echo "This script shows the EXACT commands we tested successfully"
echo ""

# ============================================
# SECTION 1: LOCAL SETUP (on your Mac)
# ============================================
echo ">>> LOCAL SETUP (Run on your Mac)"
echo ""

# Check SSH key
echo "1. Check your SSH key:"
echo "   cat ~/.ssh/id_ed25519.pub"
echo "   # Copy this to RunPod Settings → SSH Keys"
echo ""

# Install dependencies
echo "2. Install dependencies:"
echo "   pip install -r requirements.txt"
echo ""

# Create dataset
echo "3. Create dataset structure:"
echo "   python3 create_dataset_structure.py"
echo "   # Add images to hand_cls folders"
echo ""

# ============================================
# SECTION 2: RUNPOD SETUP
# ============================================
echo ">>> RUNPOD SETUP"
echo ""

echo "1. Create Pod:"
echo "   - GPU: RTX A5000"
echo "   - Template: PyTorch 2.4 + CUDA 12.4"
echo "   - SSH: Enabled"
echo ""

echo "2. Connect (example from our test):"
echo "   ssh oyzsz5hz9pd68b-64410ff0@ssh.runpod.io -i ~/.ssh/id_ed25519"
echo "   # Type 'yes' when prompted"
echo ""

echo "3. Install tmux:"
echo "   apt update && apt install -y tmux"
echo "   tmux new -s workshop"
echo ""

echo "4. Run setup:"
echo "   curl -O https://raw.githubusercontent.com/12mv2/finetune-workshop/main/runpod_setup.sh"
echo "   bash runpod_setup.sh"
echo ""

# ============================================
# SECTION 3: UPLOAD DATASET (from LOCAL)
# ============================================
echo ">>> UPLOAD DATASET (Run from LOCAL terminal)"
echo ""

echo "Use scp with port (example from our test):"
echo "   scp -r -P 40098 -i ~/.ssh/id_ed25519 hand_cls root@213.192.2.74:/workspace/"
echo ""

# ============================================
# SECTION 4: TRAIN MODEL (on RunPod)
# ============================================
echo ">>> TRAIN MODEL (Run on RunPod)"
echo ""

echo "1. Navigate to workspace:"
echo "   cd /workspace"
echo ""

echo "2. Run training (this worked without freeze parameter):"
echo "   yolo classify train \\"
echo "     model=yolov8n-cls.pt \\"
echo "     data=/workspace/hand_cls \\"
echo "     epochs=15 \\"
echo "     imgsz=224 \\"
echo "     batch=16 \\"
echo "     device=0"
echo ""

# ============================================
# SECTION 5: DOWNLOAD MODEL (from LOCAL)
# ============================================
echo ">>> DOWNLOAD MODEL (Run from LOCAL terminal)"
echo ""

echo "Download trained model (example from our test):"
echo "   scp -P 40098 -i ~/.ssh/id_ed25519 root@213.192.2.74:/workspace/runs/classify/train2/weights/best.pt ./"
echo ""

# ============================================
# SECTION 6: RUN DEMO (on LOCAL)
# ============================================
echo ">>> RUN DEMO (Run on your Mac)"
echo ""

echo "Test webcam demo:"
echo "   python3 live_demo.py --weights best.pt"
echo "   # Press 'q' to quit"
echo ""

# ============================================
# IMPORTANT REMINDERS
# ============================================
echo ">>> IMPORTANT REMINDERS"
echo ""
echo "1. STOP YOUR RUNPOD when done!"
echo "2. Keep both terminals open (local + RunPod)"
echo "3. Upload from LOCAL, train on RUNPOD"
echo "4. If rsync fails, use scp with port"
echo "5. If freeze=10 causes errors, remove it"
echo ""

echo "=== End of Tested Workflow ==="