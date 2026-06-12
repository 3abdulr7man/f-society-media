import os
import subprocess
from pathlib import Path
from src.core import config
from src.core.logger import log_info, log_success, log_error

def is_ffmpeg_available():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (FileNotFoundError, subprocess.SubprocessError):
        return False

def trim_video(input_path, start_time, duration, output_filename=None):
    if not is_ffmpeg_available():
        log_error("ffmpeg is not installed!")
        return False, "ffmpeg not found"
        
    if not os.path.exists(input_path):
        return False, "Input file not found"
        
    out_dir = Path(config.get("download_dir"))
    out_name = output_filename or "trimmed.mp4"
    out_path = out_dir / out_name
    
    cmd = ["ffmpeg", "-i", str(input_path), "-ss", str(start_time)]
    if duration:
        cmd.extend(["-t", str(duration)])
    cmd.extend(["-c", "copy", str(out_path), "-y"])
    
    try:
        log_info("Trimming video...")
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and out_path.exists():
            log_success(f"Saved: {out_path}")
            return True, str(out_path)
        return False, "FFmpeg returned error code"
    except Exception as e:
        return False, str(e)

def convert_format(input_path, target_ext):
    if not is_ffmpeg_available():
        log_error("ffmpeg is not installed!")
        return False, "ffmpeg not found"
        
    if not os.path.exists(input_path):
        return False, "Input file not found"
        
    out_dir = Path(config.get("download_dir"))
    out_path = out_dir / f"converted.{target_ext}"
    
    cmd = ["ffmpeg", "-i", str(input_path), str(out_path), "-y"]
    
    try:
        log_info("Converting format...")
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and out_path.exists():
            log_success(f"Saved: {out_path}")
            return True, str(out_path)
        return False, "FFmpeg returned error code"
    except Exception as e:
        return False, str(e)

def compress_video(input_path, crf="28"):
    if not is_ffmpeg_available():
        log_error("ffmpeg is not installed!")
        return False, "ffmpeg not found"
        
    if not os.path.exists(input_path):
        return False, "Input file not found"
        
    out_dir = Path(config.get("download_dir"))
    out_path = out_dir / "compressed.mp4"
    
    cmd = ["ffmpeg", "-i", str(input_path), "-vcodec", "libx264", "-crf", str(crf), str(out_path), "-y"]
    
    try:
        log_info("Compressing video...")
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and out_path.exists():
            log_success(f"Saved: {out_path}")
            return True, str(out_path)
        return False, "FFmpeg returned error code"
    except Exception as e:
        return False, str(e)

def extract_audio(input_path, target_format="mp3"):
    if not is_ffmpeg_available():
        log_error("ffmpeg is not installed!")
        return False, "ffmpeg not found"
        
    if not os.path.exists(input_path):
        return False, "Input file not found"
        
    out_dir = Path(config.get("download_dir"))
    out_path = out_dir / f"audio_extracted.{target_format}"
    acodec = "libmp3lame" if target_format == "mp3" else target_format
    
    cmd = ["ffmpeg", "-i", str(input_path), "-vn", "-acodec", acodec, str(out_path), "-y"]
    
    try:
        log_info("Extracting audio...")
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and out_path.exists():
            log_success(f"Saved: {out_path}")
            return True, str(out_path)
        return False, "FFmpeg returned error code"
    except Exception as e:
        return False, str(e)

def merge_video_audio(video_path, audio_path):
    if not is_ffmpeg_available():
        log_error("ffmpeg is not installed!")
        return False, "ffmpeg not found"
        
    if not os.path.exists(video_path) or not os.path.exists(audio_path):
        return False, "Video or audio file not found"
        
    out_dir = Path(config.get("download_dir"))
    out_path = out_dir / "merged.mp4"
    
    cmd = ["ffmpeg", "-i", str(video_path), "-i", str(audio_path), "-c:v", "copy", "-c:a", "aac", str(out_path), "-y"]
    
    try:
        log_info("Merging video and audio...")
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and out_path.exists():
            log_success(f"Saved: {out_path}")
            return True, str(out_path)
        return False, "FFmpeg returned error code"
    except Exception as e:
        return False, str(e)
