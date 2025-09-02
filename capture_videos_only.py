#!/usr/bin/env python3
"""
Capture videos only (no extraction) for fast upload workflow.
This is the same as capture_dataset_videos.py but emphasizes the fast upload path.
"""
import sys
import os
import subprocess

def main():
    """Run video capture and suggest fast upload workflow."""
    # First, run the standard video capture
    result = subprocess.run([sys.executable, "capture_dataset_videos.py"])
    
    if result.returncode != 0:
        return result.returncode
    
    # If successful, suggest the fast workflow
    print("\n" + "="*60)
    print("🚀 FAST UPLOAD WORKFLOW")
    print("="*60)
    print("\nYour videos are ready! For the fastest training workflow:")
    print("\n1. Upload videos (5-10x faster than images):")
    print("   ./upload_videos.sh")
    print("\n2. On RunPod, extract and train:")
    print("   bash runpod_extract_and_train.sh")
    print("\nThis uploads ~40MB instead of ~400MB!")
    print("\nAlternatively, for local extraction:")
    print("   python3 extract_frames_to_dataset.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())