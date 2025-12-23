r"""╔══════════════════════════════════════════════════════════════════╗
║    ____                 _                      _                  ║
║   |  _ \  _____   _____| | ___  _ __   ___  __| |                ║
║   | | | |/ _ \ \ / / _ \ |/ _ \| '_ \ / _ \/ _` |               ║
║   | |_| |  __/\ V /  __/ | (_) | |_) |  __/ (_| |               ║
║   |____/ \___| \_/ \___|_|\___/| .__/ \___|\__,_|               ║
║                                 |_|                               ║
╠══════════════════════════════════════════════════════════════════╣
║  by zuckdorsey • 2025                                         ║
║  https://github.com/zuckdorsey                                                       ║
╚══════════════════════════════════════════════════════════════════╝"""

import os
import threading
import queue
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal, QObject

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
        """
        Enkripsi file dengan buffer streaming untuk file besar.
        
        Menggunakan potongan baca/tulis untuk mencegah kehabisan memori pada file besar.
        File asli dipindahkan ke folder .quarantine/ (TIDAK dihapus).
        
        Format file: [garam (16 byte)] [verifikasi_hash (32 byte)] [data_terenkripsi]
        
        Catatan: Fernet tidak mendukung enkripsi streaming yang sebenarnya, begitu pula file
        dimuat ke dalam memori. File besar (>100MB) akan menampilkan peringatan.
        """
        CHUNK_SIZE = 64 * 1024
        MAX_FILE_SIZE = 100 * 1024 * 1024
        
        try:
            if os.path.islink(filepath):
                self.error.emit(f"Skipping symlink: {os.path.basename(filepath)}")
                return False
            
            file_size = os.path.getsize(filepath)
            
            MAX_FILE_SIZE = 500 * 1024 * 1024

            file_size = os.path.getsize(filepath)
            if file_size > MAX_FILE_SIZE:
                self.error.emit(f"Skipping {os.path.basename(filepath)}: File too large ({file_size/1024/1024:.2f} MB). Max supported is 500MB.")
                return False
            
            file_chunks = []
            bytes_read = 0
            
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    file_chunks.append(chunk)
                    bytes_read += len(chunk)
                    
                    if file_size > MAX_FILE_SIZE:
                        progress = int((bytes_read / file_size) * 50)
                        self.progress.emit(progress, f"Reading {os.path.basename(filepath)}...")
            
            data = b''.join(file_chunks)
            del file_chunks
            
            result = self.security_manager.encrypt_data(data, self.password)
            encrypted_data = result['data']
            salt = result['salt']
            verification_hash = result.get('verification_hash', b'')
            del data
            
            enc_path = filepath + ".enc"
            
            with open(enc_path, 'wb') as f:
                f.write(salt)
                f.write(verification_hash)
                
                offset = 0
                while offset < len(encrypted_data):
                    f.write(encrypted_data[offset:offset + CHUNK_SIZE])
                    offset += CHUNK_SIZE
            
            os.chmod(enc_path, 0o600, follow_symlinks=False)
            
            self.integrity_manager.log_audit_event(
                'file_encrypted', filepath, 
                f"Encrypted to {os.path.basename(enc_path)} (size: {file_size} bytes)"
            )
            
            self._quarantine_file(filepath)
            
            return True
        except Exception as e:
            raise e
    
    def _quarantine_file(self, filepath: str) -> bool:
        """
        Pindahkan file ke folder .quarantine alih-alih menghapus.
        
        Pengguna dapat menghapus file yang dikarantina secara manual setelah verifikasi.
        """
        try:
            import shutil
            from datetime import datetime
            
            if os.path.islink(filepath):
                return False
            
            parent_dir = os.path.dirname(filepath)
            quarantine_dir = os.path.join(parent_dir, '.quarantine')
            
            if not os.path.exists(quarantine_dir):
                os.makedirs(quarantine_dir, mode=0o700)
            
            filename = os.path.basename(filepath)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            quarantine_name = f"{timestamp}_{filename}"
            quarantine_path = os.path.join(quarantine_dir, quarantine_name)
            
            shutil.move(filepath, quarantine_path)
            
            os.chmod(quarantine_path, 0o600, follow_symlinks=False)
            
            self.integrity_manager.log_audit_event(
                'file_quarantined', filepath,
                f"Moved to quarantine: {quarantine_path}"
            )
            
            return True
            
        except Exception as e:
            self.integrity_manager.log_audit_event(
                'quarantine_failed', filepath,
                f"Failed to quarantine: {str(e)}",
                severity='warning'
            )
            return False

    def _decrypt_file(self, filepath: str) -> bool:
        """
        Dekripsi file dengan verifikasi kata sandi.
        
        Menaikkan:
            InvalidPasswordError: Jika kata sandi salah
            DecryptionError: Jika dekripsi gagal
        """
        from core.security import InvalidPasswordError, DecryptionError, DecryptionRateLimitError
        
        try:
            if not filepath.endswith('.enc'):
                self.error.emit(f"File {os.path.basename(filepath)} bukan file terenkripsi (.enc)")
                return False
            
            with open(filepath, 'rb') as f:
                salt = f.read(16)
                verification_hash = f.read(32)
                encrypted_data = f.read()
            
            if len(verification_hash) + len(encrypted_data) < 50:
                with open(filepath, 'rb') as f:
                    salt = f.read(16)
                    encrypted_data = f.read()
                verification_hash = None
            
            try:
                decrypted_data = self.security_manager.decrypt_data(
                    encrypted_data, 
                    self.password, 
                    salt,
                    verification_hash
                )
            except InvalidPasswordError as e:
                self.error.emit(f"❌ {e.message}")
                return False
            except DecryptionRateLimitError as e:
                self.error.emit(f"⏳ {e.message}")
                return False
            except DecryptionError as e:
                self.error.emit(f"❌ Dekripsi gagal: {e.message}")
                return False
            
            orig_path = filepath[:-4]
            with open(orig_path, 'wb') as f:
                f.write(decrypted_data)
                
            self.integrity_manager.log_audit_event(
                'file_decrypted', filepath,
                f"Decrypted to {os.path.basename(orig_path)}"
            )
            
            os.remove(filepath)
            
            return True
            
        except InvalidPasswordError as e:
            self.error.emit(f"❌ {e.message}")
            return False
        except DecryptionRateLimitError as e:
            self.error.emit(f"⏳ {e.message}")
            return False
        except Exception as e:
            error_msg = str(e).lower()
            if 'invalidtoken' in error_msg or 'token' in error_msg:
                self.error.emit("❌ Sandi salah! Password yang Anda masukkan tidak valid.")
            else:
                self.error.emit(f"❌ Error dekripsi: {str(e)}")
            return False
