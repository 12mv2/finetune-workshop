#!/usr/bin/env python3
"""
Live webcam demo for multi-class object classifier.

This script loads a trained YOLOv8 classifier and opens the default webcam.
For each frame, it predicts the class label and displays it with confidence.
Press `q` to quit.

Supports both binary (hand/not_hand) and multi-class (7 classes) models.
"""
import argparse
import cv2
import torch
from ultralytics import YOLO


# Color map for different classes (BGR format)
CLASS_COLORS = {
    'hand': (0, 255, 255),        # Yellow
    '9v_battery': (0, 165, 255),  # Orange
    'black_spool': (64, 64, 64),  # Dark gray (3D printer filament)
    'green_spool': (0, 255, 0),   # Green (sewing spool)
    'hammer': (0, 0, 255),        # Red
    'blue_floppy': (255, 128, 0), # Blue (floppy disk)
    'background': (200, 200, 200),  # Light gray
    'not_hand': (200, 200, 200),  # Light gray (legacy)
}

# Display names for classes
DISPLAY_NAMES = {
    '9v_battery': '9V Battery',
    'black_spool': 'Black Filament Spool',
    'green_spool': 'Green Sewing Spool',
    'hammer': 'Hammer',
    'blue_floppy': 'Blue Floppy Disk',
    'hand': 'Hand',
    'background': 'Background',
    'not_hand': 'No Hand',
}


def draw_text_with_bg(frame, text, position, font_scale=1.0, color=(255, 255, 255), thickness=2):
    """Draw text with dark background for visibility."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)

    x, y = position
    cv2.rectangle(frame, (x - 5, y - text_h - 5), (x + text_w + 5, y + baseline + 5), (0, 0, 0), -1)
    cv2.putText(frame, text, position, font, font_scale, color, thickness, cv2.LINE_AA)


def main(weights: str, imgsz: int = 640, conf_threshold: float = 15.0, source: int = 0) -> None:
    # Detect device
    if torch.backends.mps.is_available():
        device = 'mps'
        print("Using Apple Silicon GPU (MPS)")
    elif torch.cuda.is_available():
        device = 'cuda'
        print("Using NVIDIA GPU (CUDA)")
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = 'cpu'
        print("Using CPU")

    # Load trained model
    print(f"Loading model: {weights}")
    model = YOLO(weights)
    print(f"Model classes: {model.names}")

    # Open webcam
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera {source}. Check connection.")

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print(f"\nRunning inference (conf threshold: {conf_threshold}%)")
    print("Press 'q' to quit, 'd' for debug mode (show all classes)")

    debug_mode = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Mirror the frame for more intuitive interaction
        frame = cv2.flip(frame, 1)

        # Resize for model
        resized = cv2.resize(frame, (imgsz, imgsz))

        # Run inference
        results = model(resized, verbose=False, device=device)[0]

        # Get probabilities and class names
        probs = results.probs.data.tolist()
        names = results.names

        # Find top prediction
        top_idx = probs.index(max(probs))
        top_class = names[top_idx]
        top_conf = probs[top_idx] * 100

        # Get display name and color
        display_name = DISPLAY_NAMES.get(top_class, top_class.replace('_', ' ').title())
        color = CLASS_COLORS.get(top_class, (255, 255, 255))

        # Determine if detection is above threshold
        is_detected = top_conf >= conf_threshold and top_class not in ('background', 'not_hand')

        # Draw main detection
        if is_detected:
            draw_text_with_bg(frame, f"Detected: {display_name}", (20, 40), 1.2, color, 2)
            draw_text_with_bg(frame, f"Confidence: {top_conf:.1f}%", (20, 80), 0.8, color, 2)
        else:
            draw_text_with_bg(frame, f"[{display_name}]", (20, 40), 0.9, (150, 150, 150), 2)
            draw_text_with_bg(frame, f"{top_conf:.1f}%", (20, 75), 0.7, (150, 150, 150), 2)

        # Debug mode: show all class probabilities
        if debug_mode:
            y_offset = 120
            draw_text_with_bg(frame, "All classes:", (20, y_offset), 0.6, (200, 200, 200), 1)
            y_offset += 30

            # Sort by probability
            sorted_probs = sorted(enumerate(probs), key=lambda x: x[1], reverse=True)
            for idx, prob in sorted_probs:
                cls_name = names[idx]
                cls_color = CLASS_COLORS.get(cls_name, (200, 200, 200))
                bar_width = int(prob * 200)
                cv2.rectangle(frame, (20, y_offset - 12), (20 + bar_width, y_offset + 2), cls_color, -1)
                draw_text_with_bg(frame, f"{cls_name}: {prob*100:.1f}%", (230, y_offset), 0.5, cls_color, 1)
                y_offset += 25

        # Show instructions
        h = frame.shape[0]
        draw_text_with_bg(frame, "Q=Quit  D=Debug", (20, h - 20), 0.5, (150, 150, 150), 1)

        # Display
        cv2.imshow('Multi-Class Detector', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('d'):
            debug_mode = not debug_mode
            print(f"Debug mode: {'ON' if debug_mode else 'OFF'}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Live multi-class object detection demo')
    parser.add_argument('--weights', type=str, required=True,
                        help='Path to trained weights (e.g., runs/classify/train/weights/best.pt)')
    parser.add_argument('--imgsz', type=int, default=640,
                        help='Image size for model (default: 640)')
    parser.add_argument('--conf', type=float, default=15.0,
                        help='Confidence threshold percentage (default: 15.0)')
    parser.add_argument('--source', type=int, default=0,
                        help='Camera index (default: 0)')
    args = parser.parse_args()
    main(args.weights, args.imgsz, args.conf, args.source)
