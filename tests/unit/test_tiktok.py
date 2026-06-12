import unittest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.mocks import ytdlp_mock
from src.core import database, config
from src.core.platforms.tiktok import TikTokPlatformExtractor

class TestTikTokPlatform(unittest.TestCase):
    
    def setUp(self):
        database.DB_FILE = "test_f_society.db"
        database.init_db()
        config.load_settings()
        self.extractor = TikTokPlatformExtractor()
        self.video_url = "https://www.tiktok.com/@user/video/12345"

    def test_url_detection(self):
        self.assertTrue(self.extractor.detect(self.video_url))
        self.assertTrue(self.extractor.detect("https://www.tiktok.com/@user/photo/12345"))
        self.assertFalse(self.extractor.detect("https://youtube.com"))

    def test_metadata_extraction_mocked(self):
        meta = self.extractor.extract_metadata(self.video_url)
        self.assertEqual(meta["platform"], "TikTok")
        self.assertEqual(meta["title"], "Mocked Project Video")
        self.assertEqual(meta["uploader"], "Mock User")

if __name__ == "__main__":
    unittest.main()
