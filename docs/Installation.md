# Installation Manual

This guide outlines how to download, configure, and install **F-SOCIETY YT-DLP PRO** on Windows, macOS, and Linux.

---

## 1. System Requirements

Before installing the Python package, you must ensure that **Python** and **FFmpeg** are installed and configured on your system.

### A. Python
Python 3.7 or higher is required.
- [Download Python](https://www.python.org/downloads/)
- *Important (Windows)*: Check the **"Add Python to PATH"** checkbox during installation.

### B. FFmpeg
FFmpeg is critical for merging separate video/audio streams and converting media formats.
- **Windows**: Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add the `bin` folder path to your System Environment variables.
- **macOS**: Install using Homebrew: `brew install ffmpeg`
- **Linux**: Install via apt: `sudo apt install ffmpeg`

---

## 2. Package Installation

Install the F-SOCIETY client directly from source using `pip`:

```bash
# Clone the repository
git clone https://github.com/yourusername/F-SOCIETY-YTDLP.git
cd F-SOCIETY-YTDLP

# Install in editable mode
pip install -e .
```

This commands sets up build packages, installs dependencies (`yt-dlp`, `rich`, `PySide6`), and registers CLI shortcuts `fs` and `f-society`.

---

## 3. Post-Install Verifier

To verify if the binaries and commands are correctly setup:

```bash
# Verify environment checks
fs --help
```
If the command executes successfully, you are ready to launch!
