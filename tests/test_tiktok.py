import unittest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import database, config
from src.core.platforms.tiktok import TikTokPlatformExtractor

class TestTikTokPlatform(unittest.TestCase):
    
    def setUp(self):
        database.DB_FILE = "test_f_society.db"
        database.init_db()
        config.load_settings()
        self.extractor = TikTokPlatformExtractor()
        self.video_url = "https://www.tiktok.com/@mostafa.x.syed/video/7645359277888146709?is_from_webapp=1&sender_device=pc&web_id=7561433617462642188"
        self.photo_url = "https://www.tiktok.com/@abdulrahmaaaaan4/photo/7636395024451685650?is_from_webapp=1&sender_device=pc&web_id=7561433617462642188"

    def test_url_detection(self):
        self.assertTrue(self.extractor.detect(self.video_url))
        self.assertTrue(self.extractor.detect(self.photo_url))
        self.assertFalse(self.extractor.detect("https://youtube.com"))

    def test_metadata_extraction_video(self):
        try:
            meta = self.extractor.extract_metadata(self.video_url)
            self.assertEqual(meta["platform"], "TikTok")
            self.assertIn("title", meta)
            self.assertIn("uploader", meta)
        except Exception as e:
            self.fail(f"Video metadata extraction failed: {e}")

    def test_metadata_extraction_photo(self):
        try:
            meta = self.extractor.extract_metadata(self.photo_url)
            self.assertEqual(meta["platform"], "TikTok")
            self.assertIn("title", meta)
            self.assertIn("uploader", meta)
        except Exception as e:
            self.fail(f"Photo metadata extraction failed: {e}")

if __name__ == "__main__":
    unittest.main()
