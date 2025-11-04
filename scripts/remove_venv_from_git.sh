#!/usr/bin/env bash
# Safe helper to remove venv from git index if it was accidentally added.
# Usage: run from repository root: bash scripts/remove_venv_from_git.sh

set -euo pipefail

if [ ! -d .git ]; then
  echo "No .git directory found. Initialize git repository first or run this from project root."
  exit 1
fi

if git ls-files --error-unmatch venv >/dev/null 2>&1; then
  echo "Removing venv/ from git index (cached) and adding to .gitignore..."
  git rm -r --cached venv || true
else
  echo "venv/ is not tracked by git index."
fi

# Ensure .gitignore contains venv/
if ! grep -qx "venv/" .gitignore 2>/dev/null; then
  echo "Adding venv/ to .gitignore"
  printf "\nvenv/\n" >> .gitignore
else
  echo ".gitignore already contains venv/"
fi

echo "Staging .gitignore and commit suggestion."
git add .gitignore || true
echo "You can now run:"
echo "  git add ."
echo "  git commit -m \"Remove venv from repo and update .gitignore\""
echo "Then push as usual with your remote."
