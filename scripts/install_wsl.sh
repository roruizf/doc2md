#!/usr/bin/env bash
set -euo pipefail

echo "Installing doc2md system dependencies for WSL Ubuntu..."
if ! sudo apt-get update; then
  echo "apt update failed - check your network and sudo access" >&2
  exit 1
fi

if ! sudo apt-get install -y \
  tesseract-ocr \
  tesseract-ocr-eng \
  tesseract-ocr-fra \
  qpdf \
  pandoc \
  libmagic1 \
  poppler-utils; then
  echo "apt install failed - check your sudo access and package repositories" >&2
  exit 1
fi

echo "Installing doc2md Python package..."
if command -v pipx >/dev/null 2>&1; then
  if ! pipx install .; then
    echo "pipx install failed - check the Python build logs above" >&2
    exit 1
  fi
else
  if ! python3 -m pip install --user .; then
    echo "pip install --user failed - install pipx or check Python packaging logs" >&2
    exit 1
  fi
fi

echo "Verifying doc2md install..."
if ! doc2md --version; then
  echo "doc2md --version failed - ensure ~/.local/bin or pipx bin dir is on PATH" >&2
  exit 1
fi

echo "doc2md installation complete."
