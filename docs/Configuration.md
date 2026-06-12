# Configuration Guide

F-SOCIETY settings are stored inside the `settings` table of the SQLite database `f_society.db`. Upon startup, the database settings are cached in memory to ensure quick reads.

---

## 1. Setting Parameters

The following configuration parameters are customizable via CLI settings menus or the GUI settings page:

| Parameter | Type | Default Value | Description |
| --- | --- | --- | --- |
| `download_dir` | `str` | `~/Downloads/F-SOCIETY` | Target folder for download outputs. |
| `default_video_quality` | `str` | `best` | Fallback resolution choice if none is specified (`best`, `1080p`, `720p`, `480p`, `360p`). |
| `default_audio_quality` | `str` | `192` | Default audio bitrate (`320`, `256`, `192`, `128`, `96`). |
| `max_concurrent` | `int` | `3` | Maximum concurrent threads used in parallel queues. |
| `theme` | `str` | `default` | Color mapping theme for the interactive CLI (`default`, `light`, `matrix`, `hacker`, `ocean`, `purple`). |
| `ffmpeg_warnings` | `bool` | `True` | Display warnings if FFmpeg is missing. |
| `auto_rename_duplicates` | `bool` | `True` | Append counter suffixes to filenames instead of overwriting duplicates. |
| `cookie_file` | `str` | *Empty* | Path to a Netscape format cookie file for sites requiring auth. |
| `speed_limit` | `str` | *Empty* | Limit download speeds (e.g. `500K` for 500 KB/s, `2M` for 2 MB/s). |
| `sound_alerts` | `bool` | `True` | Play a system beep sound on task completions. |
| `notifications` | `bool` | `True` | Show system notifications on completion. |
| `language` | `str` | `en` | Display language (`en` or `es`). |

---

## 2. Environment Overrides
To override configurations via shell environments, create a `.env` file in the project directory matching `.env.example` configurations.
For example, to limit speeds globally in automated scripting environments:
```bash
export F_SOCIETY_SPEED_LIMIT="1M"
```
