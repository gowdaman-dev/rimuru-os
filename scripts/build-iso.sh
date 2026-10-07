#!/usr/bin/env bash
# scripts/build-iso.sh
# Master build script to generate the Rimuru OS Live ISO using mkarchiso

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ARCHISO_PROFILE="$PROJECT_ROOT/archiso"
WORK_DIR="/tmp/rimuru-build-work"
OUT_DIR="$PROJECT_ROOT/out"

echo "=========================================================="
echo "      Rimuru OS Live ISO Builder"
echo "=========================================================="

# Check requirements
if ! command -v mkarchiso >/dev/null 2>&1; then
    echo "[!] mkarchiso not found. Installing 'archiso' package via pacman..."
    sudo pacman -S --needed --noconfirm archiso
fi

# Prepare repository
echo "==> Preparing [rimuru] local package repository..."
"$SCRIPT_DIR/make-repo.sh"

# Create output folder
mkdir -p "$OUT_DIR"
rm -rf "$WORK_DIR"

echo "==> Building Rimuru OS ISO..."
sudo mkarchiso -v -w "$WORK_DIR" -o "$OUT_DIR" "$ARCHISO_PROFILE"

echo "=========================================================="
echo "==> Rimuru OS ISO build finished successfully!"
echo "    Generated ISO location: $OUT_DIR"
echo "=========================================================="
