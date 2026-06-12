import os
import sys
import shutil
import socket
import urllib.request
import sqlite3
import datetime
from pathlib import Path

from src.core import config, database, updater, ffmpeg
from src.core.logger import log_info, log_success, log_warning, log_error

class SystemDiagnostics:
    def __init__(self):
        self.report_data = []
        try:
            config.load_settings()
        except Exception:
            pass

    def log_report(self, section, key, status, details=""):
        self.report_data.append({
            "section": section,
            "key": key,
            "status": status,
            "details": details
        })

    # 1. Python Environment Check
    def check_python(self):
        log_info("Checking Python Environment...")
        ver = updater.get_python_version()
        in_venv = sys.prefix != sys.base_prefix
        
        log_success(f"  ✓ Python version: {ver}")
        self.log_report("Python", "Version", "OK", ver)
        
        venv_status = "Active" if in_venv else "Not in venv"
        if in_venv:
            log_success(f"  ✓ Virtual Environment: Active ({sys.prefix})")
        else:
            log_warning("  ⚠ Virtual Environment: Not active")
        self.log_report("Python", "Venv", "OK" if in_venv else "WARNING", venv_status)
        
        # Check required packages
        if os.getenv("CI") == "true":
            packages = ["yt_dlp", "rich", "textual"]
        else:
            packages = ["yt_dlp", "rich", "PySide6", "textual"]
            
        missing = []
        for pkg in packages:
            try:
                __import__(pkg)
            except ImportError:
                missing.append(pkg)
                
        if not missing:
            log_success("  ✓ All required Python packages installed")
            self.log_report("Python", "Packages", "OK", "All packages present")
        else:
            log_error(f"  ✗ Missing packages: {', '.join(missing)}")
            self.log_report("Python", "Packages", "FAILED", f"Missing: {missing}")
        return len(missing) == 0

    # 2. yt-dlp check
    def check_ytdlp(self):
        log_info("Checking yt-dlp engine...")
        env = updater.check_environment()
        ytdlp = env["yt-dlp"]
        
        if ytdlp["ok"]:
            local_ver = ytdlp["version"]
            log_success(f"  ✓ Installed: {local_ver}")
            self.log_report("yt-dlp", "Installation", "OK", local_ver)
            
            # Fetch latest
            latest = updater.get_latest_ytdlp_version()
            if latest != "Unknown":
                if local_ver != latest:
                    log_warning(f"  ⚠ Update available: {latest} (Current: {local_ver})")
                    self.log_report("yt-dlp", "Updates", "WARNING", f"New version available: {latest}")
                else:
                    log_success("  ✓ Version is up to date")
                    self.log_report("yt-dlp", "Updates", "OK", "Latest version active")
            else:
                log_warning("  ⚠ Could not fetch latest version (Network issue)")
                self.log_report("yt-dlp", "Updates", "UNKNOWN", "Failed to check PyPI version")
            return True
        else:
            log_error("  ✗ yt-dlp binary is missing or not in PATH!")
            self.log_report("yt-dlp", "Installation", "FAILED", "Missing")
            return False

    # 3. FFmpeg Check
    def check_ffmpeg(self):
        log_info("Checking FFmpeg & FFprobe binaries...")
        if os.getenv("CI") == "true":
            log_success("  ✓ CI environment detected: skipping FFmpeg checks")
            self.log_report("FFmpeg", "ffmpeg", "SKIPPED", "Skipped in CI")
            return True

        ffmpeg_ok = updater.check_command("ffmpeg")
        ffprobe_ok = updater.check_command("ffprobe")
        
        if ffmpeg_ok:
            log_success("  ✓ ffmpeg: Installed")
            self.log_report("FFmpeg", "ffmpeg", "OK", "Installed")
        else:
            log_error("  ✗ ffmpeg: Missing")
            self.log_report("FFmpeg", "ffmpeg", "FAILED", "Missing")
            
        if ffprobe_ok:
            log_success("  ✓ ffprobe: Installed")
            self.log_report("FFmpeg", "ffprobe", "OK", "Installed")
        else:
            log_error("  ✗ ffprobe: Missing")
            self.log_report("FFmpeg", "ffprobe", "FAILED", "Missing")
            
        return ffmpeg_ok and ffprobe_ok

    # 4. Database Check
    def check_database(self):
        log_info("Checking SQLite Database...")
        db_file = database.DB_FILE
        db_exists = os.path.exists(db_file)
        
        if not db_exists:
            log_warning("  ⚠ Database file missing. Attempting auto-rebuild...")
            try:
                database.init_db()
                log_success("  ✓ Database initialized successfully!")
                self.log_report("Database", "File", "REPAIRED", "Recreated successfully")
            except Exception as e:
                log_error(f"  ✗ Failed to initialize database: {e}")
                self.log_report("Database", "File", "FAILED", str(e))
                return False
        else:
            log_success(f"  ✓ Database file exists: {db_file}")
            self.log_report("Database", "File", "OK", db_file)
            
        # Verify connectivity & read/write
        try:
            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cursor.fetchall()]
            
            required = ["downloads", "history", "queue", "settings"]
            missing = [t for t in required if t not in tables]
            
            if not missing:
                log_success("  ✓ Database schema verified")
                self.log_report("Database", "Schema", "OK", "All tables present")
            else:
                log_warning(f"  ⚠ Missing tables: {missing}. Repairing schema...")
                database.init_db()
                self.log_report("Database", "Schema", "REPAIRED", f"Reconstructed tables: {missing}")
                
            # Test write
            cursor.execute("INSERT OR REPLACE INTO preferences (key, value) VALUES ('diag_test', '1')")
            conn.commit()
            cursor.execute("SELECT value FROM preferences WHERE key = 'diag_test'")
            val = cursor.fetchone()[0]
            conn.close()
            
            if val == '1':
                log_success("  ✓ Database read/write verified")
                self.log_report("Database", "Read/Write", "OK", "Verified")
                return True
            else:
                raise Exception("Write validation failed")
        except Exception as e:
            log_error(f"  ✗ Database check failed: {e}. Attempting database repair...")
            self.log_report("Database", "Check", "FAILED", str(e))
            # Try repair
            try:
                if os.path.exists(db_file):
                    os.remove(db_file)
                database.init_db()
                log_success("  ✓ Database fully repaired and reinitialized!")
                return True
            except Exception as repair_err:
                log_error(f"  ✗ Repair failed: {repair_err}")
                return False

    # 5. Storage Check
    def check_storage(self):
        log_info("Checking Storage details...")
        download_dir_val = config.get("download_dir")
        if not download_dir_val:
            download_dir_val = str(Path.home() / "Downloads" / "F-SOCIETY")
        dl_dir = Path(download_dir_val)
        
        if not dl_dir.exists():
            log_warning(f"  ⚠ Download folder does not exist. Attempting creation...")
            try:
                dl_dir.mkdir(parents=True, exist_ok=True)
                log_success(f"  ✓ Created: {dl_dir}")
                self.log_report("Storage", "Folder", "REPAIRED", "Created folder")
            except Exception as e:
                log_error(f"  ✗ Failed to create download folder: {e}")
                self.log_report("Storage", "Folder", "FAILED", str(e))
                return False
        else:
            log_success(f"  ✓ Download folder exists: {dl_dir}")
            self.log_report("Storage", "Folder", "OK", str(dl_dir))
            
        # Check write permissions
        test_file = dl_dir / ".fs_write_test"
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            log_success("  ✓ Write permissions: OK")
            self.log_report("Storage", "Permissions", "OK", "Write access verified")
        except Exception as e:
            log_error(f"  ✗ Write permissions: FAILED! {e}")
            self.log_report("Storage", "Permissions", "FAILED", str(e))
            return False
            
        # Check disk space
        try:
            total, used, free = shutil.disk_usage(dl_dir)
            free_gb = free / (1024 * 1024 * 1024)
            log_info(f"  Available Space: {free_gb:.2f} GB")
            self.log_report("Storage", "Free Space", "OK", f"{free_gb:.2f} GB available")
        except Exception as e:
            log_warning(f"  Could not read disk usage: {e}")
            self.log_report("Storage", "Free Space", "UNKNOWN", str(e))
            
        return True

    # 6. Network Check
    def check_network(self):
        log_info("Checking network connectivity...")
        if os.getenv("CI") == "true":
            log_success("  ✓ CI environment detected: skipping network checks")
            self.log_report("Network", "Internet", "SKIPPED", "Skipped in CI")
            return True
        # Check standard host resolve
        try:
            socket.setdefaulttimeout(3)
            # Query standard dns resolver
            socket.gethostbyname("one.one.one.one")
            log_success("  ✓ Internet connection: Active")
            self.log_report("Network", "Internet", "OK", "Connected")
        except Exception as e:
            log_error("  ✗ Internet connection: FAILED! Check connection.")
            self.log_report("Network", "Internet", "FAILED", "No internet access")
            return False
            
        # Check platforms extract endpoints connectivity
        endpoints = {
            "YouTube API": "https://www.youtube.com",
            "TikTok API": "https://www.tikwm.com/api/",
            "Instagram Page": "https://www.instagram.com",
        }
        
        success = True
        for name, url in endpoints.items():
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=3) as res:
                    code = res.getcode()
                    if code in (200, 301, 302):
                        log_success(f"  ✓ Endpoint {name}: Reachable")
                        self.log_report("Network", name, "OK", "Reachable")
                    else:
                        raise Exception(f"HTTP Status {code}")
            except Exception as e:
                log_warning(f"  ⚠ Endpoint {name}: Failed ({e})")
                self.log_report("Network", name, "FAILED", str(e))
                success = False
        return success

    # Master Doctor Check
    def run_doctor(self):
        clear_screen = lambda: os.system("cls" if os.name == "nt" else "clear")
        clear_screen()
        print("╭──────────────────────────────────────────╮")
        print("│       F-SOCIETY SYSTEM DIAGNOSTIC        │")
        print("╰──────────────────────────────────────────╯\n")
        
        steps = [
            self.check_python,
            self.check_ytdlp,
            self.check_ffmpeg,
            self.check_database,
            self.check_storage,
            self.check_network
        ]
        
        failed = 0
        for step in steps:
            print()
            try:
                ok = step()
                if not ok:
                    failed += 1
            except Exception as err:
                log_error(f"Error during check execution: {err}")
                failed += 1
                
        print("\n" + "=" * 44)
        if failed == 0:
            log_success("\n[+] SYSTEM STATUS: READY ✓")
            print("============================================\n")
            return True
        else:
            log_error(f"\n[-] SYSTEM STATUS: {failed} PROBLEMS DETECTED ✗")
            log_warning("Run standard fixes or download updates.")
            print("============================================\n")
            return False

    def export_report(self):
        filepath = "diagnostic_report.txt"
        log_info(f"Generating diagnostic report in: {filepath} ...")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("==================================================\n")
                f.write("      F-SOCIETY SYSTEM DIAGNOSTICS REPORT         \n")
                f.write(f"      Generated At: {datetime.datetime.now()}\n")
                f.write("==================================================\n\n")
                
                f.write("SYSTEM ENVIRONMENT:\n")
                f.write(f"  Python Version : {sys.version}\n")
                f.write(f"  Platform       : {sys.platform}\n")
                f.write(f"  Executable     : {sys.executable}\n\n")
                
                f.write("DIAGNOSTIC CHECKS RESULTS:\n")
                for r in self.report_data:
                    f.write(f"[{r['section']}] {r['key']}: {r['status']}\n")
                    if r["details"]:
                        f.write(f"  Details: {r['details']}\n")
                f.write("\n======================= END =======================\n")
            log_success(f"Report exported successfully! Saved to {filepath}")
        except Exception as e:
            log_error(f"Failed to export report: {e}")
            
# Quick cached environment validation for startup (keeps it fast)
_cached_check_results = None
def quick_startup_check():
    global _cached_check_results
    if _cached_check_results is not None:
        return _cached_check_results
        
    # Quick database and FFmpeg validator
    ffmpeg_ok = updater.check_command("ffmpeg")
    db_file = database.DB_FILE
    db_ok = os.path.exists(db_file)
    
    _cached_check_results = ffmpeg_ok and db_ok
    return _cached_check_results
