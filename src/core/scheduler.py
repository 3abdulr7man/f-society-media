import time
import datetime
import threading
from src.core import downloader, config
from src.core.logger import log_info, log_success, log_error

scheduled_jobs = []
scheduler_running = True
scheduler_thread = None

def execute_scheduled_job(job):
    log_info(f"\n[Scheduler] Starting scheduled job: {job['url']}")
    job["status"] = "running"
    
    mode = job["mode"]
    url = job["url"]
    quality = job["quality"]
    
    if mode == "video":
        fmt = downloader.build_format_string(quality)
        success = downloader.download_video_via_api(url, fmt)
    elif mode == "audio":
        success = downloader.download_audio_via_api(url, quality)
    elif mode == "image":
        success = downloader.download_image_gallery_via_api(url)
    else:
        success = False
        
    job["status"] = "success" if success else "failed"
    
    if success:
        log_success(f"[Scheduler] Job finished successfully: {url}")
    else:
        log_error(f"[Scheduler] Job failed: {url}")

def run_scheduler_loop():
    global scheduler_running, scheduled_jobs
    while scheduler_running:
        now = datetime.datetime.now()
        for job in scheduled_jobs:
            if job["status"] == "pending" and now >= job["target_time"]:
                job["status"] = "running"
                t_run = threading.Thread(target=execute_scheduled_job, args=(job,), daemon=True)
                t_run.start()
        time.sleep(5)

def start_scheduler():
    global scheduler_thread, scheduler_running
    scheduler_running = True
    if scheduler_thread is None or not scheduler_thread.is_alive():
        scheduler_thread = threading.Thread(target=run_scheduler_loop, daemon=True)
        scheduler_thread.start()

def stop_scheduler():
    global scheduler_running
    scheduler_running = False

def schedule_job(url, mode, quality, target_time):
    job_id = str(len(scheduled_jobs) + 1)
    job = {
        "id": job_id,
        "url": url,
        "mode": mode,
        "quality": quality,
        "target_time": target_time,
        "status": "pending"
    }
    scheduled_jobs.append(job)
    return job_id

def get_jobs():
    return scheduled_jobs

def cancel_job(job_id):
    for job in scheduled_jobs:
        if job["id"] == job_id:
            job["status"] = "cancelled"
            return True
    return False
