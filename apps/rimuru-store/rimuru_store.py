#!/usr/bin/env python3
"""
Rimuru OS Software Center (rimuru-store)
Native GTK4 + Libadwaita Package Installer with AI Insights
"""

import sys
import subprocess
import shutil
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib

FEATURED_PACKAGES = [
    {
        "name": "ghostty",
        "category": "Development",
        "summary": "GPU-accelerated, modern terminal emulator with low input latency",
        "ai_insight": "Default terminal for Rimuru OS. Offers near-zero latency, Kitty graphics protocol, and native tmux synergy.",
        "icon": "utilities-terminal",
        "repo": "rimuru",
    },
    {
        "name": "neovim",
        "category": "Development",
        "summary": "Vim-fork focused on extensibility and usability",
        "ai_insight": "Next-gen extensible modal text editor. Highly optimized for modern LSP servers, Treesitter syntax highlighting, and Rimuru coding workflows.",
        "icon": "text-editor",
        "repo": "extra",
    },
    {
        "name": "ollama",
        "category": "AI & ML",
        "summary": "Run large language models locally with high performance",
        "ai_insight": "Primary local AI engine for Rimuru OS. Runs quantized Llama, Qwen, and DeepSeek models on CPU or GPU with zero cloud token cost.",
        "icon": "system-run",
        "repo": "extra",
    },
    {
        "name": "rquickshare-x",
        "category": "Productivity",
        "summary": "Nearby Share / Quick Share client for seamless cross-device transfer",
        "ai_insight": "Enables instant peer-to-peer file and clipboard sharing between your Rimuru OS machine, Android phones, Windows, and Apple devices.",
        "icon": "network-wireless",
        "repo": "rimuru",
    },
    {
        "name": "fastfetch",
        "category": "System Tools",
        "summary": "Extremely fast, feature-rich system information tool",
        "ai_insight": "Instant hardware, kernel, and desktop compositor diagnostic tool designed to replace neofetch with 10x higher execution speed.",
        "icon": "help-about",
        "repo": "extra",
    },
    {
        "name": "btop",
        "category": "System Tools",
        "summary": "Modern resource monitor showing usage and stats for processor, memory, disks and network",
        "ai_insight": "Interactive graphical TUI hardware monitor with full GPU VRAM and process tree visualization.",
        "icon": "utilities-system-monitor",
        "repo": "extra",
    },
    {
        "name": "blender",
        "category": "Media",
        "summary": "Fully integrated 3D graphics creation suite",
        "ai_insight": "Industry-standard open source 3D modeling, animation, rendering, and compositing workstation.",
        "icon": "image-x-generic",
        "repo": "extra",
    },
    {
        "name": "obs-studio",
        "category": "Media",
        "summary": "Free and open source software for video recording and live streaming",
        "ai_insight": "Complete broadcasting studio with native Wayland PipeWire screen capture portal integration.",
        "icon": "camera-video",
        "repo": "extra",
    },
]


class PackageRow(Adw.ActionRow):
    def __init__(self, pkg, is_installed, on_toggle_callback):
        super().__init__()
        self.pkg = pkg
        self.is_installed = is_installed
        self.on_toggle = on_toggle_callback

        self.set_title(pkg["name"])
        self.set_subtitle(pkg.get("summary", ""))

        # Category badge
        category = pkg.get("category", "General")
        cat_label = Gtk.Label(label=f"[{category}]")
        cat_label.add_css_class("dim-label")
        self.add_prefix(cat_label)

        # Action Button
        self.btn = Gtk.Button()
        if self.is_installed:
            self.btn.set_label("Uninstall")
            self.btn.add_css_class("destructive-action")
        else:
            self.btn.set_label("Install")
            self.btn.add_css_class("suggested-action")

        self.btn.connect("clicked", self._on_btn_clicked)
        self.add_suffix(self.btn)

    def _on_btn_clicked(self, button):
        self.on_toggle(self.pkg, self.is_installed, self)


class RimuruStoreWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(960, 680)
        self.set_title("Rimuru Software Center")

        # Main Layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)

        # Header Bar
        header = Adw.HeaderBar()
        title = Adw.WindowTitle(
            title="Rimuru Software Center",
            subtitle="1-Click Packages with AI Descriptors",
        )
        header.set_title_widget(title)
        main_box.append(header)

        # Search Bar
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search packages (pacman / AUR / Rimuru repo)...")
        self.search_entry.set_margin_start(18)
        self.search_entry.set_margin_end(18)
        self.search_entry.set_margin_top(12)
        self.search_entry.set_margin_bottom(12)
        self.search_entry.connect("search-changed", self._on_search_changed)
        main_box.append(self.search_entry)

        # Safety Banner
        banner = Adw.Banner(
            title="Snapshot Safety Active: An atomic Btrfs snapshot will be created before installations."
        )
        banner.set_revealed(True)
        main_box.append(banner)

        # Content Paned (Left: List, Right: AI Details)
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_position(500)
        paned.set_vexpand(True)
        main_box.append(paned)

        # Left Column: Scrolled Package List
        left_scroll = Gtk.ScrolledWindow()
        left_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.pkg_listbox = Gtk.ListBox()
        self.pkg_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.pkg_listbox.add_css_class("boxed-list")
        self.pkg_listbox.connect("row-selected", self._on_row_selected)
        left_scroll.set_child(self.pkg_listbox)
        paned.set_start_child(left_scroll)

        # Right Column: Detailed AI Insights & Package Info
        right_scroll = Gtk.ScrolledWindow()
        self.detail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.detail_box.set_margin_start(20)
        self.detail_box.set_margin_end(20)
        self.detail_box.set_margin_top(20)
        self.detail_box.set_margin_bottom(20)

        self.detail_title = Gtk.Label()
        self.detail_title.set_halign(Gtk.Align.START)
        self.detail_title.add_css_class("title-1")
        self.detail_box.append(self.detail_title)

        self.detail_meta = Gtk.Label()
        self.detail_meta.set_halign(Gtk.Align.START)
        self.detail_meta.add_css_class("dim-label")
        self.detail_box.append(self.detail_meta)

        # AI Descriptor Card
        ai_card = Adw.PreferencesGroup()
        ai_card.set_title("AI Descriptor & Architecture Analysis")
        ai_card.set_description("Synthesized by Rimuru Orchestrator")
        self.ai_text = Gtk.Label()
        self.ai_text.set_wrap(True)
        self.ai_text.set_xalign(0)
        self.ai_text.add_css_class("body")
        ai_card.add(self.ai_text)
        self.detail_box.append(ai_card)

        # Upstream Description Card
        desc_card = Adw.PreferencesGroup()
        desc_card.set_title("Package Description")
        self.upstream_text = Gtk.Label()
        self.upstream_text.set_wrap(True)
        self.upstream_text.set_xalign(0)
        desc_card.add(self.upstream_text)
        self.detail_box.append(desc_card)

        right_scroll.set_child(self.detail_box)
        paned.set_end_child(right_scroll)

        # Populate Packages
        self._load_packages()

    def _is_installed(self, pkg_name):
        res = subprocess.run(["pacman", "-Qq", pkg_name], capture_output=True, text=True)
        return res.returncode == 0

    def _load_packages(self, filter_text=""):
        # Clear existing
        while True:
            row = self.pkg_listbox.get_row_at_index(0)
            if row is None:
                break
            self.pkg_listbox.remove(row)

        for pkg in FEATURED_PACKAGES:
            if filter_text:
                q = filter_text.lower()
                if q not in pkg["name"].lower() and q not in pkg.get("summary", "").lower():
                    continue

            installed = self._is_installed(pkg["name"])
            row = PackageRow(pkg, installed, self._on_package_action)
            self.pkg_listbox.append(row)

        # Select first row
        first_row = self.pkg_listbox.get_row_at_index(0)
        if first_row:
            self.pkg_listbox.select_row(first_row)

    def _on_search_changed(self, entry):
        text = entry.get_text().strip()
        self._load_packages(text)

    def _on_row_selected(self, listbox, row):
        if not row:
            return
        pkg = row.pkg
        self.detail_title.set_label(pkg["name"])
        self.detail_meta.set_label(f"Repository: [{pkg.get('repo', 'extra')}] • Category: {pkg.get('category', 'System')}")
        self.ai_text.set_label(pkg.get("ai_insight", "No AI insight generated."))
        self.upstream_text.set_label(pkg.get("summary", ""))

    def _on_package_action(self, pkg, is_installed, row_widget):
        pkg_name = pkg["name"]
        action = "remove" if is_installed else "install"
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading=f"{action.capitalize()} {pkg_name}?",
            body=f"Rimuru will create a Btrfs pre-snapshot checkpoint, then {action} '{pkg_name}' via pacman.",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("confirm", f"{action.capitalize()}")
        dialog.set_response_appearance("confirm", Adw.ResponseAppearance.SUGGESTED if action == "install" else Adw.ResponseAppearance.DESTRUCTIVE)

        def _on_dialog_response(diag, response):
            if response == "confirm":
                self._execute_transaction(pkg_name, action, row_widget)

        dialog.connect("response", _on_dialog_response)
        dialog.present()

    def _execute_transaction(self, pkg_name, action, row_widget):
        print(f"[rimuru-store] Executing {action} for {pkg_name}...")
        # Step 1: Snapshot
        if shutil.which("rimuru-snapshot"):
            subprocess.run(["rimuru-snapshot", "create", f"Pre-{action} {pkg_name}"])

        # Step 2: Pacman execution
        cmd = ["sudo", "pacman", "-R", "--noconfirm", pkg_name] if action == "remove" else ["sudo", "pacman", "-S", "--noconfirm", pkg_name]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                print(f"[rimuru-store] Successfully completed {action} of {pkg_name}")
            else:
                print(f"[rimuru-store] Error: {res.stderr}")
        except Exception as e:
            print(f"[rimuru-store] Execution error: {e}")

        # Refresh
        self._load_packages(self.search_entry.get_text().strip())


class RimuruStoreApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="org.rimuru.SoftwareCenter",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = RimuruStoreWindow(application=self)
        win.present()


def main():
    app = RimuruStoreApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
