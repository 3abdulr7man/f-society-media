# Graphical User Interface (GUI) Manual

To start the desktop application:

```bash
fs --gui
```

F-SOCIETY's GUI is built with PySide6 and styled with a cyberpunk color palette.

---

## 1. Sidebar Navigation

The sidebar menu allows switching between specialized layouts:
- **Home**: Overall statistics (total database count and folder sizes) and quick shortcuts.
- **Download**: Simple forms to download links, select quality profiles, and track progress.
- **Queue**: List of batch items, and queue threadpool controllers.
- **Library**: Scans the download directory to show files, complete with play and delete context options.
- **History**: An SQLite list of past download URL queries, resolutions, and exact timestamp logs.
- **FFmpeg Studio**: Compression, converter, and extract forms.
- **Settings**: Configuration settings (download directory paths, default bitrates, sound alert toggles, notification options).
- **About**: System version details.

---

## 2. Background Threading Model
To keep the UI responsive, downloading operations are executed in a separate thread subclassing `QThread`:
- Standard progress callbacks update the UI's progress bar, speeds, and ETA.
- Avoids GUI freeze issues.
- Sounds and system notifications are triggered in separate processes to prevent blocking.
