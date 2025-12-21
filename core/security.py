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
    
    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts = {}
        self.lock = threading.Lock()
    
    def check_limit(self, key: str) -> Dict:
        with self.lock:
            now = time.time()
            if key in self.attempts:
                self.attempts[key] = [t for t in self.attempts[key] 
                                    if now - t < self.window_seconds]
            
            current_attempts = len(self.attempts.get(key, []))
            is_allowed = current_attempts < self.max_attempts
            
            return {
                'allowed': is_allowed,
                'current_attempts': current_attempts,
                'remaining': self.max_attempts - current_attempts,
                'wait_time': 0 if is_allowed else self.window_seconds
            }
    
    def record_attempt(self, key: str, success: bool = False):
        with self.lock:
            if success:
                if key in self.attempts:
                    del self.attempts[key]
            else:
                if key not in self.attempts:
                    self.attempts[key] = []
                self.attempts[key].append(time.time())


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
