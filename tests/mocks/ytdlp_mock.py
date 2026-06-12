import os
import yt_dlp

CI_MODE = os.getenv("CI", "false") == "true"

def mock_extract_info(self, url, *args, **kwargs):
    # Determine platform based on URL to return suitable mock metadata
    platform = "Direct Link"
    if "youtube.com" in url or "youtu.be" in url or "example.com" in url:
        platform = "YouTube"
    elif "tiktok.com" in url:
        platform = "TikTok"
    elif "instagram.com" in url:
        platform = "Instagram"
    elif "twitter.com" in url or "x.com" in url:
        platform = "Twitter"

    return {
        "id": "12345",
        "title": "Mocked Project Video",
        "uploader": "Mock User",
        "duration": 120,
        "url": url,
        "extractor": platform,
        "formats": [{"url": "https://example.com/video.mp4", "ext": "mp4"}],
        "entries": [],
    }

# Monkeypatch the real YoutubeDL.extract_info method globally for tests
yt_dlp.YoutubeDL.extract_info = mock_extract_info
