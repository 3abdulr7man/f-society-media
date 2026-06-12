import os
import sqlite3
import json
import datetime
from pathlib import Path

DB_FILE = str(Path(__file__).parent.parent.parent.resolve() / "f_society.db")
HISTORY_JSON = str(Path(__file__).parent.parent.parent.resolve() / "history.json")
LOG_JSON = str(Path(__file__).parent.parent.parent.resolve() / "download_log.json")
SETTINGS_JSON = str(Path(__file__).parent.parent.parent.resolve() / "settings.json")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create downloads table (download_log.json)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            type TEXT,
            quality TEXT,
            status TEXT,
            time TEXT,
            platform TEXT
        )
    """)
    
    # Create history table (history.json)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            type TEXT,
            quality TEXT,
            time TEXT,
            size TEXT,
            platform TEXT
        )
    """)
    
    # Create queue table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            mode TEXT,
            quality TEXT,
            status TEXT
        )
    """)
    
    # Create settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    # Create preferences table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    
    # Run migrations from old JSON files if they exist
    migrate_from_json()

def migrate_from_json():
    # Only migrate if migrations haven't run or DB is empty
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Settings Migration
    cursor.execute("SELECT COUNT(*) FROM settings")
    if cursor.fetchone()[0] == 0 and os.path.exists(SETTINGS_JSON):
        try:
            with open(SETTINGS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in data.items():
                    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, str(v)))
            conn.commit()
        except Exception as e:
            print(f"Failed to migrate settings.json: {e}")

    # History Migration
    cursor.execute("SELECT COUNT(*) FROM history")
    if cursor.fetchone()[0] == 0 and os.path.exists(HISTORY_JSON):
        try:
            with open(HISTORY_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        cursor.execute("""
                            INSERT INTO history (url, type, quality, time, size, platform)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            item.get("url"),
                            item.get("type"),
                            item.get("quality"),
                            item.get("time"),
                            item.get("size"),
                            item.get("platform")
                        ))
            conn.commit()
        except Exception as e:
            print(f"Failed to migrate history.json: {e}")
            
    # Downloads Log Migration
    cursor.execute("SELECT COUNT(*) FROM downloads")
    if cursor.fetchone()[0] == 0 and os.path.exists(LOG_JSON):
        try:
            with open(LOG_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        cursor.execute("""
                            INSERT INTO downloads (url, type, quality, status, time, platform)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            item.get("url"),
                            item.get("type"),
                            item.get("quality"),
                            item.get("status"),
                            item.get("time"),
                            item.get("platform")
                        ))
            conn.commit()
        except Exception as e:
            print(f"Failed to migrate download_log.json: {e}")

    conn.close()

# Queue Operations
def get_queue():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM queue")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_to_queue(url, mode, quality=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO queue (url, mode, quality, status)
        VALUES (?, ?, ?, 'pending')
    """, (url, mode, quality))
    conn.commit()
    conn.close()

def clear_queue():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM queue")
    conn.commit()
    conn.close()

# History Operations
def get_history(limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_history(url, media_type, quality="", size="", platform=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO history (url, type, quality, time, size, platform)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (url, media_type, quality, str(datetime.datetime.now()), size, platform))
    # Enforce MAX_HISTORY limit
    cursor.execute("SELECT id FROM history ORDER BY id DESC LIMIT 1 OFFSET 49")
    offset_row = cursor.fetchone()
    if offset_row:
        cursor.execute("DELETE FROM history WHERE id <= ?", (offset_row[0],))
    conn.commit()
    conn.close()

# Download Log Operations
def get_download_logs(limit=200):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM downloads ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_download_log(url, media_type, quality="", status="success", platform=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO downloads (url, type, quality, status, time, platform)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (url, media_type, quality, status, str(datetime.datetime.now()), platform))
    # Keep logs capped
    cursor.execute("SELECT id FROM downloads ORDER BY id DESC LIMIT 1 OFFSET 199")
    offset_row = cursor.fetchone()
    if offset_row:
        cursor.execute("DELETE FROM downloads WHERE id <= ?", (offset_row[0],))
    conn.commit()
    conn.close()

def clear_download_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM downloads")
    conn.commit()
    conn.close()

# Settings Operations
def get_settings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    rows = cursor.fetchall()
    conn.close()
    return {r['key']: r['value'] for r in rows}

def save_setting(key, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()
