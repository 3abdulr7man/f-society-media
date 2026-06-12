import concurrent.futures
from src.core import config, database, downloader
from src.core.logger import log_info, log_success, log_error

class QueueManager:
    def __init__(self):
        self._active = False

    def is_active(self):
        return self._active

    def add_item(self, url, mode, quality=""):
        database.add_to_queue(url, mode, quality)

    def get_items(self):
        return database.get_queue()

    def clear(self):
        database.clear_queue()

    def run(self):
        items = self.get_items()
        if not items:
            return False, "Queue is empty"

        self._active = True
        downloader.is_parallel_batch = True
        log_info(f"\n[Queue] Starting parallel batch of {len(items)} items...")
        
        max_workers = config.get("max_concurrent", 3)
        
        def download_task(item):
            url = item["url"]
            mode = item["mode"]
            quality = item["quality"]
            
            # Update item status in db
            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE queue SET status = 'downloading' WHERE id = ?", (item["id"],))
            conn.commit()
            conn.close()
            
            if mode == "video":
                fmt = downloader.build_format_string(quality)
                success = downloader.download_video_via_api(url, fmt)
            elif mode == "audio":
                success = downloader.download_audio_via_api(url, quality)
            elif mode == "image":
                success = downloader.download_image_gallery_via_api(url)
            else:
                success = False
                
            status_val = "success" if success else "failed"
            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE queue SET status = ? WHERE id = ?", (status_val, item["id"]))
            conn.commit()
            conn.close()
            
            return success
            
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(download_task, items))
            
        downloader.is_parallel_batch = False
        self._active = False
        
        # Clear completed queue items
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM queue WHERE status = 'success'")
        conn.commit()
        conn.close()
        
        success_count = sum(1 for r in results if r)
        log_success(f"\n[Queue] Batch finished! {success_count}/{len(items)} items downloaded successfully.")
        
        if success_count > 0:
            downloader.send_notification("F-Society Queue", f"Batch download finished: {success_count} succeeded.")
            downloader.play_alert_sound()
            
        return True, f"{success_count}/{len(items)} succeeded"
