#!/usr/bin/env python3
"""
Debug version of live demo - shows ALL predictions and confidence scores.
"""
import argparse
import cv2
import torch
from ultralytics import YOLO


def main(weights: str, imgsz: int = 224) -> None:
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
    print(f"\nModel loaded: {weights}")
    print(f"Classes: {model.names}")

    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    print("\nPress 'q' to quit.")
    print("\nShowing ALL predictions with confidence scores...\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame
        resized = cv2.resize(frame, (imgsz, imgsz))

        # Run inference
        results = model(resized, verbose=False, device=device)[0]
        probs = results.probs.data.tolist()
        names = results.names

        # Display ALL classes with their confidence
        y_offset = 30
        for idx, (class_name, confidence) in enumerate(zip(names.values(), probs)):
            conf_pct = confidence * 100

            # Color code: Green if high confidence, white if low
            color = (0, 255, 0) if conf_pct > 50 else (200, 200, 200)

            text = f"{class_name}: {conf_pct:.1f}%"
            cv2.putText(
                frame,
                text,
                (20, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2,
                cv2.LINE_AA,
            )
            y_offset += 35

        # Show which class won
        top_idx = probs.index(max(probs))
        winner = names[top_idx]
        cv2.putText(
            frame,
            f"PREDICTED: {winner}",
            (20, frame.shape[0] - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 255),
            3,
            cv2.LINE_AA,
        )

        cv2.imshow('Debug Demo - All Predictions', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Debug demo showing all predictions')
    parser.add_argument('--weights', type=str, required=True, help='Path to trained weights')
    parser.add_argument('--imgsz', type=int, default=224, help='Image size (default: 224)')
    args = parser.parse_args()
    main(args.weights, args.imgsz)
