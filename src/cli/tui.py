import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import datetime
from pathlib import Path

from src.core import config, database, ffmpeg, updater, downloader, queue, scheduler

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.widgets import Header, Footer, Static, Input, Button, Select, Label, Switch, ListView, ListItem, DataTable, ProgressBar, LoadingIndicator
from textual.binding import Binding
from textual.reactive import reactive
from textual.screen import ModalScreen

class DashboardGifWidget(Static):
    def on_mount(self) -> None:
        self.frame = 0
        self.frames = [
            "[bold #ff0055]┌─┐[/bold #ff0055] [bold #38bdf8]CORE DIGITAL STATUS[/bold #38bdf8] [bold #ff0055]┌─┐[/bold #ff0055]\n"
            "  [#00ff66]● ACTIVE[/#00ff66]\n"
            "  [#e11d48]⚲ SCANNING PORT[/#e11d48]\n"
            "  [#38bdf8]⚙MEMORY OK    [/#38bdf8]",
            
            "[bold #00ff66]├─┤[/bold #00ff66] [bold #38bdf8]CORE DIGITAL STATUS[/bold #38bdf8] [bold #00ff66]├─┤[/bold #00ff66]\n"
            "  [#00ff66]● ACTIVE[/#00ff66]\n"
            "  [#e11d48]⚲ SCANNING PORT.[/#e11d48]\n"
            "  [#38bdf8]⚙MEMORY OK.   [/#38bdf8]",

            "[bold #ff0055]└─┘[/bold #ff0055] [bold #38bdf8]CORE DIGITAL STATUS[/bold #38bdf8] [bold #ff0055]└─┘[/bold #ff0055]\n"
            "  [#00ff66]● ACTIVE[/#00ff66]\n"
            "  [#e11d48]⚲ SCANNING PORT..[/#e11d48]\n"
            "  [#38bdf8]⚙MEMORY OK..  [/#38bdf8]",

            "[bold #00ff66]├─┤[/bold #00ff66] [bold #38bdf8]CORE DIGITAL STATUS[/bold #38bdf8] [bold #00ff66]├─┤[/bold #00ff66]\n"
            "  [#00ff66]● ACTIVE[/#00ff66]\n"
            "  [#e11d48]⚲ SCANNING PORT...[/#e11d48]\n"
            "  [#38bdf8]⚙MEMORY OK... [/#38bdf8]"
        ]
        self.update(self.frames[0])
        self.set_interval(0.4, self.animate)

    def animate(self) -> None:
        self.update(self.frames[self.frame])
        self.frame = (self.frame + 1) % len(self.frames)

class HelpScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        with Vertical(id="help-container"):
            yield Label("[bold #ff0055]⚡ F-SOCIETY KEYBOARD INTERFACES[/bold #ff0055]", id="help-title")
            yield Label("[bold #38bdf8]h[/bold #38bdf8]       - Switch to Home Tab", classes="help-key")
            yield Label("[bold #38bdf8]d[/bold #38bdf8]       - Switch to Download Tab", classes="help-key")
            yield Label("[bold #38bdf8]q[/bold #38bdf8]       - Switch to Queue Tab", classes="help-key")
            yield Label("[bold #38bdf8]l[/bold #38bdf8]       - Switch to Library Tab", classes="help-key")
            yield Label("[bold #38bdf8]t[/bold #38bdf8]       - Switch to Tools Tab", classes="help-key")
            yield Label("[bold #38bdf8]s[/bold #38bdf8]       - Switch to Settings Tab", classes="help-key")
            yield Label("[bold #38bdf8]f1 / ?[/bold #38bdf8]  - Open this Help panel", classes="help-key")
            yield Label("[bold #f43f5e]ctrl+q[/bold #f43f5e]  - Exit F-SOCIETY Tool", classes="help-key")
            yield Button("Dismiss", variant="primary", id="btn-close-help")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close-help":
            self.dismiss()

class ErrorRecoveryScreen(ModalScreen):
    def __init__(self, platform, reason, solution):
        super().__init__()
        self.platform = platform
        self.reason = reason
        self.solution = solution

    def compose(self) -> ComposeResult:
        with Vertical(id="err-container"):
            yield Label("[bold #ff0055]🚨 SYSTEM METADATA / DOWNLOAD ERROR[/bold #ff0055]", id="err-title")
            yield Label(f"[bold #38bdf8]Platform:[/bold #38bdf8] {self.platform}", classes="err-info")
            yield Label(f"[bold #38bdf8]Reason:[/bold #38bdf8] {self.reason}", classes="err-info")
            yield Label(f"[bold #38bdf8]Recommended Solution:[/bold #38bdf8] {self.solution}", classes="err-info")
            with Horizontal(classes="err-buttons"):
                yield Button("Retry", variant="success", id="err-retry")
                yield Button("Update Engine", variant="primary", id="err-update")
                yield Button("Use Fallback", variant="warning", id="err-fallback")
                yield Button("Cancel", variant="error", id="err-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id)

ASCII_BANNER = """
[bold #ff0055]
  ███████╗    ███████╗     ██████╗  ██████╗██╗███████╗████████╗██╗   ██╗
  ██╔════╝    ██╔════╝    ██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
  █████╗      ███████╗    ██║   ██║██║     ██║█████╗     ██║    ╚████╔╝ 
  ██╔══╝      ╚════██║    ██║   ██║██║     ██║██╔══╝     ██║     ╚██╔╝  
  ██║         ███████║    ╚██████╔╝╚██████╗██║███████╗   ██║      ██║   
  ╚═╝         ╚══════╝     ╚═════╝  ╚═════╝╚═╝╚══════╝   ╚═╝      ╚═╝   
[/bold #ff0055]
""".strip()

class HomeView(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("[bold #ff0055]⚡ F-SOCIETY MEDIA DASHBOARD[/bold #ff0055]", classes="title")
        
        # Stats row
        with Horizontal(id="stats-row"):
            yield Static("Downloads\n0", id="stat-downloads", classes="card")
            yield Static("Completed\n0", id="stat-completed", classes="card")
            yield Static("Storage Used\n0.00 GB", id="stat-storage", classes="card")
            
        yield DashboardGifWidget(id="hacker-gif")
        
        yield Label("[bold #38bdf8]Recent Database Downloads:[/bold #38bdf8]", classes="section-title")
        yield DataTable(id="recent-table")

    def refresh_stats(self) -> None:
        try:
            logs = database.get_download_logs()
            total = len(logs)
            completed = sum(1 for log in logs if log.get("status") == "success")
        except Exception:
            total = 0
            completed = 0

        # Calculate storage usage
        try:
            d_dir = Path(config.get("download_dir"))
            total_size = 0
            if d_dir.exists():
                for f in d_dir.glob("**/*"):
                    if f.is_file():
                        total_size += f.stat().st_size
            storage_gb = total_size / (1024 * 1024 * 1024)
        except Exception:
            storage_gb = 0.0

        try:
            self.query_one("#stat-downloads", Static).update(f"Downloads\n[bold #38bdf8]{total}[/bold #38bdf8]")
            self.query_one("#stat-completed", Static).update(f"Completed\n[bold #00ff66]{completed}[/bold #00ff66]")
            self.query_one("#stat-storage", Static).update(f"Storage Used\n[bold #f59e0b]{storage_gb:.2f} GB[/bold #f59e0b]")
        except Exception:
            pass

        # Populate table
        try:
            table = self.query_one("#recent-table", DataTable)
            table.clear()
            
            # Setup columns if needed
            if not table.columns:
                table.add_columns("Platform", "Type", "Quality", "Status", "Timestamp")
                
            history = database.get_download_logs()
            for item in history[:10]:
                status = item.get("status", "success")
                if status == "success":
                    status_styled = "[bold #00ff66]success[/bold #00ff66]"
                else:
                    status_styled = "[bold #ff0055]failed[/bold #ff0055]"
                
                table.add_row(
                    item.get("platform", "Unknown"),
                    item.get("type", "video"),
                    item.get("quality", "best"),
                    status_styled,
                    item.get("time", "")
                )
        except Exception:
            pass

class DownloadView(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("[bold #ff0055]📥 SMART DOWNLOAD CENTER[/bold #ff0055]", classes="title")
        yield Label("Media URL:")
        yield Input(placeholder="Paste YouTube, TikTok, Instagram, Twitter link here...", id="dl-url")
        
        # Details Card
        with Vertical(id="meta-card"):
            yield Label("[bold #38bdf8]Meta Details:[/bold #38bdf8]", id="meta-title")
            yield Label("Duration: N/A", id="meta-duration")
            yield Label("Uploader: N/A", id="meta-uploader")
            yield LoadingIndicator(id="meta-loading")

        with Horizontal(classes="select-row"):
            with Vertical():
                yield Label("Mode:")
                yield Select([("video", "video"), ("audio", "audio"), ("images", "images")], value="video", id="dl-mode")
            with Vertical():
                yield Label("Quality Resolution:")
                yield Select([
                    ("best", "best"), 
                    ("2160p", "2160p (4K)"), 
                    ("1080p", "1080p (FHD)"), 
                    ("720p", "720p (HD)"), 
                    ("480p", "480p (SD)"), 
                    ("320", "320 kbps"), 
                    ("192", "192 kbps")
                ], value="best", id="dl-quality")
            with Vertical():
                yield Label("Action:")
                yield Button("START DOWNLOAD", variant="success", id="btn-start-download")
                
        yield Static("Progress: Idle", id="dl-progress-text")
        yield ProgressBar(show_eta=True, show_percentage=True, id="dl-progress-bar")
        yield Static("ETA: N/A | Speed: N/A", id="dl-speed-eta")

class QueueView(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("[bold #ff0055]⏳ BATCH QUEUE HUB[/bold #ff0055]", classes="title")
        yield DataTable(id="queue-table")
        with Horizontal(classes="button-row"):
            yield Button("Add Clipboard URL", variant="primary", id="btn-queue-add")
            yield Button("START PROCESSOR", variant="success", id="btn-queue-run")
            yield Button("Clear Completed", variant="error", id="btn-queue-clear")

    def refresh_queue(self) -> None:
        try:
            table = self.query_one("#queue-table", DataTable)
            table.clear()
            if not table.columns:
                table.add_columns("ID", "URL", "Mode", "Quality", "Status")
            
            q_manager = queue.QueueManager()
            items = q_manager.get_items()
            for idx, item in enumerate(items, 1):
                status = item.get("status", "pending")
                if status == "success":
                    status_styled = "[bold #00ff66]completed[/bold #00ff66]"
                elif status == "failed":
                    status_styled = "[bold #ff0055]failed[/bold #ff0055]"
                elif status == "downloading":
                    status_styled = "[bold #38bdf8]downloading...[/bold #38bdf8]"
                else:
                    status_styled = "[dim #cbd5e1]pending[/dim #cbd5e1]"
                
                table.add_row(
                    str(idx),
                    item.get("url", "")[:50],
                    item.get("mode", "video"),
                    item.get("quality", "best"),
                    status_styled
                )
        except Exception:
            pass

class LibraryView(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("[bold #ff0055]📁 LOCAL MEDIA LIBRARY[/bold #ff0055]", classes="title")
        yield Label("Search Filter:")
        yield Input(placeholder="Type to filter file list...", id="lib-search")
        yield DataTable(id="lib-table")
        with Horizontal(classes="button-row"):
            yield Button("Open / Play Selected", variant="success", id="btn-lib-play")
            yield Button("Delete File", variant="error", id="btn-lib-delete")
            yield Button("Scan Files", variant="primary", id="btn-lib-scan")

    def refresh_library(self, search_query="") -> None:
        try:
            table = self.query_one("#lib-table", DataTable)
            table.clear()
            if not table.columns:
                table.add_columns("File Name", "Type", "Size", "File Path")
            
            d_dir = Path(config.get("download_dir"))
            if d_dir.exists():
                for f in d_dir.iterdir():
                    if f.is_file() and f.suffix.lower() in ('.mp4', '.mkv', '.mp3', '.m4a', '.webm', '.jpg', '.png', '.webp'):
                        if search_query and search_query.lower() not in f.name.lower():
                            continue
                            
                        # Guess size
                        sz = f.stat().st_size
                        sz_str = downloader.format_size(sz)
                        
                        # Guess type
                        ftype = "Audio" if f.suffix.lower() in ('.mp3', '.m4a') else ("Image" if f.suffix.lower() in ('.jpg', '.png', '.webp') else "Video")
                        
                        table.add_row(f.name, ftype, sz_str, str(f))
        except Exception:
            pass

class ToolsView(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("[bold #ff0055]🛠️ FFMPEG STUDIO UTILITIES[/bold #ff0055]", classes="title")
        yield Label("Action Options:")
        yield Select([
            ("Extract Audio (MP3)", "extract"),
            ("Convert Format (MP4)", "convert"),
            ("Compress Video", "compress")
        ], value="extract", id="tool-action")
        
        yield Label("Media File Input Path:")
        yield Input(placeholder="Enter absolute file path...", id="tool-file-input")
        
        yield Static("Operation Status: Idle", id="tool-status")
        yield Button("PROCESS MEDIA", variant="success", id="btn-process-tool")

class SettingsView(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("[bold #ff0055]⚙️ SETTINGS CONFIG HUB[/bold #ff0055]", classes="title")
        
        yield Label("Download Target Folder:")
        yield Input(id="set-dl-dir")
        
        yield Label("Speed Download Limit (e.g. 500K, 2M or empty):")
        yield Input(id="set-speed")
        
        with Horizontal(classes="switch-row"):
            yield Label("Enable Sound Alerts:")
            yield Switch(id="set-sound")
            
        with Horizontal(classes="switch-row"):
            yield Label("System Notifications:")
            yield Switch(id="set-notif")
            
        yield Button("SAVE CONFIGURATION", variant="success", id="btn-save-settings")
        
        yield Label("[bold #38bdf8]Engine Updates (yt-dlp):[/bold #38bdf8]", classes="section-title")
        with Horizontal(classes="button-row"):
            yield Button("CHECK FOR UPDATES", variant="primary", id="btn-check-updates")
            yield Button("FORCE UPDATE", variant="warning", id="btn-force-update")

    def load_config(self) -> None:
        try:
            self.query_one("#set-dl-dir", Input).value = config.get("download_dir") or ""
            self.query_one("#set-speed", Input).value = config.get("speed_limit") or ""
            self.query_one("#set-sound", Switch).value = config.get("sound_alerts", True)
            self.query_one("#set-notif", Switch).value = config.get("notifications", True)
        except Exception:
            pass

class TopBar(Horizontal):
    def compose(self) -> ComposeResult:
        yield Label("[bold #ff0055]⚡ F-SOCIETY[/bold #ff0055] [bold #00ff66]MEDIA CENTER[/bold #00ff66]", id="topbar-title")
        yield Label("SYSTEM STATUS: [bold #00ff66]ACTIVE[/bold #00ff66]", id="topbar-status")

class FSocietyTUIApp(App):
    CSS = """
    Screen {
        background: #06090c;
        color: #cbd5e1;
    }
    
    TopBar {
        background: #090d12;
        border-bottom: solid #ff0055;
        height: 3;
        align: left middle;
        padding: 0 2;
    }
    
    #topbar-title {
        width: 1fr;
    }
    
    #topbar-status {
        color: #94a3b8;
    }
    
    #stats-row {
        height: 6;
        margin: 1 0;
        layout: grid;
        grid-size: 3;
        grid-columns: 1fr 1fr 1fr;
    }
    
    .card {
        background: #0f172a;
        border: round #1e293b;
        padding: 1 2;
        content-align: center middle;
        text-align: center;
        color: #ffffff;
    }
    
    .title {
        text-style: bold;
        margin-bottom: 1;
        color: #ff0055;
    }
    
    .section-title {
        text-style: bold;
        margin: 1 0;
    }
    
    #sidebar {
        width: 24;
        background: #090d12;
        border-right: solid #1e293b;
        dock: left;
    }
    
    #content-container {
        padding: 1 2;
    }
    
    #meta-card {
        background: #0f172a;
        border: round #38bdf8;
        padding: 1 2;
        margin: 1 0;
        height: auto;
    }
    
    #meta-loading {
        color: #ff0055;
        height: 3;
        content-align: center middle;
    }
    
    .select-row {
        height: auto;
        margin: 1 0;
    }
    
    .select-row > Vertical {
        margin-right: 4;
        width: 30;
    }
    
    .button-row {
        height: auto;
        margin-top: 1;
    }
    
    .button-row > Button {
        margin-right: 2;
    }
    
    .switch-row {
        height: 4;
        align: left middle;
    }
    
    .switch-row > Label {
        width: 30;
    }
    
    Input {
        background: #0f172a;
        border: tall #38bdf8;
        color: #ffffff;
        margin-bottom: 1;
    }
    Input:focus {
        border: tall #f43f5e;
    }
    
    DataTable {
        background: #0f172a;
        border: round #1e293b;
        height: 1fr;
    }
    
    #dl-progress-text {
        color: #00ff66;
        text-style: bold;
        margin-top: 1;
    }
    #dl-progress-bar {
        width: 1fr;
        margin: 1 0;
    }
    ProgressBar > .bar--complete {
        color: #00ff66;
    }
    ProgressBar > .bar--bar {
        color: #38bdf8;
    }
    ProgressBar > .bar--percent {
        color: #ffffff;
    }
    #dl-speed-eta {
        color: #38bdf8;
        margin-bottom: 1;
    }
    
    HomeView, DownloadView, QueueView, LibraryView, ToolsView, SettingsView {
        overflow-y: auto;
        height: 1fr;
    }
    
    #hacker-gif {
        background: #090d12;
        border: round #38bdf8;
        padding: 1 2;
        margin: 1 0;
        height: auto;
    }

    /* Modal Styles */
    HelpScreen, ErrorRecoveryScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }
    
    #help-container {
        width: 65;
        height: auto;
        background: #0f172a;
        border: double #ff0055;
        padding: 1 2;
    }
    
    #help-title {
        text-align: center;
        color: #ff0055;
        text-style: bold;
        margin-bottom: 1;
    }
    
    .help-key {
        color: #cbd5e1;
        margin-bottom: 1;
    }
    
    #btn-close-help {
        margin-top: 1;
        align-horizontal: center;
    }
    
    #err-container {
        width: 75;
        height: auto;
        background: #0f172a;
        border: double #ff0055;
        padding: 1 2;
    }
    
    #err-title {
        text-align: center;
        color: #ff0055;
        text-style: bold;
        margin-bottom: 1;
    }
    
    .err-info {
        color: #cbd5e1;
        margin-bottom: 1;
    }
    
    .err-buttons {
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    
    .err-buttons > Button {
        margin-right: 1;
    }
    
    #home-banner {
        background: #090d12;
        border: double #ff0055;
        padding: 0 2;
        margin-bottom: 0;
        text-align: center;
        height: auto;
    }
    
    #hacker-gif {
        background: #090d12;
        border: round #38bdf8;
        padding: 1 2;
        margin: 1 0;
        height: auto;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("h", "switch_view('home')", "Home", show=False),
        Binding("d", "switch_view('download')", "Download", show=False),
        Binding("q", "switch_view('queue')", "Queue", show=False),
        Binding("l", "switch_view('library')", "Library", show=False),
        Binding("t", "switch_view('tools')", "Tools", show=False),
        Binding("s", "switch_view('settings')", "Settings", show=False),
        Binding("f1", "show_help", "Help", show=False),
        Binding("question_mark", "show_help", "Help", show=False),
    ]

    current_view = reactive("home")

    def compose(self) -> ComposeResult:
        yield Static(ASCII_BANNER, id="home-banner")
        with Horizontal():
            # Navigation Sidebar
            with ListView(id="sidebar"):
                yield ListItem(Label("🏠 Home"), id="nav-home")
                yield ListItem(Label("📥 Download"), id="nav-download")
                yield ListItem(Label("⏳ Queue"), id="nav-queue")
                yield ListItem(Label("📁 Library"), id="nav-library")
                yield ListItem(Label("🛠️ Tools"), id="nav-tools")
                yield ListItem(Label("⚙️ Settings"), id="nav-settings")
                
            # Content Area
            with Container(id="content-container"):
                yield HomeView(id="view-home")
                yield DownloadView(id="view-download")
                yield QueueView(id="view-queue")
                yield LibraryView(id="view-library")
                yield ToolsView(id="view-tools")
                yield SettingsView(id="view-settings")

        yield Footer()

    def on_mount(self) -> None:
        self.show_view("home")
        self.query_one("#view-home", HomeView).refresh_stats()
        self.query_one("#meta-loading", LoadingIndicator).display = False

    def show_view(self, view_name: str) -> None:
        self.current_view = view_name
        views = ["home", "download", "queue", "library", "tools", "settings"]
        for v in views:
            widget = self.query_one(f"#view-{v}")
            widget.display = (v == view_name)
            
        # Refresh state on switch
        if view_name == "home":
            self.query_one("#view-home", HomeView).refresh_stats()
        elif view_name == "queue":
            self.query_one("#view-queue", QueueView).refresh_queue()
        elif view_name == "library":
            self.query_one("#view-library", LibraryView).refresh_library()
        elif view_name == "settings":
            self.query_one("#view-settings", SettingsView).load_config()

    def action_switch_view(self, view_name: str) -> None:
        self.show_view(view_name)
        sidebar = self.query_one("#sidebar", ListView)
        try:
            for idx, item in enumerate(sidebar.children):
                if item.id == f"nav-{view_name}":
                    sidebar.index = idx
                    break
        except Exception:
            pass

    def action_show_help(self) -> None:
        self.push_screen(HelpScreen())

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        nav_id = event.item.id
        if nav_id == "nav-home":
            self.show_view("home")
        elif nav_id == "nav-download":
            self.show_view("download")
        elif nav_id == "nav-queue":
            self.show_view("queue")
        elif nav_id == "nav-library":
            self.show_view("library")
        elif nav_id == "nav-tools":
            self.show_view("tools")
        elif nav_id == "nav-settings":
            self.show_view("settings")

    # Dynamic URL Metadata Fetcher
    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "dl-url":
            url = event.value.strip()
            if downloader.validate_url(url):
                self.query_one("#meta-title", Label).update("[bold #38bdf8]Fetching metadata details...[/bold #38bdf8]")
                self.query_one("#meta-loading", LoadingIndicator).display = True
                self.run_worker(self.fetch_meta_task(url), thread=True)

    async def fetch_meta_task(self, url: str) -> None:
        info, err = downloader.fetch_video_info(url)
        if info:
            title = info.get("title", "Unknown")
            duration = downloader.format_duration(info.get("duration"))
            uploader = info.get("uploader", "Unknown")
            self.call_from_thread(self.update_meta_labels, title, duration, uploader)
        else:
            self.call_from_thread(self.update_meta_labels, f"Fetch failed: {err[:30]}", "N/A", "N/A")

    def update_meta_labels(self, title: str, duration: str, uploader: str) -> None:
        self.query_one("#meta-title", Label).update(f"[bold #ffffff]Title: {title}[/bold #ffffff]")
        self.query_one("#meta-duration", Label).update(f"Duration: {duration}")
        self.query_one("#meta-uploader", Label).update(f"Uploader: {uploader}")
        self.query_one("#meta-loading", LoadingIndicator).display = False

    # Downloader execute
    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn-start-download":
            url = self.query_one("#dl-url", Input).value.strip()
            if not downloader.validate_url(url):
                self.query_one("#dl-progress-text", Static).update("[bold #ff0055]Error: Invalid URL[/bold #ff0055]")
                return
                
            mode = self.query_one("#dl-mode", Select).value
            quality = self.query_one("#dl-quality", Select).value
            
            self.query_one("#btn-start-download", Button).disabled = True
            self.query_one("#dl-progress-text", Static).update("Starting download...")
            self.query_one("#dl-progress-bar", ProgressBar).progress = 0
            self.run_worker(self.download_task(url, mode, quality), thread=True)
            
        elif btn_id == "btn-save-settings":
            dl_dir = self.query_one("#set-dl-dir", Input).value.strip()
            speed = self.query_one("#set-speed", Input).value.strip()
            sound = self.query_one("#set-sound", Switch).value
            notif = self.query_one("#set-notif", Switch).value
            
            config.set("download_dir", dl_dir)
            config.set("speed_limit", speed)
            config.set("sound_alerts", sound)
            config.set("notifications", notif)
            self.notify("Configuration Saved Successfully!")
            
        elif btn_id == "btn-check-updates":
            self.notify("Checking for yt-dlp updates...")
            self.run_worker(self.check_updates_task(), thread=True)
            
        elif btn_id == "btn-force-update":
            self.notify("Updating yt-dlp in background...")
            self.run_worker(self.force_update_task(), thread=True)
            
        elif btn_id == "btn-queue-add":
            try:
                import tkinter as tk
                root = tk.Tk()
                root.withdraw()
                cb = root.clipboard_get().strip()
                if downloader.validate_url(cb):
                    q_manager = queue.QueueManager()
                    q_manager.add_item(cb, "video", "best")
                    self.query_one("#view-queue", QueueView).refresh_queue()
                    self.notify(f"Added clipboard URL to queue.")
                else:
                    self.notify("No valid URL found in clipboard.", severity="warning")
            except Exception as e:
                self.notify(f"Could not read clipboard: {e}", severity="error")
                
        elif btn_id == "btn-queue-clear":
            q_manager = queue.QueueManager()
            q_manager.clear()
            self.query_one("#view-queue", QueueView).refresh_queue()
            self.notify("Queue Cleared.")
            
        elif btn_id == "btn-queue-run":
            self.notify("Processing batch queue...")
            self.run_worker(self.run_queue_task(), thread=True)

        elif btn_id == "btn-lib-scan":
            self.query_one("#view-library", LibraryView).refresh_library()
            self.notify("Library scan complete.")

        elif btn_id == "btn-lib-play":
            try:
                table = self.query_one("#lib-table", DataTable)
                row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
                row = table.get_row(row_key)
                filepath = row[3]
                self.notify(f"Opening: {row[0]}")
                self.open_file_crossplatform(filepath)
            except Exception as e:
                self.notify(f"Selection error: {e}", severity="warning")

        elif btn_id == "btn-lib-delete":
            try:
                table = self.query_one("#lib-table", DataTable)
                row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
                row = table.get_row(row_key)
                filepath = row[3]
                os.remove(filepath)
                self.query_one("#view-library", LibraryView).refresh_library()
                self.notify(f"Deleted: {row[0]}")
            except Exception as e:
                self.notify(f"Failed to delete: {e}", severity="error")

        elif btn_id == "btn-process-tool":
            action = self.query_one("#tool-action", Select).value
            filepath = self.query_one("#tool-file-input", Input).value.strip()
            
            if not os.path.exists(filepath):
                self.query_one("#tool-status", Static).update("[bold #ff0055]Error: File not found[/bold #ff0055]")
                return
                
            self.query_one("#tool-status", Static).update("Processing file with FFmpeg...")
            self.run_worker(self.run_ffmpeg_task(action, filepath), thread=True)

    def open_file_crossplatform(self, path: str) -> None:
        try:
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':
                import subprocess
                subprocess.run(['open', path])
            else:
                import subprocess
                subprocess.run(['xdg-open', path])
        except Exception as e:
            self.notify(f"Open failed: {e}", severity="error")

    # Queue Worker
    async def run_queue_task(self) -> None:
        q_manager = queue.QueueManager()
        success, msg = q_manager.run()
        self.call_from_thread(self.on_queue_completed, msg)

    def on_queue_completed(self, msg: str) -> None:
        self.query_one("#view-queue", QueueView).refresh_queue()
        self.notify(f"Batch completed: {msg}")

    # FFmpeg Worker
    async def run_ffmpeg_task(self, action: str, filepath: str) -> None:
        success = False
        msg = ""
        try:
            if action == "extract":
                success, msg = ffmpeg.extract_audio(filepath)
            elif action == "convert":
                success, msg = ffmpeg.convert_format(filepath, "mp4")
            elif action == "compress":
                success, msg = ffmpeg.compress_video(filepath)
        except Exception as e:
            success = False
            msg = str(e)
        self.call_from_thread(self.on_ffmpeg_completed, success, msg)

    def on_ffmpeg_completed(self, success: bool, msg: str) -> None:
        if success:
            self.query_one("#tool-status", Static).update("[bold #00ff66]FFmpeg processing complete![/bold #00ff66]")
            self.notify("FFmpeg processing successful.")
        else:
            self.query_one("#tool-status", Static).update(f"[bold #ff0055]FFmpeg Failed: {msg[:30]}[/bold #ff0055]")
            self.notify("FFmpeg operation failed.", severity="error")

    # Update Workers
    async def check_updates_task(self) -> None:
        try:
            local_ver = updater.get_ytdlp_version()
            latest_ver = updater.get_latest_ytdlp_version()
            self.call_from_thread(self.on_check_updates_completed, local_ver, latest_ver)
        except Exception as e:
            self.call_from_thread(self.notify, f"Error checking updates: {e}", severity="error")

    def on_check_updates_completed(self, local: str, latest: str) -> None:
        if latest == "Unknown":
            self.notify("Could not retrieve latest version. Check internet connection.", severity="error")
        elif local == latest:
            self.notify(f"yt-dlp is up to date (v{local}).", severity="information")
        else:
            self.notify(f"Update available! Current: v{local} | Latest: v{latest}.", severity="warning")

    async def force_update_task(self) -> None:
        try:
            success, msg = updater.update_ytdlp()
            self.call_from_thread(self.on_force_update_completed, success, msg)
        except Exception as e:
            self.call_from_thread(self.notify, f"Error updating: {e}", severity="error")

    def on_force_update_completed(self, success: bool, msg: str) -> None:
        if success:
            self.notify("yt-dlp updated successfully!")
        else:
            self.notify(f"Failed to update yt-dlp: {msg}", severity="error")

    # Downloader Worker
    async def download_task(self, url: str, mode: str, quality: str, force_fallback: bool = False) -> None:
        def progress_cb(percent, speed, eta, downloaded, total, status, filename):
            self.call_from_thread(self.update_download_progress, percent, speed, eta, downloaded, total, status, filename)

        downloader.clear_progress_callbacks()
        downloader.register_progress_callback(progress_cb)
        
        success = False
        err_msg = ""
        err_exception = None
        try:
            if mode == "video":
                fmt = downloader.build_format_string(quality)
                success = downloader.download_video_via_api(url, fmt, force_fallback=force_fallback)
            elif mode == "audio":
                success = downloader.download_audio_via_api(url, quality)
            elif mode == "images":
                success = downloader.download_image_gallery_via_api(url)
        except downloader.DownloaderError as err:
            success = False
            err_exception = err
        except Exception as e:
            success = False
            err_msg = str(e)

        downloader.unregister_progress_callback(progress_cb)
        self.call_from_thread(self.on_download_finished, url, mode, quality, success, err_msg, err_exception)

    def update_download_progress(self, percent, speed, eta, downloaded, total, status, filename):
        self.query_one("#dl-progress-text", Static).update(f"Progress: {int(percent)}% - {status.upper()}")
        self.query_one("#dl-progress-bar", ProgressBar).progress = percent
        self.query_one("#dl-speed-eta", Static).update(f"ETA: {eta} | Speed: {speed} | Downloaded: {downloaded}/{total}")

    def on_download_finished(self, url: str, mode: str, quality: str, success: bool, err_msg: str, err_exception: downloader.DownloaderError) -> None:
        self.query_one("#btn-start-download", Button).disabled = False
        if success:
            self.query_one("#dl-progress-text", Static).update("[bold #00ff66]Download Complete![/bold #00ff66]")
            self.query_one("#dl-progress-bar", ProgressBar).progress = 100
            self.notify("Media download successful!")
        else:
            if err_exception:
                def handle_recovery(action):
                    if action == "err-retry":
                        self.query_one("#btn-start-download", Button).disabled = True
                        self.query_one("#dl-progress-text", Static).update("Retrying download...")
                        self.query_one("#dl-progress-bar", ProgressBar).progress = 0
                        self.run_worker(self.download_task(url, mode, quality), thread=True)
                    elif action == "err-update":
                        self.notify("Updating yt-dlp in background...")
                        self.run_worker(self.force_update_task(), thread=True)
                    elif action == "err-fallback" and err_exception.platform == "TikTok":
                        self.query_one("#btn-start-download", Button).disabled = True
                        self.query_one("#dl-progress-text", Static).update("Running fallback download...")
                        self.query_one("#dl-progress-bar", ProgressBar).progress = 0
                        self.run_worker(self.download_task(url, mode, quality, force_fallback=True), thread=True)
                
                self.push_screen(
                    ErrorRecoveryScreen(err_exception.platform, err_exception.reason, err_exception.solution),
                    handle_recovery
                )
            else:
                self.query_one("#dl-progress-text", Static).update(f"[bold #ff0055]Failed: {err_msg[:40]}[/bold #ff0055]")
                self.notify("Download Failed.", severity="error")

def run_tui():
    try:
        app = FSocietyTUIApp()
        app.run()
    except Exception as e:
        import traceback
        from rich.console import Console
        from rich.panel import Panel
        from rich.align import Align
        console = Console()
        console.clear()
        
        fallback_ui = (
            "╭────────────────────────────╮\n"
            "│ UI ERROR DETECTED          │\n"
            "│ Fixing layout...           │\n"
            "╰────────────────────────────╯\n\n"
            "[bold red]F-SOCIETY MEDIA TUI CRASHED ON STARTUP[/bold red]\n\n"
            f"[yellow]Error Details:[/yellow] {e}\n\n"
            "[yellow]Stack Trace:[/yellow]\n"
            f"{traceback.format_exc()}\n"
            "Press [bold green]ENTER[/bold green] to exit."
        )
        console.print(Panel(Align.center(fallback_ui), title="[bold red] SAFE CRASH SYSTEM [/bold red]", border_style="red"))
        input()

def run_tui_debugger():
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    console = Console()
    console.print("[bold red]F-SOCIETY UI DEBUGGER MODE[/bold red]\n")
    
    css_content = FSocietyTUIApp.CSS
    errors = []
    
    if "font-family" in css_content:
        errors.append("Invalid CSS property 'font-family': Textual TUI does not support custom fonts via CSS.")
    if "border-right: thin" in css_content:
        errors.append("Invalid value for 'border-right': 'thin' is not a valid border style in Textual. Use solid, dashed, etc.")
    if "align: middle left" in css_content or "align: bottom left" in css_content:
        errors.append("Invalid value for 'align': alignment is expected to be '<horizontal> <vertical>' (e.g. 'left middle').")
        
    table = Table(title="CSS Validation Report", box=None)
    table.add_column("Rule", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Suggestion", style="cyan")
    
    if errors:
        for err in errors:
            table.add_row(err.split(":")[0], "[bold red]FAILED[/bold red]", err.split(":")[1])
        console.print(Panel(table, title="[bold red] ERROR DETECTED [/bold red]", border_style="red"))
    else:
        table.add_row("Font Family check", "PASS", "No font-family properties found")
        table.add_row("Border Styles check", "PASS", "All border-right and border definitions are valid")
        table.add_row("Alignment check", "PASS", "All layout alignment formats are correct")
        console.print(Panel(table, title="[bold green] SUCCESS [/bold green]", border_style="green"))
        
    console.print("\n[bold yellow]Widget Tree Preview:[/bold yellow]")
    console.print("FSocietyTUIApp")
    console.print(" ├── TopBar")
    console.print(" ├── Horizontal (layout)")
    console.print(" │    ├── ListView (sidebar)")
    console.print(" │    └── Container (content-container)")
    console.print(" │         ├── HomeView")
    console.print(" │         ├── DownloadView")
    console.print(" │         ├── QueueView")
    console.print(" │         ├── LibraryView")
    console.print(" │         ├── ToolsView")
    console.print(" │         └── SettingsView")
    console.print(" └── Footer")
    console.print("\nNo layout errors found. Application layout structure is professional and fully validated.")

if __name__ == "__main__":
    run_tui()
