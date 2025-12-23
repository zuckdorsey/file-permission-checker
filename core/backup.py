import os
import stat
import shutil
import zipfile
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from core.integrity import IntegrityManager


class PermissionMetadata:
    """Kelas untuk menangani penyimpanan dan pengambilan metadata perubahan izin."""
    
    def __init__(self, metadata_dir: str = "permission_logs"):
        self.metadata_dir = metadata_dir
        self.metadata_file = os.path.join(metadata_dir, "permission_changes.json")
        self._ensure_dir()
    
    def _ensure_dir(self):
        """Pastikan direktori metadata ada dengan izin aman."""
        if not os.path.exists(self.metadata_dir):
            os.makedirs(self.metadata_dir, mode=0o700)
        if os.path.exists(self.metadata_file):
            os.chmod(self.metadata_file, 0o600)
    
    def _load_metadata(self) -> Dict:
        """load metadata dari file json"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"changes": [], "summary": {}}
        return {"changes": [], "summary": {}}
    
    def _save_metadata(self, data: Dict):
        """simpan metadata ke file json"""
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        os.chmod(self.metadata_file, 0o600)
    
    def log_permission_change(
        self,
        filepath: str,
        old_permission: str,
        new_permission: str,
        risk_level: str = None,
        reason: str = None,
        user: str = None
    ) -> Dict:
        """
        Catat perubahan izin dengan metadata lengkap.
        
        Argumen:
            filepath: Jalur absolut ke file
            old_permission: Izin asli (string oktal, misalnya '777')
            izin_baru: Izin baru (string oktal, misalnya '644')
            risk_level: Tingkat risiko file (Tinggi/Sedang/Rendah)
            alasan: Alasan perubahan
            pengguna: Pengguna yang melakukan perubahan
        
        Pengembalian:
            Entri perubahan yang dicatat
        """
        metadata = self._load_metadata()
        
        try:
            file_stat = os.stat(filepath)
            file_size = file_stat.st_size
            file_owner = file_stat.st_uid
            file_group = file_stat.st_gid
        except (OSError, FileNotFoundError):
            file_size = 0
            file_owner = -1
            file_group = -1
        
        change_entry = {
            "id": len(metadata["changes"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "filepath": filepath,
            "filename": os.path.basename(filepath),
            "directory": os.path.dirname(filepath),
            "old_permission": old_permission,
            "old_permission_symbolic": self._octal_to_symbolic(old_permission),
            "new_permission": new_permission,
            "new_permission_symbolic": self._octal_to_symbolic(new_permission),
            "risk_level": risk_level,
            "reason": reason or "Auto-fix by permission checker",
            "user": user or os.environ.get('USER', 'unknown'),
            "file_info": {
                "size": file_size,
                "owner_uid": file_owner,
                "group_gid": file_group
            },
            "reversible": True
        }
        
        metadata["changes"].append(change_entry)
        
        if "total_changes" not in metadata["summary"]:
            metadata["summary"] = {
                "total_changes": 0,
                "by_risk_level": {"High": 0, "Medium": 0, "Low": 0},
                "first_change": change_entry["timestamp"],
                "last_change": change_entry["timestamp"]
            }
        
        metadata["summary"]["total_changes"] += 1
        metadata["summary"]["last_change"] = change_entry["timestamp"]
        if risk_level in metadata["summary"]["by_risk_level"]:
            metadata["summary"]["by_risk_level"][risk_level] += 1
        
        self._save_metadata(metadata)
        
        return change_entry
    
    def _octal_to_symbolic(self, octal_str: str) -> str:
        """Ubah string izin oktal menjadi format simbolis."""
        try:
            mode = int(octal_str, 8)
            return stat.filemode(mode | stat.S_IFREG)[1:]
        except (ValueError, TypeError):
            return "unknown"
    
    def get_file_history(self, filepath: str) -> List[Dict]:
        """Dapatkan semua perubahan izin untuk file tertentu."""
        metadata = self._load_metadata()
        return [
            change for change in metadata["changes"]
            if change["filepath"] == filepath
        ]
    
    def get_changes_by_date(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Dapatkan perubahan izin dalam rentang tanggal."""
        metadata = self._load_metadata()
        changes = metadata["changes"]
        
        if start_date:
            start = datetime.fromisoformat(start_date)
            changes = [c for c in changes if datetime.fromisoformat(c["timestamp"]) >= start]
        
        if end_date:
            end = datetime.fromisoformat(end_date)
            changes = [c for c in changes if datetime.fromisoformat(c["timestamp"]) <= end]
        
        return changes
    
    def get_changes_by_risk_level(self, risk_level: str) -> List[Dict]:
        """Dapatkan semua perubahan untuk tingkat risiko tertentu."""
        metadata = self._load_metadata()
        return [
            change for change in metadata["changes"]
            if change.get("risk_level") == risk_level
        ]
    
    def get_summary(self) -> Dict:
        """Dapatkan statistik ringkasan semua perubahan izin."""
        metadata = self._load_metadata()
        return metadata.get("summary", {})
    
    def get_all_changes(self) -> List[Dict]:
        """Dapatkan semua catatan perubahan izin."""
        metadata = self._load_metadata()
        return metadata.get("changes", [])
    
    def export_to_csv(self, output_path: str) -> bool:
        """Ekspor perubahan izin ke format CSV."""
        import csv
        
        metadata = self._load_metadata()
        changes = metadata.get("changes", [])
        
        if not changes:
            return False
        
        try:
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'id', 'timestamp', 'filepath', 'filename',
                    'old_permission', 'old_permission_symbolic',
                    'new_permission', 'new_permission_symbolic',
                    'risk_level', 'reason', 'user'
                ])
                writer.writeheader()
                for change in changes:
                    writer.writerow({k: change.get(k, '') for k in writer.fieldnames})
            return True
        except IOError:
            return False
    
    def can_revert(self, change_id: int) -> bool:
        """Periksa apakah perubahan izin dapat dikembalikan."""
        metadata = self._load_metadata()
        for change in metadata["changes"]:
            if change["id"] == change_id:
                return change.get("reversible", False) and os.path.exists(change["filepath"])
        return False
    
    def revert_change(self, change_id: int) -> Dict:
        """Kembalikan perubahan izin tertentu."""
        metadata = self._load_metadata()
        
        for change in metadata["changes"]:
            if change["id"] == change_id:
                if not os.path.exists(change["filepath"]):
                    return {"success": False, "error": "File no longer exists"}
                
                try:
                    old_mode = int(change["old_permission"], 8)
                    os.chmod(change["filepath"], old_mode)
                    
                    self.log_permission_change(
                        filepath=change["filepath"],
                        old_permission=change["new_permission"],
                        new_permission=change["old_permission"],
                        risk_level=change.get("risk_level"),
                        reason=f"Reverted change #{change_id}"
                    )
                    
                    return {"success": True, "reverted": change}
                except OSError as e:
                    return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Change not found"}


class BackupManager:
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = backup_dir
        self.integrity_manager = IntegrityManager()
        self.permission_metadata = PermissionMetadata()
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
    def create_backup(self, files: List[str], note: str = "") -> str:
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
                        filesize = os.path.getsize(filepath)
                        filehash = self.integrity_manager.calculate_sha256(filepath)
                        
                        try:
                            file_stat = os.stat(filepath)
                            current_perm = oct(file_stat.st_mode)[-3:]
                            perm_symbolic = stat.filemode(file_stat.st_mode)
                        except OSError:
                            current_perm = "unknown"
                            perm_symbolic = "unknown"
                        
                        zf.write(filepath, os.path.basename(filepath))
                        
                        manifest['files'].append({
                            'path': filepath,
                            'hash': filehash,
                            'size': filesize,
                            'permission': current_perm,
                            'permission_symbolic': perm_symbolic,
                            'backed_up_at': datetime.now().isoformat()
                        })
                
                zf.writestr('manifest.json', json.dumps(manifest, indent=2))
            
            self.integrity_manager.create_checksum_file(backup_path)
            
            self.integrity_manager.log_audit_event(
                'backup_created', backup_path,
                f"Backup created with {len(files)} files"
            )
            
            return backup_path
            
        except Exception as e:
            print(f"Backup failed: {e}")
            return None
    
    def create_permission_backup(
        self, 
        files_data: List[Dict], 
        note: str = "Permission change backup"
    ) -> str:
        """
        Buat cadangan khusus untuk perubahan izin.
        
        Argumen:
            files_data: Daftar dicts dengan 'path', 'old_permission', 'new_permission', 'risk_level'
            catatan: Deskripsi cadangan
        
        Pengembalian:
            Jalur ke file manifes cadangan
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"permission_backup_{timestamp}.json"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        backup_data = {
            "created_at": datetime.now().isoformat(),
            "note": note,
            "total_files": len(files_data),
            "changes": []
        }
        
        for file_info in files_data:
            filepath = file_info.get('path', '')
            
            change_record = {
                "filepath": filepath,
                "filename": os.path.basename(filepath),
                "old_permission": file_info.get('old_permission', 'unknown'),
                "new_permission": file_info.get('new_permission', 'unknown'),
                "risk_level": file_info.get('risk_level', 'unknown'),
                "timestamp": datetime.now().isoformat()
            }
            
            backup_data["changes"].append(change_record)
            
            self.permission_metadata.log_permission_change(
                filepath=filepath,
                old_permission=file_info.get('old_permission', 'unknown'),
                new_permission=file_info.get('new_permission', 'unknown'),
                risk_level=file_info.get('risk_level'),
                reason=note
            )
        
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        os.chmod(backup_path, 0o600)
        
        self.integrity_manager.create_checksum_file(backup_path)
        
        return backup_path
            
    def restore_backup(self, backup_path: str, restore_dir: str) -> Dict:
        """
        Pulihkan cadangan dengan perlindungan Zip Slip.
        
        Memvalidasi semua jalur ekstraksi untuk mencegah serangan traversal direktori.
        """
        try:
            if not os.path.exists(backup_path):
                return {'success': False, 'error': "Backup file not found"}
            
            restore_dir = os.path.abspath(restore_dir)
            
            checksum_path = backup_path + ".sha256"
            if os.path.exists(checksum_path):
                pass
                
            results = {'success': True, 'restored': [], 'errors': []}
            
            with zipfile.ZipFile(backup_path, 'r') as zf:
                try:
                    manifest_data = zf.read('manifest.json')
                    manifest = json.loads(manifest_data)
                except:
                    return {'success': False, 'error': "Invalid backup format (no manifest)"}
                
                for file_info in manifest['files']:
                    try:
                        filename = os.path.basename(file_info['path'])
                        
                        target_path = os.path.abspath(os.path.join(restore_dir, filename))
                        if not target_path.startswith(restore_dir + os.sep):
                            results['errors'].append(f"Blocked path traversal attempt: {filename}")
                            continue
                        
                        zf.extract(filename, restore_dir)
                        
                        restored_path = os.path.join(restore_dir, filename)
                        
                        if 'permission' in file_info and file_info['permission'] != 'unknown':
                            try:
                                old_mode = int(file_info['permission'], 8)
                                os.chmod(restored_path, old_mode, follow_symlinks=False)
                            except (ValueError, OSError):
                                pass
                        
                        current_hash = self.integrity_manager.calculate_sha256(restored_path)
                        if current_hash != file_info['hash']:
                            results['errors'].append(f"Integrity check failed for {filename}")
                        else:
                            results['restored'].append({
                                'filename': filename,
                                'permission': file_info.get('permission', 'unknown')
                            })
                            
                    except Exception as e:
                        results['errors'].append(f"Failed to restore {filename}: {str(e)}")
            
            self.integrity_manager.log_audit_event(
                'backup_restored', backup_path,
                f"Restored {len(results['restored'])} files"
            )
            
            return results
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def restore_permissions_from_backup(self, backup_path: str) -> Dict:
        """
        Pulihkan hanya izin (bukan file) dari cadangan izin.
        
        Argumen:
            backup_path: Jalur ke izin file JSON cadangan
        
        Pengembalian:
            Hasil dikte dengan status sukses dan detailnya
        """
        try:
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            results = {'success': True, 'restored': [], 'errors': []}
            
            for change in backup_data.get('changes', []):
                filepath = change.get('filepath')
                old_permission = change.get('old_permission')
                
                if not filepath or not old_permission or old_permission == 'unknown':
                    continue
                
                if not os.path.exists(filepath):
                    results['errors'].append(f"File not found: {filepath}")
                    continue
                
                try:
                    old_mode = int(old_permission, 8)
                    
                    current_stat = os.stat(filepath)
                    current_perm = oct(current_stat.st_mode)[-3:]
                    
                    os.chmod(filepath, old_mode)
                    
                    self.permission_metadata.log_permission_change(
                        filepath=filepath,
                        old_permission=current_perm,
                        new_permission=old_permission,
                        risk_level=change.get('risk_level'),
                        reason="Restored from backup"
                    )
                    
                    results['restored'].append({
                        'filepath': filepath,
                        'restored_permission': old_permission
                    })
                    
                except (ValueError, OSError) as e:
                    results['errors'].append(f"Failed to restore {filepath}: {str(e)}")
            
            return results
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def list_backups(self) -> List[Dict]:
        backups = []
        for f in os.listdir(self.backup_dir):
            if f.endswith('.zip') or f.endswith('.json'):
                path = os.path.join(self.backup_dir, f)
                try:
                    size = os.path.getsize(path)
                    created = datetime.fromtimestamp(os.path.getctime(path))
                    
                    note = ""
                    file_count = 0
                    backup_type = "file" if f.endswith('.zip') else "permission"
                    
                    try:
                        if f.endswith('.zip'):
                            with zipfile.ZipFile(path, 'r') as zf:
                                manifest = json.loads(zf.read('manifest.json'))
                                note = manifest.get('note', '')
                                file_count = len(manifest.get('files', []))
                        else:
                            with open(path, 'r') as jf:
                                data = json.load(jf)
                                note = data.get('note', '')
                                file_count = data.get('total_files', 0)
                    except:
                        pass
                        
                    backups.append({
                        'name': f,
                        'path': path,
                        'size': size,
                        'created': created,
                        'note': note,
                        'file_count': file_count,
                        'type': backup_type
                    })
                except:
                    pass
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def get_permission_history(self, filepath: str) -> List[Dict]:
        """Dapatkan riwayat perubahan izin untuk file tertentu."""
        return self.permission_metadata.get_file_history(filepath)
    
    def get_all_permission_changes(self) -> List[Dict]:
        """Dapatkan semua perubahan izin di semua file."""
        return self.permission_metadata.get_all_changes()
    
    def get_permission_summary(self) -> Dict:
        """Dapatkan ringkasan semua perubahan izin."""
        return self.permission_metadata.get_summary()


class RestoreManager:
    """
    Manajer pemulihan komprehensif untuk file dan izin.
    
    Fitur:
    - Kembalikan konten file dari cadangan
    - Kembalikan izin asli
    - Validasi keberadaan file
    - Verifikasi integritas
    - Laporan pemulihan terperinci
    """
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = backup_dir
        self.integrity_manager = IntegrityManager()
        self.permission_metadata = PermissionMetadata()
        self.restore_log_file = os.path.join(backup_dir, "restore_history.json")
    
    def validate_backup(self, backup_path: str) -> Dict:
        """
        Validasi file cadangan sebelum memulihkan.
        
        Pengembalian:
            Dikte dengan status validasi dan detailnya
        """
        result = {
            'valid': False,
            'exists': False,
            'readable': False,
            'has_manifest': False,
            'integrity_ok': False,
            'file_count': 0,
            'files': [],
            'errors': []
        }
        
        if not os.path.exists(backup_path):
            result['errors'].append(f"Backup file not found: {backup_path}")
            return result
        
        result['exists'] = True
        
        try:
            if backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zf:
                    result['readable'] = True
                    
                    try:
                        manifest_data = zf.read('manifest.json')
                        manifest = json.loads(manifest_data)
                        result['has_manifest'] = True
                        result['file_count'] = len(manifest.get('files', []))
                        result['files'] = manifest.get('files', [])
                        result['created_at'] = manifest.get('created_at')
                        result['note'] = manifest.get('note', '')
                    except KeyError:
                        result['errors'].append("Manifest not found in backup")
                    except json.JSONDecodeError:
                        result['errors'].append("Invalid manifest format")
                        
            elif backup_path.endswith('.json'):
                with open(backup_path, 'r') as f:
                    data = json.load(f)
                    result['readable'] = True
                    result['has_manifest'] = True
                    result['file_count'] = data.get('total_files', 0)
                    result['files'] = data.get('changes', [])
                    result['created_at'] = data.get('created_at')
                    result['note'] = data.get('note', '')
                    
        except (zipfile.BadZipFile, IOError) as e:
            result['errors'].append(f"Cannot read backup: {str(e)}")
            return result
        
        checksum_path = backup_path + ".sha256"
        if os.path.exists(checksum_path):
            try:
                with open(checksum_path, 'r') as f:
                    stored_hash = f.read().strip().split()[0]
                
                current_hash = self.integrity_manager.calculate_sha256(backup_path)
                result['integrity_ok'] = (stored_hash == current_hash)
                
                if not result['integrity_ok']:
                    result['errors'].append("Checksum mismatch - backup may be corrupted")
            except Exception as e:
                result['errors'].append(f"Cannot verify checksum: {str(e)}")
        else:
            result['integrity_ok'] = True
        
        result['valid'] = (
            result['exists'] and 
            result['readable'] and 
            result['has_manifest'] and 
            result['integrity_ok']
        )
        
        return result
    
    def preview_restore(self, backup_path: str, restore_dir: str = None) -> Dict:
        """
        Pratinjau apa yang akan dipulihkan tanpa benar-benar memulihkan.
        
        Argumen:
            backup_path: Jalur ke file cadangan
            recovery_dir: Direktori opsional untuk memulihkan (untuk cadangan file)
        
        Pengembalian:
            Dikte dengan informasi pratinjau
        """
        validation = self.validate_backup(backup_path)
        
        if not validation['valid']:
            return {
                'can_restore': False,
                'validation': validation,
                'files_to_restore': [],
                'conflicts': [],
                'missing_destinations': []
            }
        
        preview = {
            'can_restore': True,
            'validation': validation,
            'files_to_restore': [],
            'conflicts': [],
            'missing_destinations': [],
            'permissions_to_restore': []
        }
        
        for file_info in validation['files']:
            filepath = file_info.get('path') or file_info.get('filepath', '')
            filename = os.path.basename(filepath)
            
            if restore_dir:
                target_path = os.path.join(restore_dir, filename)
            else:
                target_path = filepath
            
            file_entry = {
                'original_path': filepath,
                'target_path': target_path,
                'filename': filename,
                'permission': file_info.get('permission') or file_info.get('old_permission', 'unknown'),
                'size': file_info.get('size', 0)
            }
            
            if os.path.exists(target_path):
                file_entry['conflict'] = True
                file_entry['conflict_type'] = 'file_exists'
                preview['conflicts'].append(file_entry)
            else:
                file_entry['conflict'] = False
            
            dest_dir = os.path.dirname(target_path)
            if dest_dir and not os.path.exists(dest_dir):
                preview['missing_destinations'].append(dest_dir)
            
            preview['files_to_restore'].append(file_entry)
            
            if file_info.get('permission') or file_info.get('old_permission'):
                preview['permissions_to_restore'].append({
                    'filepath': target_path,
                    'permission': file_info.get('permission') or file_info.get('old_permission')
                })
        
        return preview
    
    def restore_files(
        self, 
        backup_path: str, 
        restore_dir: str,
        overwrite: bool = False,
        restore_permissions: bool = True,
        create_dirs: bool = True
    ) -> Dict:
        """
        Pulihkan konten file dan izin dari cadangan.
        
        Argumen:
            backup_path: Jalur ke file cadangan (.zip)
            recovery_dir: Direktori untuk memulihkan file
            overwrite: Apakah akan menimpa file yang sudah ada
            recovery_permissions: Apakah akan mengembalikan izin asli
            create_dirs: Apakah akan membuat direktori yang hilang
        
        Pengembalian:
            Hasil pemulihan terperinci
        """
        result = {
            'success': False,
            'restored_files': [],
            'restored_permissions': [],
            'skipped': [],
            'errors': [],
            'restore_time': datetime.now().isoformat()
        }
        
        validation = self.validate_backup(backup_path)
        if not validation['valid']:
            result['errors'] = validation['errors']
            return result
        
        if not restore_dir:
            result['errors'].append("Restore directory not specified")
            return result
        
        if create_dirs and not os.path.exists(restore_dir):
            try:
                os.makedirs(restore_dir, mode=0o755)
            except OSError as e:
                result['errors'].append(f"Cannot create restore directory: {str(e)}")
                return result
        
        if not backup_path.endswith('.zip'):
            result['errors'].append("File restore only supported for .zip backups")
            return result
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zf:
                manifest_data = zf.read('manifest.json')
                manifest = json.loads(manifest_data)
                
                for file_info in manifest.get('files', []):
                    filepath = file_info.get('path', '')
                    filename = os.path.basename(filepath)
                    target_path = os.path.join(restore_dir, filename)
                    
                    if os.path.exists(target_path):
                        if not overwrite:
                            result['skipped'].append({
                                'filename': filename,
                                'reason': 'file_exists',
                                'target_path': target_path
                            })
                            continue
                    
                    target_dir = os.path.dirname(target_path)
                    if create_dirs and target_dir and not os.path.exists(target_dir):
                        os.makedirs(target_dir, mode=0o755)
                    
                    try:
                        zf.extract(filename, restore_dir)
                        
                        if 'hash' in file_info:
                            current_hash = self.integrity_manager.calculate_sha256(target_path)
                            integrity_ok = (current_hash == file_info['hash'])
                        else:
                            integrity_ok = True
                        
                        permission_restored = False
                        if restore_permissions and 'permission' in file_info:
                            perm = file_info['permission']
                            if perm != 'unknown':
                                try:
                                    mode = int(perm, 8)
                                    os.chmod(target_path, mode)
                                    permission_restored = True
                                    
                                    result['restored_permissions'].append({
                                        'filepath': target_path,
                                        'permission': perm
                                    })
                                except (ValueError, OSError):
                                    pass
                        
                        result['restored_files'].append({
                            'filename': filename,
                            'target_path': target_path,
                            'original_path': filepath,
                            'size': file_info.get('size', 0),
                            'integrity_ok': integrity_ok,
                            'permission': file_info.get('permission', 'unknown'),
                            'permission_restored': permission_restored
                        })
                        
                    except Exception as e:
                        result['errors'].append(f"Failed to restore {filename}: {str(e)}")
            
            result['success'] = len(result['errors']) == 0
            
            self._log_restore(backup_path, result)
            
            return result
            
        except Exception as e:
            result['errors'].append(f"Restore failed: {str(e)}")
            return result
    
    def restore_single_file(
        self, 
        backup_path: str, 
        filename: str, 
        target_path: str = None,
        restore_permission: bool = True
    ) -> Dict:
        """
        Pulihkan satu file dari cadangan.
        
        Argumen:
            backup_path: Jalur ke file cadangan
            nama file: Nama file yang akan dipulihkan
            target_path: Jalur target opsional (default ke lokasi asli)
            recovery_permission: Apakah akan mengembalikan izin
        
        Pengembalian:
            Kembalikan hasil
        """
        result = {
            'success': False,
            'filename': filename,
            'target_path': None,
            'permission_restored': False,
            'error': None
        }
        
        validation = self.validate_backup(backup_path)
        if not validation['valid']:
            result['error'] = validation['errors'][0] if validation['errors'] else 'Invalid backup'
            return result
        
        if not backup_path.endswith('.zip'):
            result['error'] = "Single file restore only supported for .zip backups"
            return result
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zf:
                manifest_data = zf.read('manifest.json')
                manifest = json.loads(manifest_data)
                
                file_info = None
                for f in manifest.get('files', []):
                    if os.path.basename(f.get('path', '')) == filename:
                        file_info = f
                        break
                
                if not file_info:
                    result['error'] = f"File '{filename}' not found in backup"
                    return result
                
                if target_path:
                    result['target_path'] = target_path
                else:
                    result['target_path'] = file_info.get('path', filename)
                
                target_dir = os.path.dirname(result['target_path'])
                if target_dir and not os.path.exists(target_dir):
                    os.makedirs(target_dir, mode=0o755)
                
                import tempfile
                with tempfile.TemporaryDirectory() as temp_dir:
                    zf.extract(filename, temp_dir)
                    temp_file = os.path.join(temp_dir, filename)
                    shutil.copy2(temp_file, result['target_path'])
                
                if restore_permission and 'permission' in file_info:
                    perm = file_info['permission']
                    if perm != 'unknown':
                        try:
                            mode = int(perm, 8)
                            os.chmod(result['target_path'], mode)
                            result['permission_restored'] = True
                            result['permission'] = perm
                        except (ValueError, OSError):
                            pass
                
                result['success'] = True
                return result
                
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def restore_permissions_only(
        self, 
        backup_path: str,
        validate_exists: bool = True
    ) -> Dict:
        """
        Pulihkan hanya izin (bukan konten file) dari cadangan.
        
        Argumen:
            backup_path: Jalur ke file cadangan (.zip atau .json)
            validasi_exists: Lewati file yang tidak ada
        
        Pengembalian:
            Kembalikan hasil
        """
        result = {
            'success': False,
            'restored': [],
            'skipped': [],
            'errors': []
        }
        
        validation = self.validate_backup(backup_path)
        if not validation['valid']:
            result['errors'] = validation['errors']
            return result
        
        try:
            files_info = []
            
            if backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zf:
                    manifest = json.loads(zf.read('manifest.json'))
                    files_info = manifest.get('files', [])
            else:
                with open(backup_path, 'r') as f:
                    data = json.load(f)
                    files_info = data.get('changes', [])
            
            for file_info in files_info:
                filepath = file_info.get('path') or file_info.get('filepath', '')
                permission = file_info.get('permission') or file_info.get('old_permission')
                
                if not filepath or not permission or permission == 'unknown':
                    continue
                
                if validate_exists and not os.path.exists(filepath):
                    result['skipped'].append({
                        'filepath': filepath,
                        'reason': 'file_not_found'
                    })
                    continue
                
                try:
                    current_stat = os.stat(filepath)
                    current_perm = oct(current_stat.st_mode)[-3:]
                    
                    mode = int(permission, 8)
                    os.chmod(filepath, mode)
                    
                    self.permission_metadata.log_permission_change(
                        filepath=filepath,
                        old_permission=current_perm,
                        new_permission=permission,
                        risk_level=file_info.get('risk_level'),
                        reason="Restored from backup"
                    )
                    
                    result['restored'].append({
                        'filepath': filepath,
                        'old_permission': current_perm,
                        'restored_permission': permission
                    })
                    
                except (ValueError, OSError) as e:
                    result['errors'].append(f"Failed to restore {filepath}: {str(e)}")
            
            result['success'] = len(result['errors']) == 0
            return result
            
        except Exception as e:
            result['errors'].append(str(e))
            return result
    
    def get_restore_history(self) -> List[Dict]:
        """mendapatkan semua history backup"""
        if os.path.exists(self.restore_log_file):
            try:
                with open(self.restore_log_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _log_restore(self, backup_path: str, result: Dict):
        """mencatat log restore"""
        history = self.get_restore_history()
        
        history.append({
            'timestamp': datetime.now().isoformat(),
            'backup_path': backup_path,
            'success': result.get('success', False),
            'files_restored': len(result.get('restored_files', [])),
            'files_skipped': len(result.get('skipped', [])),
            'errors_count': len(result.get('errors', []))
        })
        
        try:
            with open(self.restore_log_file, 'w') as f:
                json.dump(history, f, indent=2)
        except IOError:
            pass
