# Command Line Interface (CLI) Manual

F-SOCIETY provides a premium command-line console dashboard and non-interactive script runners.

---

## 1. Non-Interactive Scripting Mode

Directly invoke download engines using parameters:

```bash
fs [URL] [FLAGS]
```

### Options and Flags

| Argument | Flag | Description |
| --- | --- | --- |
| `url` | *Position 1* | The URL of the video, channel, or playlist to download. |
| `--audio` | | Download and extract audio stream only. |
| `--images` | | Extract image slideshows or posts gallery. |
| `--playlist` | | Force playlist download mode. |
| `--channel` | | Download channel upload lists (up to 20 videos). |
| `--quality` | `[VAL]` | Override resolution (e.g. `1080p`) or audio bitrate (e.g. `320`). |
| `--dir` | `[PATH]` | Override download destination folder path. |
| `--limit` | `[SPEED]`| Custom download speed limit (e.g. `500K`, `2M`). |
| `--gui` | | Launch PySide6 desktop GUI window. |
| `--watch` | | Smart clipboard monitoring mode. |

---

## 2. Interactive Console Shell

If you run the CLI without any arguments:

```bash
fs
```

It launches the interactive **Rich Console Selector**:
- **Navigation**: Use the **UP** and **DOWN** arrow keys to move the selection highlight.
- **Selection**: Press **ENTER** to choose the highlighted option.
- **Exit**: Press **ESC** or **q** or **0** to go back to the previous menu or quit.
- **Status Panel**: Displays live dashboard logs, including total database downloads, successful compiles, and downloads folder size.
