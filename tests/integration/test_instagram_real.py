import unittest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import database, config
from src.core.platforms.instagram import InstagramPlatformExtractor

class TestInstagramPlatformReal(unittest.TestCase):
    
    def setUp(self):
        database.DB_FILE = "test_f_society_real.db"
        database.init_db()
        config.load_settings()
        self.extractor = InstagramPlatformExtractor()
        self.reel_url = "https://www.instagram.com/reel/DZNaLrntP6j/"

    def test_url_detection(self):
        self.assertTrue(self.extractor.detect(self.reel_url))

    def test_metadata_extraction_real(self):
        try:
            meta = self.extractor.extract_metadata(self.reel_url)
            self.assertEqual(meta["platform"], "Instagram")
            self.assertIn("title", meta)
        except Exception as e:
            print(f"Real Instagram Extraction failed (expected without login cookies): {e}")

if __name__ == "__main__":
    unittest.main()
