import os
import base64
import json
import time
import secrets
import threading
from typing import Tuple, Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from core.secure_memory import SecureString, SecureBuffer


class DecryptionError(Exception):
    """Base exception for decryption errors."""
    pass


class InvalidPasswordError(DecryptionError):
    """Raised when the password is incorrect."""
    
    def __init__(self, message: str = "Sandi salah!"):
        self.message = message
        super().__init__(self.message)


class DecryptionRateLimitError(DecryptionError):
    """Raised when too many failed decryption attempts."""
    
    def __init__(self, message: str, remaining_time: int = 300):
        self.message = message
        self.remaining_time = remaining_time
        super().__init__(self.message)


class RateLimiter:
    """
    Persistent rate limiter that stores failed attempts in database.
    
    Attempts are persisted to scan_logs.db, preventing reset by app restart.
    """
    
    def __init__(self, max_attempts: int = 5, window_seconds: int = 300, db_path: str = "scan_logs.db"):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_table()
    
    def _init_table(self):
        """Initialize rate limit table in database."""
        import sqlite3
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rate_limit_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    ip_address TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rate_key ON rate_limit_attempts(key)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rate_timestamp ON rate_limit_attempts(timestamp)')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Failed to initialize rate limit table: {e}")
    
    def _cleanup_old_attempts(self, key: str, conn):
        """Remove attempts older than window."""
        import sqlite3
        now = time.time()
        cutoff = now - self.window_seconds
        cursor = conn.cursor()
        cursor.execute('DELETE FROM rate_limit_attempts WHERE key = ? AND timestamp < ?', (key, cutoff))
        conn.commit()
    
    def check_limit(self, key: str) -> Dict:
        """Check if action is allowed based on persistent rate limit."""
        import sqlite3
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path, timeout=10)
                
                self._cleanup_old_attempts(key, conn)
                
                cursor = conn.cursor()
                now = time.time()
                cutoff = now - self.window_seconds
                
                cursor.execute(
                    'SELECT COUNT(*) FROM rate_limit_attempts WHERE key = ? AND timestamp >= ?',
                    (key, cutoff)
                )
                current_attempts = cursor.fetchone()[0]
                
                conn.close()
                
                is_allowed = current_attempts < self.max_attempts
                
                wait_time = 0
                if not is_allowed:
                    conn = sqlite3.connect(self.db_path, timeout=10)
                    cursor = conn.cursor()
                    cursor.execute(
                        'SELECT MIN(timestamp) FROM rate_limit_attempts WHERE key = ? AND timestamp >= ?',
                        (key, cutoff)
                    )
                    oldest = cursor.fetchone()[0]
                    conn.close()
                    if oldest:
                        wait_time = int(self.window_seconds - (now - oldest))
                
                return {
                    'allowed': is_allowed,
                    'current_attempts': current_attempts,
                    'remaining': max(0, self.max_attempts - current_attempts),
                    'wait_time': max(0, wait_time)
                }
                
            except Exception as e:
                print(f"Rate limit check failed: {e}")
                return {'allowed': True, 'current_attempts': 0, 'remaining': self.max_attempts, 'wait_time': 0}
    
    def record_attempt(self, key: str, success: bool = False):
        """Record an attempt in the persistent database."""
        import sqlite3
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path, timeout=10)
                cursor = conn.cursor()
                
                if success:
                    cursor.execute('DELETE FROM rate_limit_attempts WHERE key = ?', (key,))
                else:
                    cursor.execute(
                        'INSERT INTO rate_limit_attempts (key, timestamp) VALUES (?, ?)',
                        (key, time.time())
                    )
                
                conn.commit()
                conn.close()
                
            except Exception as e:
                print(f"Failed to record rate limit attempt: {e}")


class SecurityManager:
    
    def __init__(self):
        self.salt_file = '.master_password.secure'
        self.rate_limiter = RateLimiter()
        self.session_token = None
        self.session_expiry = 0
    
    def derive_key(self, password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
        if salt is None:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def encrypt_data(self, data: bytes, password: str) -> Dict[str, bytes]:
        """
        Encrypt data with password.
        
        Args:
            data: Data to encrypt
            password: Encryption password
        
        Returns:
            Dict with 'data' (encrypted), 'salt', and 'verification_hash'
        """
        key, salt = self.derive_key(password)
        f = Fernet(key)
        encrypted = f.encrypt(data)
        
        verification_hash = self._create_verification_hash(password, salt)
        
        return {
            'data': encrypted,
            'salt': salt,
            'verification_hash': verification_hash
        }
    
    def decrypt_data(
        self, 
        encrypted_data: bytes, 
        password: str, 
        salt: bytes,
        verification_hash: bytes = None
    ) -> bytes:
        """
        Decrypt data with password verification.
        
        Args:
            encrypted_data: Data to decrypt
            password: Decryption password
            salt: Salt used during encryption
            verification_hash: Optional hash to verify password before decryption
        
        Returns:
            Decrypted data
        
        Raises:
            InvalidPasswordError: If password is incorrect
            DecryptionError: If decryption fails for other reasons
        """
        rate_check = self.rate_limiter.check_limit("decrypt")
        if not rate_check['allowed']:
            raise DecryptionRateLimitError(
                f"Terlalu banyak percobaan gagal. Tunggu {rate_check['wait_time']} detik.",
                remaining_time=rate_check['wait_time']
            )
        
        try:
            if verification_hash:
                if not self._verify_password(password, salt, verification_hash):
                    self.rate_limiter.record_attempt("decrypt", success=False)
                    raise InvalidPasswordError("Sandi salah! Password yang Anda masukkan tidak valid.")
            
            key, _ = self.derive_key(password, salt)
            f = Fernet(key)
            
            decrypted = f.decrypt(encrypted_data)
            
            self.rate_limiter.record_attempt("decrypt", success=True)
            
            return decrypted
        
        except InvalidPasswordError:
            raise
        
        except DecryptionRateLimitError:
            raise
        
        except Exception as e:
            self.rate_limiter.record_attempt("decrypt", success=False)
            
            error_str = str(e).lower()
            if 'invalidtoken' in error_str or 'token' in error_str or 'decrypt' in error_str:
                raise InvalidPasswordError(
                    "Sandi salah! Dekripsi gagal karena password tidak valid."
                )
            
            raise DecryptionError(f"Dekripsi gagal: {str(e)}")
    
    def verify_password(self, password: str, salt: bytes, verification_hash: bytes) -> bool:
        """
        Public method to verify if a password is correct.
        
        Returns:
            True if password is correct, False otherwise
        """
        return self._verify_password(password, salt, verification_hash)
    
    def _create_verification_hash(self, password: str, salt: bytes) -> bytes:
        """Create a hash for password verification."""
        import hashlib
        data = b"VERIFY:" + password.encode() + salt
        return hashlib.sha256(data).digest()
    
    def _verify_password(self, password: str, salt: bytes, stored_hash: bytes) -> bool:
        """Verify password against stored hash."""
        expected_hash = self._create_verification_hash(password, salt)
        return secrets.compare_digest(expected_hash, stored_hash)
    
    def check_password_strength(self, password: str) -> Dict:
        score = 0
        feedback = []
        
        if len(password) < 8:
            feedback.append("Too short (min 8 chars)")
        else:
            score += 1
            if len(password) >= 12: score += 1
            
        if any(c.isupper() for c in password): score += 1
        else: feedback.append("Add uppercase letters")
            
        if any(c.islower() for c in password): score += 1
        
        if any(c.isdigit() for c in password): score += 1
        else: feedback.append("Add numbers")
            
        if any(not c.isalnum() for c in password): score += 1
        else: feedback.append("Add special characters")
        
        strength_map = {
            0: "Very Weak", 1: "Weak", 2: "Medium",
            3: "Strong", 4: "Very Strong", 5: "Excellent", 6: "Unbreakable"
        }
        
        return {
            'score': min(score, 6),
            'strength': strength_map.get(min(score, 6)),
            'feedback': feedback
        }
        
    def generate_secure_password(self, length: int = 16) -> str:
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
        return "".join(secrets.choice(alphabet) for _ in range(length))
