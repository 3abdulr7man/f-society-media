import unittest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.mocks import ytdlp_mock
from src.core import database, config
from src.core.platforms.instagram import InstagramPlatformExtractor

class TestInstagramPlatform(unittest.TestCase):
    
    def setUp(self):
        database.DB_FILE = "test_f_society.db"
        database.init_db()
        config.load_settings()
        self.extractor = InstagramPlatformExtractor()
        self.reel_url = "https://www.instagram.com/reel/DZNaLrntP6j/"

    def test_url_detection(self):
        self.assertTrue(self.extractor.detect(self.reel_url))
        self.assertTrue(self.extractor.detect("https://www.instagram.com/p/DZdVhVSiJ8H/"))
        self.assertFalse(self.extractor.detect("https://youtube.com"))

    def test_metadata_extraction_mocked(self):
        meta = self.extractor.extract_metadata(self.reel_url)
        self.assertEqual(meta["platform"], "Instagram")
        self.assertEqual(meta["title"], "Mocked Project Video")

if __name__ == "__main__":
    unittest.main()
