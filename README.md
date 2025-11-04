## Cow Teat Labelling — privacy-first local pipeline for YOLOv8

Cow Teat Labelling is a lightweight, privacy-first toolchain to annotate images and train YOLOv8 object detectors for cow teat detection. The project prioritizes a fully local workflow: annotate with a GUI, prepare the dataset, train/export models, and package inference artifacts — without uploading images or labels to third-party services.

Highlights
- Local GUI labeling (labelImg) and small helper scripts for fast iteration
- Dataset preparation utilities (train/val split, sanity checks)
- YOLOv8 training orchestration and export (TorchScript / ONNX) via `scripts/full_pipeline.py`
- Packaging helpers for reproducible inference artifacts

Quick start (macOS / Linux)
Prerequisites: Python 3.9+ (3.11 recommended), git, and a working virtual environment.

1) Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

2) Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3) Annotate images (labelImg)

```bash
# Run the labelImg console script installed inside the venv (if available)
venv/bin/labelImg || python -m labelImg

# Save YOLO-format .txt files into `datasets/labels/` next to `datasets/raw_images/` images
```

4) Prepare the dataset for training

```bash
python scripts/prepare_data.py --src datasets/raw_images --labels datasets/labels --out datasets/processed --val-size 0.2
```

5) Train and export models (example)

```bash
python scripts/full_pipeline.py --imgsz 640 --epochs 50
```

See `scripts/` for additional flags (skip labeling, reuse split, export options).

labelImg installation & usage
----------------------------

The project uses labelImg for interactive bounding-box annotation. Below are practical, cross-platform installation steps and troubleshooting tips. Use a Python virtual environment to avoid conflicts with system libraries.

1) Create & activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # macOS / Linux
# or on Windows PowerShell:
# .\\venv\\Scripts\\Activate.ps1
```

2) Install labelImg (pip - preferred)

```bash
pip install --upgrade pip
pip install labelImg
```

3) macOS / Apple Silicon (M1/M2) notes

- If `pip install labelImg` fails due to PyQt5 wheel issues, try installing PyQt5 first:

```bash
pip install PyQt5==5.15.9 PyQt5-sip
pip install labelImg
```

- Alternatively, use Homebrew or conda (conda often resolves GUI dependency issues):

```bash
brew install qt@5
# or with conda:
conda create -n labelimg python=3.10
conda activate labelimg
conda install -c conda-forge pyqt lxml
pip install labelImg
```

4) Install from source (if you prefer latest code or need to patch)

```bash
git clone https://github.com/tzutalin/labelImg.git
cd labelImg
pip install -r requirements/requirements-linux-python3.txt   # choose the matching requirements file
python labelImg.py
```

5) Launching labelImg

```bash
venv/bin/labelImg           # if the console script is installed
# or
python -m labelImg
```

6) Save YOLO-format labels

- In the labelImg GUI, set the save format to YOLO (Format → YOLO) before saving annotations.
- Label files are saved as `.txt` with the same basename as images; store them under `datasets/labels/` next to `datasets/raw_images/`.
- Use 0-based class indices for YOLO (make sure `predefined_classes.txt` matches the label order).

7) Quick troubleshooting

- "ImportError: No module named PyQt5" — install PyQt5 inside the venv: `pip install PyQt5 PyQt5-sip`.
- "sip" or wheel mismatch errors — prefer `pip install PyQt5==5.15.9 PyQt5-sip` or use conda.
- Crashes on drawing/panning (macOS) — run labelImg from the same venv where PyQt5 is installed; consider conda if crashes persist.

8) Best practices

- Always run labelImg from an activated venv.
- Keep annotation backups (e.g., `tar -czvf labels_backup_$(date +%F).tar.gz datasets/labels`).
- Keep `datasets/raw_images/` and `datasets/labels/` in sync and do not commit these to the repo.

Publishing your repository
- When you're ready to publish publicly on GitHub:
  1. Create the repo on GitHub (name it `cow-teat-labelling`)
  2. Add the remote and push:

```bash
git remote add origin https://github.com/YOUR_USERNAME/cow-teat-labelling.git
git branch -M main
git push -u origin main
```

Note: for HTTPS pushes with 2FA enabled use a Personal Access Token (PAT) when prompted for a password; for SSH pushes ensure your SSH key is registered with your GitHub account.

License & contribution
----------------------
- Suggested license: MIT (recommended for maximum reuse). If you'd like, I can add a `LICENSE` file for you.
- Contributions: open issues or pull requests. For private/internal use, keep dataset and model artifacts out of the repository and use external storage (S3, NAS, encrypted drive) for backups.

Contact & next steps
- If you want, I can:
  - add an `LICENSE` (MIT) and a `CODE_OF_CONDUCT`
  - create a small pre-commit hook that blocks large files
  - push the repository to GitHub for you if you share the remote URL

---
This README contains installation guidance for labelImg and public release instructions.
