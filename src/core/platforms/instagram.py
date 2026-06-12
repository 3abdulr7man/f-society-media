import yt_dlp
from src.core.platforms.base import BasePlatformExtractor
from src.core import config
from src.core.logger import log_error

class InstagramPlatformExtractor(BasePlatformExtractor):
    
    @classmethod
    def detect(cls, url: str) -> bool:
        url_lower = url.lower()
        return "instagram.com" in url_lower
        
    def extract_metadata(self, url: str) -> dict:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        if config.get("cookie_file"):
            ydl_opts['cookiefile'] = config.get("cookie_file")
            
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            return {
                "title": info.get("title") or info.get("description", "Instagram Post")[:50],
                "thumbnail": info.get("thumbnail") or "",
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", "Instagram User"),
                "resolution": info.get("resolution") or "N/A",
                "formats": info.get("formats", []),
                "platform": "Instagram"
            }
        except Exception as e:
            log_error(f"Instagram extraction failed: {e}")
            raise Exception(f"Instagram extraction failed. Cookies might be required. Details: {e}")
            
    def download(self, url: str, quality_fmt: str, outtmpl: str, progress_hook, force_fallback: bool = False) -> bool:
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
            
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
