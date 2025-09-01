# Data Preparation Guide

A well‑prepared dataset is critical for successful model training.  Follow the instructions below to capture and organise your images for the Halloween hand classification workshop.

## 1. Capture Photos

* **Number of images:** Aim for 50–100 photos in total.  More data generally yields better results, but even ~25 images per class can work for a simple workshop.
* **Hand images (`hand`):**
  * Photograph your 3D‑printed Halloween hand (or any hand) from various angles (front, side, top).
  * Vary the distance (close‑up and far away) and lighting (bright, dim, shadows).
  * Include different backgrounds so the model learns to focus on the hand.
* **Non‑hand images (`not_hand`):**
  * Capture random objects in your environment—books, mugs, keyboards, your face, etc.
  * Include the same backgrounds used for the hand images to avoid background bias.
* **Avoid duplicates:** Try not to take multiple identical shots.  Diversity helps the model generalise.

## 2. Create the Folder Structure

Organise your images in a folder tree like this (relative to the repository root):

```
hand_cls/
  train/
    hand/
    not_hand/
  val/
    hand/
    not_hand/
```

* **`train/`** contains the images used for training (~80 % of your photos).
* **`val/`** contains the validation images (~20 %).  The validation set provides an unbiased estimate of the model’s performance during training.

> The folder names (`hand` and `not_hand`) are the class labels—YOLOv8 automatically maps folder names to class indices.

### Example

Suppose you captured 60 images of the hand and 60 images of miscellaneous objects.  You might distribute them as follows:

* `hand_cls/train/hand` → 48 images
* `hand_cls/val/hand` → 12 images
* `hand_cls/train/not_hand` → 48 images
* `hand_cls/val/not_hand` → 12 images

There is no need to create annotation files; YOLOv8 will generate labels based on the folder names.

## 3. Optional Augmentation

If you have fewer images or want to increase robustness, you can augment your photos before or during training.  Ultralytics performs basic augmentation automatically, but you can manually create more examples by:

* Rotating images by ±10–30 degrees.
* Flipping horizontally or vertically.
* Adjusting brightness, contrast or colour.

Save augmented images in the same class folders.  Keep in mind that over‑augmentation can introduce artifacts; use moderation.

## 4. Verify the Dataset

Before training, verify that your folder structure looks like the example and that each folder contains the expected number of images.  You can run the following Python snippet to print a quick summary:

```python
import os
from collections import Counter

root = 'hand_cls'
for split in ['train', 'val']:
    for cls in ['hand', 'not_hand']:
        path = os.path.join(root, split, cls)
        count = len([f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        print(f"{split}/{cls}: {count} images")
```

If any class has far fewer images than the other, try to collect more data or augment existing images to balance the classes.
