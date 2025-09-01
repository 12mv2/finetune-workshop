#!/usr/bin/env python3
"""
Create the required dataset directory structure for the workshop.
This helps participants quickly set up their folders correctly.
"""
import os
import sys


def create_dataset_structure(base_path='hand_cls'):
    """Create the directory structure for the Halloween hand dataset."""
    
    # Define the structure
    structure = {
        'train': ['hand', 'not_hand'],
        'val': ['hand', 'not_hand']
    }
    
    # Create base directory
    if not os.path.exists(base_path):
        os.makedirs(base_path)
        print(f"✓ Created base directory: {base_path}/")
    else:
        print(f"! Base directory already exists: {base_path}/")
    
    # Create subdirectories
    for split, classes in structure.items():
        split_path = os.path.join(base_path, split)
        if not os.path.exists(split_path):
            os.makedirs(split_path)
            print(f"✓ Created split directory: {split_path}/")
        
        for class_name in classes:
            class_path = os.path.join(split_path, class_name)
            if not os.path.exists(class_path):
                os.makedirs(class_path)
                print(f"✓ Created class directory: {class_path}/")
            else:
                print(f"! Class directory already exists: {class_path}/")
    
    # Create README in each directory
    readme_content = {
        'hand': "Place images of hands (Halloween prop or real hands) here.",
        'not_hand': "Place images of other objects (not hands) here."
    }
    
    for split in ['train', 'val']:
        for class_name, description in readme_content.items():
            readme_path = os.path.join(base_path, split, class_name, 'README.txt')
            if not os.path.exists(readme_path):
                with open(readme_path, 'w') as f:
                    f.write(f"{description}\n")
                    f.write(f"\n{split.capitalize()} set - {class_name}\n")
                    if split == 'train':
                        f.write("Aim for ~40 images in this folder.\n")
                    else:
                        f.write("Aim for ~10 images in this folder.\n")
    
    print("\n✅ Dataset structure created successfully!")
    print("\n📁 Directory structure:")
    print_tree(base_path)
    
    print("\n📝 Next steps:")
    print("1. Add your images to the appropriate folders:")
    print("   - hand: Photos of hands (Halloween prop or real hands)")
    print("   - not_hand: Photos of other objects")
    print("2. Aim for ~80% train, ~20% validation split")
    print("3. Use .jpg, .jpeg, or .png formats")


def print_tree(directory, prefix=""):
    """Print directory tree structure."""
    entries = sorted(os.listdir(directory))
    entries = [e for e in entries if not e.startswith('.') and e != 'README.txt']
    
    for i, entry in enumerate(entries):
        path = os.path.join(directory, entry)
        is_last = i == len(entries) - 1
        
        print(prefix + ("└── " if is_last else "├── ") + entry + "/")
        
        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            print_tree(path, prefix + extension)


def check_dataset(base_path='hand_cls'):
    """Check if dataset is properly structured and has images."""
    print("\n🔍 Checking dataset...")
    
    total_images = 0
    image_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
    
    for split in ['train', 'val']:
        print(f"\n{split.upper()} set:")
        for class_name in ['hand', 'not_hand']:
            class_path = os.path.join(base_path, split, class_name)
            if os.path.exists(class_path):
                images = [f for f in os.listdir(class_path) 
                         if f.endswith(image_extensions)]
                count = len(images)
                total_images += count
                print(f"  {class_name}: {count} images")
                
                if count == 0:
                    print(f"    ⚠️  No images found! Add images to: {class_path}")
            else:
                print(f"  {class_name}: ❌ Directory missing!")
    
    print(f"\nTotal images: {total_images}")
    
    if total_images < 50:
        print("⚠️  Warning: You have fewer than 50 images. Consider adding more for better results.")
    elif total_images >= 100:
        print("✅ Great! You have enough images for training.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        check_dataset()
    else:
        create_dataset_structure()
        
        print("\n💡 Tip: Run 'python create_dataset_structure.py check' to verify your dataset after adding images.")