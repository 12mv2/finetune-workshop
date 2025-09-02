#!/usr/bin/env python3
"""
Capture video data for hand classification dataset.
Records two 20-second videos: one with hands, one without.
"""
import cv2
import time
import os
import sys


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
    
    # Then show countdown
    for i in range(duration, 0, -1):
        start_time = time.time()
        while time.time() - start_time < 1.0:
            ret, frame = cap.read()
            if not ret:
                return False
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Draw countdown
            h, w = frame.shape[:2]
            text = str(i)
            font_scale = 5.0
            draw_text(frame, text, (w//2 - 50, h//2), font_scale, (0, 255, 255), 8)
            
            # Also show what's about to happen
            if video_type == "hands":
                draw_text(frame, "HANDS VISIBLE IN...", (50, 50), 1.0, (0, 255, 0), 2)
            else:
                draw_text(frame, "NO HANDS IN...", (50, 50), 1.0, (255, 0, 0), 2)
            
            cv2.imshow('Video Capture', frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC key
                return False
    
    return True


def record_video(cap, output_path, duration=20, video_type="hands"):
    """Record video for specified duration with progress display."""
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0:
        fps = 30  # Default if can't detect
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    start_time = time.time()
    frame_count = 0
    
    print(f"\nRecording {video_type} video...")
    
    while True:
        elapsed = time.time() - start_time
        if elapsed >= duration:
            break
        
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame")
            break
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Write original frame to video
        out.write(frame)
        frame_count += 1
        
        # Add overlay text for display
        remaining = duration - elapsed
        progress = elapsed / duration
        
        # Draw progress bar
        bar_width = int(width * 0.8)
        bar_height = 30
        bar_x = int(width * 0.1)
        bar_y = height - 60
        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (100, 100, 100), 2)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + int(bar_width * progress), bar_y + bar_height), (0, 255, 0), -1)
        
        # Draw text
        if video_type == "hands":
            instruction = "SHOW YOUR HANDS!"
            color = (0, 255, 0)
        else:
            instruction = "HIDE YOUR HANDS!"
            color = (0, 0, 255)
        
        draw_text(frame, instruction, (50, 50), 1.5, color, 3)
        draw_text(frame, f"Recording: {int(remaining)}s remaining", (50, 100), 1.0)
        draw_text(frame, f"Press ESC to cancel", (50, 140), 0.7, (200, 200, 200))
        
        # Show frame
        cv2.imshow('Video Capture', frame)
        
        # Check for ESC key
        if cv2.waitKey(1) & 0xFF == 27:
            print("\nRecording cancelled by user")
            out.release()
            return False
    
    out.release()
    print(f"✓ Recorded {frame_count} frames ({frame_count/fps:.1f} seconds)")
    return True


def main():
    """Main function to capture both videos."""
    print("=== Hand Classification Video Capture ===")
    print("This tool will record two 20-second videos:")
    print("1. With your hands visible")
    print("2. Without hands (background only)")
    print("\nMake sure your webcam is connected and working.")
    
    # Check if this might be additional data
    if os.path.exists("hand_cls/train/hand"):
        existing_count = len([f for f in os.listdir("hand_cls/train/hand") if f.endswith(('.jpg', '.jpeg', '.png'))])
        if existing_count > 0:
            print(f"\n💡 TIP: You have {existing_count}+ existing images.")
            print("For better accuracy, try different:")
            print("  - Body positions (sitting, standing, leaning)")
            print("  - Distances from camera")
            print("  - Backgrounds or locations")
            print("  - Clothing (especially sleeves)")
    
    print("\nPress SPACE to begin or ESC to cancel...")
    
    # Initialize video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return 1
    
    # Wait for user to press SPACE
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read from webcam")
            return 1
        
        frame = cv2.flip(frame, 1)
        draw_text(frame, "Press SPACE to begin recording", (50, 50), 1.0)
        draw_text(frame, "Press ESC to cancel", (50, 100), 0.8, (200, 200, 200))
        
        cv2.imshow('Video Capture', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # SPACE
            break
        elif key == 27:  # ESC
            print("Cancelled by user")
            cap.release()
            cv2.destroyAllWindows()
            return 0
    
    # Record hand video
    print("\n--- Recording 1/2: HANDS ---")
    
    if not countdown_capture(cap, 3, "hands"):
        print("Cancelled during countdown")
        cap.release()
        cv2.destroyAllWindows()
        return 0
    
    if not record_video(cap, "hand_video.mp4", 20, "hands"):
        cap.release()
        cv2.destroyAllWindows()
        return 0
    
    # Pause between recordings
    print("\n--- Recording 2/2: NO HANDS ---")
    time.sleep(1)
    
    if not countdown_capture(cap, 3, "no_hands"):
        print("Cancelled during countdown")
        cap.release()
        cv2.destroyAllWindows()
        return 0
    
    if not record_video(cap, "not_hand_video.mp4", 20, "no hands"):
        cap.release()
        cv2.destroyAllWindows()
        return 0
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n✅ Video capture complete!")
    print("\nCreated files:")
    print("  - hand_video.mp4 (20 seconds)")
    print("  - not_hand_video.mp4 (20 seconds)")
    print("\nNext step: Run extract_frames_to_dataset.py to create training images")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())