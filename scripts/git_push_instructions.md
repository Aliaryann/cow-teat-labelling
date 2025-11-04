# Git push instructions & safety checklist

Before pushing to a remote, verify these items locally:

- .gitignore includes: `venv/`, `datasets/`, `models/`, `runs/`, `packages/`, and any other private folders.
- `requirements.txt` exists so others can recreate your environment.
- No large files (images, labels, model weights) are staged. Use `git status` and `git ls-files --exclude-standard -oi --directory` to inspect.

Common commands (replace the URL with your repo):

1. Remove venv from git index if needed:

   bash scripts/remove_venv_from_git.sh

2. Stage and commit code (no private data):

   git add .
   git commit -m "Initial commit: cow_teat_detection pipeline (no private data)"

3. Add remote and push:

   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/cow-teat-detection.git
   git push -u origin main

If you accidentally added large files, use `git rm --cached <path>` to unstage them or use the `BFG` tool to remove them from history before pushing.

If you want, I can prepare a short script to detect accidentally staged large files before commit and block the commit locally (pre-commit hook). Ask and I will add it.
