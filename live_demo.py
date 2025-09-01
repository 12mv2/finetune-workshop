#!/usr/bin/env python3
"""
Live webcam demo for the Halloween hand classifier.

This script loads a trained YOLOv8 classifier and opens the default webcam.  For
each frame, it predicts the class label.  If the hand is detected, a spooky
message is overlaid on the frame.  Press `q` to quit.
"""
import argparse
import cv2
from ultralytics import YOLO


def main(weights: str, imgsz: int = 224) -> None:
    # Load trained model
    model = YOLO(weights)

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

        # Run inference
        results = model(resized, verbose=False)[0]
        # Find the class with the highest probability
        probs = results.probs.data.tolist()
        names = results.names
        top_idx = probs.index(max(probs))
        label = names[top_idx]

        # Overlay message if hand is detected
        if label == 'hand_prop':
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
    args = parser.parse_args()
    main(args.weights, args.imgsz)
