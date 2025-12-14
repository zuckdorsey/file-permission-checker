import os
import stat
from datetime import datetime
from typing import Dict, Optional, List
from PyQt5.QtCore import QThread, pyqtSignal, QMutex

class ScanThread(QThread):
    """Thread untuk scanning folder"""
    progress = pyqtSignal(int, str)
    file_found = pyqtSignal(dict)
    stats_update = pyqtSignal(dict)
    finished = pyqtSignal(list, dict)
    error = pyqtSignal(str, str)
    
    def __init__(self, folder_path: str, custom_rules: Dict, max_files: int = 10000):
        super().__init__()
        self.folder_path = folder_path
        self.custom_rules = custom_rules
        self.max_files = max_files
        self.all_files = []
        self.is_cancelled = False
        self.mutex = QMutex()
        self.file_count = 0
        self.total_files = 0
        
        # Statistics
        self.stats = {
            'total_files': 0,
            'total_size': 0,
            'high_risk': 0,
            'medium_risk': 0,
            'low_risk': 0,
            'symlinks': 0,
            'permission_denied': 0,
            'start_time': None,
            'end_time': None,
            'duration': 0
        }
    
    def cancel(self):
        """Cancel scanning process"""
        self.mutex.lock()
        self.is_cancelled = True
        self.mutex.unlock()
    
    def run(self):
        """Main scanning process"""
        try:
            self.stats['start_time'] = datetime.now().isoformat()
            
            # Scan files
            self._scan_folder(self.folder_path)
            
            # Update final stats
            self.stats['end_time'] = datetime.now().isoformat()
            self.stats['duration'] = (datetime.now() - datetime.fromisoformat(self.stats['start_time'])).total_seconds()
            
            self.progress.emit(100, "Scan completed")
            self.finished.emit(self.all_files, self.stats)
            
        except Exception as e:
            import traceback
            self.error.emit(str(e), traceback.format_exc())
    
    def _scan_folder(self, folder_path: str):
        """Scan folder recursive"""
        try:
            for root, dirs, files in os.walk(folder_path):
                # Check cancellation
                self.mutex.lock()
                if self.is_cancelled:
                    self.mutex.unlock()
                    return
                self.mutex.unlock()
                
                for file in files:
                    filepath = os.path.join(root, file)
                    file_data = self._scan_file(filepath)
                    if file_data:
                        self.all_files.append(file_data)
                        self.file_found.emit(file_data)
                        self._update_stats(file_data)
                        
                        self.file_count += 1
                        if self.total_files > 0:
                            progress = int((self.file_count / min(self.total_files, self.max_files)) * 100)
                            self.progress.emit(min(progress, 100), f"Scanned {self.file_count} files")
                    
                    # Check if reached max files
                    if self.file_count >= self.max_files:
                        break
                
                if self.file_count >= self.max_files:
                    break
                    
        except Exception as e:
            import traceback
            self.error.emit(f"Scan error: {str(e)}", traceback.format_exc())
    
    def _scan_file(self, filepath: str) -> Optional[Dict]:
        """Scan single file"""
        try:
            # Check if symlink
            is_symlink = os.path.islink(filepath)
            if is_symlink:
                self.stats['symlinks'] += 1
                stat_func = os.lstat
            else:
                stat_func = os.stat
            
            # Get file info
            file_stat = stat_func(filepath)
            
            # Get permissions
            mode = file_stat.st_mode
            is_readable = bool(mode & stat.S_IRUSR)
            is_writable = bool(mode & stat.S_IWUSR)
            is_executable = bool(mode & stat.S_IXUSR)
            
            mode_octal = oct(mode)[-3:]
            mode_symbolic = stat.filemode(mode)
            
            relative_path = os.path.relpath(filepath, self.folder_path)
            
            # Determine risk level
            risk_level = self._determine_risk_level(mode_octal, filepath, is_symlink)
            
            # Check custom rules
            expected_perm = self._check_custom_rules(filepath)
            
            file_data = {
                'path': filepath,
                'relative': relative_path,
                'name': os.path.basename(filepath),
                'info': {
                    'readable': is_readable,
                    'writable': is_writable,
                    'executable': is_executable,
                    'mode': mode_octal,
                    'symbolic': mode_symbolic,
                    'size': file_stat.st_size,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime),
                    'is_symlink': is_symlink,
                    'is_dir': os.path.isdir(filepath) if not is_symlink else False
                },
                'risk': risk_level,
                'expected': expected_perm,
                'backup_status': 'none',
                'encryption_status': 'none'
            }
            
            return file_data
            
        except PermissionError:
            self.stats['permission_denied'] += 1
            return None
        except Exception:
            return None
    
    def _determine_risk_level(self, mode: str, filepath: str, is_symlink: bool) -> str:
        """Menentukan tingkat risiko"""
        if is_symlink:
            return 'Medium'
        
        # High risk permissions
        if mode in ['777', '666', '767', '676']:
            return 'High'
        
        # World writable or executable
        if mode[1] in ['6', '7'] or mode[2] in ['6', '7']:
            sensitive_extensions = ['.env', '.key', '.pem', '.conf', '.ini', '.sql', '.db', '.pwd']
            if any(filepath.endswith(ext) for ext in sensitive_extensions):
                return 'High'
            return 'Medium'
        
        return 'Low'
    
    def _check_custom_rules(self, filepath: str) -> Optional[str]:
        """Check custom rules"""
        filename = os.path.basename(filepath)
        for pattern, expected_perm in self.custom_rules.items():
            if pattern in filepath or filename == pattern:
                return expected_perm
        return None
    
    def _update_stats(self, file_data: Dict):
        """Update statistics"""
        self.stats['total_files'] += 1
        self.stats['total_size'] += file_data['info']['size']
        
        risk = file_data['risk']
        if risk == 'High':
            self.stats['high_risk'] += 1
        elif risk == 'Medium':
            self.stats['medium_risk'] += 1
        else:
            self.stats['low_risk'] += 1