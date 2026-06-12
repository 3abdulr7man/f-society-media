# F-SOCIETY YT-DLP PRO

[![Python Version](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Build Status](https://github.com/your-username/F-SOCIETY-YTDLP/workflows/CI/CD%20Build%20and%20Test/badge.svg)](https://github.com/your-username/F-SOCIETY-YTDLP/actions)
[![Release Version](https://img.shields.io/badge/Release-v1.0.0-red.svg)](CHANGELOG.md)

**F-SOCIETY YT-DLP PRO** is a professional desktop client, media downloader, and library manager built with Python. It abstracts the power of `yt-dlp` and `FFmpeg` into a responsive dark-themed GUI and keyboard-controlled console interface.

---

## Features

- :white_check_mark: **GUI Interface**: Fully featured dark-mode PySide6 desktop client.
- :white_check_mark: **Interactive CLI**: Interactive Rich terminal selectors navigated via arrow-keys + enter selection.
- :white_check_mark: **Downloader**: Smart engine resolving format links, downloads resolutions up to 4K, downloads playlists, and channels.
- :white_check_mark: **FFmpeg Tools**: In-app graphical media trimmer, encoder, converter, sound separator, and track binder.
- :white_check_mark: **Queue System**: Thread-safe parallel downloads dispatcher with speed overrides.
- :white_check_mark: **Media Library**: Embedded explorer directory scanner to play, delete, or reprocess downloaded media files.
- :white_check_mark: **Plugin System**: Dynamic modular hooks for custom site scripts.
- :white_check_mark: **Auto Updates**: Environment dependency logs validation and automated `yt-dlp` updates.

---

## Repository Structure

```
F-SOCIETY-YTDLP/
├── src/                  # Core modules, CLI dashboard, and PySide6 windows
├── tests/                # Automated testing suites
├── docs/                 # Multi-page markdown guides
├── resources/            # Image assets, banners, stylesheets
├── plugins/              # Dynamic python modules
├── examples/             # Code samples
├── README.md             # Standard manual
├── LICENSE               # MIT license file
├── CONTRIBUTING.md       # Contributing policy guidelines
├── CODE_OF_CONDUCT.md    # Contributor Covenant instructions
├── CHANGELOG.md          # Version changelogs tracing
└── SECURITY.md           # Secure vulnerability reports guidelines
```

---

## Installation

Install directly from PyPI (when published) or source:

```bash
# Install PyPI package
pip install f-society

# Or from source
pip install -e .
```

---

## Usage Guide

You can launch the program using entry points `fs` or `f-society`.

### A. Run Interactive CLI
Run the executable command:
```bash
fs
```
Use arrow keys to navigate and press enter to select.

### B. Run Desktop GUI App
Run the graphical user interface:
```bash
fs --gui
```

### C. Run Smart Clipboard Watcher
```bash
fs --watch
```

---

## CLI Scripting Commands

Directly script download engines:
```bash
# Download standard video
fs "https://www.youtube.com/watch?v=..."

# Extract high quality audio
fs "https://www.youtube.com/watch?v=..." --audio --quality 320

# Download channel stream
fs "https://www.youtube.com/user/..." --channel

# Target directory override
fs "https://www.youtube.com/watch?v=..." --dir "D:/Downloads"
```

---

## Documentation

Exhaustive markdown guides can be found inside the `docs/` folder:
- [Installation Guide](docs/Installation.md)
- [Features Manual](docs/Features.md)
- [Command Line Interface (CLI)](docs/CLI.md)
- [Graphical Desktop GUI](docs/GUI.md)
- [Configuration Settings](docs/Configuration.md)
- [Troubleshooting Reference](docs/Troubleshooting.md)
