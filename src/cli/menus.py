import os
import sys
import time
import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich import box

from src.core import config, database, ffmpeg, updater, downloader, queue, scheduler
from src.core.diagnostics import quick_startup_check

console = Console()

def get_key():
    if os.name == 'nt':
        import msvcrt
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            if ch2 == b'H': return 'up'
            if ch2 == b'P': return 'down'
            if ch2 == b'K': return 'left'
            if ch2 == b'M': return 'right'
        if ch == b'\r': return 'enter'
        if ch == b'\x1b': return 'esc'
        try:
            return ch.decode('utf-8', errors='ignore').lower()
        except:
            return None
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(2)
                if ch2 == '[A': return 'up'
                if ch2 == '[B': return 'down'
                if ch2 == '[D': return 'left'
                if ch2 == '[C': return 'right'
            elif ch == '\r' or ch == '\n':
                return 'enter'
            elif ch == '\x1b':
                return 'esc'
            return ch.lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def get_storage_stats():
    d_dir = Path(config.get("download_dir"))
    total_size = 0
    count = 0
    if d_dir.exists():
        for f in d_dir.glob("**/*"):
            if f.is_file():
                total_size += f.stat().st_size
                count += 1
    return count, total_size

def print_banner():
    banner = f"""
     ███████╗      ███████╗ ██████╗  ██████╗██╗███████╗████████╗██╗   ██╗
     ██╔════╝      ██╔════╝██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
     █████╗        ███████╗██║   ██║██║     ██║█████╗     ██║    ╚████╔╝
     ██╔══╝        ╚════██║██║   ██║██║     ██║██╔══╝     ██║     ╚██╔╝
     ██║           ███████║╚██████╔╝╚██████╗██║███████╗   ██║      ██║
     ╚═╝           ╚══════╝ ╚═════╝  ╚═════╝╚═╝╚══════╝   ╚═╝      ╚═╝
"""
    console.print(Align.center(f"[bold red]{banner}[/bold red]"))
    console.print(Align.center(f"[bold blue]F-SOCIETY YT-DLP MEDIA SUITE v1.0.0[/bold blue]"))
    console.print(Align.center(f"[magenta]======================================================================[/magenta]"))

def draw_dashboard():
    logs = database.get_download_logs()
    total_downloads = len(logs)
    completed_downloads = sum(1 for log in logs if log.get("status") == "success")
    file_count, storage_bytes = get_storage_stats()
    storage_gb = storage_bytes / (1024 * 1024 * 1024)

    table = Table(show_header=False, expand=True, box=None)
    table.add_column(justify="center")
    table.add_column(justify="center")
    table.add_column(justify="center")
    
    table.add_row(
        f"[bold cyan]Downloads[/bold cyan]\n[white]{total_downloads}[/white]",
        f"[bold green]Completed[/bold green]\n[white]{completed_downloads}[/white]",
        f"[bold yellow]Storage[/bold yellow]\n[white]{storage_gb:.2f} GB ({file_count} files)[/white]"
    )
    
    panel = Panel(
        table,
        title="[bold green] D-15 DASHBOARD CONTROL [/bold green]",
        border_style="cyan",
        box=box.DOUBLE
    )
    console.print(panel)

def run_interactive_selector(title, options, default_index=0):
    selected_index = default_index
    while True:
        clear_screen()
        print_banner()
        draw_dashboard()
        
        menu_text = ""
        for idx, option in enumerate(options):
            if idx == selected_index:
                menu_text += f"[bold green]>[/bold green] [bold white on red] {option} [/bold white on red]\n"
            else:
                menu_text += f"  [dim white] {option} [/dim white]\n"
                
        panel = Panel(
            menu_text.strip(),
            title=f"[bold red] {title} [/bold red]",
            border_style="magenta",
            box=box.ROUNDED,
            expand=True
        )
        console.print(panel)
        console.print("\n[bold dim cyan]Use UP/DOWN arrows to navigate, ENTER to select, ESC or 'q' to go back.[/bold dim cyan]")
        
        key = get_key()
        if key == 'up':
            selected_index = (selected_index - 1) % len(options)
        elif key == 'down':
            selected_index = (selected_index + 1) % len(options)
        elif key == 'enter':
            return selected_index
        elif key in ('esc', 'q', '0'):
            return -1

def show_error_recovery_dialog(err_exception, url, mode, quality):
    # Formatted Error Box
    console.print(f"\n[bold red]╭──────────── ERROR ────────────╮[/bold red]")
    console.print(f"[bold red]│[/bold red] Platform: [yellow]{err_exception.platform:<20}[/yellow] [bold red]│[/bold red]")
    console.print(f"[bold red]│[/bold red] Reason: [white]{err_exception.reason[:21]:<22}[/white] [bold red]│[/bold red]")
    console.print(f"[bold red]│[/bold red] Solution: [cyan]{err_exception.solution[:19]:<20}[/cyan] [bold red]│[/bold red]")
    console.print(f"[bold red]╰───────────────────────────────╯[/bold red]")
    
    options = [
        "Retry Download",
        "Update Engine (yt-dlp)",
        "Use Alternative Fallback Method",
        "Cancel"
    ]
    
    choice = run_interactive_selector("ERROR RECOVERY OPTIONS", options)
    if choice == 0:
        # Retry
        return "retry"
    elif choice == 1:
        # Update
        console.print("\nUpdating yt-dlp...")
        success, msg = updater.update_ytdlp()
        if success:
            console.print("[bold green]yt-dlp successfully updated![/bold green]")
        else:
            console.print(f"[bold red]Failed: {msg}[/bold red]")
        time.sleep(2)
        return "retry"
    elif choice == 2:
        return "fallback"
    return "cancel"

def download_video_flow():
    clear_screen()
    print_banner()
    console.print(f"[bold cyan]{config.t('menu_opt_video').upper()}[/bold cyan]")
    url = console.input(f"\n[bold green]{config.t('prompt_url')}[/bold green]").strip()
    if not downloader.validate_url(url):
        console.print(f"[bold red]{config.t('invalid_url')}[/bold red]")
        time.sleep(1)
        return
        
    platform = downloader.detect_platform(url)
    content_type = downloader.detect_content_type(url)
    
    # Smart Download Flow details
    console.print(f"\n[bold yellow]Platform detected:[/bold yellow] [white]{platform}[/white]")
    console.print(f"[bold yellow]Content Type     :[/bold yellow] [white]{content_type}[/white]")
    
    # Pre-fetch meta
    info, err = downloader.fetch_video_info(url)
    if info:
        console.print(f"[bold yellow]Title            :[/bold yellow] [white]{info.get('title', 'Unknown')}[/white]")
        console.print(f"[bold yellow]Duration         :[/bold yellow] [white]{downloader.format_duration(info.get('duration'))}[/white]")
        
    if content_type in ("playlist", "channel"):
        use_playlist = console.input("[bold yellow]This looks like a playlist/channel. Use playlist mode? (Y/n): [/bold yellow]").lower() != 'n'
        if use_playlist:
            if content_type == "playlist":
                downloader.download_playlist_via_api(url)
            else:
                downloader.download_channel_via_api(url)
            console.input("\nPress Enter to continue...")
            return
            
    qualities = ["best", "2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"]
    res_index = run_interactive_selector("Select Quality", qualities)
    if res_index == -1:
        return
        
    quality = qualities[res_index]
    fmt = downloader.build_format_string(quality)
    
    console.print(f"\n[bold green]Starting Download...[/bold green]")
    while True:
        try:
            downloader.download_video_via_api(url, fmt)
            break
        except downloader.DownloaderError as err_exc:
            action = show_error_recovery_dialog(err_exc, url, "video", quality)
            if action == "retry":
                continue
            elif action == "fallback" and platform == "TikTok":
                # Trigger fallback via platform tiktok
                from src.core.platforms.tiktok import TikTokPlatformExtractor
                t_ext = TikTokPlatformExtractor()
                outtmpl = str(Path(config.get("download_dir")) / config.get("output_template"))
                t_ext.download(url, "best", outtmpl, downloader.progress_hook)
                break
            break
    console.input("\nPress Enter to continue...")

def download_audio_flow():
    clear_screen()
    print_banner()
    console.print(f"[bold cyan]{config.t('menu_opt_audio').upper()}[/bold cyan]")
    url = console.input(f"\n[bold green]{config.t('prompt_url')}[/bold green]").strip()
    if not downloader.validate_url(url):
        console.print(f"[bold red]{config.t('invalid_url')}[/bold red]")
        time.sleep(1)
        return
        
    bitrates = ["320", "256", "192", "128", "96", "64", "48"]
    res_index = run_interactive_selector("Select Audio Bitrate", [f"{b} kbps" for b in bitrates])
    if res_index == -1:
        return
        
    bitrate = bitrates[res_index]
    console.print(f"\n[bold green]Starting Audio Extraction...[/bold green]")
    while True:
        try:
            downloader.download_audio_via_api(url, bitrate)
            break
        except downloader.DownloaderError as err_exc:
            action = show_error_recovery_dialog(err_exc, url, "audio", bitrate)
            if action == "retry":
                continue
            break
    console.input("\nPress Enter to continue...")

def download_image_flow():
    clear_screen()
    print_banner()
    console.print(f"[bold cyan]{config.t('menu_opt_images').upper()}[/bold cyan]")
    url = console.input(f"\n[bold green]{config.t('prompt_url')}[/bold green]").strip()
    if not downloader.validate_url(url):
        console.print(f"[bold red]{config.t('invalid_url')}[/bold red]")
        time.sleep(1)
        return
        
    console.print(f"\n[bold green]Starting Images/Gallery extraction...[/bold green]")
    while True:
        try:
            downloader.download_image_gallery_via_api(url)
            break
        except downloader.DownloaderError as err_exc:
            action = show_error_recovery_dialog(err_exc, url, "images", None)
            if action == "retry":
                continue
            break
    console.input("\nPress Enter to continue...")

def queue_manager_flow():
    q_manager = queue.QueueManager()
    while True:
        options = [
            "Add Video to Queue",
            "Add Audio to Queue",
            "Add Images to Queue",
            "View Queue items",
            "Start Batch Processing",
            "Clear Queue",
            "Batch URLs from File",
            "Go Back"
        ]
        choice = run_interactive_selector("Batch Queue Manager", options)
        if choice in (-1, 7):
            break
        elif choice in (0, 1, 2):
            clear_screen()
            print_banner()
            url = console.input(f"[bold green]Enter URL: [/bold green]").strip()
            if not downloader.validate_url(url):
                console.print(f"[bold red]{config.t('invalid_url')}[/bold red]")
                time.sleep(1)
                continue
                
            mode_map = {0: "video", 1: "audio", 2: "image"}
            mode = mode_map[choice]
            
            quality = ""
            if mode == "video":
                qualities = ["best", "1080p", "720p", "480p"]
                q_choice = run_interactive_selector("Select Quality", qualities)
                if q_choice != -1:
                    quality = qualities[q_choice]
            elif mode == "audio":
                bitrates = ["320", "192", "128"]
                b_choice = run_interactive_selector("Select Bitrate", [f"{b}kbps" for b in bitrates])
                if b_choice != -1:
                    quality = bitrates[b_choice]
                    
            q_manager.add_item(url, mode, quality)
            console.print("[bold green]Added to queue successfully.[/bold green]")
            time.sleep(1)
            
        elif choice == 3:
            clear_screen()
            print_banner()
            items = q_manager.get_items()
            if not items:
                console.print("[bold yellow]Queue is empty![/bold yellow]")
            else:
                table = Table(title="F-SOCIETY Batch Queue")
                table.add_column("ID", justify="center")
                table.add_column("URL", style="cyan")
                table.add_column("Mode", style="magenta")
                table.add_column("Quality", style="yellow")
                table.add_column("Status", style="green")
                
                for idx, item in enumerate(items, 1):
                    table.add_row(str(idx), item["url"][:50], item["mode"], item["quality"], item["status"])
                console.print(table)
            console.input("\nPress Enter to continue...")
        elif choice == 4:
            clear_screen()
            print_banner()
            q_manager.run()
            console.input("\nPress Enter to continue...")
        elif choice == 5:
            q_manager.clear()
            console.print("[bold green]Queue cleared successfully.[/bold green]")
            time.sleep(1)
        elif choice == 6:
            clear_screen()
            print_banner()
            fp = console.input("[bold yellow]Enter file path with URLs (one per line): [/bold yellow]").strip()
            if os.path.exists(fp):
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        urls = [l.strip() for l in f if l.strip() and downloader.validate_url(l.strip())]
                    for u in urls:
                        q_manager.add_item(u, "video")
                    console.print(f"[bold green]Added {len(urls)} URLs to queue successfully.[/bold green]")
                except Exception as e:
                    console.print(f"[bold red]Error reading file: {e}[/bold red]")
            else:
                console.print("[bold red]File not found![/bold red]")
            time.sleep(2.5)

def scheduler_flow():
    while True:
        options = [
            "Schedule a Download",
            "View Scheduled Jobs",
            "Cancel a Job",
            "Go Back"
        ]
        choice = run_interactive_selector("Scheduler (Timed Downloads)", options)
        if choice in (-1, 3):
            break
        elif choice == 0:
            clear_screen()
            print_banner()
            url = console.input("[bold green]Enter URL to schedule: [/bold green]").strip()
            if not downloader.validate_url(url):
                console.print(f"[bold red]{config.t('invalid_url')}[/bold red]")
                time.sleep(1)
                continue
                
            modes = ["video", "audio", "image"]
            m_choice = run_interactive_selector("Select Mode", modes)
            if m_choice == -1: continue
            mode = modes[m_choice]
            
            quality = ""
            if mode == "video":
                quality = "best"
            elif mode == "audio":
                quality = "192"
                
            times = ["Specific Delay (Minutes)", "Specific Clock Time (HH:MM or YYYY-MM-DD HH:MM)"]
            t_choice = run_interactive_selector("Select Timing Option", times)
            if t_choice == -1: continue
            
            target_time = None
            if t_choice == 0:
                delay = console.input("[bold yellow]Delay in minutes: [/bold yellow]").strip()
                try:
                    target_time = datetime.datetime.now() + datetime.timedelta(minutes=float(delay))
                except:
                    console.print("[bold red]Invalid delay value![/bold red]")
                    time.sleep(1)
                    continue
            else:
                time_str = console.input("[bold yellow]Target time (HH:MM or YYYY-MM-DD HH:MM): [/bold yellow]").strip()
                try:
                    if len(time_str) == 5 and ":" in time_str:
                        hh, mm = map(int, time_str.split(":"))
                        now = datetime.datetime.now()
                        target_time = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
                        if target_time < now:
                            target_time += datetime.timedelta(days=1)
                    else:
                        target_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                except:
                    console.print("[bold red]Invalid format! Use HH:MM or YYYY-MM-DD HH:MM.[/bold red]")
                    time.sleep(2)
                    continue
                    
            if target_time:
                job_id = scheduler.schedule_job(url, mode, quality, target_time)
                console.print(f"[bold green]Job #{job_id} scheduled for {target_time.strftime('%Y-%m-%d %H:%M')}[/bold green]")
                time.sleep(2)
        elif choice == 1:
            clear_screen()
            print_banner()
            jobs = scheduler.get_jobs()
            if not jobs:
                console.print("[bold yellow]No scheduled jobs.[/bold yellow]")
            else:
                table = Table(title="Scheduled Jobs")
                table.add_column("ID", justify="center")
                table.add_column("URL", style="cyan")
                table.add_column("Mode", style="magenta")
                table.add_column("Time", style="yellow")
                table.add_column("Status", style="green")
                
                for j in jobs:
                    table.add_row(j["id"], j["url"][:40], j["mode"], j["target_time"].strftime("%Y-%m-%d %H:%M"), j["status"])
                console.print(table)
            console.input("\nPress Enter to continue...")
        elif choice == 2:
            clear_screen()
            print_banner()
            job_id = console.input("[bold yellow]Enter Job ID to cancel: [/bold yellow]").strip()
            if scheduler.cancel_job(job_id):
                console.print(f"[bold green]Job #{job_id} cancelled.[/bold green]")
            else:
                console.print("[bold red]Job ID not found![/bold red]")
            time.sleep(1)

def metadata_editor_flow():
    if not ffmpeg.is_ffmpeg_available():
        console.print("[bold red]ffmpeg not found! Installed ffmpeg required to edit metadata.[/bold red]")
        time.sleep(2)
        return
        
    while True:
        clear_screen()
        print_banner()
        console.print("[bold cyan]METADATA TAG EDITOR[/bold cyan]\n")
        
        d_dir = Path(config.get("download_dir"))
        if not d_dir.exists():
            console.print("[bold yellow]Download directory does not exist.[/bold yellow]")
            console.input("\nPress Enter to continue...")
            break
            
        files = [f for f in d_dir.iterdir() if f.is_file() and f.suffix.lower() in ('.mp4', '.mkv', '.mp3', '.m4a', '.webm')]
        if not files:
            console.print("[bold yellow]No media files found in download directory.[/bold yellow]")
            console.input("\nPress Enter to continue...")
            break
            
        options = [f.name for f in files[:20]] + ["Go Back"]
        choice = run_interactive_selector("Select Media File", options)
        if choice in (-1, len(options) - 1):
            break
            
        target_file = files[choice]
        clear_screen()
        print_banner()
        console.print(f"[bold yellow]Editing: [cyan]{target_file.name}[/cyan][/bold yellow]\n")
        
        title = console.input("Title (Enter to keep): ").strip()
        artist = console.input("Artist (Enter to keep): ").strip()
        album = console.input("Album (Enter to keep): ").strip()
        genre = console.input("Genre (Enter to keep): ").strip()
        comment = console.input("Comment (Enter to keep): ").strip()
        
        temp_file = target_file.with_name(f"{target_file.stem}_meta_tmp{target_file.suffix}")
        cmd = ["ffmpeg", "-i", str(target_file)]
        if title: cmd.extend(["-metadata", f"title={title}"])
        if artist: cmd.extend(["-metadata", f"artist={artist}"])
        if album: cmd.extend(["-metadata", f"album={album}"])
        if genre: cmd.extend(["-metadata", f"genre={genre}"])
        if comment: cmd.extend(["-metadata", f"comment={comment}"])
        cmd.extend(["-c", "copy", str(temp_file), "-y"])
        
        console.print("\n[bold info]Applying metadata...[/bold info]")
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and temp_file.exists():
            try:
                os.remove(target_file)
                os.rename(temp_file, target_file)
                console.print("[bold green]Metadata updated successfully![/bold green]")
            except Exception as e:
                console.print(f"[bold red]Failed to replace file: {e}[/bold red]")
        else:
            if temp_file.exists():
                os.remove(temp_file)
            console.print("[bold red]Failed to update metadata.[/bold red]")
        time.sleep(2)

def ffmpeg_tools_flow():
    if not ffmpeg.is_ffmpeg_available():
        console.print("[bold red]ffmpeg not found! Please install FFmpeg.[/bold red]")
        time.sleep(2)
        return
        
    while True:
        options = [
            "Trim Video",
            "Convert Format",
            "Compress Video",
            "Extract Audio",
            "Merge Video + Audio",
            "Go Back"
        ]
        choice = run_interactive_selector("FFmpeg Studio UTILITIES", options)
        if choice in (-1, 5):
            break
        elif choice == 0:
            clear_screen(); print_banner()
            fp = console.input("[bold green]Video path: [/bold green]").strip()
            start = console.input("[bold green]Start time (e.g. 00:01:30): [/bold green]").strip()
            dur = console.input("[bold green]Duration (Enter for end): [/bold green]").strip()
            out = console.input("[bold green]Output filename (trimmed.mp4): [/bold green]").strip() or "trimmed.mp4"
            success, msg = ffmpeg.trim_video(fp, start, dur, out)
            if success:
                console.print(f"[bold green]Trimmed file successfully saved to downloads folder![/bold green]")
            else:
                console.print(f"[bold red]Trimming failed: {msg}[/bold red]")
            console.input("\nPress Enter to continue...")
        elif choice == 1:
            clear_screen(); print_banner()
            fp = console.input("[bold green]Media path: [/bold green]").strip()
            ext = console.input("[bold green]Target format (mp4/avi/mkv/webm): [/bold green]").strip().lower()
            success, msg = ffmpeg.convert_format(fp, ext)
            if success:
                console.print("[bold green]File converted successfully![/bold green]")
            else:
                console.print(f"[bold red]Conversion failed: {msg}[/bold red]")
            console.input("\nPress Enter to continue...")
        elif choice == 2:
            clear_screen(); print_banner()
            fp = console.input("[bold green]Video path: [/bold green]").strip()
            crf = console.input("[bold green]CRF value (0-51, default 28): [/bold green]").strip() or "28"
            success, msg = ffmpeg.compress_video(fp, crf)
            if success:
                console.print("[bold green]Video compressed successfully![/bold green]")
            else:
                console.print(f"[bold red]Compression failed: {msg}[/bold red]")
            console.input("\nPress Enter to continue...")
        elif choice == 3:
            clear_screen(); print_banner()
            fp = console.input("[bold green]Video path: [/bold green]").strip()
            fmt = console.input("[bold green]Target format (mp3/wav/flac) [mp3]: [/bold green]").strip().lower() or "mp3"
            success, msg = ffmpeg.extract_audio(fp, fmt)
            if success:
                console.print("[bold green]Audio extracted successfully![/bold green]")
            else:
                console.print(f"[bold red]Extraction failed: {msg}[/bold red]")
            console.input("\nPress Enter to continue...")
        elif choice == 4:
            clear_screen(); print_banner()
            vf = console.input("[bold green]Video path: [/bold green]").strip()
            af = console.input("[bold green]Audio path: [/bold green]").strip()
            success, msg = ffmpeg.merge_video_audio(vf, af)
            if success:
                console.print("[bold green]Media merged successfully![/bold green]")
            else:
                console.print(f"[bold red]Merging failed: {msg}[/bold red]")
            console.input("\nPress Enter to continue...")

def history_logs_flow():
    while True:
        options = [
            "View Download History",
            "View Download Logs",
            "Clear History",
            "Clear Logs",
            "Go Back"
        ]
        choice = run_interactive_selector("History & Logs", options)
        if choice in (-1, 4):
            break
        elif choice == 0:
            clear_screen()
            print_banner()
            history = database.get_history()
            if not history:
                console.print("[bold yellow]History is empty.[/bold yellow]")
            else:
                table = Table(title="Download History")
                table.add_column("ID", justify="center")
                table.add_column("URL", style="cyan")
                table.add_column("Type", style="magenta")
                table.add_column("Size", style="yellow")
                table.add_column("Time", style="green")
                
                for idx, item in enumerate(history, 1):
                    table.add_row(str(idx), item["url"][:40], item["type"], item["size"], item["time"])
                console.print(table)
            console.input("\nPress Enter to continue...")
        elif choice == 1:
            clear_screen()
            print_banner()
            logs = database.get_download_logs()
            if not logs:
                console.print("[bold yellow]No logs recorded yet.[/bold yellow]")
            else:
                table = Table(title="Download logs")
                table.add_column("ID", justify="center")
                table.add_column("Platform", style="yellow")
                table.add_column("Type", style="magenta")
                table.add_column("Quality", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Time", style="dim")
                
                for idx, log in enumerate(logs, 1):
                    status_text = f"[bold green]success[/bold green]" if log["status"] == "success" else f"[bold red]failed[/bold red]"
                    table.add_row(str(idx), log["platform"], log["type"], log["quality"], status_text, log["time"])
                console.print(table)
            console.input("\nPress Enter to continue...")
        elif choice == 2:
            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history")
            conn.commit()
            conn.close()
            console.print("[bold green]History cleared![/bold green]")
            time.sleep(1)
        elif choice == 3:
            database.clear_download_logs()
            console.print("[bold green]Logs cleared![/bold green]")
            time.sleep(1)

def environment_flow():
    clear_screen()
    print_banner()
    console.print("[bold cyan]ENVIRONMENT STATUS[/bold cyan]\n")
    
    env = updater.check_environment()
    
    table = Table(box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Dependency", style="yellow")
    table.add_column("Installed Version / Status", style="cyan")
    
    table.add_row("Python Version", env["python"]["version"])
    
    ytdlp_text = env["yt-dlp"]["version"]
    if not env["yt-dlp"]["ok"]:
         ytdlp_text = "[bold red]MISSING[/bold red]"
    table.add_row("yt-dlp", ytdlp_text)
    
    ffmpeg_text = env["ffmpeg"]["version"]
    if not env["ffmpeg"]["ok"]:
         ffmpeg_text = "[bold red]MISSING[/bold red]"
    table.add_row("FFmpeg", ffmpeg_text)
    
    aria2c_text = env["aria2c"]["version"]
    if not env["aria2c"]["ok"]:
         aria2c_text = "[dim white]Not installed[/dim white]"
    table.add_row("aria2c", aria2c_text)
    
    console.print(table)
    
    console.print("\n[bold yellow]1.[/bold yellow] Update yt-dlp via pip")
    console.print("[bold yellow]0.[/bold yellow] Back")
    
    ch = console.input("\nChoice: ").strip()
    if ch == "1":
        console.print("\nUpdating yt-dlp...")
        success, msg = updater.update_ytdlp()
        if success:
            console.print("[bold green]yt-dlp successfully updated![/bold green]")
        else:
            console.print(f"[bold red]Failed to update: {msg}[/bold red]")
        console.input("\nPress Enter to continue...")

def settings_flow():
    while True:
        options = [
            f"{config.t('settings_download_dir'):<25}: {config.get('download_dir')}",
            f"{config.t('settings_video_quality'):<25}: {config.get('default_video_quality')}",
            f"{config.t('settings_audio_quality'):<25}: {config.get('default_audio_quality')}kbps",
            f"{config.t('settings_max_concurrent'):<25}: {config.get('max_concurrent')}",
            f"{config.t('settings_theme'):<25}: {config.get('theme')}",
            f"{config.t('settings_ffmpeg_warnings'):<25}: {'ON' if config.get('ffmpeg_warnings') else 'OFF'}",
            f"{config.t('settings_auto_rename'):<25}: {'ON' if config.get('auto_rename_duplicates') else 'OFF'}",
            f"{config.t('settings_cookie'):<25}: {config.get('cookie_file') or 'None'}",
            f"{config.t('settings_speed'):<25}: {config.get('speed_limit') or 'Unlimited'}",
            f"{config.t('settings_sound'):<25}: {'ON' if config.get('sound_alerts') else 'OFF'}",
            f"{config.t('settings_notif'):<25}: {'ON' if config.get('notifications') else 'OFF'}",
            f"{config.t('settings_language'):<25}: {config.get('language').upper()}",
            "Go Back"
        ]
        choice = run_interactive_selector("Configure Settings Center", options)
        if choice in (-1, 12):
            break
        elif choice == 0:
            clear_screen(); print_banner()
            p = console.input(f"Enter download directory [{config.get('download_dir')}]: ").strip()
            if p:
                config.set("download_dir", os.path.abspath(p))
                console.print("[bold green]Settings saved.[/bold green]")
                time.sleep(1)
        elif choice == 1:
            qualities = ["best", "2160p", "1440p", "1080p", "720p", "480p", "360p"]
            q_choice = run_interactive_selector("Default Video Quality", qualities)
            if q_choice != -1:
                config.set("default_video_quality", qualities[q_choice])
        elif choice == 2:
            bitrates = ["320", "256", "192", "128", "96"]
            b_choice = run_interactive_selector("Default Audio Bitrate", [f"{b}kbps" for b in bitrates])
            if b_choice != -1:
                config.set("default_audio_quality", bitrates[b_choice])
        elif choice == 3:
            clear_screen(); print_banner()
            m = console.input(f"Enter max concurrent downloads (1-10) [{config.get('max_concurrent')}]: ").strip()
            if m.isdigit() and 1 <= int(m) <= 10:
                config.set("max_concurrent", int(m))
                console.print("[bold green]Settings saved.[/bold green]")
                time.sleep(1)
        elif choice == 4:
            themes_list = list(config.THEMES.keys())
            t_choice = run_interactive_selector("Select Theme", themes_list)
            if t_choice != -1:
                config.set("theme", themes_list[t_choice])
        elif choice == 5:
            config.set("ffmpeg_warnings", not config.get("ffmpeg_warnings"))
        elif choice == 6:
            config.set("auto_rename_duplicates", not config.get("auto_rename_duplicates"))
        elif choice == 7:
            clear_screen(); print_banner()
            fp = console.input("Enter cookie file path: ").strip()
            config.set("cookie_file", fp)
            console.print("[bold green]Settings saved.[/bold green]")
            time.sleep(1)
        elif choice == 8:
            clear_screen(); print_banner()
            s = console.input("Speed limit (e.g. 500K/5M or empty for Unlimited): ").strip()
            config.set("speed_limit", s)
            console.print("[bold green]Settings saved.[/bold green]")
            time.sleep(1)
        elif choice == 9:
            config.set("sound_alerts", not config.get("sound_alerts"))
        elif choice == 10:
            config.set("notifications", not config.get("notifications"))
        elif choice == 11:
            lang = config.get("language")
            new_lang = "es" if lang == "en" else "en"
            config.set("language", new_lang)

def run_cli_dashboard():
    config.load_settings()
    
    # 1. Automatic yt-dlp version check on startup
    clear_screen()
    print_banner()
    console.print("\n[bold info]Checking yt-dlp version...[/bold info]")
    local_v = updater.get_ytdlp_version()
    latest_v = updater.get_latest_ytdlp_version()
    
    console.print(f"  Current: {local_v}")
    console.print(f"  Latest : {latest_v}")
    
    if latest_v != "Unknown" and local_v != latest_v:
        ans = console.input("\n[bold yellow]Update yt-dlp now? (Y/n): [/bold yellow]").strip().lower()
        if ans != 'n':
            console.print("Updating yt-dlp in child process...")
            success, msg = updater.update_ytdlp()
            if success:
                console.print("[bold green]Update successful![/bold green]")
            else:
                console.print(f"[bold red]Update failed: {msg}[/bold red]")
            time.sleep(1.5)
            
    # 2. Animated startup diagnostics verifier
    clear_screen()
    print_banner()
    console.print("\n[bold info]Checking environment dependencies...[/bold info]")
    time.sleep(0.3)
    
    # Check checks
    env = updater.check_environment()
    db_ok = quick_startup_check()
    
    print(f"  [bold green]✓[/bold green] Python ({env['python']['version']})")
    time.sleep(0.2)
    print(f"  [bold green]✓[/bold green] yt-dlp ({env['yt-dlp']['version']})")
    time.sleep(0.2)
    
    ffmpeg_icon = "[bold green]✓[/bold green]" if env["ffmpeg"]["ok"] else "[bold red]✗[/bold red]"
    print(f"  {ffmpeg_icon} FFmpeg")
    time.sleep(0.2)
    
    db_icon = "[bold green]✓[/bold green]" if db_ok else "[bold yellow]⚠[/bold yellow]"
    print(f"  {db_icon} Database")
    time.sleep(0.5)
    
    scheduler.start_scheduler()
    
    try:
        from src.cli.tui import run_tui
        run_tui()
    except KeyboardInterrupt:
        pass
    finally:
        scheduler.stop_scheduler()
