import sys
import subprocess
import urllib.request
import json
from src.core.ffmpeg import is_ffmpeg_available

def check_command(cmd):
    try:
        if cmd == "yt-dlp":
            try:
                subprocess.run([sys.executable, "-m", "yt_dlp", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except:
                pass
        subprocess.run([cmd, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (FileNotFoundError, subprocess.SubprocessError):
        return False

def get_python_version():
    v = sys.version_info
    return f"{v.major}.{v.minor}.{v.micro}"

def get_ytdlp_version():
    try:
        return subprocess.check_output([sys.executable, "-m", "yt_dlp", "--version"], text=True).strip()
    except:
        pass
    if check_command("yt-dlp"):
        try:
            return subprocess.check_output(["yt-dlp", "--version"], text=True).strip()
        except:
            pass
    return "Not found"

def get_latest_ytdlp_version():
    try:
        req = urllib.request.Request("https://pypi.org/pypi/yt-dlp/json", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode("utf-8"))
            return data.get("info", {}).get("version", "Unknown")
    except Exception:
        return "Unknown"

def check_environment():
    yt_dlp_ok = check_command("yt-dlp")
    ffmpeg_ok = is_ffmpeg_available()
    aria2c_ok = check_command("aria2c")
    
    return {
        "python": {"ok": True, "version": get_python_version()},
        "yt-dlp": {"ok": yt_dlp_ok, "version": get_ytdlp_version()},
        "ffmpeg": {"ok": ffmpeg_ok, "version": "Available" if ffmpeg_ok else "Not found"},
        "aria2c": {"ok": aria2c_ok, "version": "Available" if aria2c_ok else "Not installed"},
    }

def update_ytdlp():
    try:
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-U", "yt-dlp", "--quiet"], capture_output=True, text=True)
        return r.returncode == 0, r.stderr.strip()
    except Exception as e:
        return False, str(e)
