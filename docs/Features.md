# Project Features Manual

**F-SOCIETY YT-DLP PRO** is equipped with advanced media management and downloading capabilities, transitioning yt-dlp into a production-level utility.

---

## 1. Smart Downloader
Our downloader uses a metadata pre-fetch routine to identify media platforms:
- **YouTube / YouTube Music**: Fetches formats, titles, upload dates, views, uploader information, and resolves best merging layouts.
- **TikTok**: Downloads video feeds. Integrates custom TikWM slideshow parsers to download original photos slide-by-slide.
- **Instagram**: Retrieves individual posts, reels, and galleries.
- **SoundCloud / Bandcamp**: Audio stream extracts with custom metadata tag writes.
- **Generic Direct Link**: Checks URL extensions for direct video/audio file writing.

---

## 2. Advanced Parallel Queue
- Queue records are stored inside the SQLite database.
- Uses a background threadpool with customizable `max_concurrent` settings to download multiple links simultaneously.
- Provides visual ETA, download speed, and percent progress updates in real-time.

---

## 3. Media Library
- Scan and manage downloads directly inside the client GUI.
- Interactive actions to open/play, delete, convert formats, or inspect details of downloaded media.

---

## 4. FFmpeg Studio
Integrates direct subprocess controls over `ffmpeg` binaries:
- **Trim Video**: Cut segments by specifying start and duration time ranges.
- **Format Converter**: Re-encode media container layouts (e.g. mp4, avi, webm, mkv).
- **Compress Video**: Compresses videos to smaller sizes using customizable Constant Rate Factor (CRF) scaling.
- **Extract Audio**: Separate sound streams from videos into high-quality MP3s.
- **Merge Tracks**: Bind separate video and audio files together.
