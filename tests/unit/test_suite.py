import unittest
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import database, config, downloader, ffmpeg

class TestFSocietyCore(unittest.TestCase):
    
    def setUp(self):
        # Use a temporary database for testing
        database.DB_FILE = "test_f_society.db"
        database.init_db()
        config.load_settings()
        
    def tearDown(self):
        if os.path.exists("test_f_society.db"):
            try:
                os.remove("test_f_society.db")
            except:
                pass

    def test_database_initialization(self):
        # Verify db is created and tables exist
        self.assertTrue(os.path.exists("test_f_society.db"))
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cursor.fetchall()]
        conn.close()
        self.assertIn("downloads", tables)
        self.assertIn("history", tables)
        self.assertIn("queue", tables)
        self.assertIn("settings", tables)

    def test_url_validation(self):
        self.assertTrue(downloader.validate_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.assertTrue(downloader.validate_url("http://youtube.com/embed/dQw4w9WgXcQ"))
        self.assertTrue(downloader.validate_url("https://tiktok.com/@user/photo/12345"))
        self.assertFalse(downloader.validate_url("youtube.com"))
        self.assertFalse(downloader.validate_url("invalid-url"))

    def test_platform_detection(self):
        self.assertEqual(downloader.detect_platform("https://www.youtube.com/watch?v=123"), "YouTube")
        self.assertEqual(downloader.detect_platform("https://tiktok.com/@user/photo/123"), "TikTok")
        self.assertEqual(downloader.detect_platform("https://instagram.com/p/123"), "Instagram")
        self.assertEqual(downloader.detect_platform("https://unknownsite.com/media/file.mp4"), "Direct Link (.mp4)")

    def test_config_get_set(self):
        config.set("default_video_quality", "720p")
        self.assertEqual(config.get("default_video_quality"), "720p")
        
        # Verify persistence inside testing DB
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'default_video_quality'")
        val = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(val, "720p")

if __name__ == "__main__":
    unittest.main()
