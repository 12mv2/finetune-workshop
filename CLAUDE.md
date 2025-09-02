# Claude Handoff Document - Halloween Hand Classification Workshop

## Project Overview
This is a 90-minute workshop teaching participants how to fine-tune YOLOv8 for binary image classification using RunPod GPUs. The workflow is: prepare data locally → train on RunPod → download model → run demo locally.

## Current Project State (Fully Tested & Working)

### What We Built
1. **Complete workshop materials** for fine-tuning YOLOv8 to detect hands (Halloween prop or real)
2. **Tested end-to-end** on September 1, 2025 with RunPod RTX A5000
3. **All scripts working** - dataset creation, training, live webcam demo
4. **Comprehensive documentation** including troubleshooting from real testing

### Key Technical Details
- **Model**: YOLOv8n-cls.pt (classification, not detection)
- **Classes**: `hand` and `not_hand` (binary classification)
- **Framework**: Ultralytics YOLOv8 with PyTorch
- **Cloud GPU**: RunPod with RTX A5000, PyTorch 2.4 + CUDA 12.4 template
- **Local inference**: Uses MPS on Apple Silicon Macs
- **Dataset format**: Folder-based (no annotations needed)

### Repository Structure
```
finetune-workshop/
├── README.md                    # Main documentation with tested workflow
├── QUICK_REFERENCE.md          # One-page command reference
├── CLAUDE.md                   # This file - context for Claude
├── requirements.txt            # ultralytics, opencv-python
├── create_dataset_structure.py # Creates hand_cls folder structure
├── live_demo.py               # Webcam demo with MPS support
├── train.sh                   # Training script (updated, no freeze)
├── tested_workflow.sh         # Exact commands from successful test
├── prepare_and_upload.sh      # Dataset upload helper
├── runpod_setup.sh           # RunPod environment setup
├── runpod_train.sh           # RunPod training script
├── notebooks/
│   └── 01_train.ipynb        # Optional Jupyter notebook
├── docs/
│   ├── workshop_slides.md
│   ├── runpod_setup.md
│   ├── runpod_quick_setup.md
│   ├── runpod_setup_troubleshooting.md
│   ├── troubleshooting.md
│   ├── data_prep.md
│   └── next_steps.md
└── assets/
    └── overlay_info.md       # Instructions for ghost overlays
```

## Project Timeline

### Initial Development (September 1, 2025 - Earlier)
- **Time**: ~14:00-15:00 PST
- Created initial workshop materials
- Implemented dataset structure script
- Built live demo with MPS support
- Created documentation structure

### Major Updates (September 1, 2025 - Mid-session)
- **Time**: ~15:00-16:00 PST
- Switched from hand_prop to hand class naming
- Added freeze=10 parameter (later removed)
- Updated to SSH-first workflow
- Added tmux instructions

### Live Testing (September 1, 2025 - Later)
- **Time**: ~16:00-17:00 PST

#### Test Run Details
1. Created RunPod account and added SSH key
2. Deployed RTX A5000 pod with PyTorch 2.4 + CUDA 12.4
3. Connected via SSH: `ssh oyzsz5hz9pd68b-64410ff0@ssh.runpod.io`
4. Installed tmux (not pre-installed)
5. Created test dataset with 20 images
6. Uploaded via scp with port: `scp -r -P 40098 hand_cls root@213.192.2.74:/workspace/`
7. Trained model successfully (removed freeze=10 due to gradient error)
8. Downloaded model and ran webcam demo with MPS acceleration

### Key Learnings & Fixes

#### SSH & Connection
- SSH keys must be added to RunPod BEFORE creating pod
- First connection shows fingerprint warning - this is normal
- RunPod provides two SSH options - use the first, fallback to second with port

#### File Transfer
- rsync failed with "unexpected tag" error
- Solution: Use scp with port flag instead
- Must run from LOCAL terminal, not RunPod terminal

#### Training Issues
- `freeze=10` parameter caused "does not require grad" error
- Solution: Remove freeze parameter or use smaller batch size
- Default batch reduced from 32 to 16 for stability

#### Environment
- tmux not installed by default on RunPod
- Solution: `apt update && apt install -y tmux`
- Python environment uses /usr/local paths

## Important URLs & Resources
- GitHub repo: https://github.com/12mv2/finetune-workshop
- RunPod: https://runpod.io
- YOLOv8 docs: https://docs.ultralytics.com
- Model source: Hugging Face (auto-downloads)

## For Next Claude Session

### If continuing development:
1. Read this file first for context
2. Check `git status` for any uncommitted changes
3. The project is fully tested and working - be careful with changes
4. All major issues are documented in troubleshooting guides

### Common tasks you might be asked to do:
- Update for newer YOLOv8 versions
- Add support for multi-class classification
- Create slides for the workshop presentation
- Add more dataset examples
- Update for different cloud providers (Lambda Labs, etc.)

### Testing checklist:
- [ ] Local environment: `pip install -r requirements.txt`
- [ ] Dataset creation: `python3 create_dataset_structure.py`
- [ ] Model download: YOLOv8 auto-downloads from Hugging Face
- [ ] MPS detection: `torch.backends.mps.is_available()`
- [ ] Webcam access: `cv2.VideoCapture(0)`

## Critical Information

### What NOT to change without testing:
1. Don't add `freeze=10` back - it causes gradient errors
2. Don't change batch size above 16 for small datasets
3. Don't use rsync for uploads - scp is more reliable
4. Don't assume tmux is installed on RunPod

### Terminal Management
- **Local terminal**: For uploads, downloads, and local demo
- **RunPod terminal**: For training only
- Common mistake: Running upload commands on RunPod (won't work)

### Cost Management
- RTX A5000 costs ~$0.20-0.30/hour
- Training takes 5-10 minutes for real dataset
- **ALWAYS remind users to STOP their pod**

## Final Notes
This workshop has been successfully tested end-to-end. The materials are production-ready. Any changes should be tested with an actual RunPod instance before committing. The workflow is optimized for beginners and handles all common issues we encountered during testing.

## Session Summary

### Timeline
- **Session Start**: September 1, 2025, ~14:00 PST
- **Initial Development**: 14:00-15:00 PST
- **Major Refactoring**: 15:00-16:00 PST
- **RunPod Testing**: 16:00-17:00 PST
- **Documentation Updates**: 17:00-17:30 PST
- **Session End**: September 1, 2025, ~17:30 PST

### Key Milestones
1. **14:15** - Created initial project structure
2. **14:45** - Implemented MPS support for Mac
3. **15:20** - Switched to SSH-first workflow
4. **16:10** - Successfully connected to RunPod
5. **16:30** - Completed first training run
6. **17:00** - Fixed all issues and updated docs
7. **17:30** - Created handoff documentation

Last updated: September 1, 2025, 17:30 PST
Tested by: Colin Rooney with Claude
Total session time: ~3.5 hours
Status: ✅ Fully working and documented