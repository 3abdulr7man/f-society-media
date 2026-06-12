from abc import ABC, abstractmethod

class BasePlatformExtractor(ABC):
    
    @classmethod
    @abstractmethod
    def detect(cls, url: str) -> bool:
        """Return True if the URL belongs to this platform."""
        pass
        
    @abstractmethod
    def extract_metadata(self, url: str) -> dict:
        """Extract metadata details (title, uploader, duration, formats, thumbnail)."""
        pass
        
    @abstractmethod
    def download(self, url: str, quality_fmt: str, outtmpl: str, progress_hook, force_fallback: bool = False) -> bool:
        """Execute media download."""
        pass
