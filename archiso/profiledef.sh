#!/usr/bin/env bash
# profiledef.sh for Rimuru OS Live Media

iso_name="rimuru-os"
iso_label="RIMURU_$(date +%Y%m)"
iso_publisher="Rimuru OS Project <https://github.com/gowdaman/rimuru-os>"
iso_application="Rimuru OS - AI-Native Orchestrator Operating System"
iso_version="$(date +%Y.%m.%d)"
install_dir="rimuru"
buildmodes=('iso')
bootmodes=('bios.syslinux.mbr' 'bios.syslinux.eltorito' 'uefi-ia32.systemd-boot.eltorito' 'uefi-x64.systemd-boot.eltorito')
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd' '-Xcompression-level' '15' '-b' '1M')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/etc/gshadow"]="0:0:400"
  ["/etc/sudoers"]="0:0:440"
  ["/root"]="0:0:700"
  ["/root/.automated_script.sh"]="0:0:755"
  ["/usr/local/bin/choose-mirror"]="0:0:755"
  ["/usr/local/bin/rimuru-installer"]="0:0:755"
  ["/usr/bin/rimuru"]="0:0:755"
  ["/usr/bin/rimuru-snapshot"]="0:0:755"
)
