#!/usr/bin/env python3
"""
Build a multi-class dataset from individual binary classifiers.

Takes datasets structured as:
    Training Data/
        hand1_cls/train/hand/, not_hand/
        orangeBall_cls/train/hand/, not_hand/
        ...

And reorganizes into:
    multi_cls/
        train/
            hand/
            orange_ball/
            hammer/
            ...
            background/  (combined negatives)
        val/
            [same structure]
"""
import os
import shutil
import random
import argparse
from pathlib import Path

# Configuration: Map source folders to class names
# Format: (source_folder_name, target_class_name)
#
# Default mapping for capture_multiclass.py output:
CLASS_MAPPING = [
    ("hand_cls", "hand"),
    ("9v_battery_cls", "9v_battery"),
    ("black_spool_cls", "black_spool"),
    ("green_spool_cls", "green_spool"),
    ("hammer_cls", "hammer"),
    ("blue_floppy_cls", "blue_floppy"),
]

# Legacy mapping (for old dataset structure):
# CLASS_MAPPING = [
#     ("hand1_cls", "hand"),
#     ("orangeBall_cls", "orange_ball"),
#     ("orange2_cls", "orange_ball"),  # Merged with orange_ball
#     ("hammer_cls", "hammer"),
#     ("greenSpool_cls", "green_spool"),
#     ("blackSpoolFilament_cls", "black_spool"),
#     ("9vBatteryExchange_cls", "9v_battery"),
# ]

SOURCE_DIR = Path("Training Data")


def count_files(directory: Path) -> int:
    """Count image files in a directory."""
    if not directory.exists():
        return 0
    return len([f for f in directory.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png')])


def copy_images(src_dir: Path, dst_dir: Path, prefix: str = "", max_count: int = None) -> int:
    """Copy images from src to dst, optionally adding a prefix to avoid name collisions.

    Args:
        max_count: If specified, randomly sample this many images instead of copying all.
    """
    if not src_dir.exists():
        print(f"  Warning: {src_dir} does not exist, skipping")
        return 0

    dst_dir.mkdir(parents=True, exist_ok=True)
    copied = 0

    # Get all image files
    img_files = [f for f in src_dir.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png')]

    # Apply random sampling if max_count specified
    if max_count is not None and len(img_files) > max_count:
        img_files = random.sample(img_files, max_count)

    for img_file in img_files:
        if prefix:
            new_name = f"{prefix}_{img_file.name}"
        else:
            new_name = img_file.name

        dst_path = dst_dir / new_name
        # Handle duplicates by adding a number
        counter = 1
        while dst_path.exists():
            stem = img_file.stem
            suffix = img_file.suffix
            dst_path = dst_dir / f"{prefix}_{stem}_{counter}{suffix}" if prefix else dst_dir / f"{stem}_{counter}{suffix}"
            counter += 1

        shutil.copy2(img_file, dst_path)
        copied += 1

    return copied


def main():
    parser = argparse.ArgumentParser(description="Build multi-class dataset from binary classifiers")
    parser.add_argument("--undersample-background", type=int, metavar="N",
                        help="Randomly sample N background images per split (default: use all)")
    parser.add_argument("--output", type=str, default="multi_cls",
                        help="Output directory name (default: multi_cls)")
    args = parser.parse_args()

    output_dir = Path(args.output)
    bg_limit = args.undersample_background

    print("=" * 60)
    if bg_limit:
        print(f"Building Balanced Multi-Class Dataset (background={bg_limit})")
    else:
        print("Building Multi-Class Dataset (full background)")
    print("=" * 60)

    # Check source exists
    if not SOURCE_DIR.exists():
        print(f"Error: Source directory '{SOURCE_DIR}' not found")
        return 1

    # Clean output directory if exists
    if output_dir.exists():
        print(f"\nRemoving existing {output_dir}...")
        shutil.rmtree(output_dir)

    # Create output structure
    for split in ['train', 'val']:
        (output_dir / split / 'background').mkdir(parents=True, exist_ok=True)
        for _, class_name in CLASS_MAPPING:
            (output_dir / split / class_name).mkdir(parents=True, exist_ok=True)

    print(f"\nSource: {SOURCE_DIR.absolute()}")
    print(f"Output: {output_dir.absolute()}")
    print(f"\nClasses: {[c[1] for c in CLASS_MAPPING]} + background")
    if bg_limit:
        print(f"Background limit: {bg_limit} images per split")
    print()

    # Process each source dataset
    stats = {'train': {}, 'val': {}}

    for source_name, class_name in CLASS_MAPPING:
        source_path = SOURCE_DIR / source_name

        if not source_path.exists():
            print(f"⚠ Skipping {source_name} (not found)")
            continue

        print(f"Processing {source_name} → {class_name}")

        for split in ['train', 'val']:
            # Copy positive class (currently named 'hand' in source)
            positive_src = source_path / split / 'hand'
            positive_dst = output_dir / split / class_name

            count = copy_images(positive_src, positive_dst, prefix=class_name)
            stats[split][class_name] = stats[split].get(class_name, 0) + count
            print(f"  {split}/hand → {split}/{class_name}: {count} images")

            # Copy negative class to background (with prefix to avoid collisions)
            negative_src = source_path / split / 'not_hand'
            background_dst = output_dir / split / 'background'

            count = copy_images(negative_src, background_dst, prefix=f"{class_name}_bg")
            stats[split]['background'] = stats[split].get('background', 0) + count
            print(f"  {split}/not_hand → {split}/background: {count} images")

    # Apply background undersampling if requested
    if bg_limit:
        print(f"\nUndersampling background class to {bg_limit} per split...")
        for split in ['train', 'val']:
            bg_dir = output_dir / split / 'background'
            bg_files = [f for f in bg_dir.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png')]

            if len(bg_files) > bg_limit:
                # Keep random sample
                files_to_keep = set(random.sample(bg_files, bg_limit))
                # Remove the rest
                removed = 0
                for f in bg_files:
                    if f not in files_to_keep:
                        f.unlink()
                        removed += 1

                stats[split]['background'] = bg_limit
                print(f"  {split}/background: {len(bg_files)} → {bg_limit} (removed {removed})")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for split in ['train', 'val']:
        print(f"\n{split.upper()}:")
        total = 0
        for class_name in sorted(stats[split].keys()):
            count = stats[split][class_name]
            total += count
            print(f"  {class_name}: {count} images")
        print(f"  TOTAL: {total} images")

    print("\n" + "=" * 60)
    print("DATASET READY!")
    print("=" * 60)
    print(f"\nOutput: {output_dir}/")
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("\nTrain your model:")
    print("  source .venv/bin/activate")
    print(f"  yolo classify train model=yolov8n-cls.pt data={output_dir} epochs=25 batch=16 patience=10 device=cpu")
    print("\nAfter training, test your model:")
    print("  python3 live_demo.py --weights runs/classify/trainN/weights/best.pt")
    print("  (replace trainN with your actual folder from 'Results saved to' output)")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
