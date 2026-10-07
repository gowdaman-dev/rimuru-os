# Rimuru OS — Comprehensive Architecture & Development Plan
**The AI-Native, Autonomous Orchestrator Operating System**

---

## 1. Executive Summary & Vision

### 1.1 What is Rimuru OS?
**Rimuru OS** (or simply **Rimuru**) is a next-generation, AI-native, rolling Linux operating system engineered from scratch on top of an Arch Linux foundation. Built as a high-performance alternative and architectural leap beyond distributions like Omarchy, Rimuru transforms the operating system from a passive collection of utilities into an **autonomous system-level orchestrator**.

In traditional computing environments, users install disparate agent frameworks (such as CrewAI, AutoGen, LangGraph, or Arca) that operate with limited system context and brittle terminal integrations. In **Rimuru OS**, the operating system *itself* acts as the orchestrator. It natively understands system state, manages resources, breaks down complex human requests into parallel sub-problems, schedules concurrent agent workers, and executes operations safely within hardware-isolated harnesses—all backed by atomic Btrfs snapshot rollbacks.

### 1.2 Core Pillars
1. **Bleeding-Edge Linux Foundation**: Powered by the modern Linux 7.2.x series kernel with `PREEMPT_DYNAMIC`, Btrfs optimizations, and low-latency Wayland graphics pathways.
2. **Arch Upstream Base**: Utilizes `pacman` and `yay` (AUR) with custom `[rimuru]` curated repositories and a custom declarative system configuration.
3. **Native Desktop Suite**: Features **Hyprland** (dynamic Wayland tiling compositor), **Ghostty** as the default GPU-accelerated terminal, an integrated **tmux** workspace manager, and native **Quick Share** file sharing.
4. **Autonomous OS-Level Orchestrator (`rimuru-orchestratord`)**: A unified, kernel-adjacent agent harness that decomposes tasks, coordinates parallel worker agents, routes between local (Ollama/vLLM) and cloud models (Claude, OpenAI, Gemini), and executes system calls through a secure sandbox.
5. **Bulletproof Snapshot & Self-Healing Engine**: Integrated Btrfs + Snapper architecture with automated pre/post transaction hooks, instant bootloader rollback (Limine/systemd-boot), and AI self-healing when package or configuration faults occur.
6. **Curated Default Applications**: Includes **Rimuru Store** (a modern GUI package installer powered by Rust and `libalpm`), **Rimuru Cockpit** (orchestration monitor), and a seamless **Calamares** live installer.

---

## 2. System Architecture & Foundation

```
+-----------------------------------------------------------------------------------+
|                                  RIMURU USERSPACE                                 |
|  +-----------------------------------------------------------------------------+  |
|  |           Hyprland Wayland Compositor (Aquamarine / Wayland Protocols)       |  |
|  |  +---------------------+  +----------------------+  +--------------------+  |  |
|  |  | Ghostty + Tmux      |  | Rimuru Store (GUI)   |  | Rimuru Cockpit UI  |  |  |
|  |  | Default AI Terminal |  | One-Click Package Ctr|  | Multi-Agent Monitor|  |  |
|  |  +---------------------+  +----------------------+  +--------------------+  |  |
|  |  +---------------------+  +----------------------+  +--------------------+  |  |
|  |  | Quick Share Applet  |  | Rimuru Snapshot GUI  |  | rimuru-shell (Bar) |  |  |
|  |  +---------------------+  +----------------------+  +--------------------+  |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
|                       RIMURU ORCHESTRATION & HARNESS LAYER                        |
|  +-----------------------------------------------------------------------------+  |
|  |  rimuru-orchestratord (Rust Daemon / Unix Socket / D-Bus / gRPC)            |  |
|  |  * Syscall Harness (Shell, Filesystem, Package, Network, Window, Memory)    |  |
|  |  * Task Decomposition Engine (Goal -> DAG of Sub-Problems)                 |  |
|  |  * Parallel State Scheduler (Multi-agent concurrent processing)            |  |
|  |  * Hybrid Model Router (Local: Ollama/vLLM | Cloud: Anthropic/OpenAI/Gemini)|  |
|  |  * Memory Engine (Working KV Cache + Persistent SQLite-vec RAG Memory)     |  |
|  |  * Sandboxed Execution Subsystem (Bubblewrap / cgroups v2 / Landlock)       |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
|                        PACKAGE & SNAPSHOT INFRASTRUCTURE                          |
|  +-------------------------------------+ +-------------------------------------+  |
|  | Pacman + yay + [rimuru] Repo        | | Snapper + Btrfs Subvolume Hierarchy |  |
|  | Libalpm Native Bindings             | | Instant Checkpoints & Auto-Rollback |  |
|  +-------------------------------------+ +-------------------------------------+  |
+-----------------------------------------------------------------------------------+
|                       KERNEL & HARDWARE ABSTRACTION LAYER                         |
|  Linux Kernel 7.2.x (PREEMPT_DYNAMIC, Btrfs ZSTD, Wayland DRM/KMS, KVM/cgroups)  |
+-----------------------------------------------------------------------------------+
```

### 2.1 Kernel Specifications
* **Kernel Series**: Linux 7.2.x (rolling modern tree with PREEMPT_DYNAMIC enabled for sub-millisecond audio/display scheduling and agent responsiveness).
* **Key Kernel Modules & Tuning**:
  * `CONFIG_BTRFS_FS=y` with native ZSTD compression and asynchronous discard (`discard=async`).
  * `CONFIG_USER_NS=y` & `CONFIG_SECURITY_LANDLOCK=y` for zero-overhead agent sandboxing.
  * Direct rendering infrastructure (DRI/DRM) with Wayland Aquamarine backend for Hyprland.
  * BBRv3 TCP congestion control and io_uring support for ultra-low latency agent networking.

### 2.2 Base Distribution & Package Infrastructure
* **Foundation**: Custom Arch Linux spin generated via `archiso`.
* **Repositories**:
  1. `[core]`, `[extra]`, `[multilib]` (Standard upstream Arch Linux mirrors).
  2. `[rimuru]` (Curated Rimuru repository containing `rimuru-orchestratord`, `rimuru-store`, `rimuru-shell`, custom themes, and patched utilities).
  3. **AUR Support**: Pre-configured `yay` AUR helper for seamless access to community packages.
* **Declarative Manifest**:
  * Unified system configuration stored in `/etc/rimuru/rimuru.toml` and user configuration in `~/.config/rimuru/config.toml`.
  * Allows reproducing or snapshotting the entire user environment, installed apps, active agents, and desktop preferences in a single declarative file.

---

## 3. Storage, Snapshot & AI Self-Healing Architecture

Rimuru OS implements an enterprise-grade, immutable-like safety architecture while remaining a 100% customizable, writable Linux installation.

### 3.1 Btrfs Subvolume Hierarchy
During installation (via the Rimuru Calamares installer), the system partitions the NVMe/SSD drive with the following Btrfs layout:

| Subvolume | Mount Point | Compression | Purpose |
| :--- | :--- | :--- | :--- |
| `@` | `/` | `zstd:3` | Root operating system files, packages, libraries |
| `@home` | `/home` | `zstd:3` | User data, agent workspaces, projects |
| `@snapshots` | `/.snapshots` | `zstd:3` | Root snapshot history managed by Snapper |
| `@home-snapshots` | `/home/.snapshots` | `zstd:3` | User file snapshot history |
| `@var_log` | `/var/log` | `zstd:3` | Systemd journal logs (excluded from rollbacks) |
| `@var_cache` | `/var/cache` | None / Default | Pacman package cache & AI model weights |

### 3.2 Automated Checkpoints (Pacman & Agent Hooks)
* **Pre-Transaction Hooks**: Every `pacman` or `yay` operation automatically triggers `/usr/share/libalpm/hooks/00-rimuru-pre-snapshot.hook`, creating a tagged snapshot: `[pacman-pre] Upgrade: <package_names>`.
* **Post-Transaction Hooks**: If an update succeeds, a post-snapshot is generated.
* **Agent Mutation Hooks**: Before `rimuru-orchestratord` performs major filesystem changes, it requests an atomic snapshot via the Snapper D-Bus API: `[agent-pre] Task: <task_id>`.

### 3.3 Bootloader & AI Self-Healing Rollback
* **Bootloader Integration**: Compatible with **Limine** and **systemd-boot** (via `snap-pac` and `grub-btrfs`/`limine-snapper-sync`). If a bad kernel, driver, or system library prevents the OS from booting, users can select any past snapshot directly from the UEFI boot screen.
* **AI Self-Healing Daemon**:
  * If the system detects repeated `systemd` unit failures, display crashes, or broken shared libraries, the Rimuru recovery daemon notifies the user via desktop OSD or boots into a safe read-only snapshot.
  * The user or autonomous harness can run `rimuru snapshot rollback --latest-good` to restore the system in under 2 seconds without data loss in `/home`.

---

## 4. Desktop Environment & User Experience

```
+------------------------------------------------------------------------------------+
|  [Rimuru Bar: Workspaces 1..10 | CPU 12% | RAM 4.2GB | Agent: 3 Tasks | QuickShare | 12:45] |
|------------------------------------------------------------------------------------|
|  +----------------------------------+  +-----------------------------------------+ |
|  | GHOSTTY (Default Terminal)       |  | RIMURU ORCHESTRATOR COCKPIT             | |
|  | +------------------------------+ |  |                                         | |
|  | | TMUX Session: [rimuru-main]  | |  | [Goal] Build full-stack Axum API webapp | |
|  | | Pane 1: nvim src/main.rs     | |  |                                         | |
|  | | ---------------------------- | |  | +-[Worker 1] Scaffold database schema   | |
|  | | Pane 2: cargo watch -x run   | |  | +-[Worker 2] Generate frontend Slint UI | |
|  | | ---------------------------- | |  | +-[Worker 3] Run automated test suite   | |
|  | | Pane 3: rimuru agent live-log| |  |                                         | |
|  | +------------------------------+ |  | Status: [RUNNING] | Models: Claude + 8B | |
|  +----------------------------------+  +-----------------------------------------+ |
|                                                                                    |
|  +----------------------------------+  +-----------------------------------------+ |
|  | RIMURU STORE (GUI Package App)   |  | QUICK SHARE TRAY & PREVIEW PICKER       | |
|  | [Search Packages: "neovim"]     |  | "Galaxy S24 Ultra" connected            | |
|  | -> One-Click Install             |  | Drop files to transfer via NearShare    | |
|  | -> AI Security & Feature Summary |  |                                         | |
|  +----------------------------------+  +-----------------------------------------+ |
+------------------------------------------------------------------------------------+
```

### 4.1 Hyprland Wayland Compositor
* **Version**: Bleeding-edge Hyprland built on the `Aquamarine` rendering backend.
* **Window Management**: Dynamic dwindle and master tiling layouts with smooth cubic-bezier animations, rounded borders, active glowing borders indicating running agent operations, and multi-monitor fractional scaling.
* **Desktop Shell (`rimuru-shell`)**:
  * Fast, lightweight Wayland bar (built with QuickShell / AGS / Waybar).
  * Built-in modules: Workspace indicator, system load, network/Bluetooth, Quick Share status applet, snapshot manager status, and the **AI Orchestrator Task Indicator** (displaying active sub-agents and token throughput).
* **Preview Share Picker**: Integrated `hyprland-preview-share-picker` providing Wayland desktop portal screen sharing and camera capture with live window previews.

### 4.2 Ghostty Terminal & Tmux Workflow
* **Default Terminal**: **Ghostty**, the GPU-accelerated terminal emulator known for near-zero input latency, true color fidelity, Kitty graphics protocol support, and shader-driven visual polish.
* **Native Tmux Synergy**:
  * Rimuru ships with an out-of-the-box, fine-tuned `tmux` configuration (`~/.config/tmux/tmux.conf`).
  * Features custom status bar styling matching Rimuru OS colors, automated session persistence (`tmux-resurrect` + custom snapshot save), and hotkeys to split panes dynamically for agent observation (`Super + Enter` opens Ghostty attached to the default Rimuru tmux session).
  * AI-Assisted Pane Integration: The orchestrator can spawn a dedicated tmux pane (`rimuru-agent-worker`) where users can watch the AI compile code or execute sandboxed commands in real time.

### 4.3 Native Quick Share (Nearby Share) Integration
* **Protocol Support**: Native Linux implementation of Google Nearby Share / Quick Share (powered by `rquickshare-x` daemon).
* **Features**:
  * Zero-configuration peer discovery over Bluetooth Low Energy (BLE) and high-speed Wi-Fi Direct / Local Wi-Fi transfer.
  * Interoperable with Android devices, Windows PCs, and macOS (via NearDrop/LocalSend).
  * Desktop Integration: Hyprland drag-and-drop target, right-click file manager action ("Send via Quick Share"), and toast notifications upon receiving incoming transfers.

---

## 5. The Operating System as an Orchestrator (`rimuru-orchestratord`)

Instead of requiring users to install third-party multi-agent frameworks that run in isolation without system context, **Rimuru OS natively embeds the orchestration harness into the operating system architecture**.

```
+----------------------------------------------------------------------------------+
|                           RIMURU ORCHESTRATOR ARCHITECTURE                       |
+----------------------------------------------------------------------------------+
|                               USER & AGENT INTENT                                |
|  CLI (`rimuru run ...`) | GUI Cockpit | Voice/Voxtype | Keybind `Super + Space`   |
+----------------------------------------------------------------------------------+
                                        │
                                        ▼
+----------------------------------------------------------------------------------+
|                       TASK DECOMPOSITION & DAG SCHEDULER                         |
|  * Analyzes complex user goal                                                    |
|  * Deconstructs into Directed Acyclic Graph (DAG) of parallel sub-tasks          |
|  * Defines dependencies, I/O schemas, and rollback checkpoints                   |
+----------------------------------------------------------------------------------+
                                        │
               ┌────────────────────────┼────────────────────────┐
               ▼                        ▼                        ▼
      [Sub-Problem 1]          [Sub-Problem 2]          [Sub-Problem 3]
       Worker: CodeGen          Worker: Research         Worker: Compiling
        (Cloud Model)            (Web Search)             (Local Model)
               │                        │                        │
               └────────────────────────┼────────────────────────┘
                                        │
                                        ▼
+----------------------------------------------------------------------------------+
|                           PARALLEL STATE ENGINE                                  |
|  * Actor-based concurrent execution queue (Tokio / Async Rust)                   |
|  * Centralized Event Bus & State Transition Tracker                              |
|  * Shared Context & Memory (SQLite-vec Vector DB + In-Memory KV Cache)           |
+----------------------------------------------------------------------------------+
                                        │
                                        ▼
+----------------------------------------------------------------------------------+
|                         OS SYSCALL HARNESS (SAFE EXECUTION)                      |
|  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────────┐   |
|  | Syscall::Shell      |  | Syscall::FileSystem |  | Syscall::Package        |   |
|  | Sandboxed bash exec |  | Read/write/diff     |  | Pacman / yay / Flatpak  |   |
|  | (bwrap / cgroups)   |  | with atomic rollback|  | with auto Btrfs snapshot|   |
|  └─────────────────────┘  └─────────────────────┘  └─────────────────────────┘   |
|  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────────┐   |
|  | Syscall::Window     |  | Syscall::Network    |  | Syscall::Share          |   |
|  | Hyprland IPC control|  | HTTP / Scrape / RAG |  | Quick Share dispatch    |   |
|  └─────────────────────┘  └─────────────────────┘  └─────────────────────────┘   |
+----------------------------------------------------------------------------------+
                                        │
                                        ▼
+----------------------------------------------------------------------------------+
|                           HYBRID MODEL INGRESS LAYER                             |
|  ┌──────────────────────────────────────┐ ┌────────────────────────────────────┐ |
|  | LOCAL INFERENCE ENGINE               | | CLOUD FRONTIER MULTIPLEXER         | |
|  | Ollama / vLLM / llama.cpp (Offline,  | | Anthropic Claude 3.7/3.5, OpenAI,  | |
|  | zero token cost, private sub-tasks)  | | Google Gemini 2.5/3, DeepSeek API  | |
|  └──────────────────────────────────────┘ └────────────────────────────────────┘ |
+----------------------------------------------------------------------------------+
```

### 5.1 The OS Syscall Harness
In Rimuru, AI agents do not run arbitrary unconstrained commands directly against the root filesystem. Instead, they interact with the **Rimuru Syscall Interface**:

1. `Syscall::Shell(command, env, timeout)`:
   * Executes inside an ephemeral **Bubblewrap (`bwrap`) container** with private mount namespaces and cgroups v2 resource caps (CPU, memory, disk I/O limits).
   * Sensitive directories (`/etc/shadow`, `/root`, private keys) are blacklisted or mounted read-only unless explicit privilege escalation is authorized by the user.
2. `Syscall::FileSystem(op, path, content)`:
   * Provides atomic file write, read, search, and semantic AST code editing.
   * If an edit introduces syntax breakages or regressions, the transaction is rejected or rolled back.
3. `Syscall::Package(action, pkg_name)`:
   * Coordinates package installation or upgrades via `libalpm` / `pacman` / `yay`.
   * Automatically invokes the Snapper engine to create a snapshot prior to the operation.
4. `Syscall::Window(action, args)`:
   * Communicates with Hyprland via `/tmp/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock`.
   * Allows the orchestrator to open Ghostty windows, arrange split layouts, launch apps, or capture screens for visual inspection.
5. `Syscall::Share(device_id, payload)`:
   * Triggers Quick Share to send generated documents or images to the user's phone or desktop peers.

### 5.2 Task Decomposition & Parallel State Processing
* **Goal Parsing**: When a user gives a high-level goal (e.g., *"Set up a Rust Axum microservice with PostgreSQL, configure Docker, write integration tests, and test live in tmux"*), the Orchestrator generates a **DAG of Sub-Problems**.
* **Parallel Worker Threads**:
  * Independent sub-problems execute in parallel threads/workers.
  * Worker 1 scaffolds the Rust project; Worker 2 pulls and configures the PostgreSQL container; Worker 3 searches the web for modern dependency versions.
* **Dynamic Model Routing**:
  * Routine tasks (formatting code, running tests, checking syntax, scanning files) route to fast, zero-cost **local models** (e.g., Llama 3.3 8B, Qwen 2.5 Coder, DeepSeek R1 local quant via Ollama/vLLM).
  * High-complexity architecture, refactoring, and logical synthesis tasks route to **cloud models** (Claude 3.7 Sonnet, GPT-4o, Gemini 2.5 Pro).
* **State Machine & Failure Recovery**:
  * If a worker encounters an error (e.g., compile error), the orchestrator triggers an automatic self-correction loop or consults the user via a native desktop notification or interactive tmux prompt.

### 5.3 Unified Memory & Context System
* **Working Memory**: In-memory Redis/SQLite state tracking active sub-tasks, process IDs, and temporary variables.
* **Persistent Semantic Memory**: Built-in vector database (`sqlite-vec` / `LanceDB`) that indexes system documentation, man pages, user dotfiles, recent terminal commands, and project codebases for real-time RAG context retrieval.

---

## 6. Curated Default Applications Suite

Rimuru OS ships with a lean, curated set of purpose-built native applications designed to deliver a cohesive experience out of the box.

### 6.1 Rimuru Store (`rimuru-store`) — Modern GUI Software Installer
* **Technology**: Written in **Rust** using **GTK4 + Libadwaita** (or **Slint**) for instant startup and native Wayland performance.
* **Core Functionality**:
  * **Unified Package Search**: Queries local Pacman databases, official Arch repositories, AUR (`yay`), and Flatpak simultaneously.
  * **Click-and-Install Simplicity**: One-click install, remove, and upgrade with clear dependency resolution.
  * **Rich Package Descriptors & AI Metadata**:
    * Clean category browsing (Development, Multimedia, AI/ML, System, Gaming, Productivity).
    * AI-powered package explanations: Translates technical Arch package descriptions into human-readable summaries highlighting key features, caveats, and recommended companion tools.
    * Security & Health Badges: Displays AUR voting scores, package maintainer status, and build health.
  * **Integrated Snapshot Safety**: Automatically invokes `rimuru snapshot create` before executing package installations, ensuring any failed installation can be reverted in one click.
  * **Privilege Separation**: Low-privilege UI communicating with a Polkit-authenticated system daemon over D-Bus.

```
+-----------------------------------------------------------------------------------+
|  Rimuru Software Center                                                [-] [口] [X] |
+-----------------------------------------------------------------------------------+
|  [🔍 Search packages, e.g. "blender", "docker", "neovim"...                      ] |
|-----------------------------------------------------------------------------------|
|  CATEGORIES: [All] [Development] [AI & Data] [Productivity] [Media] [System Tools]|
|-----------------------------------------------------------------------------------|
|  +-----------------------------------------------------------------------------+  |
|  |  📦 Ghostty (Terminal)                                     [ Installed  v ] |  |
|  |  GPU-accelerated, modern terminal emulator with low input latency           |  |
|  |  AI Insight: Optimal terminal for Rimuru. Pre-configured for tmux workflow. |  |
|  |  Source: [rimuru] Repo | Size: 42 MB | Dependencies: All met                |  |
|  +-----------------------------------------------------------------------------+  |
|  |  📦 Neovim (Editor)                                        [   Install    ] |  |
|  |  Vim-fork focused on extensibility and usability                           |  |
|  |  AI Insight: Modern modal editor. Includes pre-configured Rimuru LSP plugins.|  |
|  |  Source: [extra] Arch | Size: 28 MB | License: Apache 2.0                   |  |
|  +-----------------------------------------------------------------------------+  |
|  |  🛡️ Snapshot Check: "A snapshot [pre-install-neovim] will be created auto"    |  |
+-----------------------------------------------------------------------------------+
```

### 6.2 Rimuru Cockpit (`rimuru-cockpit`) — Orchestrator Control Plane
* Available as both a **GUI app** and a **TUI command** (`rimuru cockpit` / `rimuru top`).
* Displays:
  * Active orchestrator task graph (visual DAG nodes and sub-tasks).
  * Real-time worker logs and status (Running, Pending, Succeeded, Failed).
  * Local model VRAM/RAM utilization (Ollama/vLLM) and cloud API token expenditure.
  * Interactive action buttons: Pause task, rollback sub-problem, inspect sandboxed output, attach tmux pane.

### 6.3 Rimuru Share (`rimuru-share`) — Quick Share Center
* Desktop GUI and Hyprland status bar tray icon for Google Quick Share / Nearby Share.
* Features:
  * Visibility toggle: "Everyone", "Contacts Only", or "Hidden".
  * Receive tray: Pop-up prompt with sender name, file preview, accept/decline buttons, and automatic save to `~/Downloads`.
  * Send drawer: Drag any file or folder to the drop target to broadcast to nearby Android, Windows, or Mac devices.

### 6.4 Rimuru Snapshot Manager (`rimuru-snapshot-gui`)
* Visual timeline of all system and user snapshots.
* Inspect file-by-file differentials between snapshots.
* One-click rollback button with automatic reboot/restore orchestration.

### 6.5 Rimuru Control Center & Welcome Setup
* First-boot onboarding wizard:
  * Select default local AI model (Download Ollama + Llama 3 / Qwen model with single click).
  * Configure Cloud API keys (Anthropic, OpenAI, Google Gemini) stored in the secure system keyring (`libsecret`).
  * Customize Hyprland themes, monitor refresh rates, and Ghostty terminal fonts.

### 6.6 Rimuru Calamares Live Installer
* Branded Calamares installer packaged in the Live ISO.
* Automated partitioning module:
  * Detects NVMe/SSD, creates EFI partition (`/boot/efi`) and Btrfs root with the standard Rimuru subvolume scheme (`@`, `@home`, `@snapshots`).
  * Automatic GPU hardware detection and driver configuration (NVIDIA proprietary with Wayland patches, AMD Mesa, or Intel Xe).

---

## 7. Project Monorepo Structure

The Rimuru OS development repository will be organized as follows:

```
rimuru-os/
├── .github/
│   └── workflows/              # CI/CD: ISO build pipeline, package building, linting
├── archiso/                    # Archiso Profile for Rimuru Live ISO
│   ├── airootfs/               # Root filesystem overlay
│   │   ├── etc/
│   │   │   ├── pacman.conf     # Pacman configuration inside ISO
│   │   │   ├── rimuru/         # Default Rimuru system configuration
│   │   │   └── skel/           # Default user skel (.config/hypr, ghostty, tmux)
│   │   └── usr/share/
│   ├── efiboot/                # UEFI bootloader configuration
│   ├── syslinux/               # BIOS fallback bootloader
│   ├── packages.x86_64         # Master package manifest for Rimuru ISO
│   └── profiledef.sh           # Archiso profile definitions
├── apps/                       # Native Rimuru Applications
│   ├── rimuru-store/           # GUI Package Installer (Rust + GTK4/Libadwaita)
│   │   ├── Cargo.toml
│   │   └── src/                # libalpm integration, package search, UI
│   ├── rimuru-cockpit/         # Orchestrator GUI/TUI Dashboard
│   ├── rimuru-share/           # Quick Share Wayland frontend & tray
│   └── rimuru-snapshot-gui/    # Visual Btrfs Snapshot Manager
├── orchestrator/               # rimuru-orchestratord (The OS Orchestration Engine)
│   ├── Cargo.toml
│   ├── src/
│   │   ├── main.rs             # Daemon entrypoint & D-Bus / socket server
│   │   ├── scheduler/          # Task decomposition & parallel DAG scheduler
│   │   ├── harness/            # Syscall execution (bwrap sandbox, fs, hyprland)
│   │   ├── models/             # Local (Ollama/vLLM) & Cloud (Claude/OpenAI/Gemini)
│   │   ├── memory/             # Vector memory (sqlite-vec) & KV session store
│   │   └── safety/             # Snapshot rollback triggers & policy engine
├── shell/                      # Desktop Environment Configurations
│   ├── hyprland/               # hyprland.conf, hypridle, hyprlock
│   ├── ghostty/                # config, keybindings, custom shaders
│   ├── tmux/                   # tmux.conf, plugins, session-resurrect scripts
│   └── rimuru-shell/           # Bar, widget modules, OSD, notification center
├── installer/                  # Calamares installer configuration & branding
│   ├── branding/rimuru/
│   └── modules/                # Custom btrfs-subvolume & AI-setup modules
├── repo/                       # PKGBUILD recipes for [rimuru] repository
│   ├── rimuru-base/
│   ├── rimuru-orchestratord/
│   ├── rimuru-store/
│   └── rquickshare-x/
├── scripts/                    # Development & Build Automation
│   ├── build-iso.sh            # One-command ISO build script
│   ├── setup-dev-chroot.sh     # Set up clean build environment
│   └── test-qemu.sh            # Run generated ISO in QEMU with GPU passthrough
├── plan.md                     # Master architecture & project plan (this document)
└── README.md                   # Project overview & quickstart
```

---

## 8. Detailed Implementation Roadmap

### Phase 1: Base System, Kernel & Package Infrastructure
* **Goal**: Establish the automated Archiso build system, Linux 7.2.x kernel profile, and repository foundation.
* **Deliverables**:
  1. Initialize `archiso/` profile with custom `packages.x86_64` (base, kernel, firmware, btrfs-progs, snapper, networkmanager).
  2. Configure local package repository `[rimuru]` with automated `repo-add` build scripts.
  3. Validate standard Btrfs subvolume layout (`@`, `@home`, `@snapshots`) and automated Snapper hooks (`snap-pac`).
  4. Build prototype ISO and test boot in QEMU virtual machine.

### Phase 2: Desktop Environment, Terminal & Sharing Suite
* **Goal**: Assemble the modern Hyprland desktop environment, Ghostty terminal, tmux integration, and Quick Share.
* **Deliverables**:
  1. Configure **Hyprland** with fluid animations, dynamic tiling, and Aquamarine Wayland backends.
  2. Implement **Ghostty** as the default terminal with custom color schemes and low-latency font rendering.
  3. Pre-configure **tmux** with custom status line, agent monitoring hooks, and hotkey mappings.
  4. Package and configure **Quick Share** (`rquickshare-x`) daemon with autostart, system tray indicator, and Hyprland share-picker integration.
  5. Assemble `rimuru-shell` (Wayland top bar, notifications, and AI status widget).

### Phase 3: Rimuru Store (`rimuru-store`) Development
* **Goal**: Build the native GUI package installer for click-and-install software management.
* **Deliverables**:
  1. Develop Rust GUI application using GTK4 / Libadwaita with responsive, asynchronous architecture.
  2. Bind to `libalpm` for reading local databases, search, and package metadata.
  3. Integrate Polkit authentication helper daemon for safe root operations without running GUI as root.
  4. Integrate `yay` (AUR) and Flatpak querying capabilities.
  5. Add AI package descriptors (curated summaries, security ratings, and usage recommendations).
  6. Connect to Snapper: trigger automated snapshot before installing/removing packages.

### Phase 4: OS Orchestrator Engine (`rimuru-orchestratord`)
* **Goal**: Implement the core autonomous operating system orchestrator and execution harness.
* **Deliverables**:
  1. Develop `rimuru-orchestratord` in Rust with an asynchronous Tokio runtime and Unix Domain Socket / D-Bus API.
  2. Build the **OS Syscall Harness**:
     * `Syscall::Shell`: Sandboxed execution using Bubblewrap (`bwrap`) with cgroups resource limiting.
     * `Syscall::FileSystem`: AST-aware file operations with automatic diff tracking.
     * `Syscall::Package`: Programmatic package queries and installations.
     * `Syscall::Window`: Hyprland socket integration for window management and screen capture.
  3. Build the **Task Decomposition & DAG Scheduler**:
     * Splits user goals into sub-tasks with dependency graphs.
     * Actor-based parallel processing pipeline for concurrent agent execution.
  4. Build the **Hybrid Model Ingress**:
     * Local model integration (Ollama / vLLM / llama.cpp).
     * Cloud model adapters (Anthropic Claude, OpenAI, Gemini, DeepSeek).
     * Rule-based and cost-effective routing between local and cloud models.
  5. Build the **Memory Subsystem**:
     * Working memory cache + persistent SQLite-vec database for OS-level RAG.

### Phase 5: Rimuru Cockpit & Default Application Suite
* **Goal**: Build the user-facing interfaces to interact with and control the orchestrator.
* **Deliverables**:
  1. Develop **Rimuru Cockpit** (GUI & TUI versions) showing live task graphs, sub-worker progress, and token metrics.
  2. Develop **Rimuru Snapshot Manager GUI** for visual timeline rollbacks.
  3. Create Rimuru Welcome & Settings app for API key configuration and hardware tweaks.
  4. Package all components into `.pkg.tar.zst` packages in the `[rimuru]` repository.

### Phase 6: Live Installer, ISO Mastering & Public Release
* **Goal**: Finalize the complete standalone operating system ISO.
* **Deliverables**:
  1. Customize **Calamares** with Rimuru branding, automatic Btrfs partitioning, and driver setup.
  2. Run end-to-end ISO builds via `mkarchiso`.
  3. Perform bare-metal and VM tests:
     * UEFI boot & installation.
     * NVIDIA, AMD, and Intel GPU driver switching.
     * Snapper snapshot creation and bootloader rollback.
     * Quick Share transfers to/from Android and Windows.
     * Orchestrator parallel task stress tests.
  4. Release Rimuru OS ISO v1.0.0.

---

## 9. Testing, Safety & Verification Matrix

| Subsystem | Test Objective | Verification Criteria |
| :--- | :--- | :--- |
| **Boot & Installer** | Bare-metal & VM ISO installation | Successful boot, automatic Btrfs layout creation, subvolumes correctly mounted |
| **Btrfs Snapshots** | Automated rollback on failure | Snapper pre-hook executes prior to `pacman -S`, instant rollback boots cleanly |
| **Ghostty & Tmux** | Terminal responsiveness & multiplexing | Zero font artifacts, sub-5ms latency, tmux sessions persist across reboots |
| **Quick Share** | Android / Windows / Linux discovery | Device discovered within 3 seconds, bi-directional file transfer completes |
| **Rimuru Store** | 1-Click package installation | Libalpm transaction completes, UI remains fluid, pre-install snapshot generated |
| **Orchestrator Sandbox** | Containment of malicious or broken code | Bubblewrap blocks access to unauthorized paths, cgroups caps CPU/RAM usage |
| **Parallel Scheduling** | Multi-agent DAG execution | 3+ concurrent sub-tasks run simultaneously without deadlock; state correctly synced |
| **Model Routing** | Local & Cloud dispatch | Fast tasks route to local Ollama; complex architecture tasks route to Claude/OpenAI |

---

## 10. Conclusion & Next Steps

Rimuru OS is uniquely positioned to bridge the gap between traditional developer Linux distributions and the rapidly emerging era of autonomous AI computing. By baking multi-agent orchestration, sandboxed execution, and atomic snapshots directly into the operating system fabric, Rimuru empowers users to work alongside an intelligent, self-healing system partner.

To begin building Rimuru OS, proceed with the implementation steps outlined in **Phase 1: Base System, Kernel & Package Infrastructure**.
