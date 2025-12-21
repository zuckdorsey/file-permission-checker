import sqlite3
import os
from datetime import datetime

def init_database():
    try:
        conn = sqlite3.connect('scan_logs.db', timeout=10)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_date DATETIME,
                folder_path TEXT,
                total_files INTEGER,
                total_size INTEGER,
                high_risk INTEGER,
                medium_risk INTEGER,
                low_risk INTEGER,
                duration REAL,
                cache_key TEXT UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS encryption_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                operation TEXT,
                file_path TEXT,
                file_size INTEGER,
                status TEXT,
                hash TEXT,
                error_message TEXT,
                duration REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                backup_name TEXT,
                file_count INTEGER,
                total_size INTEGER,
                backup_path TEXT,
                status TEXT,
                description TEXT,
                duration REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permission_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                file_path TEXT,
                old_permission TEXT,
                new_permission TEXT,
                operation TEXT,
                user TEXT,
                success BOOLEAN,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scan_date ON scan_logs(scan_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_encryption_timestamp ON encryption_logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_backup_timestamp ON backup_logs(timestamp)')
        
        conn.commit()
        
        try:
            os.chmod('scan_logs.db', 0o600)
            for ext in ['-wal', '-shm']:
                wal_file = f'scan_logs.db{ext}'
                if os.path.exists(wal_file):
                    os.chmod(wal_file, 0o600)
        except:
            pass
        
        return conn
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        return sqlite3.connect(':memory:')

def log_scan(conn, scan_data: dict):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scan_logs 
            (scan_date, folder_path, total_files, total_size, high_risk, medium_risk, low_risk, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            scan_data.get('folder_path', ''),
            scan_data.get('total_files', 0),
            scan_data.get('total_size', 0),
            scan_data.get('high_risk', 0),
            scan_data.get('medium_risk', 0),
            scan_data.get('low_risk', 0),
            scan_data.get('duration', 0)
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False

def log_encryption(conn, encryption_data: dict):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO encryption_logs 
            (timestamp, operation, file_path, file_size, status, hash, error_message, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            encryption_data.get('operation', ''),
            encryption_data.get('file_path', ''),
            encryption_data.get('file_size', 0),
            encryption_data.get('status', ''),
            encryption_data.get('hash', ''),
            encryption_data.get('error_message', ''),
            encryption_data.get('duration', 0)
        ))
        conn.commit()
        return True
    except:
        return False

def log_backup(conn, backup_data: dict):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO backup_logs 
            (timestamp, backup_name, file_count, total_size, backup_path, status, description, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            backup_data.get('backup_name', ''),
            backup_data.get('file_count', 0),
            backup_data.get('total_size', 0),
            backup_data.get('backup_path', ''),
            backup_data.get('status', ''),
            backup_data.get('description', ''),
            backup_data.get('duration', 0)
        ))
        conn.commit()
        return True
    except:
        return False

def log_permission_change(conn, change_data: dict):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO permission_changes 
            (timestamp, file_path, old_permission, new_permission, operation, user, success)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            change_data.get('file_path', ''),
            change_data.get('old_permission', ''),
            change_data.get('new_permission', ''),
            change_data.get('operation', ''),
            change_data.get('user', ''),
            change_data.get('success', False)
        ))
        conn.commit()
        return True
    except:
        return False

def get_scan_history(conn, limit=100):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM scan_logs 
            ORDER BY scan_date DESC 
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()
    except:
        return []

def get_statistics(conn):
    try:
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM scan_logs')
        total_scans = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(total_files) FROM scan_logs')
        total_files = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(total_size) FROM scan_logs')
        total_size = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT folder_path, total_files, scan_date 
            FROM scan_logs 
            ORDER BY scan_date DESC 
            LIMIT 5
        ''')
        recent_scans = cursor.fetchall()
        
        return {
            'total_scans': total_scans,
            'total_files': total_files,
            'total_size': total_size,
            'recent_scans': recent_scans
        }
    except:
        return {}
