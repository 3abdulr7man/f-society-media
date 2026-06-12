import os
import sys
from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QListWidget, QFileDialog, QProgressBar, QMessageBox,
    QTableWidget, QTableWidgetItem, QCheckBox, QListWidgetItem, QMenu,
    QFrame
)
from PySide6.QtGui import QFont, QColor, QIcon, QAction

from src.core import config, database, downloader, ffmpeg, queue, scheduler, updater

CYBER_STYLE_PRO = """
QMainWindow {
    background-color: #06090c;
}
QWidget {
    background-color: #06090c;
    color: #cbd5e1;
    font-family: "Courier New", monospace, "Segoe UI";
    font-size: 13px;
}
QLabel {
    color: #00ff66;
}
QLabel#titleLabel {
    color: #ff0055;
    font-size: 22px;
    font-weight: bold;
}
QLineEdit {
    background-color: #0f172a;
    border: 1px solid #38bdf8;
    border-radius: 6px;
    color: #ffffff;
    padding: 8px;
    font-size: 14px;
}
QLineEdit:focus {
    border: 1px solid #f43f5e;
}
QPushButton {
    background-color: #0f172a;
    border: 1px solid #00ff66;
    border-radius: 6px;
    color: #00ff66;
    font-weight: bold;
    font-size: 13px;
    padding: 10px 20px;
}
QPushButton:hover {
    background-color: #00ff66;
    color: #06090c;
}
QPushButton:pressed {
    background-color: #059669;
}
QPushButton#startButton {
    background-color: #1e1b4b;
    border: 2px solid #ff0055;
    color: #ff0055;
    font-size: 15px;
    border-radius: 6px;
    padding: 12px 24px;
}
QPushButton#startButton:hover {
    background-color: #ff0055;
    color: #ffffff;
}
QComboBox {
    background-color: #0f172a;
    border: 1px solid #38bdf8;
    border-radius: 6px;
    padding: 6px 12px;
    color: #ffffff;
}
QProgressBar {
    background-color: #0f172a;
    border: 1px solid #00ff66;
    border-radius: 6px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
}
QProgressBar::chunk {
    background-color: #00ff66;
}
QListWidget {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 6px;
}
QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid #1e293b;
}
QListWidget::item:selected {
    background-color: #f43f5e;
    color: #ffffff;
}
QTableWidget {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    gridline-color: #1e293b;
}
QTableWidget::item {
    padding: 6px;
}
QHeaderView::section {
    background-color: #06090c;
    color: #38bdf8;
    padding: 6px;
    border: 1px solid #1e293b;
    font-weight: bold;
}
QFrame#cardFrame {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 15px;
}
"""

class FetchMetaThread(QThread):
    finished_signal = Signal(dict, str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        info, err = downloader.fetch_video_info(self.url)
        if info:
            self.finished_signal.emit(info, "")
        else:
            self.finished_signal.emit({}, err or "Failed to fetch metadata")

class DownloadThread(QThread):
    progress_signal = Signal(float, str, str, str, str, str, str)
    finished_signal = Signal(bool, str, object) # success, message, exception if failed
    
    def __init__(self, url, mode, quality):
        super().__init__()
        self.url = url
        self.mode = mode
        self.quality = quality
        
    def run(self):
        def progress_cb(percent, speed, eta, downloaded, total, status, filename):
            self.progress_signal.emit(percent, speed, eta, downloaded, total, status, filename)
            
        downloader.clear_progress_callbacks()
        downloader.register_progress_callback(progress_cb)
        
        success = False
        exception_err = None
        try:
            if self.mode == "video":
                fmt = downloader.build_format_string(self.quality)
                success = downloader.download_video_via_api(self.url, fmt)
            elif self.mode == "audio":
                success = downloader.download_audio_via_api(self.url, self.quality)
            elif self.mode == "images":
                success = downloader.download_image_gallery_via_api(self.url)
        except downloader.DownloaderError as err:
            success = False
            exception_err = err
        except Exception as e:
            success = False
            exception_err = downloader.DownloaderError("Unknown", str(e), "Verify logs")
            
        downloader.unregister_progress_callback(progress_cb)
        self.finished_signal.emit(success, "Completed" if success else "Failed", exception_err)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F-SOCIETY YT-DLP PRO - MEDIA CENTER")
        self.resize(1100, 720)
        self.setStyleSheet(CYBER_STYLE_PRO)
        
        config.load_settings()
        self.download_thread = None
        self.meta_thread = None
        self.init_ui()
        
    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar Menu
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #090d12; border-right: 1px solid #1e293b;")
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 25, 15, 25)
        sidebar_layout.setSpacing(12)
        
        logo = QLabel("F-SOCIETY")
        logo.setFont(QFont("Courier New", 24, QFont.Bold))
        logo.setStyleSheet("color: #f43f5e; margin-bottom: 25px;")
        logo.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo)
        
        self.nav_buttons = []
        nav_items = [
            ("Home", 0),
            ("Download Center", 1),
            ("Batch Queue", 2),
            ("Media Library", 3),
            ("History Logs", 4),
            ("FFmpeg Studio", 5),
            ("Settings Hub", 6),
            ("About", 7)
        ]
        
        for name, index in nav_items:
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    border: none;
                    color: #94a3b8;
                    padding: 12px 18px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0f172a;
                    color: #38bdf8;
                }
            """)
            btn.clicked.connect(lambda checked=False, idx=index: self.change_page(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
        sidebar_layout.addStretch()
        
        # System check on sidebar
        self.sidebar_check = QLabel("Engine check: Verifying...")
        self.sidebar_check.setStyleSheet("color: #f59e0b; font-size: 11px;")
        sidebar_layout.addWidget(self.sidebar_check)
        
        self.status_label = QLabel("SYSTEM STATUS: READY")
        self.status_label.setStyleSheet("color: #00ff66; font-size: 12px; font-weight: bold;")
        sidebar_layout.addWidget(self.status_label)
        
        main_layout.addWidget(sidebar)
        
        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages)
        
        # Setup Pages
        self.setup_home_page()
        self.setup_download_page()
        self.setup_queue_page()
        self.setup_library_page()
        self.setup_history_page()
        self.setup_ffmpeg_page()
        self.setup_settings_page()
        self.setup_about_page()
        
        self.change_page(0)
        self.run_startup_version_check()
        
    def change_page(self, index):
        self.pages.setCurrentIndex(index)
        for idx, btn in enumerate(self.nav_buttons):
            if idx == index:
                btn.setStyleSheet("""
                    text-align: left;
                    border-left: 4px solid #f43f5e;
                    background-color: #0f172a;
                    color: #f43f5e;
                    padding: 12px 18px;
                    font-weight: bold;
                """)
            else:
                btn.setStyleSheet("""
                    text-align: left;
                    border: none;
                    color: #94a3b8;
                    padding: 12px 18px;
                    border-radius: 6px;
                """)
                
        if index == 3: self.refresh_library()
        elif index == 4: self.refresh_history()
        
    def run_startup_version_check(self):
        # Quick health validation
        ytdlp_ver = updater.get_ytdlp_version()
        self.sidebar_check.setText(f"Engine: yt-dlp {ytdlp_ver}")
        self.sidebar_check.setStyleSheet("color: #00ff66; font-size: 11px;")

    # 1. Home / Dashboard Page
    def setup_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(45, 45, 45, 45)
        layout.setSpacing(20)
        
        title = QLabel("D-15 MEDIA CENTER DASHBOARD")
        title.setFont(QFont("Courier New", 22, QFont.Bold))
        title.setStyleSheet("color: #f43f5e;")
        layout.addWidget(title)
        
        desc = QLabel("Modular media engine running database tags, queue systems, and FFmpeg converters.")
        desc.setFont(QFont("Segoe UI", 12))
        desc.setStyleSheet("color: #94a3b8;")
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        
        # Dashboard cards
        cards_layout = QHBoxLayout()
        
        self.card_dl = QFrame()
        self.card_dl.setObjectName("cardFrame")
        self.card_dl.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 20px;")
        cdl_lay = QVBoxLayout(self.card_dl)
        self.card_dl_title = QLabel("DATABASE HISTORY")
        self.card_dl_title.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 14px;")
        self.card_dl_val = QLabel("0 Downloads")
        self.card_dl_val.setStyleSheet("color: #ffffff; font-size: 20px; font-weight: bold; margin-top: 10px;")
        cdl_lay.addWidget(self.card_dl_title)
        cdl_lay.addWidget(self.card_dl_val)
        
        self.card_storage = QFrame()
        self.card_storage.setObjectName("cardFrame")
        self.card_storage.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 20px;")
        cst_lay = QVBoxLayout(self.card_storage)
        self.card_storage_title = QLabel("USED STORAGE")
        self.card_storage_title.setStyleSheet("color: #00ff66; font-weight: bold; font-size: 14px;")
        self.card_storage_val = QLabel("0.00 GB")
        self.card_storage_val.setStyleSheet("color: #ffffff; font-size: 20px; font-weight: bold; margin-top: 10px;")
        cst_lay.addWidget(self.card_storage_title)
        cst_lay.addWidget(self.card_storage_val)
        
        cards_layout.addWidget(self.card_dl)
        cards_layout.addWidget(self.card_storage)
        layout.addLayout(cards_layout)
        
        layout.addSpacing(30)
        
        quick_btn = QPushButton("LAUNCH SMART DOWNLOADER")
        quick_btn.clicked.connect(lambda: self.change_page(1))
        layout.addWidget(quick_btn)
        
        layout.addStretch()
        self.pages.addWidget(page)
        self.refresh_home_stats()

    def refresh_home_stats(self):
        logs = database.get_download_logs()
        self.card_dl_val.setText(f"{len(logs)} Downloads")
        
        d_dir = Path(config.get("download_dir"))
        total_size = 0
        if d_dir.exists():
            for f in d_dir.glob("**/*"):
                if f.is_file():
                    total_size += f.stat().st_size
        gb = total_size / (1024 * 1024 * 1024)
        self.card_storage_val.setText(f"{gb:.2f} GB")

    # 2. Download Page
    def setup_download_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(45, 45, 45, 45)
        layout.setSpacing(15)
        
        title = QLabel("SMART DOWNLOAD CENTER")
        title.setFont(QFont("Courier New", 20, QFont.Bold))
        title.setStyleSheet("color: #f43f5e;")
        layout.addWidget(title)
        
        layout.addWidget(QLabel("Media URL Link:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste URL (YouTube, TikTok, Instagram, Twitter/X)")
        self.url_input.textChanged.connect(self.on_url_pasted)
        layout.addWidget(self.url_input)
        
        # Details Card (Smart Download Flow)
        self.meta_card = QFrame()
        self.meta_card.setObjectName("cardFrame")
        self.meta_card.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 15px;")
        meta_lay = QVBoxLayout(self.meta_card)
        self.lbl_detected = QLabel("Platform: N/A")
        self.lbl_detected.setStyleSheet("color: #38bdf8; font-weight: bold;")
        self.lbl_title = QLabel("Title: Idle")
        self.lbl_title.setStyleSheet("color: #ffffff;")
        self.lbl_duration = QLabel("Duration: N/A")
        self.lbl_duration.setStyleSheet("color: #cbd5e1;")
        
        meta_lay.addWidget(self.lbl_detected)
        meta_lay.addWidget(self.lbl_title)
        meta_lay.addWidget(self.lbl_duration)
        layout.addWidget(self.meta_card)
        
        conf_layout = QHBoxLayout()
        mode_layout = QVBoxLayout()
        mode_layout.addWidget(QLabel("Mode Options:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["video", "audio", "images"])
        mode_layout.addWidget(self.mode_combo)
        conf_layout.addLayout(mode_layout)
        
        qual_layout = QVBoxLayout()
        qual_layout.addWidget(QLabel("Quality Selection:"))
        self.qual_combo = QComboBox()
        self.qual_combo.addItems(["best", "2160p (4K)", "1080p", "720p", "480p", "320kbps", "192kbps"])
        qual_layout.addWidget(self.qual_combo)
        conf_layout.addLayout(qual_layout)
        layout.addLayout(conf_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.dl_info_label = QLabel("ETA: N/A | Speed: N/A")
        self.dl_info_label.setStyleSheet("color: #38bdf8;")
        layout.addWidget(self.dl_info_label)
        
        self.dl_filename_label = QLabel("File: Idle")
        self.dl_filename_label.setStyleSheet("color: #94a3b8;")
        layout.addWidget(self.dl_filename_label)
        
        self.start_btn = QPushButton("START DOWNLOAD")
        self.start_btn.setObjectName("startButton")
        self.start_btn.clicked.connect(self.start_download)
        layout.addWidget(self.start_btn)
        
        layout.addStretch()
        self.pages.addWidget(page)

    def on_url_pasted(self, text):
        url = text.strip()
        if downloader.validate_url(url):
            platform = downloader.detect_platform(url)
            type_lbl = downloader.detect_content_type(url)
            self.lbl_detected.setText(f"Platform: {platform} ({type_lbl.upper()})")
            self.lbl_title.setText("Title: Fetching details in background thread...")
            self.lbl_duration.setText("Duration: Loading...")
            
            # Start background metadata fetch
            if self.meta_thread and self.meta_thread.isRunning():
                self.meta_thread.terminate()
            self.meta_thread = FetchMetaThread(url)
            self.meta_thread.finished_signal.connect(self.on_meta_fetched)
            self.meta_thread.start()

    @Slot(dict, str)
    def on_meta_fetched(self, info, err):
        if info:
            self.lbl_title.setText(f"Title: {info.get('title', 'Unknown')}")
            self.lbl_duration.setText(f"Duration: {downloader.format_duration(info.get('duration'))}")
        else:
            self.lbl_title.setText(f"Title: Fetch failed ({err[:40]})")
            self.lbl_duration.setText("Duration: N/A")

    def start_download(self):
        url = self.url_input.text().strip()
        if not downloader.validate_url(url):
            QMessageBox.critical(self, "Error", "Invalid URL format!")
            return
            
        mode = self.mode_combo.currentText()
        quality_raw = self.qual_combo.currentText()
        quality = quality_raw.split(" ")[0].replace("kbps", "")
        
        self.status_label.setText("SYSTEM: DOWNLOADING")
        self.start_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        self.download_thread = DownloadThread(url, mode, quality)
        self.download_thread.progress_signal.connect(self.on_download_progress)
        self.download_thread.finished_signal.connect(self.on_download_finished)
        self.download_thread.start()

    @Slot(float, str, str, str, str, str, str)
    def on_download_progress(self, percent, speed, eta, downloaded, total, status, filename):
        self.progress_bar.setValue(int(percent))
        self.dl_info_label.setText(f"ETA: {eta} | Speed: {speed} | Downloaded: {downloaded}/{total}")
        self.dl_filename_label.setText(f"File: {filename}")
        
    @Slot(bool, str, object)
    def on_download_finished(self, success, msg, exception_err):
        self.start_btn.setEnabled(True)
        self.status_label.setText("SYSTEM: READY")
        
        if success:
            QMessageBox.information(self, "Success", "Download completed successfully!")
            self.refresh_home_stats()
            self.progress_bar.setValue(100)
        else:
            if exception_err:
                self.show_gui_error_recovery(exception_err)
            else:
                QMessageBox.critical(self, "Failed", "Download failed! Please run system check.")

    def show_gui_error_recovery(self, err):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("DOWNLOAD ERROR")
        msg_box.setIcon(QMessageBox.Warning)
        
        error_details = (
            f"Platform: {err.platform}\n"
            f"Reason  : {err.reason}\n"
            f"Solution: {err.solution}"
        )
        msg_box.setText(error_details)
        
        retry_btn = msg_box.addButton("Retry", QMessageBox.ActionRole)
        update_btn = msg_box.addButton("Update Engine", QMessageBox.ActionRole)
        fallback_btn = msg_box.addButton("Use Fallback", QMessageBox.ActionRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.RejectRole)
        
        msg_box.exec_()
        
        clicked = msg_box.clickedButton()
        if clicked == retry_btn:
            self.start_download()
        elif clicked == update_btn:
            self.status_label.setText("SYSTEM: UPDATING ENGINE")
            succ, m = updater.update_ytdlp()
            self.status_label.setText("SYSTEM: READY")
            if succ:
                QMessageBox.information(self, "Updated", "Engine updated! Retrying download...")
                self.start_download()
            else:
                QMessageBox.critical(self, "Failed", f"Update failed: {m}")
        elif clicked == fallback_btn and err.platform == "TikTok":
            # Direct fallback trigger
            self.status_label.setText("SYSTEM: FALLBACK ACTIVE")
            from src.core.platforms.tiktok import TikTokPlatformExtractor
            t_ext = TikTokPlatformExtractor()
            outtmpl = str(Path(config.get("download_dir")) / config.get("output_template"))
            
            def mock_prog(d):
                if d['status'] == 'downloading':
                    percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                    self.progress_bar.setValue(int(percent))
                    self.dl_info_label.setText("Status: Fallback downloading...")
            
            res = t_ext.download(self.url_input.text().strip(), "best", outtmpl, mock_prog)
            self.status_label.setText("SYSTEM: READY")
            if res:
                QMessageBox.information(self, "Success", "Fallback download complete!")
                self.refresh_home_stats()
            else:
                QMessageBox.critical(self, "Failed", "Fallback extraction failed.")

    # 3. Queue Page
    def setup_queue_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(45, 45, 45, 45)
        
        title = QLabel("CONCURRENCY QUEUE HUB")
        title.setFont(QFont("Courier New", 20, QFont.Bold))
        title.setStyleSheet("color: #f43f5e;")
        layout.addWidget(title)
        
        self.queue_list = QListWidget()
        layout.addWidget(self.queue_list)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Quick Add Clipboard URL")
        add_btn.clicked.connect(self.add_queue_item_dialog)
        btn_layout.addWidget(add_btn)
        
        run_btn = QPushButton("START BATCH PROCESSOR")
        run_btn.clicked.connect(self.run_batch_queue)
        btn_layout.addWidget(run_btn)
        
        clear_btn = QPushButton("Clear Completed")
        clear_btn.clicked.connect(self.clear_queue)
        btn_layout.addWidget(clear_btn)
        
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        self.pages.addWidget(page)
        self.refresh_queue_list()

    def refresh_queue_list(self):
        self.queue_list.clear()
        q_manager = queue.QueueManager()
        items = q_manager.get_items()
        for item in items:
            self.queue_list.addItem(f"[{item['mode'].upper()}] {item['url']} (Quality: {item['quality']}) | Status: {item['status']}")

    def add_queue_item_dialog(self):
        clipboard = QApplication.clipboard()
        cb_text = clipboard.text().strip()
        if downloader.validate_url(cb_text):
            q_manager = queue.QueueManager()
            q_manager.add_item(cb_text, "video", "best")
            self.refresh_queue_list()
            QMessageBox.information(self, "Queue", f"Added URL: {cb_text}")
        else:
            QMessageBox.warning(self, "Queue", "No valid URL in clipboard.")

    def run_batch_queue(self):
        self.status_label.setText("SYSTEM: RUNNING QUEUE")
        q_manager = queue.QueueManager()
        success, msg = q_manager.run()
        self.status_label.setText("SYSTEM: READY")
        QMessageBox.information(self, "Queue Batch", f"Result: {msg}")
        self.refresh_queue_list()
        self.refresh_home_stats()

    def clear_queue(self):
        q_manager = queue.QueueManager()
        q_manager.clear()
        self.refresh_queue_list()

    # 4. Library Page
    def setup_library_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(45, 45, 45, 45)
        
        title = QLabel("LOCAL MEDIA LIBRARY")
        title.setFont(QFont("Courier New", 20, QFont.Bold))
        title.setStyleSheet("color: #f43f5e;")
        layout.addWidget(title)
        
        self.library_list = QListWidget()
        self.library_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.library_list.customContextMenuRequested.connect(self.show_library_context_menu)
        layout.addWidget(self.library_list)
        
        refresh_btn = QPushButton("Scan Directory Files")
        refresh_btn.clicked.connect(self.refresh_library)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        self.pages.addWidget(page)

    def refresh_library(self):
        self.library_list.clear()
        d_dir = Path(config.get("download_dir"))
        if d_dir.exists():
            for f in d_dir.iterdir():
                if f.is_file() and f.suffix.lower() in ('.mp4', '.mkv', '.mp3', '.m4a', '.webm', '.jpg', '.png', '.webp'):
                    item = QListWidgetItem(f.name)
                    item.setData(Qt.UserRole, str(f))
                    self.library_list.addItem(item)

    def show_library_context_menu(self, pos):
        item = self.library_list.currentItem()
        if not item: return
        file_path = item.data(Qt.UserRole)
        
        menu = QMenu(self)
        open_action = QAction("Open / Play file", self)
        open_action.triggered.connect(lambda: self.open_file(file_path))
        menu.addAction(open_action)
        
        delete_action = QAction("Delete file", self)
        delete_action.triggered.connect(lambda: self.delete_file(file_path))
        menu.addAction(delete_action)
        menu.exec_(self.library_list.mapToGlobal(pos))

    def open_file(self, path):
        try:
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':
                import subprocess
                subprocess.run(['open', path])
            else:
                import subprocess
                subprocess.run(['xdg-open', path])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {e}")

    def delete_file(self, path):
        confirm = QMessageBox.question(self, "Delete", f"Are you sure you want to delete this file?\n{Path(path).name}", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                os.remove(path)
                self.refresh_library()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {e}")

    # 5. History Page
    def setup_history_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(45, 45, 45, 45)
        
        title = QLabel("SYSTEM HISTORY LOGS")
        title.setFont(QFont("Courier New", 20, QFont.Bold))
        title.setStyleSheet("color: #f43f5e;")
        layout.addWidget(title)
        
        self.history_table = QTableWidget(0, 5)
        self.history_table.setHorizontalHeaderLabels(["URL", "Type", "Quality", "Size", "Time"])
        self.history_table.setColumnWidth(0, 320)
        self.history_table.setColumnWidth(4, 180)
        layout.addWidget(self.history_table)
        self.pages.addWidget(page)

    def refresh_history(self):
        history = database.get_history()
        self.history_table.setRowCount(0)
        for item in history:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            self.history_table.setItem(row, 0, QTableWidgetItem(item["url"]))
            self.history_table.setItem(row, 1, QTableWidgetItem(item["type"]))
            self.history_table.setItem(row, 2, QTableWidgetItem(item["quality"]))
            self.history_table.setItem(row, 3, QTableWidgetItem(item["size"]))
            self.history_table.setItem(row, 4, QTableWidgetItem(item["time"]))

    # 6. FFmpeg Page
    def setup_ffmpeg_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(45, 45, 45, 45)
        layout.setSpacing(15)
        
        title = QLabel("FFMPEG STUDIO")
        title.setFont(QFont("Courier New", 20, QFont.Bold))
        title.setStyleSheet("color: #f43f5e;")
        layout.addWidget(title)
        
        layout.addWidget(QLabel("Media Input File:"))
        self.ffmpeg_input = QLineEdit()
        layout.addWidget(self.ffmpeg_input)
        
        file_btn = QPushButton("Browse File")
        file_btn.clicked.connect(self.browse_ffmpeg_file)
        layout.addWidget(file_btn)
        
        layout.addWidget(QLabel("Action:"))
        self.ffmpeg_action = QComboBox()
        self.ffmpeg_action.addItems(["Extract Audio (MP3)", "Convert Format (MP4)", "Compress Video"])
        layout.addWidget(self.ffmpeg_action)
        
        convert_btn = QPushButton("PROCESS FILE")
        convert_btn.clicked.connect(self.run_ffmpeg_action)
        layout.addWidget(convert_btn)
        
        layout.addStretch()
        self.pages.addWidget(page)

    def browse_ffmpeg_file(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Open Media File", "")
        if fp:
            self.ffmpeg_input.setText(fp)

    def run_ffmpeg_action(self):
        fp = self.ffmpeg_input.text().strip()
        if not os.path.exists(fp):
            QMessageBox.critical(self, "Error", "Input file not found!")
            return
            
        action = self.ffmpeg_action.currentText()
        self.status_label.setText("SYSTEM: FFMPEG ACTIVE")
        
        success = False
        msg = ""
        if "Extract" in action:
            success, msg = ffmpeg.extract_audio(fp)
        elif "Convert" in action:
            success, msg = ffmpeg.convert_format(fp, "mp4")
        elif "Compress" in action:
            success, msg = ffmpeg.compress_video(fp)
            
        self.status_label.setText("SYSTEM: READY")
        if success:
            QMessageBox.information(self, "FFmpeg Studio", f"Processing completed successfully!")
            self.refresh_library()
        else:
            QMessageBox.critical(self, "FFmpeg Failed", f"FFmpeg error: {msg}")

    # 7. Settings Page
    def setup_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(45, 45, 45, 45)
        layout.setSpacing(15)
        
        title = QLabel("SETTINGS CENTER")
        title.setFont(QFont("Courier New", 20, QFont.Bold))
        title.setStyleSheet("color: #f43f5e;")
        layout.addWidget(title)
        
        layout.addWidget(QLabel("Download Folder Directory:"))
        self.set_dl_dir = QLineEdit()
        self.set_dl_dir.setText(config.get("download_dir"))
        layout.addWidget(self.set_dl_dir)
        
        dir_btn = QPushButton("Select Folder")
        dir_btn.clicked.connect(self.browse_settings_dir)
        layout.addWidget(dir_btn)
        
        layout.addWidget(QLabel("Speed Limit (e.g. 500K, 2M):"))
        self.set_speed = QLineEdit()
        self.set_speed.setText(config.get("speed_limit"))
        layout.addWidget(self.set_speed)
        
        self.sound_check = QCheckBox("Enable Sound Alerts")
        self.sound_check.setChecked(config.get("sound_alerts"))
        layout.addWidget(self.sound_check)
        
        self.notif_check = QCheckBox("Enable System Notifications")
        self.notif_check.setChecked(config.get("notifications"))
        layout.addWidget(self.notif_check)
        
        save_btn = QPushButton("SAVE CONFIGURATION")
        save_btn.clicked.connect(self.save_gui_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        self.pages.addWidget(page)

    def browse_settings_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Directory", config.get("download_dir"))
        if folder:
            self.set_dl_dir.setText(folder)

    def save_gui_settings(self):
        config.set("download_dir", self.set_dl_dir.text().strip())
        config.set("speed_limit", self.set_speed.text().strip())
        config.set("sound_alerts", self.sound_check.isChecked())
        config.set("notifications", self.notif_check.isChecked())
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        self.refresh_home_stats()

    # 8. About Page
    def setup_about_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(45, 45, 45, 45)
        
        title = QLabel("F-SOCIETY YT-DLP PRO")
        title.setFont(QFont("Courier New", 22, QFont.Bold))
        title.setStyleSheet("color: #f43f5e;")
        layout.addWidget(title)
        
        layout.addWidget(QLabel("Version: 1.0.0 (Release Edition)"))
        layout.addWidget(QLabel("Engine: yt-dlp compatibility wrappers"))
        layout.addWidget(QLabel("Diagnostics: fs --doctor report checks supported"))
        
        layout.addSpacing(30)
        quote = QLabel("Leave me alone. We have a lot of work to do.\n- Elliot Alderson")
        quote.setStyleSheet("font-style: italic; color: #38bdf8;")
        layout.addWidget(quote)
        
        layout.addStretch()
        self.pages.addWidget(page)

def launch_gui():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
