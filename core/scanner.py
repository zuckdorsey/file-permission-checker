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
import stat
from datetime import datetime
from typing import Dict, Optional, List
from PyQt5.QtCore import QThread, pyqtSignal, QMutex

class ScanThread(QThread):
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
        self.mutex.lock()
        self.is_cancelled = True
        self.mutex.unlock()
    
    def run(self):
        try:
            self.stats['start_time'] = datetime.now().isoformat()
            
            self._scan_folder(self.folder_path)
            
            self.stats['end_time'] = datetime.now().isoformat()
            self.stats['duration'] = (datetime.now() - datetime.fromisoformat(self.stats['start_time'])).total_seconds()
            
            self.progress.emit(100, "Scan completed")
            self.finished.emit(self.all_files, self.stats)
            
        except Exception as e:
            import traceback
            self.error.emit(str(e), traceback.format_exc())
    
    def _scan_folder(self, folder_path: str):
        try:
            for root, dirs, files in os.walk(folder_path):
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
                    
                    if self.file_count >= self.max_files:
                        break
                
                if self.file_count >= self.max_files:
                    break
                    
        except Exception as e:
            import traceback
            self.error.emit(f"Scan error: {str(e)}", traceback.format_exc())
    
    def _scan_file(self, filepath: str) -> Optional[Dict]:
        try:
            is_symlink = os.path.islink(filepath)
            if is_symlink:
                self.stats['symlinks'] += 1
                stat_func = os.lstat
            else:
                stat_func = os.stat
            
            file_stat = stat_func(filepath)
            
            mode = file_stat.st_mode
            is_readable = bool(mode & stat.S_IRUSR)
            is_writable = bool(mode & stat.S_IWUSR)
            is_executable = bool(mode & stat.S_IXUSR)
            
            mode_octal = oct(mode)[-3:]
            mode_symbolic = stat.filemode(mode)
            
            relative_path = os.path.relpath(filepath, self.folder_path)
            
            risk_level = self._determine_risk_level(mode_octal, filepath, is_symlink)
            
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
        """
        Determine risk level based on FILE SENSITIVITY + PERMISSION MATRIX.
        
        Risk Level indicates security posture:
        - High Risk: Sensitive file with LOOSE permissions (needs fixing)
        - Medium Risk: Moderately sensitive file or symlink
        - Low Risk: Non-sensitive OR properly secured sensitive file
        
        Matrix:
        | Sensitivity | Permission | Result     |
        |-------------|------------|------------|
        | High        | > 600      | High Risk  |
        | High        | <= 600     | Low Risk   |
        | Medium      | > 644      | Medium Risk|
        | Medium      | <= 644     | Low Risk   |
        | Low         | Any        | Low Risk   |
        """
        filename = os.path.basename(filepath).lower()
        
        try:
            mode_int = int(mode, 8)
        except ValueError:
            mode_int = 0o644
        
        high_sensitivity_extensions = [
            '.env', '.key', '.pem', '.crt', '.p12', '.pfx',
            '.pwd', '.password', '.secret', '.token',
            '.credentials', '.auth',
        ]
        
        high_sensitivity_patterns = [
            'id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519',
            'authorized_keys', 'known_hosts',
            '.htpasswd', '.htaccess',
            'shadow', 'passwd', 'sudoers',
            'master.key', 'credentials.yml',
            'secrets.yaml', 'secrets.json',
            'wp-config.php',
            '.netrc', '.pgpass',
        ]
        
        high_sensitivity_dirs = ['.ssh', '.gnupg', 'private', 'secrets', 'credentials']
        
        medium_sensitivity_extensions = [
            '.conf', '.config', '.cfg', '.ini', '.yaml', '.yml',
            '.xml', '.properties',
            '.sql', '.db', '.sqlite', '.sqlite3',
            '.log',
            '.sh', '.bash', '.zsh', '.py', '.rb', '.pl',
        ]
        
        medium_sensitivity_patterns = [
            'config', 'settings', 'database',
            'nginx', 'apache', 'httpd',
            'docker-compose', 'dockerfile',
            'makefile', 'rakefile',
        ]
        
        sensitivity = 'low'
        
        if any(filepath.lower().endswith(ext) for ext in high_sensitivity_extensions):
            sensitivity = 'high'
        elif any(pattern in filename for pattern in high_sensitivity_patterns):
            sensitivity = 'high'
        elif any(f'/{dir_name}/' in filepath.lower() or filepath.lower().endswith(f'/{dir_name}') 
               for dir_name in high_sensitivity_dirs):
            sensitivity = 'high'
        elif any(filepath.lower().endswith(ext) for ext in medium_sensitivity_extensions):
            sensitivity = 'medium'
        elif any(pattern in filename for pattern in medium_sensitivity_patterns):
            sensitivity = 'medium'
        elif is_symlink:
            try:
                target = os.readlink(filepath)
                if os.path.isabs(target) or '..' in target:
                    sensitivity = 'high'
                else:
                    sensitivity = 'medium'
            except OSError:
                sensitivity = 'medium'
            
            try:
                target = os.readlink(filepath)
                if not os.path.isabs(target):
                    target = os.path.normpath(os.path.join(os.path.dirname(filepath), target))
                
                sensitive_system_paths = [
                    '/etc', '/bin', '/sbin', '/usr/bin', '/usr/sbin',
                    '/lib', '/lib64', '/usr/lib',
                    '/root', '/var/log', '/var/run',
                    '/boot', '/proc', '/sys', '/dev',
                    '/home/root', '/.ssh', '/.gnupg',
                    '/etc/passwd', '/etc/shadow', '/etc/sudoers',
                ]
                
                for sensitive_path in sensitive_system_paths:
                    if target.startswith(sensitive_path) or sensitive_path in target:
                        return 'High'
                        
            except (OSError, ValueError):
                pass
        
        if sensitivity == 'high':
            others_perms = mode_int & 0o007
            group_perms = mode_int & 0o070
            
            if others_perms > 0 or group_perms > 0:
                return 'High'
            elif (mode_int & 0o777) > 0o600:
                return 'High' if (mode_int & 0o077) > 0 else 'Low'
            else:
                return 'Low'
        
        elif sensitivity == 'medium':
            others_write = mode_int & 0o002
            group_write = mode_int & 0o020
            
            if others_write > 0 or group_write > 0:
                return 'Medium'
            elif (mode_int & 0o777) > 0o755:
                return 'Medium'
            else:
                return 'Low'
        
        else:
            return 'Low'
    
    def _check_custom_rules(self, filepath: str) -> Optional[str]:
        filename = os.path.basename(filepath)
        for pattern, expected_perm in self.custom_rules.items():
            if pattern in filepath or filename == pattern:
                return expected_perm
        return None
    
    def _update_stats(self, file_data: Dict):
        self.stats['total_files'] += 1
        self.stats['total_size'] += file_data['info']['size']
        
        risk = file_data['risk']
        if risk == 'High':
            self.stats['high_risk'] += 1
        elif risk == 'Medium':
            self.stats['medium_risk'] += 1
        else:
            self.stats['low_risk'] += 1
