#!/usr/bin/env python3
"""
Combined workflow: Capture videos and prepare dataset in one step.
This is the recommended tool for workshop participants.
"""
import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error: {description} failed!")
        return False
    return True


def main():
    """Main workflow combining video capture and frame extraction."""
    print("=== Dataset Creator ===")
    print("Records videos → Extracts frames → Creates dataset (80/20 split)\n")

    # Check for existing dataset
    existing_count = 0
    if os.path.exists('hand_cls'):
        for split in ['train', 'val']:
            for class_name in ['hand', 'not_hand']:
                path = f'hand_cls/{split}/{class_name}'
                if os.path.exists(path):
                    count = len([f for f in os.listdir(path) if f.endswith(('.jpg', '.jpeg', '.png'))])
                    existing_count += count

    if existing_count > 0:
        print(f"Found {existing_count} existing images (you can add more for better accuracy)\n")

    # Check if dataset structure exists
    if not os.path.exists('hand_cls'):
        if not run_command("python3 create_dataset_structure.py", "Creating directories"):
            return 1

    # Step 1: Capture videos
    print("="*50)
    print("STEP 1: Video Capture")
    print("="*50)

    result = subprocess.run("python3 capture_dataset_videos.py", shell=True)
    if result.returncode != 0:
        print("\nCancelled or failed.")
        return 1

    # Check if videos were created
    if not os.path.exists("hand_video.mp4") or not os.path.exists("not_hand_video.mp4"):
        print("\nError: Videos not created.")
        return 1

    # Step 2: Extract frames
    print("\n" + "="*50)
    print("STEP 2: Frame Extraction")
    print("="*50)

    result = subprocess.run("python3 extract_frames_to_dataset.py", shell=True)
    if result.returncode != 0:
        print("\nExtraction failed.")
        return 1

    # Optional: Clean up video files
    response = input("\nDelete video files? (y/n): ").lower()
    if response == 'y':
        try:
            os.remove("hand_video.mp4")
            os.remove("not_hand_video.mp4")
            print("✓ Deleted")
        except Exception as e:
            print(f"Warning: {e}")

    print("\n✅ Dataset ready!")
    print("\n" + "="*50)
    print("NEXT STEP: Train your model")
    print("="*50)
    print("\nOption A: Cloud GPU (faster)")
    print("  1. Get SSH command from RunPod: ssh root@<IP> -p <PORT> -i ~/.ssh/id_ed25519")
    print("  2. Upload (change -p to -P):    scp -r -P <PORT> -i ~/.ssh/id_ed25519 hand_cls root@<IP>:/workspace/")
    print("  3. SSH to RunPod and train (see WORKSHOP.md)")
    print("\nOption B: Local CPU (no cloud needed)")
    print("  source .venv/bin/activate")
    print("  yolo classify train model=yolov8n-cls.pt data=hand_cls epochs=15 batch=16 device=cpu")
    print("\nAfter training completes, look for 'Results saved to' path, then test:")
    print("  python3 live_demo.py --weights runs/classify/trainN/weights/best.pt")
    print("  (replace trainN with your actual folder, e.g., train, train2, train3)")

    return 0


if __name__ == "__main__":
    sys.exit(main())