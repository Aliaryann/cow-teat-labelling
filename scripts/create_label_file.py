import os

def create_yolo_label_file(image_filename, image_width, image_height, output_dir, labels):
    """
    Creates a YOLO format label file programmatically from pixel coordinates.

    Args:
        image_filename (str): The filename of the image (e.g., 'cow1.jpg').
        image_width (int): The total width of the image in pixels.
        image_height (int): The total height of the image in pixels.
        output_dir (str): Directory to save the .txt label file.
        labels (list of dicts): A list of labels for the image.
            Each dict should have:
            - 'class_id': The integer ID for the class (e.g., 0 for 'teat').
            - 'box': A list/tuple of [x_min, y_min, x_max, y_max] in pixel coordinates.
    """
    yolo_lines = []
    for label in labels:
        class_id = label['class_id']
        box = label['box']
        x_min, y_min, x_max, y_max = box

        # Convert pixel coordinates to YOLO format (normalized center_x, center_y, width, height)
        x_center = (x_min + x_max) / 2.0
        y_center = (y_min + y_max) / 2.0
        width = x_max - x_min
        height = y_max - y_min

        x_center_norm = x_center / image_width
        y_center_norm = y_center / image_height
        width_norm = width / image_width
        height_norm = height / image_height

        yolo_lines.append(f"{class_id} {x_center_norm:.6f} {y_center_norm:.6f} {width_norm:.6f} {height_norm:.6f}")

    label_filename = os.path.splitext(image_filename)[0] + '.txt'
    output_path = os.path.join(output_dir, label_filename)

    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join(yolo_lines))
    
    print(f"Successfully created label file: {output_path}")

if __name__ == '__main__':
    # --- Example Usage ---
    # Suppose you have an image 'test_cow.jpg' with dimensions 1920x1080
    # And you know the coordinates of two teats.

    image_file = 'test_cow.jpg'
    img_w, img_h = 1920, 1080
    labels_dir = 'datasets/labels'

    # The coordinates for two teats in pixels: [x_min, y_min, x_max, y_max]
    known_labels = [
        {
            'class_id': 0,  # 'teat' is class 0
            'box': [800, 600, 850, 680]  # First teat
        },
        {
            'class_id': 0,
            'box': [950, 610, 1000, 690] # Second teat
        }
    ]

    create_yolo_label_file(image_file, img_w, img_h, labels_dir, known_labels)

    # This will create 'datasets/labels/test_cow.txt' with the corresponding YOLO-formatted data.
