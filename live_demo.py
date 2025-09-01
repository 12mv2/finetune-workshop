#!/usr/bin/env python3
"""
Live webcam demo for the Halloween hand classifier.

This script loads a trained YOLOv8 classifier and opens the default webcam.  For
each frame, it predicts the class label.  If the hand is detected, a spooky
message is overlaid on the frame.  Press `q` to quit.
"""
import argparse
import cv2
import numpy as np
import os
import torch
from ultralytics import YOLO


def load_overlay_image(path: str, width: int, height: int):
    """Load and resize an overlay image with transparency."""
    if os.path.exists(path):
        overlay = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if overlay is not None:
            return cv2.resize(overlay, (width, height))
    return None


def apply_overlay(frame, overlay, x, y):
    """Apply an overlay image with transparency to a frame."""
    if overlay is None:
        return frame
    
    h, w = overlay.shape[:2]
    if y + h > frame.shape[0] or x + w > frame.shape[1]:
        return frame
    
    if overlay.shape[2] == 4:  # Has alpha channel
        alpha = overlay[:, :, 3] / 255.0
        for c in range(3):
            frame[y:y+h, x:x+w, c] = (1 - alpha) * frame[y:y+h, x:x+w, c] + alpha * overlay[:, :, c]
    else:
        frame[y:y+h, x:x+w] = overlay[:, :, :3]
    
    return frame


def main(weights: str, imgsz: int = 224, use_overlay: bool = True) -> None:
    # Detect device
    if torch.backends.mps.is_available():
        device = 'mps'
        print("Using Apple Silicon GPU (MPS)")
    elif torch.cuda.is_available():
        device = 'cuda'
        print("Using NVIDIA GPU (CUDA)")
    else:
        device = 'cpu'
        print("Using CPU")
    
    # Load trained model
    model = YOLO(weights)
    
    # Try to load overlay images
    ghost_overlay = None
    if use_overlay:
        ghost_overlay = load_overlay_image('assets/ghost.png', 150, 150)
        if ghost_overlay is None:
            print("Warning: Could not load overlay image. Using text only.")

    # Open webcam (0 is usually the default camera)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam. Check your camera connection.")

    print("Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame to the model's expected image size
        resized = cv2.resize(frame, (imgsz, imgsz))

        # Run inference with specified device
        results = model(resized, verbose=False, device=device)[0]
        # Find the class with the highest probability
        probs = results.probs.data.tolist()
        names = results.names
        top_idx = probs.index(max(probs))
        label = names[top_idx]

        # Overlay message if hand is detected
        if label == 'hand':
            # Apply ghost overlay if available
            if ghost_overlay is not None:
                # Position ghost in upper right
                x = frame.shape[1] - 200
                y = 50
                frame = apply_overlay(frame, ghost_overlay, x, y)
            
            # Add spooky text
            cv2.putText(
                frame,
                'Spooky hand detected!',
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )
            
            # Add confidence score
            confidence = max(probs) * 100
            cv2.putText(
                frame,
                f'Confidence: {confidence:.1f}%',
                (50, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

        # Display the resulting frame
        cv2.imshow('Halloween Hand Demo', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Live webcam demo for the Halloween hand classifier')
    parser.add_argument('--weights', type=str, required=True, help='Path to trained weights (e.g., runs/classify/train/weights/best.pt)')
    parser.add_argument('--imgsz', type=int, default=224, help='Image size expected by the model (default: 224)')
    parser.add_argument('--no-overlay', action='store_true', help='Disable overlay images (use text only)')
    args = parser.parse_args()
    main(args.weights, args.imgsz, use_overlay=not args.no_overlay)
