import os
import sys
import re
import time
import subprocess
import urllib.request
import urllib.parse
import json
import datetime
from pathlib import Path
import threading

from src.core import config, database
from src.core.logger import log_info, log_success, log_warning, log_error
from src.core.platforms import get_extractor

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

print_lock = threading.Lock()
is_parallel_batch = False
_progress_callbacks = []

class DownloaderError(Exception):
    def __init__(self, platform, reason, solution):
        self.platform = platform
        self.reason = reason
        self.solution = solution
        super().__init__(f"[{platform}] {reason} -> Solution: {solution}")

def register_progress_callback(cb):
    if cb not in _progress_callbacks:
        _progress_callbacks.append(cb)

def unregister_progress_callback(cb):
    if cb in _progress_callbacks:
        _progress_callbacks.remove(cb)

def clear_progress_callbacks():
    global _progress_callbacks
    _progress_callbacks = []

def play_alert_sound():
    if not config.get("sound_alerts", True):
        return
    try:
        if sys.platform == "win32":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        else:
            sys.stdout.write('\a')
            sys.stdout.flush()
    except:
        pass

def send_notification(title, message):
    if not config.get("notifications", True):
        return
    try:
        title = title.replace('"', '\\"').replace("'", "\\'")
        message = message.replace('"', '\\"').replace("'", "\\'")
        if sys.platform == "win32":
            ps_code = f"""
            [void] [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms')
            $notification = New-Object System.Windows.Forms.NotifyIcon
            $notification.Icon = [System.Drawing.SystemIcons]::Information
            $notification.BalloonTipTitle = '{title}'
            $notification.BalloonTipText = '{message}'
            $notification.Visible = $True
            $notification.ShowBalloonTip(5000)
            """
            subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "-Command", ps_code], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform == "darwin":
            cmd = f'display notification "{message}" with title "{title}"'
            subprocess.Popen(["osascript", "-e", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["notify-send", title, message], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

def validate_url(url):
    url = url.strip()
    if not url:
        return False
    patterns = [r'^https?://', r'^www\.']
    for p in patterns:
        if re.match(p, url, re.IGNORECASE):
            return True
    if re.search(r'\.(mp4|webm|mkv|avi|mov|flv|m3u8|ts)$', url, re.IGNORECASE):
        return True
    return False

def format_size(bytes_val):
    if not bytes_val or bytes_val == 0:
        return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.2f} PB"

def format_duration(seconds):
    if not seconds:
        return "Unknown"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m {s}s" if h else (f"{m}m {s}s" if m else f"{s}s")

def format_time(t_str):
    try:
        dt = datetime.datetime.fromisoformat(t_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return t_str

def detect_platform(url):
    extractor = get_extractor(url)
    if extractor:
        # Detect name from class
        name = extractor.__class__.__name__.replace("PlatformExtractor", "")
        if name == "YouTube": return "YouTube"
        if name == "TikTok": return "TikTok"
        if name == "Instagram": return "Instagram"
        if name == "Twitter": return "Twitter/X"
        return name
    
    # Fallback platform detectors
    url_lower = url.lower()
    platforms = {
        "facebook.com": "Facebook", "fb.watch": "Facebook",
        "vimeo.com": "Vimeo", "soundcloud.com": "SoundCloud",
        "reddit.com": "Reddit",
    }
    for domain, name in platforms.items():
        if domain in url_lower:
            return name
            
    ext_match = re.search(r'\.(mp4|webm|mkv|avi|mov|flv|m3u8|ts|mp3|wav|flac|ogg|m4a)$', url_lower)
    if ext_match:
        return f"Direct Link (.{ext_match.group(1)})"
        
    return "Unknown"

def detect_content_type(url):
    url_lower = url.lower()
    playlist_patterns = [r'[?&]list=', r'/playlist/', r'/playlists/', r'/set/', r'spotify\.com/playlist/']
    for p in playlist_patterns:
        if re.search(p, url_lower):
            return "playlist"
    channel_patterns = [r'/channel/', r'/c/', r'/user/', r'/@', r'youtube\.com/@']
    for p in channel_patterns:
        if re.search(p, url_lower):
            return "channel"
    image_patterns = [r'instagram\.com/p/', r'instagram\.com/reel/', r'tiktok\.com/.*/photo/']
    for p in image_patterns:
        if re.search(p, url_lower):
            return "image_or_gallery"
    audio_platforms = ["soundcloud.com", "bandcamp.com", "audiomack.com"]
    for d in audio_platforms:
        if d in url_lower:
            return "audio"
    return "video"

def fetch_video_info(url):
    extractor = get_extractor(url)
    if extractor:
        try:
            return extractor.extract_metadata(url), None
        except Exception as e:
            return None, str(e)
            
    # Fallback to standard yt-dlp
    if not yt_dlp:
        return None, "yt-dlp is not installed"
    try:
        ydl_opts = {'quiet': True, 'no_warnings': True}
        if config.get("cookie_file"):
            ydl_opts['cookiefile'] = config.get("cookie_file")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info, None
    except Exception as e:
        return None, str(e)

def build_format_string(quality):
    quality_map = {
        "144p": "bestvideo[height<=144]+bestaudio/best",
        "240p": "bestvideo[height<=240]+bestaudio/best",
        "360p": "bestvideo[height<=360]+bestaudio/best",
        "480p": "bestvideo[height<=480]+bestaudio/best",
        "720p": "bestvideo[height<=720]+bestaudio/best",
        "1080p": "bestvideo[height<=1080]+bestaudio/best",
        "1440p": "bestvideo[height<=1440]+bestaudio/best",
        "2160p": "bestvideo[height<=2160]+bestaudio/best",
        "best": "bestvideo+bestaudio/best",
    }
    quality_num_map = {
        "1": "144p", "2": "240p", "3": "360p", "4": "480p",
        "5": "720p", "6": "1080p", "7": "1440p", "8": "2160p", "9": "best",
    }
    if quality in quality_num_map:
        quality = quality_num_map[quality]
    return quality_map.get(quality, quality_map["best"])

def progress_hook(d):
    global is_parallel_batch
    try:
        status = d['status']
        filename = Path(d.get('filename', 'video')).name
        
        if status == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            speed = d.get('speed')
            eta = d.get('eta')
            
            percent = (downloaded / total * 100) if total > 0 else 0
            percent = min(100.0, percent)
            
            speed_str = format_speed(speed)
            eta_str = f"{eta}s" if eta is not None else "N/A"
            downloaded_str = format_size(downloaded)
            total_str = format_size(total) if total > 0 else "Unknown"
            
            for cb in _progress_callbacks:
                try:
                    cb(percent, speed_str, eta_str, downloaded_str, total_str, "downloading", filename)
                except:
                    pass
            
            if not _progress_callbacks:
                if is_parallel_batch:
                    with print_lock:
                        print(f"\r{config.c('cyan')}[Queue] {filename[:25]}... | {percent:.1f}% | {speed_str} | ETA: {eta_str}{config.C.RESET}", end="", flush=True)
                else:
                    bar_len = 25
                    filled = int(bar_len * percent / 100)
                    bar = '█' * filled + '░' * (bar_len - filled)
                    with print_lock:
                        sys.stdout.write(f"\r{config.c('cyan')}[{bar}] {percent:.1f}% | Speed: {speed_str} | ETA: {eta_str} | {downloaded_str}/{total_str}{config.C.RESET}")
                        sys.stdout.flush()
        elif status == 'finished':
            for cb in _progress_callbacks:
                try:
                    cb(100.0, "0 B/s", "0s", "Done", "Done", "finished", filename)
                except:
                    pass
            if not _progress_callbacks:
                if not is_parallel_batch:
                    with print_lock:
                        sys.stdout.write("\n")
                        log_success(f"Finished downloading: {filename}")
    except Exception:
        pass

def format_speed(bps):
    if bps is None:
        return "N/A"
    for unit in ['B/s', 'KB/s', 'MB/s', 'GB/s']:
        if bps < 1024:
            return f"{bps:.1f} {unit}"
        bps /= 1024
    return f"{bps:.1f} TB/s"

def get_ydl_opts(media_type, quality_fmt=None, filename_override=None):
    ydl_opts = {
        'noprogress': True,
        'progress_hooks': [progress_hook],
        'quiet': True,
        'no_warnings': True,
    }
    
    limit = config.get("speed_limit")
    if limit:
        # Parse speed limit
        match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMG]?)$', str(limit).strip().upper())
        if match:
            val, unit = match.groups()
            multiplier = {"": 1, "K": 1024, "M": 1024 * 1024, "G": 1024 * 1024 * 1024}.get(unit, 1)
            ydl_opts['ratelimit'] = int(float(val) * multiplier)
        
    if config.get("cookie_file"):
        ydl_opts['cookiefile'] = config.get("cookie_file")
        
    ydl_opts['concurrent_fragment_downloads'] = 8
    
    if media_type == "video":
        ydl_opts['format'] = quality_fmt or "bestvideo+bestaudio/best"
        ydl_opts['merge_output_format'] = "mp4"
    elif media_type == "audio":
        ydl_opts['format'] = "bestaudio/best"
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality_fmt or config.get("default_audio_quality"),
        }, {
            'key': 'FFmpegMetadata',
            'add_metadata': True,
        }, {
            'key': 'EmbedThumbnail',
        }]
        
    if filename_override:
        ydl_opts['outtmpl'] = filename_override
    else:
        ydl_opts['outtmpl'] = str(Path(config.get("download_dir")) / config.get("output_template"))
        
    return ydl_opts

def handle_downloader_exception(url, err_msg):
    platform = detect_platform(url)
    log_error(f"Downloader failed for [{platform}] {url}: {err_msg}")
    
    # Format specific recommendations
    if platform == "TikTok":
        raise DownloaderError("TikTok", "Extraction failed (Rehydration error / universal extraction block).", "Update yt-dlp via update checks, or use the built-in TikWM fallback.")
    elif platform == "Instagram":
        raise DownloaderError("Instagram", "Bot/Auth login verification required.", "Add cookies via Settings Chrome/Edge cookies import.")
    elif platform == "YouTube":
        raise DownloaderError("YouTube", "Video unavailable / Bot detection block.", "Update yt-dlp version, or configure custom cookies.")
    else:
        raise DownloaderError(platform, f"Download failed: {err_msg}", "Check internet access or run `fs --doctor` to check system readiness.")

def download_video_via_api(url, quality_fmt=None, retries=3, force_fallback=False):
    platform = detect_platform(url)
    try:
        extractor = get_extractor(url)
        title = "video"
        
        # Determine expected output filename
        out_dir = Path(config.get("download_dir"))
        if extractor:
            try:
                meta = extractor.extract_metadata(url)
                title = meta.get("title", "video")
            except Exception as meta_err:
                handle_downloader_exception(url, str(meta_err))
        else:
            info, err = fetch_video_info(url)
            if info:
                title = info.get("title", "video")
            else:
                handle_downloader_exception(url, err or "Metadata fetch failed")
                
        title = re.sub(r'[\\/*?:"<>|]', "", title)
        expected_filename = str(out_dir / f"{title}.mp4")
        
        # Handle auto renaming
        auto_rename = config.get("auto_rename_duplicates", True)
        if auto_rename and os.path.exists(expected_filename):
            stem = Path(expected_filename).stem
            counter = 1
            while os.path.exists(str(out_dir / f"{stem} ({counter}).mp4")):
                counter += 1
            expected_filename = str(out_dir / f"{stem} ({counter}).mp4")
            
        success = False
        if extractor:
            success = extractor.download(url, quality_fmt, expected_filename, progress_hook, force_fallback=force_fallback)
        else:
            # Fallback to standard yt-dlp download
            ydl_opts = get_ydl_opts("video", quality_fmt, expected_filename)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            success = True
            
        if success:
            database.add_download_log(url, "video", quality_fmt or "best", "success", platform)
            database.add_history(url, "video", quality_fmt or "best", format_size(Path(expected_filename).stat().st_size if Path(expected_filename).exists() else 0), platform)
            play_alert_sound()
            send_notification(config.t("download_completed"), title)
            return True
        else:
            raise Exception("Extractor returned failure status")
            
    except Exception as e:
        database.add_download_log(url, "video", quality_fmt or "best", "failed", platform)
        handle_downloader_exception(url, str(e))

def download_audio_via_api(url, bitrate=None, retries=3):
    platform = detect_platform(url)
    try:
        extractor = get_extractor(url)
        title = "audio"
        out_dir = Path(config.get("download_dir"))
        
        if extractor:
            try:
                meta = extractor.extract_metadata(url)
                title = meta.get("title", "audio")
            except Exception as meta_err:
                handle_downloader_exception(url, str(meta_err))
        else:
            info, err = fetch_video_info(url)
            if info:
                title = info.get("title", "audio")
            else:
                handle_downloader_exception(url, err or "Metadata fetch failed")
                
        title = re.sub(r'[\\/*?:"<>|]', "", title)
        expected_filename = str(out_dir / f"{title}.mp3")
        
        auto_rename = config.get("auto_rename_duplicates", True)
        if auto_rename and os.path.exists(expected_filename):
            stem = Path(expected_filename).stem
            counter = 1
            while os.path.exists(str(out_dir / f"{stem} ({counter}).mp3")):
                counter += 1
            expected_filename = str(out_dir / f"{stem} ({counter}).mp3")
            
        path_obj = Path(expected_filename)
        outtmpl = str(path_obj.with_suffix('.%(ext)s'))
        
        success = False
        if extractor:
            success = extractor.download(url, "bestaudio/best", outtmpl, progress_hook)
            # Extractor downloads raw formats, we need post-processing if it's fallback
            if success and not os.path.exists(expected_filename):
                # Fallback downloaded the file as video (or standard), let's rename or let FFmpeg extract audio
                from src.core import ffmpeg as core_ffmpeg
                raw_file = outtmpl.replace(".%(ext)s", ".mp4")
                if os.path.exists(raw_file):
                    core_ffmpeg.extract_audio(raw_file, "mp3")
                    # Clean up
                    try: os.remove(raw_file)
                    except: pass
                    # Rename
                    extracted_file = str(Path(config.get("download_dir")) / "audio_extracted.mp3")
                    if os.path.exists(extracted_file):
                        if os.path.exists(expected_filename):
                            os.remove(expected_filename)
                        os.rename(extracted_file, expected_filename)
        else:
            ydl_opts = get_ydl_opts("audio", bitrate, outtmpl)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            success = True
            
        if success:
            database.add_download_log(url, "audio", f"{bitrate or config.get('default_audio_quality')}kbps", "success", platform)
            database.add_history(url, "audio", f"{bitrate or config.get('default_audio_quality')}kbps", format_size(Path(expected_filename).stat().st_size if Path(expected_filename).exists() else 0), platform)
            play_alert_sound()
            send_notification(config.t("audio_completed"), title)
            return True
        else:
            raise Exception("Extractor returned failure status")
    except Exception as e:
        database.add_download_log(url, "audio", f"{bitrate or config.get('default_audio_quality')}kbps", "failed", platform)
        handle_downloader_exception(url, str(e))

def download_image_gallery_via_api(url, retries=3):
    platform = detect_platform(url)
    try:
        extractor = get_extractor(url)
        success = False
        if extractor:
            # outtmpl mock
            outtmpl = str(Path(config.get("download_dir")) / "%(title)s.%(ext)s")
            success = extractor.download(url, None, outtmpl, progress_hook)
        else:
            # Fallback direct download
            info, err = fetch_video_info(url)
            if not info:
                handle_downloader_exception(url, err or "Metadata fetch failed")
            title = info.get("title", "gallery")
            title = re.sub(r'[\\/*?:"<>|]', "", title)
            outtmpl = str(Path(config.get("download_dir")) / f"{title}_img_%(id)s.%(ext)s")
            ydl_opts = get_ydl_opts("image", None, outtmpl)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            success = True
            
        if success:
            database.add_download_log(url, "images", "gallery", "success", platform)
            database.add_history(url, "images", "gallery", "multiple", platform)
            play_alert_sound()
            send_notification(config.t("images_completed"), "Photos")
            return True
        else:
            raise Exception("Download returned failure status")
    except Exception as e:
        database.add_download_log(url, "images", "gallery", "failed", platform)
        handle_downloader_exception(url, str(e))

def download_playlist_via_api(url, quality="best"):
    platform = detect_platform(url)
    try:
        log_info(f"Downloading playlist ({quality})...")
        playlist_output = str(Path(config.get("download_dir")) / "%(playlist_title)s" / "%(playlist_index)s - %(title)s.%(ext)s")
        ydl_opts = get_ydl_opts("video", quality, playlist_output)
        ydl_opts['noplaylist'] = False
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        database.add_download_log(url, "playlist", quality, "success", platform)
        database.add_history(url, "playlist", quality, "playlist", platform)
        log_success(config.t("playlist_completed"))
        play_alert_sound()
        send_notification(config.t("playlist_completed"), url[:30])
        return True
    except Exception as e:
        database.add_download_log(url, "playlist", quality, "failed", platform)
        handle_downloader_exception(url, str(e))

def download_channel_via_api(url, max_videos=20, quality="best"):
    platform = detect_platform(url)
    try:
        log_info(f"Downloading channel (max {max_videos})...")
        channel_output = str(Path(config.get("download_dir")) / "%(channel)s" / "%(title)s.%(ext)s")
        ydl_opts = get_ydl_opts("video", quality, channel_output)
        ydl_opts['playlistend'] = int(max_videos)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        database.add_download_log(url, "channel", quality, "success", platform)
        database.add_history(url, "channel", quality, f"{max_videos} videos", platform)
        log_success(config.t("channel_completed"))
        play_alert_sound()
        send_notification(config.t("channel_completed"), url[:30])
        return True
    except Exception as e:
        database.add_download_log(url, "channel", quality, "failed", platform)
        handle_downloader_exception(url, str(e))
