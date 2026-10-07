#!/usr/bin/env bash
# scripts/test-qemu.sh
# Tests the generated Rimuru OS ISO in QEMU with UEFI (OVMF) and KVM acceleration

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
OUT_DIR="$PROJECT_ROOT/out"

ISO_FILE=$(ls -t "$OUT_DIR"/rimuru-os-*.iso 2>/dev/null | head -n 1 || true)

if [ -z "$ISO_FILE" ]; then
    echo "[-] No ISO found in $OUT_DIR. Please run ./scripts/build-iso.sh first."
    exit 1
fi

echo "[+] Booting $ISO_FILE in QEMU/KVM..."

qemu-system-x86_64 \
    -enable-kvm \
    -m 4G \
    -smp 4 \
    -cpu host \
    -vga virtio \
    -display sdl,gl=on \
    -device virtio-net-pci,netdev=net0 \
    -netdev user,id=net0 \
    -drive file="$ISO_FILE",media=cdrom,readonly=on \
    -boot d
