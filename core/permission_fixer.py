import os
import stat
from typing import List, Tuple, Dict
from concurrent.futures import ThreadPoolExecutor

class PermissionFixer:
    """Class khusus untuk memperbaiki permissions"""
    
    @staticmethod
    def fix_file_permission(filepath: str, new_mode: int, is_dir: bool = False) -> Tuple[bool, str]:
        """Fix permission untuk single file/directory"""
        try:
            # Validasi mode
            if new_mode < 0 or new_mode > 0o777:
                return False, "Invalid permission mode"
            
            # Check if file exists
            if not os.path.exists(filepath):
                return False, "File tidak ditemukan"
            
            # Get current mode untuk logging
            current_mode = os.stat(filepath).st_mode & 0o777
            
            # Apply new permission
            os.chmod(filepath, new_mode)
            
            # Verify the change
            verify_mode = os.stat(filepath).st_mode & 0o777
            if verify_mode != new_mode:
                return False, f"Failed to set permission (expected {oct(new_mode)}, got {oct(verify_mode)})"
            
            return True, f"Changed from {oct(current_mode)} to {oct(new_mode)}"
            
        except PermissionError:
            return False, "Permission denied"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def determine_appropriate_permission(filepath: str) -> int:
        """Tentukan permission yang appropriate berdasarkan file type"""
        if os.path.isdir(filepath):
            return 0o755  # Directory
        
        if os.path.islink(filepath):
            return 0o777  # Symlink
        
        # Check if file is executable
        if os.access(filepath, os.X_OK):
            return 0o755  # Executable file
        
        # Check file extension
        executable_extensions = ['.sh', '.py', '.exe', '.bin', '.run', '.app']
        if any(filepath.endswith(ext) for ext in executable_extensions):
            return 0o755
        
        # Check if file has executable bit set
        try:
            mode = os.stat(filepath).st_mode
            if mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
                return 0o755
        except:
            pass
        
        # Default for regular files
        return 0o644
    
    @staticmethod
    def batch_fix_permissions(filepaths: List[str], progress_callback=None) -> Dict:
        """Fix permissions untuk batch files"""
        results = {
            'total': len(filepaths),
            'success': 0,
            'failed': 0,
            'errors': [],
            'details': []
        }
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for filepath in filepaths:
                if not os.path.exists(filepath):
                    continue
                
                # Determine appropriate permission
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