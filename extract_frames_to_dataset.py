#!/usr/bin/env python3
"""
Extract frames from recorded videos and organize them into the dataset structure.
Extracts at 5 fps to get 100 frames per 20-second video.
"""
import os
import sys
import shutil
import ffmpeg
import subprocess


def check_ffmpeg():
    """Check if ffmpeg is installed."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def create_dataset_dirs():
    """Ensure dataset directory structure exists."""
    dirs = [
        'hand_cls/train/hand',
        'hand_cls/train/not_hand',
        'hand_cls/val/hand',
        'hand_cls/val/not_hand'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    return dirs


def count_existing_images(directory):
    """Count existing images in a directory."""
    if not os.path.exists(directory):
        return 0
    
    image_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
    return len([f for f in os.listdir(directory) if f.endswith(image_extensions)])


def clear_directory(directory):
    """Clear all images from a directory."""
    if not os.path.exists(directory):
        return
    
    image_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
    for f in os.listdir(directory):
        if f.endswith(image_extensions):
            os.remove(os.path.join(directory, f))


def extract_frames(video_path, output_pattern, fps=5):
    """Extract frames from video at specified fps."""
    try:
        # Use ffmpeg to extract frames
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.filter(stream, 'fps', fps=fps)
        stream = ffmpeg.output(stream, output_pattern, start_number=1, pix_fmt='yuvj444p')
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        return True
    except ffmpeg.Error as e:
        print(f"Error extracting frames: {e}")
        return False


def get_next_file_number(directory, class_name):
    """Get the next available file number for a class."""
    if not os.path.exists(directory):
        return 1
    
    existing_files = [f for f in os.listdir(directory) if f.startswith(class_name) and f.endswith('.jpg')]
    if not existing_files:
        return 1
    
    # Extract numbers from filenames
    numbers = []
    for f in existing_files:
        try:
            # Extract number from filename like "hand_001.jpg"
            num = int(f.split('_')[1].split('.')[0])
            numbers.append(num)
        except:
            pass
    
    return max(numbers) + 1 if numbers else 1


def distribute_frames(temp_dir, class_name, train_dir, val_dir, total_frames=100, append=False):
    """Distribute frames 80/20 between train and val."""
    # Get all extracted frames
    frames = sorted([f for f in os.listdir(temp_dir) if f.endswith('.jpg')])
    
    # Split 80/20
    train_count = int(len(frames) * 0.8)
    train_frames = frames[:train_count]
    val_frames = frames[train_count:]
    
    # Get starting numbers if appending
    train_start = get_next_file_number(train_dir, class_name) if append else 1
    val_start = get_next_file_number(val_dir, class_name) if append else 1
    
    # Copy to train directory
    for i, frame in enumerate(train_frames):
        src = os.path.join(temp_dir, frame)
        dst = os.path.join(train_dir, f"{class_name}_{train_start + i:03d}.jpg")
        shutil.copy2(src, dst)
    
    # Copy to val directory
    for i, frame in enumerate(val_frames):
        src = os.path.join(temp_dir, frame)
        dst = os.path.join(val_dir, f"{class_name}_{val_start + i:03d}.jpg")
        shutil.copy2(src, dst)
    
    return len(train_frames), len(val_frames)


def main():
    """Main function to extract frames from videos."""
    print("=== Frame Extraction Tool ===")
    
    # Check for ffmpeg
    if not check_ffmpeg():
        print("Error: ffmpeg not found. Please install ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: sudo apt-get install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return 1
    
    # Check for video files
    if not os.path.exists("hand_video.mp4"):
        print("Error: hand_video.mp4 not found.")
        print("Please run capture_dataset_videos.py first.")
        return 1
    
    if not os.path.exists("not_hand_video.mp4"):
        print("Error: not_hand_video.mp4 not found.")
        print("Please run capture_dataset_videos.py first.")
        return 1
    
    # Create dataset structure
    print("\nCreating dataset directories...")
    create_dataset_dirs()
    
    # Check for existing images
    total_existing = 0
    for class_name in ['hand', 'not_hand']:
        train_count = count_existing_images(f'hand_cls/train/{class_name}')
        val_count = count_existing_images(f'hand_cls/val/{class_name}')
        total_existing += train_count + val_count

    if total_existing > 0:
        print(f"\nFound {total_existing} existing images. Replace or add to them?")
        print("  1. Replace (start fresh)")
        print("  2. Add (append new images)")
        print("  3. Cancel")

        response = input("Choice (1/2/3): ").strip()

        if response == '1':
            for class_name in ['hand', 'not_hand']:
                clear_directory(f'hand_cls/train/{class_name}')
                clear_directory(f'hand_cls/val/{class_name}')
            append_mode = False
        elif response == '2':
            append_mode = True
        else:
            print("Cancelled.")
            return 0
    else:
        append_mode = False
    
    # Create temp directory
    temp_dir = 'temp_frames'
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        print("\nExtracting frames (5 fps)...")
        output_pattern = os.path.join(temp_dir, 'frame_%03d.jpg')

        # Process hand video
        if not extract_frames("hand_video.mp4", output_pattern, fps=5):
            return 1

        hand_train, hand_val = distribute_frames(
            temp_dir, 'hand',
            'hand_cls/train/hand',
            'hand_cls/val/hand',
            append=append_mode
        )

        # Clear temp directory
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))

        # Process not_hand video
        if not extract_frames("not_hand_video.mp4", output_pattern, fps=5):
            return 1

        nothand_train, nothand_val = distribute_frames(
            temp_dir, 'not_hand',
            'hand_cls/train/not_hand',
            'hand_cls/val/not_hand',
            append=append_mode
        )

        print(f"✓ Extracted {hand_train + hand_val} hand, {nothand_train + nothand_val} not_hand images")
        
    finally:
        # Cleanup temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    # Final summary
    total = 0
    for split in ['train', 'val']:
        for class_name in ['hand', 'not_hand']:
            count = count_existing_images(f'hand_cls/{split}/{class_name}')
            total += count

    print(f"\n✅ Dataset ready: {total} total images (80/20 train/val split)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())