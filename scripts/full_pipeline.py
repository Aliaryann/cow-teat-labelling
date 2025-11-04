import os
import sys
import subprocess
import yaml
import shutil
import argparse
from datetime import datetime
from pathlib import Path
import random


def read_classes(path='datasets/predefined_classes.txt'):
    if os.path.exists(path):
        with open(path) as f:
            return [ln.strip() for ln in f if ln.strip() and not ln.startswith('#')]
    return ['teat']


class CowTeatDetection:
    def __init__(self, project_dir, skip_labeling=False):
        self.project_dir = project_dir
        self.skip_labeling = skip_labeling
        self.raw_images_dir = os.path.join(project_dir, 'datasets/raw_images')
        self.labels_dir = os.path.join(project_dir, 'datasets/labels')

    def setup_directories(self):
        dirs = [
            'datasets/raw_images',
            'datasets/labels',
            'datasets/processed/images/train',
            'datasets/processed/images/val',
            'datasets/processed/labels/train',
            'datasets/processed/labels/val',
            'models',
            'results',
            'packages'
        ]
        for d in dirs:
            os.makedirs(os.path.join(self.project_dir, d), exist_ok=True)
        print("Directory structure verified / created")

    def start_labeling(self):
        if self.skip_labeling:
            print("Skipping labeling phase (--skip-labeling).")
            return
        print("Starting LabelImg...")
        print(f"Image directory: {self.raw_images_dir}")
        python_executable_dir = os.path.dirname(sys.executable)
        labelimg_path = os.path.join(python_executable_dir, 'labelImg')
        if sys.platform == 'win32':
            labelimg_path = os.path.join(python_executable_dir, 'Scripts', 'labelImg.exe')
        try:
            subprocess.run([
                labelimg_path,
                self.raw_images_dir,
                os.path.join(self.project_dir, 'datasets/predefined_classes.txt'),
                self.labels_dir
            ], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print('\n--- ERROR ---')
            print(f'Could not launch LabelImg. Tried: {labelimg_path}')
            print('pip install --force-reinstall labelImg')
            sys.exit(1)

    def train_model(self, model_size='n', epochs=100, imgsz=640):
        from ultralytics import YOLO
        classes = read_classes()
        cfg = {
            'path': os.path.abspath('datasets/processed'),
            'train': 'images/train',
            'val': 'images/val',
            'nc': len(classes),
            'names': classes
        }
        with open('teat_dataset.yaml', 'w') as f:
            yaml.safe_dump(cfg, f)
        run_name = f'teat_detector_v8{model_size}'
        print(f'Training with classes: {classes}')
        model = YOLO(f'yolov8{model_size}.pt')
        model.train(data='teat_dataset.yaml', epochs=epochs, imgsz=imgsz, batch=16, name=run_name)

        # Copy best weights
        best_src = Path(f'runs/detect/{run_name}/weights/best.pt')
        best_dst = Path(f'models/best_{run_name}.pt')
        if best_src.exists():
            shutil.copy2(best_src, best_dst)
            print(f'Best weights copied to {best_dst}')
        else:
            print('WARNING: best.pt not found.')

        # Exports
        try:
            print('Exporting ONNX...')
            model.export(format='onnx', imgsz=imgsz, opset=12)
        except Exception as e:
            print(f'ONNX export failed: {e}')
        try:
            print('Exporting TorchScript...')
            model.export(format='torchscript', imgsz=imgsz)
        except Exception as e:
            print(f'TorchScript export failed: {e}')

        # Freeze environment
        try:
            req_file = Path('models/requirements_freeze.txt')
            with open(req_file, 'w') as f:
                subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=f, check=True)
            print(f'Environment frozen to {req_file}')
        except Exception as e:
            print(f'Requirements freeze failed: {e}')

        # Package
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pkg_dir = Path('packages') / f'package_{run_name}_{timestamp}'
        pkg_dir.mkdir(parents=True, exist_ok=True)
        to_copy = [
            best_dst,
            Path('teat_dataset.yaml'),
            Path('datasets/predefined_classes.txt'),
            Path(f'runs/detect/{run_name}/weights/{run_name}.onnx'),
            Path(f'runs/detect/{run_name}/weights/{run_name}.torchscript'),
            Path('models/requirements_freeze.txt')
        ]
        for p in to_copy:
            if p.exists():
                shutil.copy2(p, pkg_dir / p.name)
        meta = {
            'run_name': run_name,
            'classes': classes,
            'epochs': epochs,
            'imgsz': imgsz,
            'timestamp': timestamp,
            'weights': f'best_{run_name}.pt'
        }
        with open(pkg_dir / 'package_meta.yaml', 'w') as f:
            yaml.safe_dump(meta, f)
        print(f'Packaged artifacts -> {pkg_dir}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip-labeling', action='store_true')
    parser.add_argument('--model-size', default='n')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--reuse-split', action='store_true', help='Do not regenerate train/val split if processed data exists')
    args = parser.parse_args()

    det = CowTeatDetection('.', skip_labeling=args.skip_labeling)
    det.setup_directories()
    if not args.skip_labeling:
        print("1. Place images in datasets/raw_images/")
        print("2. Label when tool opens (YOLO format). Press Enter to continue.")
        input()
    det.start_labeling()
    def processed_has_content():
        p = Path('datasets/processed/images/train')
        return p.exists() and any(p.iterdir())

    if args.reuse_split and processed_has_content():
        print('Reusing existing processed dataset split.')
    else:
        print('Preparing dataset...')
        # Try to import the official prepare script; fallback to internal splitter if it fails
        try:
            from scripts.prepare_data import prepare_yolo_dataset  # type: ignore
            prepare_yolo_dataset('datasets', 'datasets/processed')
        except Exception as e:  # broad fallback: we want robustness here
            print(f'prepare_data.py failed ({e}); using simple internal splitter.')
            # Simple fallback splitter not requiring sklearn
            raw_images = Path('datasets/raw_images')
            labels_root = Path('datasets/labels')
            all_imgs = [f for f in raw_images.iterdir() if f.suffix.lower() in {'.jpg','.jpeg','.png'}]
            random.seed(42)
            random.shuffle(all_imgs)
            split_idx = int(0.8 * len(all_imgs))
            train_imgs = all_imgs[:split_idx]
            val_imgs = all_imgs[split_idx:]
            for split, collection in [('train', train_imgs), ('val', val_imgs)]:
                (Path('datasets/processed/images')/split).mkdir(parents=True, exist_ok=True)
                (Path('datasets/processed/labels')/split).mkdir(parents=True, exist_ok=True)
                for img in collection:
                    shutil.copy2(img, Path('datasets/processed/images')/split/img.name)
                    label_file = labels_root / (img.stem + '.txt')
                    if label_file.exists():
                        shutil.copy2(label_file, Path('datasets/processed/labels')/split/label_file.name)
            print(f"Fallback dataset prepared: {len(train_imgs)} train, {len(val_imgs)} val images")
    print('Starting training...')
    det.train_model(model_size=args.model_size, epochs=args.epochs, imgsz=args.imgsz)


if __name__ == '__main__':
    main()
