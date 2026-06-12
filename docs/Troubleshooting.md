# Troubleshooting Guide

Here are standard solutions to common issues when using **F-SOCIETY YT-DLP PRO**.

---

## 1. Missing FFmpeg Warning
**Symptom**: CLI or GUI reports `FFmpeg is missing`.
**Cause**: FFmpeg binaries are not installed or not registered in your system environment PATH.
**Fix**:
1. Verify if `ffmpeg` works in a terminal:
   ```bash
   ffmpeg -version
   ```
2. If it is not found:
   - **Windows**: Download build zip from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/), extract it, copy the path to the `bin` folder (containing `ffmpeg.exe` and `ffprobe.exe`), and append it to your system's Environment Variables (under `PATH`). Restart the terminal/IDE.
   - **macOS**: Run `brew install ffmpeg`.
   - **Linux**: Run `sudo apt update && sudo apt install ffmpeg`.

---

## 2. Audio Extraction Fails
**Symptom**: Video downloads successfully but extracting audio fails with errors.
**Cause**: `yt-dlp` cannot convert files to MP3 without FFmpeg/ffprobe.
**Fix**: Follow the steps in Section 1 to register FFmpeg in your PATH.

---

## 3. SSL verification / certificate fails
**Symptom**: Downloader fails with SSL handshake errors.
**Cause**: Missing or outdated system certificates.
**Fix**:
- On macOS, run Python's built-in certificate installer:
  ```bash
  open "/Applications/Python 3.x/Install Certificates.command"
  ```
- Or try bypassing SSL checking using the config (only if necessary for private endpoints).

---

## 4. PySide6 / GUI fails to start
**Symptom**: Launching `fs --gui` displays `ModuleNotFoundError: No module named 'PySide6'` or errors during display bindings.
**Cause**: The PySide6 package is not installed in the active environment.
**Fix**:
- Make sure you are in the correct virtual environment and run:
  ```bash
  pip install PySide6
  ```
