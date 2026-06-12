import unittest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import database, config
from src.core.platforms.tiktok import TikTokPlatformExtractor

class TestTikTokPlatformReal(unittest.TestCase):
    
    def setUp(self):
        database.DB_FILE = "test_f_society_real.db"
        database.init_db()
        config.load_settings()
        self.extractor = TikTokPlatformExtractor()
        self.video_url = "https://www.tiktok.com/@mostafa.x.syed/video/7645359277888146709?is_from_webapp=1&sender_device=pc&web_id=7561433617462642188"

    def test_url_detection(self):
        self.assertTrue(self.extractor.detect(self.video_url))

    def test_metadata_extraction_real_video(self):
        try:
            meta = self.extractor.extract_metadata(self.video_url)
            self.assertEqual(meta["platform"], "TikTok")
            self.assertIn("title", meta)
            self.assertIn("uploader", meta)
        except Exception as e:
            self.fail(f"Real TikTok Video metadata extraction failed: {e}")

if __name__ == "__main__":
    unittest.main()
