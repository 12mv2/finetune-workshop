#!/usr/bin/env python3
"""
Combined workflow: Capture videos and prepare dataset in one step.
This is the recommended tool for workshop participants.

Self-contained script that creates dataset structure, captures videos,
and extracts frames - no external dependencies on other scripts.
"""
import cv2
import time
import os
import sys
import shutil
import subprocess
import ffmpeg



def draw_text(frame, text, position=(50, 50), font_scale=1.0, color=(255, 255, 255), thickness=2):
    """Draw text with a dark background for better visibility."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    # Draw background rectangle
    cv2.rectangle(frame, 
                  (position[0] - 10, position[1] - text_height - 10),
                  (position[0] + text_width + 10, position[1] + baseline + 10),
                  (0, 0, 0), -1)
    
    # Draw text
    cv2.putText(frame, text, position, font, font_scale, color, thickness)


def countdown_capture(cap, duration=3, video_type="hands"):
    """Show preparation message and countdown before recording starts."""
    # First show preparation message for 2 seconds
    prep_start = time.time()
    while time.time() - prep_start < 2.0:
        ret, frame = cap.read()
        if not ret:
            return False
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Draw preparation message
        h, w = frame.shape[:2]
        if video_type == "hands":
            draw_text(frame, "GET READY TO SHOW YOUR HANDS!", (50, h//2 - 50), 1.2, (0, 255, 255), 2)
            draw_text(frame, "Position your hands in view", (50, h//2), 1.0, (255, 255, 255), 2)
        else:
            draw_text(frame, "GET READY TO HIDE YOUR HANDS!", (50, h//2 - 50), 1.2, (255, 0, 0), 2)
            draw_text(frame, "Remove all hands from view", (50, h//2), 1.0, (255, 255, 255), 2)
        
        cv2.imshow('Video Capture', frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            return False
    
    # Show countdown
    for i in range(duration, 0, -1):
        countdown_start = time.time()
        while time.time() - countdown_start < 1.0:
            ret, frame = cap.read()
            if not ret:
                return False
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Draw countdown
            h, w = frame.shape[:2]
            draw_text(frame, f"Starting in {i}...", (w//2 - 100, h//2), 2.0, (0, 255, 0), 3)
            
            cv2.imshow('Video Capture', frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC key
                return False
    
    return True


def record_video(filename, duration=20, video_type="hands"):
    """Record a video of specified duration."""
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return False
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Define codec and create VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    # Show countdown and preparation
    if not countdown_capture(cap, video_type=video_type):
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        return False
    
    # Record video
    print(f"Recording {video_type} video...")
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Add recording indicator
        elapsed = time.time() - start_time
        remaining = duration - elapsed
        h, w = frame.shape[:2]
        
        # Recording dot
        cv2.circle(frame, (w - 50, 50), 15, (0, 0, 255), -1)
        draw_text(frame, f"REC {remaining:.1f}s", (w - 150, 80), 0.7, (255, 255, 255), 2)
        
        # Instructions
        if video_type == "hands":
            draw_text(frame, "Show your hands clearly", (50, h - 50), 1.0, (0, 255, 255), 2)
        else:
            draw_text(frame, "Keep hands out of view", (50, h - 50), 1.0, (255, 0, 0), 2)
        
        out.write(frame)
        cv2.imshow('Video Capture', frame)
        frame_count += 1
        
        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    print(f"✓ Recorded {frame_count} frames ({time.time() - start_time:.1f} seconds)")
    return True


def capture_videos():
    """Capture both hand and not-hand videos."""
    print("=== Hand Classification Video Capture ===")
    print("This tool will record two 20-second videos:")
    print("1. With your hands visible")
    print("2. Without hands (background only)")
    print("\nMake sure your webcam is connected and working.")
    print("\nPress SPACE to begin or ESC to cancel...")
    
    # Wait for user input
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # SPACE
            break
        elif key == 27:  # ESC
            return False
    
    # Record hands video
    print("\n--- Recording 1/2: HANDS ---")
    if not record_video("hand_video.mp4", video_type="hands"):
        return False
    
    # Record not-hands video
    print("\n--- Recording 2/2: NO HANDS ---")
    if not record_video("not_hand_video.mp4", video_type="not_hands"):
        return False
    
    print("\n✅ Video capture complete!")
    print("\nCreated files:")
    print("  - hand_video.mp4 (20 seconds)")
    print("  - not_hand_video.mp4 (20 seconds)")
    
    return True


def check_ffmpeg():
    """Check if ffmpeg is installed."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def count_existing_images(directory):
    """Count existing images in a directory."""
    if not os.path.exists(directory):
        return 0
    
    image_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
    return len([f for f in os.listdir(directory) if f.endswith(image_extensions)])


def extract_frames_from_video(video_path, output_dir, class_name, fps=5):
    """Extract frames from video at specified fps."""
    if not os.path.exists(video_path):
        print(f"Error: Video file {video_path} not found")
        return 0
    
    print(f"Extracting frames at {fps} fps...")
    
    # Create temporary directory for extracted frames
    temp_dir = f"temp_frames_{class_name}"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Extract frames using ffmpeg
        (
            ffmpeg
            .input(video_path)
            .filter('fps', fps=fps)
            .output(f'{temp_dir}/{class_name}_%03d.jpg')
            .overwrite_output()
            .run(quiet=True)
        )
        
        # Get list of extracted frames
        frames = [f for f in os.listdir(temp_dir) if f.endswith('.jpg')]
        frames.sort()
        frame_count = len(frames)
        
        if frame_count < 50:
            print(f"Warning: Only extracted {frame_count} frames. Consider checking video quality.")
        else:
            print(f"Warning: Expected 100 frames, got {frame_count}")
        
        # Split frames 80/20 between train and val
        train_count = int(frame_count * 0.8)
        
        # Get starting indices for numbering
        train_start = count_existing_images(f'hand_cls/train/{class_name}') + 1
        val_start = count_existing_images(f'hand_cls/val/{class_name}') + 1
        
        # Move training frames
        for i, frame in enumerate(frames[:train_count]):
            src = os.path.join(temp_dir, frame)
            dst = f'hand_cls/train/{class_name}/{class_name}_{train_start + i:03d}.jpg'
            shutil.move(src, dst)
        
        # Move validation frames
        for i, frame in enumerate(frames[train_count:]):
            src = os.path.join(temp_dir, frame)
            dst = f'hand_cls/val/{class_name}/{class_name}_{val_start + i:03d}.jpg'
            shutil.move(src, dst)
        
        print(f"✓ Created {train_count} training images")
        print(f"✓ Created {frame_count - train_count} validation images")
        
        return frame_count
        
    except Exception as e:
        print(f"Error extracting frames: {e}")
        return 0
    finally:
        # Clean up temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def extract_frames():
    """Extract frames from both videos and organize into dataset."""
    if not check_ffmpeg():
        print("Error: ffmpeg not found!")
        print("Install with: brew install ffmpeg (macOS) or pip install ffmpeg-python")
        return False
    
    print("=== Frame Extraction Tool ===")
    print("\nCreating dataset directories...")
    
    # Ensure directories exist
    for split in ['train', 'val']:
        for class_name in ['hand', 'not_hand']:
            os.makedirs(f'hand_cls/{split}/{class_name}', exist_ok=True)
    
    # Extract frames from hand video
    print("\n--- Processing hand_video.mp4 ---")
    hand_frames = extract_frames_from_video('hand_video.mp4', 'hand_cls', 'hand')
    
    # Extract frames from not_hand video
    print("\n--- Processing not_hand_video.mp4 ---")
    not_hand_frames = extract_frames_from_video('not_hand_video.mp4', 'hand_cls', 'not_hand')
    
    if hand_frames == 0 or not_hand_frames == 0:
        return False
    
    # Show summary
    print("\n✅ Dataset creation complete!")
    print("\n📊 Dataset summary:")
    
    for split in ['train', 'val']:
        print(f"\n{split.upper()}:")
        for class_name in ['hand', 'not_hand']:
            count = count_existing_images(f'hand_cls/{split}/{class_name}')
            print(f"  {class_name}: {count} images")
    
    total = sum(count_existing_images(f'hand_cls/{split}/{class_name}') 
                for split in ['train', 'val'] 
                for class_name in ['hand', 'not_hand'])
    print(f"\nTotal images: {total}")
    
    print("\n🚀 Your dataset is ready for training!")
    print("Next steps:")
    print("1. Review images in hand_cls/ directory")
    print("2. Upload to RunPod for training")
    print("3. Or run locally with: yolo classify train model=yolov8n-cls.pt data=hand_cls epochs=15")
    
    return True


def main():
    """Main workflow combining video capture and frame extraction."""
    print("=== Hand Classification Dataset Creator ===")
    print("This tool will:")
    print("1. Record two 20-second videos (hands and no hands)")
    print("2. Extract frames at 5 fps (100 images each)")
    print("3. Create/expand a balanced dataset")
    print("4. Split 80/20 for training/validation")
    
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
        print(f"\n📊 Found existing dataset with {existing_count} total images")
        print("This is great for adding variety to improve model accuracy!")
    
    # Verify dataset structure exists
    if not os.path.exists('hand_cls'):
        print("Error: hand_cls directory not found!")
        print("The dataset structure should already exist in the repository.")
        return 1
    
    print("✅ Found existing dataset structure")
    
    # Step 1: Capture videos
    print("\n" + "="*50)
    print("STEP 1: VIDEO CAPTURE")
    print("="*50)
    
    if not capture_videos():
        print("\nVideo capture failed or was cancelled.")
        return 1
    
    # Check if videos were created
    if not os.path.exists("hand_video.mp4") or not os.path.exists("not_hand_video.mp4"):
        print("\nError: Videos were not created. Exiting.")
        return 1
    
    # Step 2: Extract frames
    print("\n" + "="*50)
    print("STEP 2: FRAME EXTRACTION")
    print("="*50)
    
    if not extract_frames():
        print("\nFrame extraction failed.")
        return 1
    
    # Step 3: Cleanup
    print("\n" + "="*50)
    print("CLEANUP")
    print("="*50)
    
    response = input("\nDelete original video files to save space? (y/n): ").lower().strip()
    if response == 'y':
        try:
            os.remove("hand_video.mp4")
            os.remove("not_hand_video.mp4")
            print("✓ Video files deleted")
        except:
            print("! Could not delete video files")
    else:
        print("✓ Video files preserved")
    
    print("\n🎉 Dataset creation complete!")
    print("Your dataset is ready for training on RunPod!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())