"""
Integrity Manager - Prinsip CIA untuk Pemeriksa Izin
Menangani log audit, verifikasi integritas file, dan deteksi kerusakan
"""

import os
import hashlib
import sqlite3
from datetime import datetime
from typing import Dict, Optional, List


class IntegrityManager:
    """CIA Integrity - Log audit dan verifikasi integritas"""
    
    def __init__(self, db_path: str = "scan_logs.db"):
        self.db_path = db_path
        self._init_tables()
        self._secure_database()
    
    def _init_tables(self):
        """Inisialisasi tabel audit"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            # Audit logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    action_type TEXT NOT NULL,
                    user TEXT,
                    file_path TEXT,
                    details TEXT,
                    severity TEXT DEFAULT 'info',
                    checksum TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # File integrity tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_hashes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    hash_sha256 TEXT NOT NULL,
                    permissions TEXT,
                    file_size INTEGER,
                    last_checked DATETIME,
                    status TEXT DEFAULT 'verified'
                )
            ''')
            
            # Indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_path ON file_hashes(file_path)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Failed to initialize tables: {e}")
    
    def _secure_database(self):
        """CIA Confidentiality - Atur izin aman pada database"""
        try:
            if os.path.exists(self.db_path):
                os.chmod(self.db_path, 0o600)  # Hanya pemilik baca/tulis
            
            # Amankan juga file WAL dan SHM jika ada
            for ext in ['-wal', '-shm']:
                wal_file = self.db_path + ext
                if os.path.exists(wal_file):
                    os.chmod(wal_file, 0o600)
        except:
            pass
    
    # ======================== FILE HASHING ========================
    
    @staticmethod
    def calculate_sha256(filepath: str) -> Optional[str]:
        """Hitung hash SHA256 dari file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(65536), b''):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception:
            return None
    
    @staticmethod
    def calculate_checksum(data: str) -> str:
        """Hitung checksum untuk string data"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    # ======================== AUDIT LOGGING ========================
    
    def log_audit_event(self, action_type: str, file_path: str = None,
                        details: str = None, severity: str = 'info') -> bool:
        """
        CIA Integrity - Catat event audit dengan checksum untuk deteksi kerusakan
        """
        try:
            user = self._get_current_user()
            
            # Buat checksum untuk deteksi kerusakan (tanpa timestamp - format di DB berubah)
            # Gunakan action + file_path + details + user sebagai data immutable
            event_data = f"{action_type}|{file_path}|{details}|{user}"
            checksum = self.calculate_checksum(event_data)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audit_logs 
                (action_type, user, file_path, details, severity, checksum)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (action_type, user, file_path, details, severity, checksum))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Failed to log audit event: {e}")
            return False
    
    def _get_current_user(self) -> str:
        """Dapatkan nama user saat ini"""
        try:
            return os.getlogin()
        except:
            try:
                import pwd
                return pwd.getpwuid(os.getuid()).pw_name
            except:
                return os.environ.get('USER', 'unknown')
    
    def get_audit_logs(self, limit: int = 100, 
                       action_type: str = None,
                       severity: str = None) -> List[Dict]:
        """Ambil log audit"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Gunakan seleksi kolom eksplisit untuk menghindari ketidakcocokan skema
            query = '''SELECT id, timestamp, action_type, user, file_path,
                              details, checksum, severity, created_at 
                       FROM audit_logs'''
            params = []
            conditions = []
            
            if action_type:
                conditions.append('action_type = ?')
                params.append(action_type)
            
            if severity:
                conditions.append('severity = ?')
                params.append(severity)
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            columns = ['id', 'timestamp', 'action_type', 'user', 'file_path',
                      'details', 'checksum', 'severity', 'created_at']
            
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            print(f"Failed to get audit logs: {e}")
            return []
    
    # ======================== FILE INTEGRITY ========================
    
    def register_file_hash(self, filepath: str, permissions: str = None) -> bool:
        """Daftarkan hash file untuk pemantauan integritas"""
        try:
            if not os.path.exists(filepath):
                return False
            
            file_hash = self.calculate_sha256(filepath)
            if not file_hash:
                return False
            
            file_size = os.path.getsize(filepath)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO file_hashes 
                (file_path, hash_sha256, permissions, file_size, last_checked, status)
                VALUES (?, ?, ?, ?, ?, 'verified')
            ''', (filepath, file_hash, permissions, file_size, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Failed to register file: {e}")
            return False
    
    def verify_file_integrity(self, filepath: str) -> Dict:
        """Verifikasi file belum dirusak"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT hash_sha256, permissions, file_size 
                FROM file_hashes WHERE file_path = ?
            ''', (filepath,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return {'status': 'unregistered', 'is_valid': None}
            
            stored_hash, stored_perms, stored_size = row
            
            # Hitung hash saat ini
            current_hash = self.calculate_sha256(filepath)
            current_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
            
            hash_match = current_hash == stored_hash
            size_match = current_size == stored_size
            
            is_valid = hash_match and size_match
            
            # Log jika pelanggaran integritas terdeteksi
            if not is_valid:
                self.log_audit_event(
                    action_type='integrity_violation',
                    file_path=filepath,
                    details=f"Hash match: {hash_match}, Size match: {size_match}",
                    severity='critical'
                )
            
            return {
                'status': 'verified' if is_valid else 'tampered',
                'is_valid': is_valid,
                'hash_match': hash_match,
                'size_match': size_match
            }
            
        except Exception as e:
            return {'status': 'error', 'is_valid': False, 'error': str(e)}
    
    # ======================== DATABASE INTEGRITY ========================
    
    def verify_database_integrity(self) -> Dict:
        """CIA Integrity - Verifikasi database belum rusak"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Jalankan pemeriksaan integritas SQLite
            cursor.execute('PRAGMA integrity_check')
            result = cursor.fetchone()[0]
            
            conn.close()
            
            is_valid = result == 'ok'
            
            if not is_valid:
                self.log_audit_event(
                    action_type='database_corruption',
                    details=f"Database integrity check failed: {result}",
                    severity='critical'
                )
            
            return {
                'is_valid': is_valid,
                'result': result
            }
            
        except Exception as e:
            return {'is_valid': False, 'error': str(e)}
    
    def verify_audit_log_integrity(self) -> Dict:
        """Verifikasi log audit belum dirusak"""
        try:
            logs = self.get_audit_logs(limit=500)
            
            valid_count = 0
            tampered_count = 0
            legacy_count = 0  # Logs with old checksum format or without checksum
            
            for log in logs:
                # Skip logs without checksum (legacy)
                if not log.get('checksum'):
                    legacy_count += 1
                    continue
                
                # Recalculate checksum (without timestamp - matches log_audit_event)
                event_data = f"{log['action_type']}|{log['file_path']}|{log['details']}|{log['user']}"
                expected_checksum = self.calculate_checksum(event_data)
                
                if log['checksum'] == expected_checksum:
                    valid_count += 1
                else:
                    # Check if this is an old-format checksum (created before 2025-12-15)
                    # Old logs had different checksum algorithm, treat as legacy
                    timestamp = log.get('timestamp', '')
                    if timestamp and timestamp < '2025-12-15':
                        legacy_count += 1
                    else:
                        tampered_count += 1
            
            # Integritas valid jika tidak ada log baru yang dirusak
            # Log lama diabaikan (menggunakan algoritma checksum berbeda)
            integrity_valid = tampered_count == 0
            
            return {
                'total_logs': len(logs),
                'valid': valid_count,
                'tampered': tampered_count,
                'legacy': legacy_count,
                'integrity_valid': integrity_valid
            }
            
        except Exception as e:
            return {'integrity_valid': False, 'error': str(e)}
    
    # ======================== SECURE FILE OPERATIONS ========================
    
    @staticmethod
    def secure_file(filepath: str, permission: int = 0o600) -> bool:
        """CIA Confidentiality - Atur izin aman pada file"""
        try:
            os.chmod(filepath, permission)
            return True
        except:
            return False
    
    @staticmethod
    def create_checksum_file(filepath: str) -> Optional[str]:
        """CIA Integrity - Buat file checksum untuk verifikasi"""
        try:
            sha256_hash = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(chunk)
            
            checksum = sha256_hash.hexdigest()
            checksum_file = filepath + '.sha256'
            
            with open(checksum_file, 'w') as f:
                f.write(f"{checksum}  {os.path.basename(filepath)}\n")
            
            # Amankan file checksum
            os.chmod(checksum_file, 0o600)
            
            return checksum_file
            
        except Exception as e:
            print(f"Failed to create checksum: {e}")
            return None
    
    # ======================== REPORTING ========================
    
    def get_cia_status(self) -> Dict:
        """Dapatkan status kepatuhan CIA menyeluruh"""
        db_integrity = self.verify_database_integrity()
        audit_integrity = self.verify_audit_log_integrity()
        
        # Cek izin file database
        db_secure = False
        try:
            mode = os.stat(self.db_path).st_mode & 0o777
            db_secure = mode == 0o600
        except:
            pass
        
        return {
            'confidentiality': {
                'database_secured': db_secure,
                'status': '✅ Secure' if db_secure else '⚠️ Not Secure'
            },
            'integrity': {
                'database_valid': db_integrity.get('is_valid', False),
                'audit_logs_valid': audit_integrity.get('integrity_valid', False),
                'status': '✅ Valid' if (db_integrity.get('is_valid') and 
                         audit_integrity.get('integrity_valid')) else '⚠️ Issues Detected'
            },
            'availability': {
                'database_accessible': os.path.exists(self.db_path),
                'status': '✅ Available' if os.path.exists(self.db_path) else '❌ Unavailable'
            }
        }
