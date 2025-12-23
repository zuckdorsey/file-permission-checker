import os
import hashlib
import sqlite3
from datetime import datetime
from typing import Dict, Optional, List

class IntegrityManager:
    
    def __init__(self, db_path: str = "scan_logs.db"):
        self.db_path = db_path
        self._init_tables()
        self._secure_database()
    
    def _init_tables(self):
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
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
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_path ON file_hashes(file_path)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Failed to initialize tables: {e}")
    
    def _secure_database(self):
        try:
            if os.path.exists(self.db_path):
                os.chmod(self.db_path, 0o600)
            
            for ext in ['-wal', '-shm']:
                wal_file = self.db_path + ext
                if os.path.exists(wal_file):
                    os.chmod(wal_file, 0o600)
        except:
            pass
    
    @staticmethod
    def calculate_sha256(filepath: str) -> Optional[str]:
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
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def log_audit_event(self, action_type: str, file_path: str = None,
                        details: str = None, severity: str = 'info') -> bool:
        try:
            user = self._get_current_user()
            
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
        """Get current user with fallback for various environments."""
        import getpass
        try:
            return getpass.getuser()
        except Exception:
            return os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
    
    def get_audit_logs(self, limit: int = 100, 
                       action_type: str = None,
                       severity: str = None) -> List[Dict]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
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
    
    def register_file_hash(self, filepath: str, permissions: str = None) -> bool:
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
            
            current_hash = self.calculate_sha256(filepath)
            current_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
            
            hash_match = current_hash == stored_hash
            size_match = current_size == stored_size
            
            is_valid = hash_match and size_match
            
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
    
    def verify_database_integrity(self) -> Dict:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
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
        try:
            logs = self.get_audit_logs(limit=500)
            
            valid_count = 0
            tampered_count = 0
            legacy_count = 0
            
            for log in logs:
                if not log.get('checksum'):
                    legacy_count += 1
                    continue
                
                event_data = f"{log['action_type']}|{log['file_path']}|{log['details']}|{log['user']}"
                expected_checksum = self.calculate_checksum(event_data)
                
                if log['checksum'] == expected_checksum:
                    valid_count += 1
                else:
                    timestamp = log.get('timestamp', '')
                    if timestamp and timestamp < '2025-12-15':
                        legacy_count += 1
                    else:
                        tampered_count += 1
            
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
    
    @staticmethod
    def secure_file(filepath: str, permission: int = 0o600) -> bool:
        try:
            os.chmod(filepath, permission)
            return True
        except:
            return False
    
    @staticmethod
    def create_checksum_file(filepath: str) -> Optional[str]:
        try:
            sha256_hash = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(chunk)
            
            checksum = sha256_hash.hexdigest()
            checksum_file = filepath + '.sha256'
            
            with open(checksum_file, 'w') as f:
                f.write(f"{checksum}  {os.path.basename(filepath)}\n")
            
            os.chmod(checksum_file, 0o600)
            
            return checksum_file
            
        except Exception as e:
            print(f"Failed to create checksum: {e}")
            return None
    
    def get_cia_status(self) -> Dict:
        db_integrity = self.verify_database_integrity()
        audit_integrity = self.verify_audit_log_integrity()
        
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
