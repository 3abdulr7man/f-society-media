import os
import sys
import argparse
from pathlib import Path

from src.core import config, database, downloader

def parse_cli_args_and_run():
    parser = argparse.ArgumentParser(description="F-SOCIETY YT-DLP TOOL - Command Line Utility")
    parser.add_argument("url", nargs="?", help="URL of the media to download")
    parser.add_argument("--url", dest="url_opt", help="Alternate option for URL specification")
    parser.add_argument("--audio", action="store_true", help="Download audio extraction only")
    parser.add_argument("--images", action="store_true", help="Download image/photo gallery posts")
    parser.add_argument("--playlist", action="store_true", help="Download playlist collection")
    parser.add_argument("--channel", action="store_true", help="Download channel uploads")
    parser.add_argument("--quality", help="Set video resolution (e.g. 1080p) or audio bitrate (e.g. 320)")
    parser.add_argument("--dir", help="Custom target download folder")
    parser.add_argument("--limit", help="Custom speed download limit (e.g. 500K, 2M)")
    parser.add_argument("--gui", action="store_true", help="Launch in graphical user interface desktop mode")
    parser.add_argument("--watch", action="store_true", help="Watch clipboard for media URL copies")
    parser.add_argument("--doctor", action="store_true", help="Verify system environment diagnostics")
    parser.add_argument("--report", action="store_true", help="Export diagnostics report (combined with --doctor)")
    parser.add_argument("--debug-ui", action="store_true", help="Validate and debug Textual TUI CSS/layouts")

    args, unknown = parser.parse_known_args()
    
    # Check if UI debug mode is requested
    if args.debug_ui:
        from src.cli.tui import run_tui_debugger
        run_tui_debugger()
        sys.exit(0)
        
    # Check if doctor mode is requested
    if args.doctor:
        from src.core.diagnostics import SystemDiagnostics
        diag = SystemDiagnostics()
        diag.run_doctor()
        if args.report:
            diag.export_report()
        sys.exit(0)
        
    # Check if GUI is explicitly requested or watch mode
    if args.gui or args.watch:
        return args
        
    url = args.url or args.url_opt
    if not url:
        # No CLI arguments provided, flag launch interactive CLI dashboard
        return None
        
    # Standard CLI download execute flow
    config.load_settings()
    if args.dir:
        config.set("download_dir", os.path.abspath(args.dir))
    if args.limit:
        config.set("speed_limit", args.limit)
        
    url = url.strip()
    if not downloader.validate_url(url):
        print(f"Error: Invalid URL '{url}'")
        sys.exit(1)
        
    print(f"[F-SOCIETY] Running CLI Download for: {url} ...")
    
    try:
        success = False
        if args.audio:
            bitrate = args.quality or config.get("default_audio_quality")
            success = downloader.download_audio_via_api(url, bitrate)
        elif args.images:
            success = downloader.download_image_gallery_via_api(url)
        elif args.playlist:
            quality = args.quality or "best"
            success = downloader.download_playlist_via_api(url, quality)
        elif args.channel:
            quality = args.quality or "best"
            success = downloader.download_channel_via_api(url, 20, quality)
        else:
            quality = args.quality or config.get("default_video_quality")
            fmt = downloader.build_format_string(quality)
            success = downloader.download_video_via_api(url, fmt)
            
        if success:
            print("[F-SOCIETY] Download complete successfully!")
            sys.exit(0)
        else:
            print("[F-SOCIETY] Error: Download failed.")
            sys.exit(1)
    except downloader.DownloaderError as err:
        # Downloader Error Handling System formatted box
        print("\n╭──────────── ERROR ────────────╮")
        print(f"│ Platform: {err.platform:<20} │")
        print(f"│ Reason: {err.reason[:21]:<22} │")
        print(f"│ Solution: {err.solution[:19]:<20} │")
        print("╰───────────────────────────────╯")
        sys.exit(1)
    except Exception as e:
        print(f"[F-SOCIETY] Fatal error: {e}")
        sys.exit(1)
