"""
Encryption Manager - CIA Confidentiality (Kerahasiaan CIA)
Menangani enkripsi dan dekripsi file secara aman
"""

import os
import threading
import queue
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal, QObject

from core.security import SecurityManager
from core.secure_memory import SecureString, secure_delete_file
from core.integrity import IntegrityManager


class EncryptionWorker(QObject):
    """Worker untuk tugas enkripsi asinkron"""
    finished = pyqtSignal()
    progress = pyqtSignal(int, str)
    error = pyqtSignal(str)
    
    def __init__(self, mode: str, files: list, password: str):
        super().__init__()
        self.mode = mode  # 'encrypt' or 'decrypt'
        self.files = files
        self.password = password
        self.security_manager = SecurityManager()
        self.integrity_manager = IntegrityManager()
        self._is_cancelled = False
        
    def run(self):
        total = len(self.files)
        success_count = 0
        
        for i, filepath in enumerate(self.files):
            if self._is_cancelled:
                break
                
            try:
                self.progress.emit(int((i / total) * 100), f"Processing {os.path.basename(filepath)}...")
                
                if self.mode == 'encrypt':
                    if self._encrypt_file(filepath):
                        success_count += 1
                else:
                    if self._decrypt_file(filepath):
                        success_count += 1
                        
            except Exception as e:
                self.error.emit(f"Error processing {filepath}: {str(e)}")
        
        self.finished.emit()
        
    def cancel(self):
        self._is_cancelled = True

    def _encrypt_file(self, filepath: str) -> bool:
        """Enkripsi satu file"""
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            result = self.security_manager.encrypt_data(data, self.password)
            encrypted_data = result['data']
            salt = result['salt']
            
            # Buat file terenkripsi
            enc_path = filepath + ".enc"
            
            # Format: SALT (16 bytes) + ENCRYPTED_DATA
            with open(enc_path, 'wb') as f:
                f.write(salt)
                f.write(encrypted_data)
            
            # Catat audit
            self.integrity_manager.log_audit_event(
                'file_encrypted', filepath, 
                f"Encrypted to {os.path.basename(enc_path)}"
            )
            
            # Hapus file asli secara aman
            secure_delete_file(filepath)
            
            return True
        except Exception as e:
            raise e

    def _decrypt_file(self, filepath: str) -> bool:
        """Dekripsi satu file"""
        try:
            if not filepath.endswith('.enc'):
                return False
                
            with open(filepath, 'rb') as f:
                # Baca salt (16 byte pertama)
                salt = f.read(16)
                # Baca sisanya
                encrypted_data = f.read()
            
            # Dekripsi
            decrypted_data = self.security_manager.decrypt_data(
                encrypted_data, self.password, salt
            )
            
            # Kembalikan file asli
            orig_path = filepath[:-4] # Remove .enc
            with open(orig_path, 'wb') as f:
                f.write(decrypted_data)
                
            # Catat audit
            self.integrity_manager.log_audit_event(
                'file_decrypted', filepath,
                f"Decrypted to {os.path.basename(orig_path)}"
            )
            
            # Hapus file terenkripsi (tidak perlu hapus aman karena sudah terenkripsi)
            os.remove(filepath)
            
            return True
        except Exception as e:
            raise e
