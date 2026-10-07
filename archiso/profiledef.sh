#!/usr/bin/env bash
# profiledef.sh for Rimuru OS Live Media

iso_name="rimuru-os"
iso_label="RIMURU_$(date +%Y%m)"
iso_publisher="Rimuru OS Project <https://github.com/gowdaman/rimuru-os>"
iso_application="Rimuru OS - AI-Native Orchestrator Operating System"
iso_version="$(date +%Y.%m.%d)"
install_dir="rimuru"
buildmodes=('iso')
bootmodes=('uefi-x64.systemd-boot.esp' 'uefi-x64.systemd-boot.eltorito')
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd' '-Xcompression-level' '15' '-b' '1M')
file_permissions=(
  ["/usr/bin/rimuru"]="0:0:755"
  ["/usr/bin/rimuru-snapshot"]="0:0:755"
  ["/usr/bin/rimuru-store"]="0:0:755"
  ["/usr/bin/rimuru-orchestratord"]="0:0:755"
)
