import os
import threading
import queue
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal, QObject

from core.security import SecurityManager
from core.secure_memory import SecureString, secure_delete_file
from core.integrity import IntegrityManager


class EncryptionWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int, str)
    error = pyqtSignal(str)
    
    def __init__(self, mode: str, files: list, password: str):
        super().__init__()
        self.mode = mode
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
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            result = self.security_manager.encrypt_data(data, self.password)
            encrypted_data = result['data']
            salt = result['salt']
            
            enc_path = filepath + ".enc"
            
            with open(enc_path, 'wb') as f:
                f.write(salt)
                f.write(encrypted_data)
            
            self.integrity_manager.log_audit_event(
                'file_encrypted', filepath, 
                f"Encrypted to {os.path.basename(enc_path)}"
            )
            
            secure_delete_file(filepath)
            
            return True
        except Exception as e:
            raise e

    def _decrypt_file(self, filepath: str) -> bool:
        try:
            if not filepath.endswith('.enc'):
                return False
                
            with open(filepath, 'rb') as f:
                salt = f.read(16)
                encrypted_data = f.read()
            
            decrypted_data = self.security_manager.decrypt_data(
                encrypted_data, self.password, salt
            )
            
            orig_path = filepath[:-4]
            with open(orig_path, 'wb') as f:
                f.write(decrypted_data)
                
            self.integrity_manager.log_audit_event(
                'file_decrypted', filepath,
                f"Decrypted to {os.path.basename(orig_path)}"
            )
            
            os.remove(filepath)
            
            return True
        except Exception as e:
            raise e
