# Rimuru OS
> **The AI-Native, Autonomous Orchestrator Operating System**

Rimuru OS is a rolling, Arch-based operating system designed from scratch to integrate multi-agent AI orchestration, Btrfs snapshots, and a modern developer desktop environment into a single, cohesive operating system experience.

---

## Key Highlights

- **The Operating System IS the Orchestrator**: Instead of managing disparate third-party multi-agent frameworks, `rimuru-orchestratord` runs at the system level. It decomposes user goals into parallel Directed Acyclic Graphs (DAGs), spawns concurrent workers, schedules operations via an isolated Bubblewrap syscall harness, and persists state across sessions.
- **Atomic Btrfs Snapshots & Recovery**: Built-in Snapper integration with automated pre/post transaction hooks (`snap-pac`). Any package upgrade, installation, or agent-initiated file modification can be rolled back instantly via `rimuru-snapshot rollback <id>` or through the UEFI boot menu.
- **Bleeding-Edge Kernel & Arch Base**: Modern rolling Linux 7.2.x series kernel with `PREEMPT_DYNAMIC` and Wayland optimizations, powered by `pacman`, `yay`, and a curated `[rimuru]` repository.
- **Fluid Wayland Desktop**: Native **Hyprland** dynamic tiling compositor with Aquamarine backend, glowing agent indicators, preview share picker, and custom window rules.
- **Ghostty + Tmux Experience**: Ultra-low latency, GPU-accelerated **Ghostty** terminal pre-configured with **tmux** workspace sessions and real-time AI worker monitoring splits.
- **Native Quick Share**: Out-of-the-box Nearby Share / Quick Share daemon (`rquickshare-x`) enabling peer-to-peer file transfers between Rimuru OS, Android, Windows, and Apple devices.
- **Rimuru Store**: A native GTK4/Libadwaita GUI software installer with AI-generated package descriptions, dependency breakdowns, security ratings, and one-click installs.

---

## Directory Structure

```
rimuru-os/
├── archiso/                    # mkarchiso profile for the Live ISO
│   ├── airootfs/               # Filesystem overlay (/etc, /usr, skel dotfiles)
│   ├── packages.x86_64         # Master ISO package manifest
│   ├── pacman.conf             # Build-time pacman repository config
│   └── profiledef.sh           # ISO metadata and permissions
├── apps/                       # Native Rimuru Applications
│   ├── rimuru-store/           # GTK4 / Libadwaita GUI package installer
│   ├── rimuru-cockpit/         # Multi-agent orchestrator dashboard
│   └── rimuru-share/           # Quick Share Wayland frontend
├── orchestrator/               # rimuru-orchestratord
│   └── src/                    # Syscall harness, DAG scheduler, socket API
├── shell/                      # Desktop Environment Configuration
│   ├── hyprland/               # Hyprland window manager rules & keybindings
│   ├── ghostty/                # Ghostty terminal styling & font setup
│   ├── tmux/                   # Tmux configuration with AI agent pane split
│   └── rimuru-shell/           # Status bar and desktop widgets
├── scripts/                    # Automation Scripts
│   ├── build-iso.sh            # One-click ISO builder using mkarchiso
│   ├── make-repo.sh            # Local [rimuru] repository generator
│   └── test-qemu.sh            # QEMU / KVM virtual machine tester
├── plan.md                     # Full master specification & roadmap
└── README.md                   # This file
```

---

## Quickstart & CLI Commands

Rimuru OS ships with the central `/usr/bin/rimuru` command center:

```bash
# Submit an autonomous goal to the OS Orchestrator
rimuru run "Scaffold a modern Axum web service and launch in tmux"

# Launch the visual Orchestrator Cockpit
rimuru cockpit --live

# Open the 1-click GUI Software Store with AI descriptors
rimuru store

# Send files to a nearby phone or laptop via Quick Share
rimuru share ./document.pdf

# Manage Btrfs snapshots
rimuru snapshot list
rimuru snapshot create "Manual checkpoint before risky build"
rimuru snapshot rollback <snapshot_id>

# Safely update the operating system with an automated pre-snapshot
rimuru update
```

---

## Building the Live ISO

To build the bootable ISO image:

```bash
# 1. Ensure dependencies are met and generate repository index
./scripts/make-repo.sh

# 2. Build the live ISO
./scripts/build-iso.sh

# 3. Test the built ISO in QEMU
./scripts/test-qemu.sh
```
