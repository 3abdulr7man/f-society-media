import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import threading
import datetime
from pathlib import Path
from src.core import config

print_lock = threading.Lock()
if getattr(sys, 'frozen', False):
    PROJECT_ROOT = Path(sys.executable).parent.resolve()
else:
    PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
LOG_DIR = PROJECT_ROOT / "logs"

def init_logger():
    try:
        LOG_DIR.mkdir(exist_ok=True)
    except Exception as e:
        print(f"Failed to create logs directory: {e}")

def write_to_log_file(filename, level, message):
    init_logger()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}\n"
    try:
        with open(LOG_DIR / filename, "a", encoding="utf-8") as f:
            f.write(log_line)
    except:
        pass

def cprint(tag, text, end="\n", flush=False):
    with print_lock:
        sys.stdout.write(f"{config.c(tag)}{text}{config.C.RESET}{end}")
        if flush:
            sys.stdout.flush()

def log_info(text, end="\n"):
    cprint("info", text, end=end)
    write_to_log_file("download.log", "INFO", text.strip())

def log_success(text, end="\n"):
    cprint("success", text, end=end)
    write_to_log_file("download.log", "SUCCESS", text.strip())

def log_warning(text, end="\n"):
    cprint("warning", text, end=end)
    write_to_log_file("download.log", "WARNING", text.strip())

def log_error(text, end="\n"):
    cprint("error", text, end=end)
    write_to_log_file("errors.log", "ERROR", text.strip())
    write_to_log_file("download.log", "ERROR", text.strip())

def log_dim(text, end="\n"):
    cprint("dim", text, end=end)
