"""
Security Manager - CIA Confidentiality & Availability (Kerahasiaan & Ketersediaan)
Menangani enkripsi, password, dan pembatasan laju (rate limiting)
"""

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


class RateLimiter:
    """CIA Availability - Lindungi dari serangan brute force"""
    
    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts = {}  # {ip/user: [timestamp, ...]}
        self.lock = threading.Lock()
    
    def check_limit(self, key: str) -> Dict:
        """Cek apakah permintaan diizinkan"""
        with self.lock:
            now = time.time()
            # Bersihkan percobaan lama
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
        """Catat percobaan"""
        with self.lock:
            if success:
                # Reset jika sukses
                if key in self.attempts:
                    del self.attempts[key]
            else:
                if key not in self.attempts:
                    self.attempts[key] = []
                self.attempts[key].append(time.time())


class SecurityManager:
    """Mengelola kunci enkripsi dan password"""
    
    def __init__(self):
        self.salt_file = '.master_password.secure'
        self.rate_limiter = RateLimiter()
        self.session_token = None
        self.session_expiry = 0
    
    def derive_key(self, password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
        """Turunkan kunci kriptografi dari password menggunakan PBKDF2"""
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
        """Enkripsi data menggunakan AES-GCM (melalui Fernet untuk kesederhanaan)"""
        # Catatan: Fernet menggunakan AES-128-CBC dengan HMAC-SHA256
        # Untuk kebutuhan AES-GCM spesifik CIA, kita bisa mengimplementasikannya langsung
        # Tapi Fernet adalah wrapper aman standar.
        # Mari gunakan Fernet untuk konsistensi dengan implementasi sebelumnya
        
        key, salt = self.derive_key(password)
        f = Fernet(key)
        encrypted = f.encrypt(data)
        return {
            'data': encrypted,
            'salt': salt
        }
        
    def decrypt_data(self, encrypted_data: bytes, password: str, salt: bytes) -> bytes:
        """Dekripsi data"""
        key, _ = self.derive_key(password, salt)
        f = Fernet(key)
        return f.decrypt(encrypted_data)
    
    def check_password_strength(self, password: str) -> Dict:
        """Analisis kekuatan password"""
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
        """Generate password yang aman secara kriptografi"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
        return "".join(secrets.choice(alphabet) for _ in range(length))
