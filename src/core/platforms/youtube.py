import re
import yt_dlp
from src.core.platforms.base import BasePlatformExtractor
from src.core import config

class YouTubePlatformExtractor(BasePlatformExtractor):
    
    @classmethod
    def detect(cls, url: str) -> bool:
        url_lower = url.lower()
        return any(d in url_lower for d in ["youtube.com", "youtu.be", "m.youtube.com", "music.youtube.com"])
        
    def extract_metadata(self, url: str) -> dict:
        ydl_opts = {'quiet': True, 'no_warnings': True}
        if config.get("cookie_file"):
            ydl_opts['cookiefile'] = config.get("cookie_file")
            
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        return {
            "title": info.get("title", "YouTube Video"),
            "thumbnail": info.get("thumbnail") or (info.get("thumbnails")[-1].get("url") if info.get("thumbnails") else ""),
            "duration": info.get("duration", 0),
            "uploader": info.get("uploader", "Unknown Uploader"),
            "resolution": info.get("resolution") or f"{info.get('width', 'N/A')}x{info.get('height', 'N/A')}",
            "formats": info.get("formats", []),
            "platform": "YouTube"
        }
        
    def download(self, url: str, quality_fmt: str, outtmpl: str, progress_hook, force_fallback: bool = False) -> bool:
        ydl_opts = {
            'format': quality_fmt or "bestvideo+bestaudio/best",
            'outtmpl': outtmpl,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook],
            'noprogress': True
        }
        if config.get("cookie_file"):
            ydl_opts['cookiefile'] = config.get("cookie_file")
            
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
