import os
import stat
import json
from datetime import datetime
from typing import List, Tuple, Dict, Optional
from concurrent.futures import ThreadPoolExecutor


class PermissionBackup:
    """
    Handles automatic backup of file permissions before changes.
    
    Backup Structure:
    backups/
    └── permissions/
        └── YYYY-MM-DD/
            └── backup_HHMMSS.json
    """
    
    def __init__(self, backup_base_dir: str = "backups"):
        self.backup_base_dir = backup_base_dir
        self.permission_backup_dir = os.path.join(backup_base_dir, "permissions")
        self._ensure_backup_dirs()
    
    def _ensure_backup_dirs(self):
        """Create backup directory structure if it doesn't exist."""
        if not os.path.exists(self.permission_backup_dir):
            os.makedirs(self.permission_backup_dir, mode=0o700)
    
    def _get_daily_backup_dir(self) -> str:
        """Get or create today's backup directory."""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_dir = os.path.join(self.permission_backup_dir, today)
        if not os.path.exists(daily_dir):
            os.makedirs(daily_dir, mode=0o700)
        return daily_dir
    
    def create_backup(self, files_data: List[Dict], note: str = "") -> str:
        """
        Create a backup of file permissions before chmod.
        
        Args:
            files_data: List of dicts with 'path', 'old_permission', 'new_permission', 'risk_level'
            note: Description of the backup
        
        Returns:
            Path to the backup file
        """
        daily_dir = self._get_daily_backup_dir()
        timestamp = datetime.now().strftime("%H%M%S")
        backup_filename = f"backup_{timestamp}.json"
        backup_path = os.path.join(daily_dir, backup_filename)
        
        backup_data = {
            "created_at": datetime.now().isoformat(),
            "timestamp": timestamp,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "note": note or "Permission change backup",
            "total_files": len(files_data),
            "summary": {
                "high_risk": 0,
                "medium_risk": 0,
                "low_risk": 0
            },
            "files": []
        }
        
        for file_info in files_data:
            filepath = file_info.get('path', '')
            
            try:
                file_stat = os.stat(filepath)
                file_size = file_stat.st_size
                owner_uid = file_stat.st_uid
                group_gid = file_stat.st_gid
            except (OSError, FileNotFoundError):
                file_size = 0
                owner_uid = -1
                group_gid = -1
            
            file_record = {
                "filepath": filepath,
                "filename": os.path.basename(filepath),
                "directory": os.path.dirname(filepath),
                "old_permission": file_info.get('old_permission', 'unknown'),
                "old_permission_symbolic": self._octal_to_symbolic(file_info.get('old_permission', '')),
                "new_permission": file_info.get('new_permission', 'unknown'),
                "new_permission_symbolic": self._octal_to_symbolic(file_info.get('new_permission', '')),
                "risk_level": file_info.get('risk_level', 'unknown'),
                "timestamp": datetime.now().isoformat(),
                "file_info": {
                    "size": file_size,
                    "owner_uid": owner_uid,
                    "group_gid": group_gid
                }
            }
            
            backup_data["files"].append(file_record)
            
            risk = file_info.get('risk_level', '').lower()
            if risk == 'high':
                backup_data["summary"]["high_risk"] += 1
            elif risk == 'medium':
                backup_data["summary"]["medium_risk"] += 1
            elif risk == 'low':
                backup_data["summary"]["low_risk"] += 1
        
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        os.chmod(backup_path, 0o600)
        
        return backup_path
    
    def _octal_to_symbolic(self, octal_str: str) -> str:
        """Convert octal permission string to symbolic format."""
        try:
            mode = int(octal_str, 8)
            return stat.filemode(mode | stat.S_IFREG)[1:]
        except (ValueError, TypeError):
            return "unknown"
    
    def list_backups(self, date: str = None) -> List[Dict]:
        """
        List all backup files.
        
        Args:
            date: Optional date filter (YYYY-MM-DD format)
        
        Returns:
            List of backup info dicts
        """
        backups = []
        
        if not os.path.exists(self.permission_backup_dir):
            return backups
        
        if date:
            date_dirs = [date] if os.path.exists(os.path.join(self.permission_backup_dir, date)) else []
        else:
            date_dirs = sorted(os.listdir(self.permission_backup_dir), reverse=True)
        
        for date_dir in date_dirs:
            date_path = os.path.join(self.permission_backup_dir, date_dir)
            if not os.path.isdir(date_path):
                continue
            
            for backup_file in sorted(os.listdir(date_path), reverse=True):
                if backup_file.endswith('.json'):
                    backup_path = os.path.join(date_path, backup_file)
                    try:
                        with open(backup_path, 'r') as f:
                            data = json.load(f)
                        
                        backups.append({
                            'path': backup_path,
                            'filename': backup_file,
                            'date': date_dir,
                            'created_at': data.get('created_at'),
                            'total_files': data.get('total_files', 0),
                            'note': data.get('note', ''),
                            'summary': data.get('summary', {})
                        })
                    except (json.JSONDecodeError, IOError):
                        pass
        
        return backups
    
    def get_backup_details(self, backup_path: str) -> Optional[Dict]:
        """Get full details of a specific backup."""
        try:
            with open(backup_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, FileNotFoundError):
            return None


class PermissionFixer:
    
    def __init__(self, auto_backup: bool = True, backup_dir: str = "backups"):
        """
        Initialize PermissionFixer with optional auto-backup.
        
        Args:
            auto_backup: Enable automatic backup before chmod
            backup_dir: Base directory for backups
        """
        self.auto_backup = auto_backup
        self.backup_manager = PermissionBackup(backup_dir) if auto_backup else None
        self.last_backup_path = None
    
    def fix_file_permission(
        self, 
        filepath: str, 
        new_mode: int, 
        is_dir: bool = False,
        risk_level: str = None,
        create_backup: bool = True
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Fix file permission with automatic backup.
        
        Returns:
            Tuple of (success, message, backup_path)
        """
        backup_path = None
        
        try:
            if new_mode < 0 or new_mode > 0o777:
                return False, "Mode izin tidak valid", None
            
            if not os.path.exists(filepath):
                return False, "File tidak ditemukan", None
            
            current_mode = os.stat(filepath).st_mode & 0o777
            current_mode_str = oct(current_mode)[2:]
            new_mode_str = oct(new_mode)[2:]
            
            if create_backup and self.auto_backup and self.backup_manager:
                backup_data = [{
                    'path': filepath,
                    'old_permission': current_mode_str,
                    'new_permission': new_mode_str,
                    'risk_level': risk_level or 'unknown'
                }]
                backup_path = self.backup_manager.create_backup(
                    backup_data, 
                    note=f"Single file permission change: {os.path.basename(filepath)}"
                )
                self.last_backup_path = backup_path
            
            os.chmod(filepath, new_mode)
            
            verify_mode = os.stat(filepath).st_mode & 0o777
            if verify_mode != new_mode:
                return False, f"Gagal mengatur izin (diharapkan {oct(new_mode)}, didapat {oct(verify_mode)})", backup_path
            
            return True, f"Berubah dari {oct(current_mode)} menjadi {oct(new_mode)}", backup_path
            
        except PermissionError:
            return False, "Izin ditolak", backup_path
        except Exception as e:
            return False, str(e), backup_path
    
    @staticmethod
    def determine_appropriate_permission(filepath: str) -> int:
        if os.path.isdir(filepath):
            return 0o755
        
        if os.path.islink(filepath):
            return 0o777
        
        if os.access(filepath, os.X_OK):
            return 0o755
        
        executable_extensions = ['.sh', '.py', '.exe', '.bin', '.run', '.app']
        if any(filepath.endswith(ext) for ext in executable_extensions):
            return 0o755
        
        try:
            mode = os.stat(filepath).st_mode
            if mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
                return 0o755
        except:
            pass
        
        return 0o644
    
    def batch_fix_permissions(
        self, 
        filepaths: List[str], 
        progress_callback=None, 
        custom_mode: int = None, 
        recursive: bool = False,
        files_data: List[Dict] = None
    ) -> Dict:
        """
        Batch fix permissions with automatic backup.
        
        Args:
            filepaths: List of file paths to fix
            progress_callback: Optional callback for progress updates
            custom_mode: Optional custom permission mode
            recursive: Whether to process directories recursively
            files_data: Optional list of file data with risk levels for backup
        
        Returns:
            Results dict with backup info
        """
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

        all_paths = list(set(all_paths))

        results = {
            'total': len(all_paths),
            'success': 0,
            'failed': 0,
            'errors': [],
            'details': [],
            'backup_path': None,
            'backup_created': False
        }
        
        backup_files_data = []
        path_to_risk = {}
        
        if files_data:
            for fd in files_data:
                path_to_risk[fd.get('path', '')] = fd.get('risk', 'unknown')
        
        for filepath in all_paths:
            if not os.path.exists(filepath):
                continue
            
            try:
                current_mode = os.stat(filepath).st_mode & 0o777
                current_mode_str = oct(current_mode)[2:]
                
                if custom_mode is not None:
                    if os.path.isdir(filepath) and (custom_mode & 0o400):
                        new_mode = custom_mode | 0o100
                    else:
                        new_mode = custom_mode
                else:
                    new_mode = PermissionFixer.determine_appropriate_permission(filepath)
                
                new_mode_str = oct(new_mode)[2:]
                
                backup_files_data.append({
                    'path': filepath,
                    'old_permission': current_mode_str,
                    'new_permission': new_mode_str,
                    'risk_level': path_to_risk.get(filepath, 'unknown')
                })
            except:
                pass
        
        if self.auto_backup and self.backup_manager and backup_files_data:
            try:
                backup_path = self.backup_manager.create_backup(
                    backup_files_data,
                    note=f"Batch permission fix: {len(backup_files_data)} files"
                )
                results['backup_path'] = backup_path
                results['backup_created'] = True
                self.last_backup_path = backup_path
            except Exception as e:
                results['errors'].append(f"Backup failed: {str(e)}")
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for filepath in all_paths:
                if not os.path.exists(filepath):
                    continue
                
                if custom_mode is not None:
                    if os.path.isdir(filepath) and (custom_mode & 0o400):
                        new_mode = custom_mode | 0o100
                    else:
                        new_mode = custom_mode
                else:
                    new_mode = PermissionFixer.determine_appropriate_permission(filepath)
                
                is_dir = os.path.isdir(filepath)
                
                future = executor.submit(
                    self._fix_single_permission,
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
    
    @staticmethod
    def _fix_single_permission(filepath: str, new_mode: int, is_dir: bool = False) -> Tuple[bool, str]:
        """Internal method to fix permission without backup (for batch operations)."""
        try:
            if new_mode < 0 or new_mode > 0o777:
                return False, "Mode izin tidak valid"
            
            if not os.path.exists(filepath):
                return False, "File tidak ditemukan"
            
            current_mode = os.stat(filepath).st_mode & 0o777
            
            os.chmod(filepath, new_mode)
            
            verify_mode = os.stat(filepath).st_mode & 0o777
            if verify_mode != new_mode:
                return False, f"Gagal mengatur izin (diharapkan {oct(new_mode)}, didapat {oct(verify_mode)})"
            
            return True, f"Berubah dari {oct(current_mode)} menjadi {oct(new_mode)}"
            
        except PermissionError:
            return False, "Izin ditolak"
        except Exception as e:
            return False, str(e)
    
    def get_last_backup_path(self) -> Optional[str]:
        """Get the path of the last created backup."""
        return self.last_backup_path
    
    def list_backups(self, date: str = None) -> List[Dict]:
        """List all permission backups."""
        if self.backup_manager:
            return self.backup_manager.list_backups(date)
        return []
