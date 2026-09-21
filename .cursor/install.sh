#!/usr/bin/env bash
# Idempotent setup for the sketch-icons asset library.
# Installs tooling used to validate, convert, and optimize the SVG/PNG icon
# assets, then generates the static preview gallery.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> Installing system asset tooling (librsvg, ImageMagick, optipng)"
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  librsvg2-bin \
  imagemagick \
  optipng

# svgo optimizes/pretty-prints SVGs. The user's npm global prefix requires root
# to write, so preserve PATH when installing under sudo. Skip if already present.
if ! command -v svgo >/dev/null 2>&1; then
  echo "==> Installing svgo (SVG optimizer)"
  sudo env "PATH=$PATH" npm install -g svgo
else
  echo "==> svgo already installed: $(svgo --version)"
fi

echo "==> Generating preview gallery"
python3 .cursor/gallery.py

echo "==> Install complete"
