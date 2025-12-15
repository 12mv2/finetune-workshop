#!/usr/bin/env python3
"""
Multi-class training data capture tool.

Captures training data for multiple object classes in a single session.
Designed to be run multiple times by different people to accumulate diverse data.

Usage:
    python3 capture_multiclass.py
    python3 capture_multiclass.py --camera 1  # Use camera index 1

Output structure (compatible with build_multiclass_dataset.py):
    Training Data/
        {class}_cls/
            train/
                hand/       (images WITH object)
                not_hand/   (images WITHOUT object - becomes background)
            val/
                hand/
                not_hand/
"""
import argparse
import cv2
import time
import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
CAMERA_INDEX = 0  # USB webcam (index 1 is built-in, not present on Xavier)
RECORD_DURATION = 20  # seconds per video
EXTRACT_FPS = 5  # frames per second to extract
TRAIN_SPLIT = 0.8  # 80% train, 20% val


def check_ffmpeg():
    """Check if ffmpeg is installed."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def draw_text(frame, text, position=(50, 50), font_scale=1.0, color=(255, 255, 255), thickness=2):
    """Draw text with a dark background for better visibility."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)

    cv2.rectangle(frame,
                  (position[0] - 10, position[1] - text_height - 10),
                  (position[0] + text_width + 10, position[1] + baseline + 10),
                  (0, 0, 0), -1)
    cv2.putText(frame, text, position, font, font_scale, color, thickness)


def wait_for_space(cap, message, submessage=""):
    """Wait for user to press SPACE to continue."""
    while True:
        ret, frame = cap.read()
        if not ret:
            return False

        frame = cv2.flip(frame, 1)
        draw_text(frame, message, (50, 50), 1.0, (0, 255, 255))
        if submessage:
            draw_text(frame, submessage, (50, 100), 0.8, (200, 200, 200))
        draw_text(frame, "Press SPACE to continue, ESC to quit", (50, 150), 0.7, (150, 150, 150))

        cv2.imshow('Capture', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # SPACE
            return True
        elif key == 27:  # ESC
            return False


def countdown(cap, seconds=3, message=""):
    """Show countdown before recording."""
    for i in range(seconds, 0, -1):
        start = time.time()
        while time.time() - start < 1.0:
            ret, frame = cap.read()
            if not ret:
                return False

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            draw_text(frame, str(i), (w//2 - 30, h//2), 4.0, (0, 255, 255), 6)
            if message:
                draw_text(frame, message, (50, 50), 1.0, (0, 255, 0))

            cv2.imshow('Capture', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                return False
    return True


def record_video(cap, output_path, duration, class_name, is_present):
    """Record video with progress display."""
    # Measure actual FPS
    test_start = time.time()
    test_frames = 0
    while time.time() - test_start < 0.5:
        ret, _ = cap.read()
        if ret:
            test_frames += 1
    actual_fps = max(test_frames * 2, 15)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, actual_fps, (width, height))

    start_time = time.time()
    frame_count = 0

    status = "WITH" if is_present else "WITHOUT"
    color = (0, 255, 0) if is_present else (0, 0, 255)

    while True:
        elapsed = time.time() - start_time
        if elapsed >= duration:
            break

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        out.write(frame)
        frame_count += 1

        # Draw overlay
        remaining = int(duration - elapsed)
        progress = elapsed / duration

        draw_text(frame, f"Recording {status} {class_name.upper()}", (50, 50), 1.2, color, 2)
        draw_text(frame, f"{remaining}s remaining", (50, 100), 0.9)

        # Progress bar
        bar_w = int(width * 0.8)
        bar_x = int(width * 0.1)
        bar_y = height - 50
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + 20), (100, 100, 100), 2)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + int(bar_w * progress), bar_y + 20), color, -1)

        cv2.imshow('Capture', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            out.release()
            return False

    out.release()
    return True


def extract_frames_ffmpeg(video_path, output_dir, prefix, fps=5):
    """Extract frames from video using ffmpeg."""
    os.makedirs(output_dir, exist_ok=True)
    output_pattern = os.path.join(output_dir, f"{prefix}_%04d.jpg")

    cmd = [
        'ffmpeg', '-i', video_path,
        '-vf', f'fps={fps}',
        '-q:v', '2',
        '-start_number', '1',
        output_pattern,
        '-y', '-loglevel', 'error'
    ]

    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0


def create_class_structure(base_dir, class_name):
    """Create directory structure for a class."""
    class_dir = base_dir / f"{class_name}_cls"

    dirs = [
        class_dir / "train" / "hand",
        class_dir / "train" / "not_hand",
        class_dir / "val" / "hand",
        class_dir / "val" / "not_hand",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    return class_dir


def distribute_frames(temp_dir, class_dir, session_id, is_present):
    """Distribute frames 80/20 between train and val."""
    frames = sorted([f for f in os.listdir(temp_dir) if f.endswith('.jpg')])
    if not frames:
        return 0, 0

    split_idx = int(len(frames) * TRAIN_SPLIT)
    train_frames = frames[:split_idx]
    val_frames = frames[split_idx:]

    target_subdir = "hand" if is_present else "not_hand"

    # Copy to train
    train_dir = class_dir / "train" / target_subdir
    for i, f in enumerate(train_frames):
        src = Path(temp_dir) / f
        dst = train_dir / f"{session_id}_{i:04d}.jpg"
        shutil.copy2(src, dst)

    # Copy to val
    val_dir = class_dir / "val" / target_subdir
    for i, f in enumerate(val_frames):
        src = Path(temp_dir) / f
        dst = val_dir / f"{session_id}_{i:04d}.jpg"
        shutil.copy2(src, dst)

    return len(train_frames), len(val_frames)


def get_class_names():
    """Prompt user for class names."""
    print("\n=== Multi-Class Training Data Capture ===\n")

    # Default classes for QuestV3
    default_classes = ["hand", "9v_battery", "black_spool", "green_spool", "hammer", "blue_floppy"]

    print("Default classes for QuestV3:")
    for i, c in enumerate(default_classes, 1):
        print(f"  {i}. {c}")

    print("\nOptions:")
    print("  1. Use defaults (recommended for QuestV3)")
    print("  2. Enter custom classes")

    choice = input("\nChoice (1/2): ").strip()

    if choice == "2":
        try:
            num_classes = int(input("\nHow many classes? "))
        except ValueError:
            print("Invalid number")
            return None

        classes = []
        print("\nEnter class names (lowercase, no spaces):")
        for i in range(num_classes):
            name = input(f"  Class {i+1}: ").strip().lower().replace(" ", "_")
            if name:
                classes.append(name)

        return classes if classes else None
    else:
        return default_classes


def main():
    """Main capture loop."""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Capture multi-class training data')
    parser.add_argument('--camera', type=int, default=CAMERA_INDEX,
                        help=f'Camera index (default: {CAMERA_INDEX})')
    args = parser.parse_args()
    camera_index = args.camera

    # Check ffmpeg
    if not check_ffmpeg():
        print("Error: ffmpeg not found. Install with:")
        print("  Ubuntu: sudo apt install ffmpeg")
        print("  macOS: brew install ffmpeg")
        return 1

    # Get class names
    classes = get_class_names()
    if not classes:
        print("No classes specified. Exiting.")
        return 1

    print(f"\nWill capture data for {len(classes)} classes: {', '.join(classes)}")
    print(f"Recording duration: {RECORD_DURATION}s per video")
    print(f"Extraction rate: {EXTRACT_FPS} fps (~{RECORD_DURATION * EXTRACT_FPS} images per class)")

    # Initialize camera
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: Could not open camera {camera_index}")
        print("Try: python3 capture_multiclass.py --camera 1")
        return 1

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Create session ID (timestamp-based for unique filenames)
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Setup directories
    base_dir = Path("Training Data")
    temp_dir = Path("temp_capture")
    temp_dir.mkdir(exist_ok=True)

    total_images = 0

    try:
        # Wait to start
        if not wait_for_space(cap, "Ready to capture training data", f"Session: {session_id}"):
            return 0

        for idx, class_name in enumerate(classes):
            print(f"\n[{idx+1}/{len(classes)}] Capturing: {class_name.upper()}")

            class_dir = create_class_structure(base_dir, class_name)

            # --- Capture WITH object ---
            if not wait_for_space(cap, f"Show {class_name.upper()} to camera", "Position object clearly in view"):
                break

            if not countdown(cap, 3, f"Recording WITH {class_name}..."):
                break

            video_with = temp_dir / f"{class_name}_with.mp4"
            if not record_video(cap, str(video_with), RECORD_DURATION, class_name, True):
                break

            # --- Capture WITHOUT object ---
            if not wait_for_space(cap, f"REMOVE {class_name.upper()} from view", "Show only background"):
                break

            if not countdown(cap, 3, f"Recording WITHOUT {class_name}..."):
                break

            video_without = temp_dir / f"{class_name}_without.mp4"
            if not record_video(cap, str(video_without), RECORD_DURATION, class_name, False):
                break

            # Extract and distribute frames
            print(f"  Extracting frames...")

            # Extract "with" frames
            frames_with_dir = temp_dir / "frames_with"
            if frames_with_dir.exists():
                shutil.rmtree(frames_with_dir)
            extract_frames_ffmpeg(str(video_with), str(frames_with_dir), class_name, EXTRACT_FPS)
            train_w, val_w = distribute_frames(str(frames_with_dir), class_dir, session_id, True)

            # Extract "without" frames
            frames_without_dir = temp_dir / "frames_without"
            if frames_without_dir.exists():
                shutil.rmtree(frames_without_dir)
            extract_frames_ffmpeg(str(video_without), str(frames_without_dir), class_name, EXTRACT_FPS)
            train_wo, val_wo = distribute_frames(str(frames_without_dir), class_dir, session_id, False)

            class_total = train_w + val_w + train_wo + val_wo
            total_images += class_total
            print(f"  Done! {class_total} images ({train_w + val_w} with, {train_wo + val_wo} without)")

        print("\n" + "=" * 50)
        print("CAPTURE COMPLETE!")
        print("=" * 50)
        print(f"Session ID: {session_id}")
        print(f"Total images: {total_images}")
        print(f"Location: {base_dir.absolute()}")
        print("\n" + "=" * 50)
        print("NEXT STEPS")
        print("=" * 50)
        print("\nOption 1: Capture more data (recommended for better accuracy)")
        print("  python3 capture_multiclass.py --camera 4")
        print("  (try different angles, lighting, people)")
        print("\nOption 2: Build dataset and train")
        print("  # Balanced dataset (recommended):")
        print("  python3 build_multiclass_dataset.py --undersample-background 280")
        print("\n  # Full dataset (more background images):")
        print("  python3 build_multiclass_dataset.py")

    finally:
        cap.release()
        cv2.destroyAllWindows()

        # Cleanup temp
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
