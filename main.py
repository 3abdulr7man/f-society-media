import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core import database, config
from src.cli import terminal_ui, menus

def watch_clipboard():
    import tkinter as tk
    import time
    from src.core import downloader
    
    root = tk.Tk()
    root.withdraw()
    
    print("[F-SOCIETY] Clipboard Smart Mode active. Watching for media URLs...")
    print("Press Ctrl+C to stop watching.")
    
    last_clip = ""
    try:
        while True:
            try:
                clip = root.clipboard_get().strip()
                if clip != last_clip and downloader.validate_url(clip):
                    last_clip = clip
                    platform = downloader.detect_platform(clip)
                    print(f"\n[+] URL detected ({platform}): {clip}")
                    ans = input("Download now? (Y/n): ").strip().lower()
                    if ans != 'n':
                        downloader.download_video_via_api(clip)
            except Exception:
                pass
            time.sleep(1.2)
    except KeyboardInterrupt:
        print("\nClipboard watch stopped.")

def entry_point():
    print("F-SOCIETY MEDIA STARTING...")
    print("✓ Environment check")
    print("✓ Dependencies loaded")
    print("✓ Core initialized\n")

    # 1. Initialize SQLite Database
    database.init_db()
    
    # 2. Parse command line arguments
    args = terminal_ui.parse_cli_args_and_run()
    
    if os.environ.get("CI") == "true":
        print("[CI DETECTED] Running headless system diagnostics...")
        from src.core.diagnostics import SystemDiagnostics
        diag = SystemDiagnostics()
        success = diag.run_doctor()
        if not success:
            sys.exit(1)
        sys.exit(0)
        
    if args is not None:
        if args.gui:
            # Import GUI inside condition to prevent importing PySide6 in headless CLI environments
            try:
                from src.gui import main_window
                main_window.launch_gui()
            except ImportError as e:
                print(f"Error: GUI PySide6 package is not available. {e}")
                sys.exit(1)
        elif args.watch:
            watch_clipboard()
    else:
        # Launch beautiful console menu
        try:
            menus.run_cli_dashboard()
        except KeyboardInterrupt:
            print("\nExiting F-SOCIETY YT-DLP Tool...")

if __name__ == "__main__":
    entry_point()
