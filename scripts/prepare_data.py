import os
import shutil
import random
from sklearn.model_selection import train_test_split

def prepare_yolo_dataset(data_dir, output_dir, train_ratio=0.8):
    images_dir = os.path.join(data_dir, 'raw_images')
    labels_dir = os.path.join(data_dir, 'labels')
    
    # Get all image files
    image_files = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    
    # Split train/val
    train_files, val_files = train_test_split(image_files, train_size=train_ratio, random_state=42)
    
    # Create directories
    for split in ['train', 'val']:
        os.makedirs(os.path.join(output_dir, 'images', split), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'labels', split), exist_ok=True)
    
    # Copy files
    for split, files in [('train', train_files), ('val', val_files)]:
        for file in files:
            # Copy image
            shutil.copy(
                os.path.join(images_dir, file),
                os.path.join(output_dir, 'images', split, file)
            )
            # Copy label
            label_file = os.path.splitext(file)[0] + '.txt'
            if os.path.exists(os.path.join(labels_dir, label_file)):
                shutil.copy(
                    os.path.join(labels_dir, label_file),
                    os.path.join(output_dir, 'labels', split, label_file)
                )
    
    print(f"Dataset prepared: {len(train_files)} train, {len(val_files)} val images")

if __name__ == "__main__":
    prepare_yolo_dataset('datasets', 'datasets/processed')
