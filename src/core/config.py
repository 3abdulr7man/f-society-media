import os
from pathlib import Path
from src.core import database

DEFAULT_SETTINGS = {
    "download_dir": str(Path.home() / "Downloads" / "F-SOCIETY"),
    "default_video_quality": "best",
    "default_audio_quality": "192",
    "max_concurrent": 3,
    "theme": "default",
    "ffmpeg_warnings": True,
    "output_template": "%(title)s.%(ext)s",
    "auto_rename_duplicates": True,
    "cookie_file": "",
    "speed_limit": "",
    "notifications": True,
    "language": "en",
    "sound_alerts": True,
}

# Theme settings
class C:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"
    WHITE = "\033[97m"

THEMES = {
    "default": {"info": C.CYAN, "success": C.GREEN, "warning": C.YELLOW, "error": C.RED, "menu": C.MAGENTA, "prompt": C.BLUE, "dim": C.DIM},
    "light": {"info": C.BLUE, "success": C.GREEN, "warning": C.YELLOW, "error": C.RED, "menu": C.WHITE, "prompt": C.CYAN, "dim": C.DIM},
    "matrix": {"info": C.GREEN, "success": C.GREEN, "warning": C.GREEN, "error": C.RED, "menu": C.GREEN, "prompt": C.GREEN, "dim": C.DIM},
    "hacker": {"info": C.RED, "success": C.RED, "warning": C.YELLOW, "error": C.RED, "menu": C.RED, "prompt": C.RED, "dim": C.DIM},
    "ocean": {"info": C.CYAN, "success": C.CYAN, "warning": C.YELLOW, "error": C.RED, "menu": C.BLUE, "prompt": C.CYAN, "dim": C.DIM},
    "purple": {"info": C.MAGENTA, "success": C.MAGENTA, "warning": C.YELLOW, "error": C.RED, "menu": C.MAGENTA, "prompt": C.MAGENTA, "dim": C.DIM},
}

current_theme = dict(THEMES["default"])

LANG_DATA = {
    "en": {
        "check_env": "Checking environment...",
        "status_python": "Python",
        "status_ytdlp": "yt-dlp",
        "status_ffmpeg": "FFmpeg",
        "status_aria2c": "Aria2c",
        "menu_title_download": "DOWNLOAD ENGINES",
        "menu_title_playlists": "COLLECTIONS",
        "menu_title_tools": "HACKER UTILITIES",
        "menu_title_system": "SYSTEM CONTROL",
        "menu_opt_video": "Download Video",
        "menu_opt_audio": "Download Audio",
        "menu_opt_images": "Download Photo/Gallery",
        "menu_opt_queue": "Batch Queue Manager",
        "menu_opt_scheduler": "Scheduler (Timed Downloads)",
        "menu_opt_metadata": "Metadata Tag Editor",
        "menu_opt_ffmpeg": "FFmpeg Tools (Trim/Compress)",
        "menu_opt_history_logs": "History & Logs",
        "menu_opt_update_status": "Update & Environment Status",
        "menu_opt_settings": "Configure Settings",
        "menu_opt_quit": "Quit Application",
        "prompt_url": "Enter URL: ",
        "invalid_url": "Invalid URL!",
        "save_to": "Save to",
        "download_completed": "DOWNLOAD COMPLETED!",
        "audio_completed": "AUDIO COMPLETED!",
        "images_completed": "IMAGES DOWNLOADED!",
        "playlist_completed": "PLAYLIST COMPLETED!",
        "channel_completed": "CHANNEL COMPLETED!",
        "download_failed": "Download failed!",
        "history_empty": "History empty.",
        "logs_empty": "No download logs yet.",
        "settings_download_dir": "Download Folder",
        "settings_video_quality": "Video Quality",
        "settings_audio_quality": "Audio Bitrate",
        "settings_max_concurrent": "Max Concurrent",
        "settings_theme": "Theme",
        "settings_ffmpeg_warnings": "FFmpeg Warnings",
        "settings_auto_rename": "Auto-Rename Dupes",
        "settings_cookie": "Cookie File",
        "settings_speed": "Speed Limit",
        "settings_language": "Language",
        "settings_sound": "Sound Alerts",
        "settings_notif": "Notifications",
        "enter_choice": "Select an option",
        "queue_empty": "Queue empty!",
    },
    "es": {
        "check_env": "Comprobando el entorno...",
        "status_python": "Python",
        "status_ytdlp": "yt-dlp",
        "status_ffmpeg": "FFmpeg",
        "status_aria2c": "Aria2c",
        "menu_title_download": "MOTORES DE DESCARGA",
        "menu_title_playlists": "COLECCIONES",
        "menu_title_tools": "UTILIDADES HACKER",
        "menu_title_system": "CONTROL DEL SISTEMA",
        "menu_opt_video": "Descargar Video",
        "menu_opt_audio": "Descargar Audio",
        "menu_opt_images": "Descargar Fotos/Galería",
        "menu_opt_queue": "Gestor de Cola por Lotes",
        "menu_opt_scheduler": "Programador (Descargas programadas)",
        "menu_opt_metadata": "Editor de Metadatos",
        "menu_opt_ffmpeg": "Herramientas FFmpeg (Recortar/Comprimir)",
        "menu_opt_history_logs": "Historial y Registros",
        "menu_opt_update_status": "Actualizar y Estado del Entorno",
        "menu_opt_settings": "Configurar Ajustes",
        "menu_opt_quit": "Salir de la Aplicación",
        "prompt_url": "Ingrese URL: ",
        "invalid_url": "¡URL no válida!",
        "save_to": "Guardar en",
        "download_completed": "¡DESCARGA COMPLETADA!",
        "audio_completed": "¡AUDIO COMPLETADO!",
        "images_completed": "¡IMÁGENES DESCARGADAS!",
        "playlist_completed": "¡LISTA COMPLETADA!",
        "channel_completed": "¡CANAL COMPLETADO!",
        "download_failed": "¡Descarga fallida!",
        "history_empty": "Historial vacío.",
        "logs_empty": "Aún no hay registros de descarga.",
        "settings_download_dir": "Carpeta de Descarga",
        "settings_video_quality": "Calidad de Video",
        "settings_audio_quality": "Bitrate de Audio",
        "settings_max_concurrent": "Máx Concurrentes",
        "settings_theme": "Tema",
        "settings_ffmpeg_warnings": "Advertencias de FFmpeg",
        "settings_auto_rename": "Auto-Renombrar Duplicados",
        "settings_cookie": "Archivo de Cookies",
        "settings_speed": "Límite de Velocidad",
        "settings_language": "Idioma",
        "settings_sound": "Alertas de Sonido",
        "settings_notif": "Notificaciones",
        "enter_choice": "Seleccione una opción",
        "queue_empty": "¡Cola vacía!",
    }
}

# In-memory settings cache
settings_cache = {}

def load_settings():
    global settings_cache
    settings_cache = dict(DEFAULT_SETTINGS)
    try:
        db_settings = database.get_settings()
        for k, v in db_settings.items():
            if k in DEFAULT_SETTINGS:
                # Convert types accordingly
                default_val = DEFAULT_SETTINGS[k]
                if isinstance(default_val, bool):
                    settings_cache[k] = v.lower() == 'true'
                elif isinstance(default_val, int):
                    settings_cache[k] = int(v)
                else:
                    settings_cache[k] = v
    except Exception as e:
        print(f"Error loading settings from DB: {e}")
    
    # Apply initial theme
    apply_theme(settings_cache.get("theme", "default"))
    
    # Create directory if it doesn't exist
    try:
        Path(settings_cache["download_dir"]).mkdir(parents=True, exist_ok=True)
    except:
        pass

def get(key, default=None):
    return settings_cache.get(key, default)

def set(key, value):
    settings_cache[key] = value
    try:
        database.save_setting(key, str(value))
    except Exception as e:
        print(f"Error saving setting to DB: {e}")
    if key == "theme":
        apply_theme(value)

def t(key):
    lang = get("language", "en")
    return LANG_DATA.get(lang, LANG_DATA["en"]).get(key, LANG_DATA["en"].get(key, key))

def apply_theme(theme_name):
    global current_theme
    selected = THEMES.get(theme_name, THEMES["default"])
    current_theme.update(selected)

def get_theme_color(tag):
    return current_theme.get(tag, C.RESET)

def c(tag, text=""):
    clr = get_theme_color(tag)
    return f"{clr}{text}{C.RESET}" if text else clr
