import os
import stat
from typing import List, Tuple, Dict
from concurrent.futures import ThreadPoolExecutor

class PermissionFixer:
    """Kelas khusus untuk memperbaiki izin file"""
    
    @staticmethod
    def fix_file_permission(filepath: str, new_mode: int, is_dir: bool = False) -> Tuple[bool, str]:
        """Perbaiki izin untuk satu file/direktori"""
        try:
            # Validasi mode
            if new_mode < 0 or new_mode > 0o777:
                return False, "Mode izin tidak valid"
            
            # Cek jika file ada
            if not os.path.exists(filepath):
                return False, "File tidak ditemukan"
            
            # Dapatkan mode saat ini untuk logging
            current_mode = os.stat(filepath).st_mode & 0o777
            
            # Terapkan izin baru
            os.chmod(filepath, new_mode)
            
            # Verifikasi perubahan
            verify_mode = os.stat(filepath).st_mode & 0o777
            if verify_mode != new_mode:
                return False, f"Gagal mengatur izin (diharapkan {oct(new_mode)}, didapat {oct(verify_mode)})"
            
            return True, f"Berubah dari {oct(current_mode)} menjadi {oct(new_mode)}"
            
        except PermissionError:
            return False, "Izin ditolak"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def determine_appropriate_permission(filepath: str) -> int:
        """Tentukan izin yang sesuai berdasarkan tipe file"""
        if os.path.isdir(filepath):
            return 0o755  # Direktori
        
        if os.path.islink(filepath):
            return 0o777  # Symlink
        
        # Cek jika file dapat dieksekusi
        if os.access(filepath, os.X_OK):
            return 0o755  # File eksekusi
        
        # Cek ekstensi file
        executable_extensions = ['.sh', '.py', '.exe', '.bin', '.run', '.app']
        if any(filepath.endswith(ext) for ext in executable_extensions):
            return 0o755
        
        # Cek jika file memiliki bit eksekusi diatur
        try:
            mode = os.stat(filepath).st_mode
            if mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
                return 0o755
        except:
            pass
        
        # Default untuk file reguler
        return 0o644
    
    @staticmethod
    def batch_fix_permissions(filepaths: List[str], progress_callback=None, 
                            custom_mode: int = None, recursive: bool = False) -> Dict:
        """
        Perbaiki izin untuk banyak file sekaligus
        Args:
            filepaths: Daftar path yang akan diperbaiki
            progress_callback: Callback untuk progress (0-100)
            custom_mode: Mode spesifik opsional (misal 0o755). Jika None, deteksi otomatis.
            recursive: Terapkan secara rekursif untuk direktori
        """
        # Expand direktori jika rekursif
        all_paths = []
        if recursive:
            for path in filepaths:
                if os.path.exists(path):
                    all_paths.append(path)
                    if os.path.isdir(path):
                        for root, dirs, files in os.walk(path):
                            for d in dirs: all_paths.append(os.path.join(root, d))
                            for f in files: all_paths.append(os.path.join(root, f))
        else:
            all_paths = filepaths

        # Hapus duplikat
        all_paths = list(set(all_paths))

        results = {
            'total': len(all_paths),
            'success': 0,
            'failed': 0,
            'errors': [],
            'details': []
        }
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for filepath in all_paths:
                if not os.path.exists(filepath):
                    continue
                
                # Tentukan mode
                if custom_mode is not None:
                    # Jika direktori dan rekursif, pastikan execute bit untuk traversal
                    if os.path.isdir(filepath) and (custom_mode & 0o400):
                        new_mode = custom_mode | 0o100 # Pastikan owner exec jika owner read
                    else:
                        new_mode = custom_mode
                else:
                    new_mode = PermissionFixer.determine_appropriate_permission(filepath)
                
                is_dir = os.path.isdir(filepath)
                
                future = executor.submit(
                    PermissionFixer.fix_file_permission,
                    filepath, new_mode, is_dir
                )
                futures.append((filepath, future))
            
            for i, (filepath, future) in enumerate(futures):
                try:
                    success, message = future.result(timeout=10)
                    
                    if success:
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"{os.path.basename(filepath)}: {message}")
                    
                    results['details'].append({
                        'file': filepath,
                        'success': success,
                        'message': message
                    })
                    
                    if progress_callback:
                        progress_callback(int((i + 1) / len(futures) * 100))
                        
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"{os.path.basename(filepath)}: {str(e)}")
        
        return results