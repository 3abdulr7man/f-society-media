import os
import re
import json
import urllib.request
import urllib.parse
from pathlib import Path
import yt_dlp

from src.core.platforms.base import BasePlatformExtractor
from src.core import config
from src.core.logger import log_info, log_success, log_warning, log_error

class TikTokPlatformExtractor(BasePlatformExtractor):
    
    @classmethod
    def detect(cls, url: str) -> bool:
        url_lower = url.lower()
        return any(d in url_lower for d in ["tiktok.com", "vm.tiktok.com"])
        
    def extract_metadata(self, url: str) -> dict:
        # Try yt-dlp first
        try:
            ydl_opts = {'quiet': True, 'no_warnings': True}
            if config.get("cookie_file"):
                ydl_opts['cookiefile'] = config.get("cookie_file")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title", "TikTok Post"),
                "thumbnail": info.get("thumbnail") or "",
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", "TikTok User"),
                "resolution": info.get("resolution") or "N/A",
                "formats": info.get("formats", []),
                "platform": "TikTok",
                "type": "video",
                "is_fallback": False
            }
        except Exception as e:
            log_warning(f"yt-dlp TikTok extraction failed: {e}. Trying TikWM API fallback...")
            
        # Try TikWM API Fallback
        try:
            api_data = self._query_tikwm_api(url)
            if not api_data:
                raise Exception("TikWM API returned no data")
                
            title = api_data.get("title") or "TikTok Post"
            images = api_data.get("images")
            
            return {
                "title": title,
                "thumbnail": api_data.get("cover") or "",
                "duration": api_data.get("duration", 0),
                "uploader": api_data.get("author", {}).get("nickname") or "TikTok User",
                "resolution": "N/A",
                "formats": [],
                "platform": "TikTok",
                "type": "images" if images else "video",
                "is_fallback": True,
                "api_data": api_data
            }
        except Exception as fallback_err:
            log_error(f"TikWM Fallback failed: {fallback_err}")
            raise Exception(f"Failed to extract TikTok media: {fallback_err}")

    def download(self, url: str, quality_fmt: str, outtmpl: str, progress_hook, force_fallback: bool = False) -> bool:
        # We need to perform extract_metadata first to know if we need fallback
        try:
            meta = self.extract_metadata(url)
        except Exception as e:
            log_error(f"TikTok download failed during metadata phase: {e}")
            return False
            
        if not force_fallback and not meta.get("is_fallback"):
            # Standard yt-dlp download
            ydl_opts = {
                'format': quality_fmt or "best",
                'outtmpl': outtmpl,
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [progress_hook],
                'noprogress': True
            }
            if config.get("cookie_file"):
                ydl_opts['cookiefile'] = config.get("cookie_file")
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                return True
            except Exception as e:
                log_warning(f"yt-dlp download failed: {e}. Trying TikWM fallback download...")
                # Try fallback download below
                
        # Fallback Download using TikWM API data
        try:
            api_data = meta.get("api_data") or self._query_tikwm_api(url)
            if not api_data:
                return False
                
            images = api_data.get("images")
            title = api_data.get("title") or "tiktok_post"
            title = re.sub(r'[\\/*?:"<>|]', "", title)[:50]
            
            if images:
                # Download slides
                log_success(f"Downloading {len(images)} slideshow images...")
                out_dir = Path(config.get("download_dir"))
                for idx, img_url in enumerate(images, 1):
                    # Guess extension
                    ext = "jpg"
                    if ".png" in img_url: ext = "png"
                    elif ".webp" in img_url: ext = "webp"
                    
                    filepath = out_dir / f"{title}_{idx}.{ext}"
                    req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req) as res:
                        with open(filepath, "wb") as f:
                            f.write(res.read())
                    log_info(f"  [{idx}/{len(images)}] Saved: {filepath.name}")
                return True
            else:
                # Download watermark-free video
                video_url = api_data.get("play") or api_data.get("wmplay")
                if not video_url:
                    return False
                    
                # Setup output template path
                # outtmpl could be like D:\Downloads\%(title)s.%(ext)s or direct filepath
                out_path = outtmpl.replace("%(title)s", title).replace("%(ext)s", "mp4")
                if out_path.endswith(".%(ext)s"):
                    out_path = out_path[:-8] + ".mp4"
                
                log_info(f"Downloading direct watermark-free video to: {out_path}")
                req = urllib.request.Request(video_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req) as res:
                    # To mock progress hook for fallback
                    content_len = int(res.headers.get('content-length', 0))
                    chunk_size = 1024 * 64
                    downloaded = 0
                    
                    with open(out_path, "wb") as f:
                        while True:
                            chunk = res.read(chunk_size)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Fire mock progress hook callback
                            if progress_hook and content_len > 0:
                                progress_hook({
                                    'status': 'downloading',
                                    'downloaded_bytes': downloaded,
                                    'total_bytes': content_len,
                                    'filename': out_path,
                                    'speed': 1024 * 1024, # dummy 1MB/s
                                    'eta': 5
                                })
                if progress_hook:
                    progress_hook({'status': 'finished', 'filename': out_path})
                return True
        except Exception as err:
            log_error(f"Fallback download failed: {err}")
            return False

    def _query_tikwm_api(self, url: str) -> dict:
        api_url = "https://www.tikwm.com/api/"
        data = urllib.parse.urlencode({"url": url}).encode("utf-8")
        req = urllib.request.Request(api_url, data=data, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as res:
            response = json.loads(res.read().decode("utf-8"))
        return response.get("data")
