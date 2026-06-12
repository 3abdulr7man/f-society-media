import unittest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.mocks import ytdlp_mock
from src.core import database, config
from src.core.platforms.youtube import YouTubePlatformExtractor

class TestYouTubePlatform(unittest.TestCase):
    
    def setUp(self):
        database.DB_FILE = "test_f_society.db"
        database.init_db()
        config.load_settings()
        self.extractor = YouTubePlatformExtractor()
        self.test_url = "https://example.com/video.mp4"

    def test_url_detection(self):
        self.assertTrue(self.extractor.detect("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.assertTrue(self.extractor.detect("https://youtu.be/dQw4w9WgXcQ"))
        self.assertFalse(self.extractor.detect("https://tiktok.com"))

    def test_metadata_extraction_mocked(self):
        meta = self.extractor.extract_metadata(self.test_url)
        self.assertEqual(meta["platform"], "YouTube")
        self.assertEqual(meta["title"], "Mocked Project Video")
        self.assertEqual(meta["uploader"], "Mock User")
        self.assertEqual(meta["duration"], 120)
            
if __name__ == "__main__":
    unittest.main()
