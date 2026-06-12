from src.core.platforms.youtube import YouTubePlatformExtractor
from src.core.platforms.tiktok import TikTokPlatformExtractor
from src.core.platforms.instagram import InstagramPlatformExtractor
from src.core.platforms.twitter import TwitterPlatformExtractor

PLATFORMS = [
    YouTubePlatformExtractor,
    TikTokPlatformExtractor,
    InstagramPlatformExtractor,
    TwitterPlatformExtractor
]

def get_extractor(url: str):
    for platform_cls in PLATFORMS:
        if platform_cls.detect(url):
            return platform_cls()
    return None
