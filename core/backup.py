"""
Backup Manager - CIA Availability
Handles file backup and restore operations with integrity checks
"""

import os
import shutil
import zipfile
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from core.integrity import IntegrityManager


class BackupManager:
    """Manages file backups"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = backup_dir
        self.integrity_manager = IntegrityManager()
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
    def create_backup(self, files: List[str], note: str = "") -> str:
        """Create a backup of specified files"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.zip"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            manifest = {
                'created_at': datetime.now().isoformat(),
                'note': note,
                'files': []
            }
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for filepath in files:
                    if os.path.exists(filepath):
                        # Store relative path in zip
                        filesize = os.path.getsize(filepath)
                        filehash = self.integrity_manager.calculate_sha256(filepath)
                        
                        zf.write(filepath, os.path.basename(filepath))
                        
                        manifest['files'].append({
                            'path': filepath,
                            'hash': filehash,
                            'size': filesize
                        })
                
                # Add manifest
                zf.writestr('manifest.json', json.dumps(manifest, indent=2))
            
            # Create checksum for the backup file itself
            self.integrity_manager.create_checksum_file(backup_path)
            
            # Log audit
            self.integrity_manager.log_audit_event(
                'backup_created', backup_path,
                f"Backup created with {len(files)} files"
            )
            
            return backup_path
            
        except Exception as e:
            print(f"Backup failed: {e}")
            return None
            
    def restore_backup(self, backup_path: str, restore_dir: str) -> Dict:
        """Restore files from backup"""
        try:
            if not os.path.exists(backup_path):
                return {'success': False, 'error': "Backup file not found"}
            
            # Verify backup integrity first
            # Check checksum file
            checksum_path = backup_path + ".sha256"
            if os.path.exists(checksum_path):
                # Verify logic here... (simplified for now)
                pass
                
            results = {'success': True, 'restored': [], 'errors': []}
            
            with zipfile.ZipFile(backup_path, 'r') as zf:
                # Read manifest
                try:
                    manifest_data = zf.read('manifest.json')
                    manifest = json.loads(manifest_data)
                except:
                    return {'success': False, 'error': "Invalid backup format (no manifest)"}
                
                # Restore files
                for file_info in manifest['files']:
                    try:
                        filename = os.path.basename(file_info['path'])
                        # Extract
                        zf.extract(filename, restore_dir)
                        
                        restored_path = os.path.join(restore_dir, filename)
                        
                        # Verify restored file
                        current_hash = self.integrity_manager.calculate_sha256(restored_path)
                        if current_hash != file_info['hash']:
                            results['errors'].append(f"Integrity check failed for {filename}")
                        else:
                            results['restored'].append(filename)
                            
                    except Exception as e:
                        results['errors'].append(f"Failed to restore {filename}: {str(e)}")
            
            # Log audit
            self.integrity_manager.log_audit_event(
                'backup_restored', backup_path,
                f"Restored {len(results['restored'])} files"
            )
            
            return results
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def list_backups(self) -> List[Dict]:
        """List available backups"""
        backups = []
        for f in os.listdir(self.backup_dir):
            if f.endswith('.zip'):
                path = os.path.join(self.backup_dir, f)
                try:
                    size = os.path.getsize(path)
                    created = datetime.fromtimestamp(os.path.getctime(path))
                    
                    # Try to read manifest for more info
                    note = ""
                    file_count = 0
                    try:
                        with zipfile.ZipFile(path, 'r') as zf:
                            manifest = json.loads(zf.read('manifest.json'))
                            note = manifest.get('note', '')
                            file_count = len(manifest.get('files', []))
                    except:
                        pass
                        
                    backups.append({
                        'name': f,
                        'path': path,
                        'size': size,
                        'created': created,
                        'note': note,
                        'file_count': file_count
                    })
                except:
                    pass
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
