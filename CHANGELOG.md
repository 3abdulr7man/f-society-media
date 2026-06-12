# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-06-12

### Added
- **Modular Refactoring**: Split single-file script into distinct modules in `src/core/`, `src/cli/`, and `src/gui/`.
- **Desktop GUI Client**: Fully-functional PySide6 graphical user interface with responsive dark styling, sidebar panels, media library management, and background downloader thread locks.
- **Interactive Console Dash**: Keyboard-controlled Rich shell launcher allowing selections via UP/DOWN arrows and ENTER.
- **SQLite Database Support**: Integrated SQLite schemas for queues, download histories, and configuration values, deprecating JSON persistence files.
- **Clipboard Watcher**: Automatic clipboard listener running in an independent tkinter thread to catch and prompt media link copies.
- **CI/CD Action**: GitHub build workflows compiled to build packages and run tests across Windows, Linux, and macOS.
- **Documentation Docs**: Added modular Installation, Features, CLI, GUI, Configuration, and Troubleshooting markdown manuals.
