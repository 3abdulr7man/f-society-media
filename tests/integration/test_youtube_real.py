import unittest
import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import database, config
from src.core.platforms.youtube import YouTubePlatformExtractor

@unittest.skipIf(os.getenv("CI") == "true", "Skipping integration test in CI")
class TestYouTubePlatformReal(unittest.TestCase):
    
    def setUp(self):
        database.DB_FILE = "test_f_society_real.db"
        database.init_db()
        config.load_settings()
        self.extractor = YouTubePlatformExtractor()
        self.test_url = "https://youtu.be/2PuFyjAs7JA?si=C-0Y7i6Hyj3vRAlK"

    def test_url_detection(self):
        self.assertTrue(self.extractor.detect(self.test_url))

    def test_metadata_extraction_real(self):
        try:
            meta = self.extractor.extract_metadata(self.test_url)
            self.assertEqual(meta["platform"], "YouTube")
            self.assertIn("title", meta)
            self.assertIn("uploader", meta)
            self.assertTrue(meta["duration"] > 0)
        except Exception as e:
            self.fail(f"Real YouTube Metadata extraction failed: {e}")
            
if __name__ == "__main__":
    unittest.main()
