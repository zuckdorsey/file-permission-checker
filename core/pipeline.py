import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field

from core.integrity import IntegrityManager
from core.permission_fixer import PermissionFixer, PermissionBackup
from core.security import SecurityManager


class PipelineStep(Enum):
    """Enum for pipeline steps."""
    SCAN = "scan"
    BACKUP = "backup"
    HASH_BEFORE = "hash_before"
    ENCRYPT = "encrypt"
    CHANGE_PERMISSION = "change_permission"
    HASH_AFTER = "hash_after"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class StepResult:
    """Result of a single pipeline step."""
    step: PipelineStep
    success: bool
    message: str
    data: Dict = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    rollback_data: Dict = field(default_factory=dict)


@dataclass
class PipelineResult:
    """Result of the entire pipeline execution."""
    success: bool
    completed_steps: List[StepResult] = field(default_factory=list)
    failed_step: Optional[StepResult] = None
    rolled_back: bool = False
    rollback_results: List[Dict] = field(default_factory=list)
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    total_files: int = 0
    files_processed: int = 0


class PermissionPipeline:
    """
    Orchestrates the permission fix workflow with rollback capability.
    
    Flow: Scan → Backup → Hash → Encrypt → Change Permission → Hash Again
    
    If any step fails, previous steps are rolled back.
    """
    
    def __init__(
        self, 
        backup_dir: str = "backups",
        enable_encryption: bool = False,
        encryption_password: str = None
    ):
        self.backup_dir = backup_dir
        self.enable_encryption = enable_encryption
        self.encryption_password = encryption_password
        
        self.integrity_manager = IntegrityManager()
        self.permission_fixer = PermissionFixer(auto_backup=False, backup_dir=backup_dir)
        self.permission_backup = PermissionBackup(backup_dir)
        self.security_manager = SecurityManager() if enable_encryption else None
        
        self.current_step = None
        self.pipeline_result = None
        self._is_cancelled = False
        self._hashes_before = {}
        self._encrypted_files = set()
        
        self.progress_callback: Optional[Callable[[int, str], None]] = None
        self.step_callback: Optional[Callable[[PipelineStep, str], None]] = None
    
    def set_progress_callback(self, callback: Callable[[int, str], None]):
        """Set callback for progress updates."""
        self.progress_callback = callback
    
    def set_step_callback(self, callback: Callable[[PipelineStep, str], None]):
        """Set callback for step completion updates."""
        self.step_callback = callback
    
    def cancel(self):
        """Cancel the pipeline execution."""
        self._is_cancelled = True
    
    def execute(
        self, 
        files_data: List[Dict],
        custom_mode: int = None
    ) -> PipelineResult:
        """
        Execute the full permission fix pipeline.
        
        Args:
            files_data: List of file data dicts with 'path', 'risk', 'info' (containing 'mode')
            custom_mode: Optional custom permission mode
        
        Returns:
            PipelineResult with all step results
        """
        self._is_cancelled = False
        
        result = PipelineResult(
            success=False,
            total_files=len(files_data),
            start_time=datetime.now().isoformat()
        )
        
        self.pipeline_result = result
        
        rollback_stack = []
        
        try:
            step_result = self._step_scan(files_data)
            result.completed_steps.append(step_result)
            
            if not step_result.success or self._is_cancelled:
                result.failed_step = step_result
                self._log_step(PipelineStep.SCAN, "Failed", step_result.error)
                return self._finalize_result(result)
            
            rollback_stack.append(step_result)
            self._notify_step(PipelineStep.SCAN, "Completed")
            
            step_result = self._step_backup(files_data)
            result.completed_steps.append(step_result)
            
            if not step_result.success or self._is_cancelled:
                result.failed_step = step_result
                self._rollback(rollback_stack, result)
                return self._finalize_result(result)
            
            rollback_stack.append(step_result)
            self._notify_step(PipelineStep.BACKUP, "Completed")
            
            step_result = self._step_hash_before(files_data)
            result.completed_steps.append(step_result)
            
            if not step_result.success or self._is_cancelled:
                result.failed_step = step_result
                self._rollback(rollback_stack, result)
                return self._finalize_result(result)
            
            rollback_stack.append(step_result)
            self._notify_step(PipelineStep.HASH_BEFORE, "Completed")
            
            if self.enable_encryption and self.encryption_password:
                step_result = self._step_encrypt(step_result.data.get('backup_path'))
                result.completed_steps.append(step_result)
                
                if not step_result.success or self._is_cancelled:
                    result.failed_step = step_result
                    self._rollback(rollback_stack, result)
                    return self._finalize_result(result)
                
                rollback_stack.append(step_result)
                self._notify_step(PipelineStep.ENCRYPT, "Completed")
            
            step_result = self._step_change_permission(files_data, custom_mode)
            result.completed_steps.append(step_result)
            
            if not step_result.success or self._is_cancelled:
                result.failed_step = step_result
                self._rollback(rollback_stack, result)
                return self._finalize_result(result)
            
            rollback_stack.append(step_result)
            result.files_processed = step_result.data.get('success_count', 0)
            self._notify_step(PipelineStep.CHANGE_PERMISSION, "Completed")
            
            step_result = self._step_hash_after(files_data)
            result.completed_steps.append(step_result)
            
            if not step_result.success or self._is_cancelled:
                result.failed_step = step_result
                self._rollback(rollback_stack, result)
                return self._finalize_result(result)
            
            self._notify_step(PipelineStep.HASH_AFTER, "Completed")
            
            result.success = True
            self._notify_step(PipelineStep.COMPLETED, "Pipeline completed successfully")
            
            return self._finalize_result(result)
            
        except Exception as e:
            result.failed_step = StepResult(
                step=self.current_step or PipelineStep.FAILED,
                success=False,
                message="Pipeline execution failed",
                error=str(e)
            )
            self._rollback(rollback_stack, result)
            return self._finalize_result(result)
    
    def _step_scan(self, files_data: List[Dict]) -> StepResult:
        """Step 1: Scan and validate all files exist."""
        self.current_step = PipelineStep.SCAN
        self._notify_progress(0, "Scanning files...")
        
        valid_files = []
        missing_files = []
        
        for i, file_info in enumerate(files_data):
            filepath = file_info.get('path', '')
            
            if os.path.exists(filepath):
                valid_files.append(filepath)
            else:
                missing_files.append(filepath)
            
            if self.progress_callback:
                progress = int((i + 1) / len(files_data) * 100)
                self._notify_progress(progress, f"Scanning: {os.path.basename(filepath)}")
        
        if missing_files:
            return StepResult(
                step=PipelineStep.SCAN,
                success=False,
                message=f"Missing files: {len(missing_files)}",
                error=f"Files not found: {', '.join(missing_files[:5])}{'...' if len(missing_files) > 5 else ''}"
            )
        
        return StepResult(
            step=PipelineStep.SCAN,
            success=True,
            message=f"All {len(valid_files)} files validated",
            data={'valid_files': valid_files}
        )
    
    def _step_backup(self, files_data: List[Dict]) -> StepResult:
        """Step 2: Create backup of current permissions."""
        self.current_step = PipelineStep.BACKUP
        self._notify_progress(0, "Creating backup...")
        
        try:
            backup_data = []
            for file_info in files_data:
                filepath = file_info.get('path', '')
                
                try:
                    current_mode = os.stat(filepath).st_mode & 0o777
                    current_mode_str = oct(current_mode)[2:]
                except OSError:
                    current_mode_str = 'unknown'
                
                backup_data.append({
                    'path': filepath,
                    'old_permission': current_mode_str,
                    'new_permission': file_info.get('expected', current_mode_str),
                    'risk_level': file_info.get('risk', 'unknown')
                })
            
            backup_path = self.permission_backup.create_backup(
                backup_data,
                note="Pipeline backup before permission changes"
            )
            
            self._notify_progress(100, "Backup created")
            
            return StepResult(
                step=PipelineStep.BACKUP,
                success=True,
                message=f"Backup created: {os.path.basename(backup_path)}",
                data={'backup_path': backup_path, 'backup_data': backup_data},
                rollback_data={'backup_path': backup_path}
            )
            
        except Exception as e:
            return StepResult(
                step=PipelineStep.BACKUP,
                success=False,
                message="Backup creation failed",
                error=str(e)
            )
    
    def _step_hash_before(self, files_data: List[Dict]) -> StepResult:
        """Step 3: Calculate and store hashes before changes."""
        self.current_step = PipelineStep.HASH_BEFORE
        self._notify_progress(0, "Calculating file hashes...")
        
        try:
            hashes = {}
            
            for i, file_info in enumerate(files_data):
                filepath = file_info.get('path', '')
                
                file_hash = self.integrity_manager.calculate_sha256(filepath)
                if file_hash:
                    hashes[filepath] = file_hash
                    self._hashes_before[filepath] = file_hash
                    
                    current_mode = oct(os.stat(filepath).st_mode & 0o777)[2:]
                    self.integrity_manager.register_file_hash(filepath, current_mode)
                
                progress = int((i + 1) / len(files_data) * 100)
                self._notify_progress(progress, f"Hashing: {os.path.basename(filepath)}")
            
            hash_file = os.path.join(
                self.backup_dir, 
                f"hashes_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(hash_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'before_changes',
                    'hashes': hashes
                }, f, indent=2)
            
            return StepResult(
                step=PipelineStep.HASH_BEFORE,
                success=True,
                message=f"Calculated hashes for {len(hashes)} files",
                data={'hashes': hashes, 'hash_file': hash_file}
            )
            
        except Exception as e:
            return StepResult(
                step=PipelineStep.HASH_BEFORE,
                success=False,
                message="Hash calculation failed",
                error=str(e)
            )
    
    def _step_encrypt(self, backup_path: str) -> StepResult:
        """Step 4: Encrypt the backup file."""
        self.current_step = PipelineStep.ENCRYPT
        self._notify_progress(0, "Encrypting backup...")
        
        if not self.security_manager or not backup_path:
            return StepResult(
                step=PipelineStep.ENCRYPT,
                success=True,
                message="Encryption skipped (not configured)",
                data={'encrypted': False}
            )
        
        try:
            with open(backup_path, 'rb') as f:
                data = f.read()
            
            result = self.security_manager.encrypt_data(data, self.encryption_password)
            encrypted_data = result['data']
            salt = result['salt']
            
            enc_path = backup_path + ".enc"
            
            with open(enc_path, 'wb') as f:
                f.write(salt)
                f.write(encrypted_data)
            
            os.chmod(enc_path, 0o600)
            
            self._notify_progress(100, "Backup encrypted")
            
            return StepResult(
                step=PipelineStep.ENCRYPT,
                success=True,
                message=f"Backup encrypted: {os.path.basename(enc_path)}",
                data={'encrypted_path': enc_path, 'original_path': backup_path},
                rollback_data={'encrypted_path': enc_path}
            )
            
        except Exception as e:
            return StepResult(
                step=PipelineStep.ENCRYPT,
                success=False,
                message="Encryption failed",
                error=str(e)
            )
    
    def _step_change_permission(self, files_data: List[Dict], custom_mode: int = None) -> StepResult:
        """Step 5: Change file permissions."""
        self.current_step = PipelineStep.CHANGE_PERMISSION
        self._notify_progress(0, "Changing permissions...")
        
        try:
            success_count = 0
            failed_count = 0
            failed_files = []
            changed_files = []
            
            for i, file_info in enumerate(files_data):
                filepath = file_info.get('path', '')
                
                if custom_mode is not None:
                    new_mode = custom_mode
                elif file_info.get('expected'):
                    new_mode = int(file_info['expected'], 8)
                else:
                    new_mode = self.permission_fixer.determine_appropriate_permission(filepath)
                
                try:
                    current_mode = os.stat(filepath).st_mode & 0o777
                except OSError:
                    failed_count += 1
                    failed_files.append(filepath)
                    continue
                
                try:
                    os.chmod(filepath, new_mode)
                    
                    verify_mode = os.stat(filepath).st_mode & 0o777
                    if verify_mode == new_mode:
                        success_count += 1
                        changed_files.append({
                            'path': filepath,
                            'old_mode': current_mode,
                            'new_mode': new_mode
                        })
                    else:
                        failed_count += 1
                        failed_files.append(filepath)
                        
                except (PermissionError, OSError):
                    failed_count += 1
                    failed_files.append(filepath)
                
                progress = int((i + 1) / len(files_data) * 100)
                self._notify_progress(progress, f"chmod: {os.path.basename(filepath)}")
            
            failure_rate = failed_count / len(files_data) if files_data else 0
            
            if failure_rate > 0.5:
                return StepResult(
                    step=PipelineStep.CHANGE_PERMISSION,
                    success=False,
                    message=f"Too many failures: {failed_count}/{len(files_data)}",
                    error=f"Failed files: {', '.join(failed_files[:5])}{'...' if len(failed_files) > 5 else ''}",
                    rollback_data={'changed_files': changed_files}
                )
            
            return StepResult(
                step=PipelineStep.CHANGE_PERMISSION,
                success=True,
                message=f"Changed {success_count} files, {failed_count} failed",
                data={
                    'success_count': success_count,
                    'failed_count': failed_count,
                    'changed_files': changed_files
                },
                rollback_data={'changed_files': changed_files}
            )
            
        except Exception as e:
            return StepResult(
                step=PipelineStep.CHANGE_PERMISSION,
                success=False,
                message="Permission change failed",
                error=str(e)
            )
    
    def _step_hash_after(self, files_data: List[Dict]) -> StepResult:
        """Step 6: Calculate hashes after changes and verify integrity.
        
        IMPORTANT: For permission-only changes, file hash MUST NOT change.
        If hash changed and file was not encrypted, it indicates data corruption.
        """
        self.current_step = PipelineStep.HASH_AFTER
        self._notify_progress(0, "Verifying file integrity...")
        
        try:
            hashes_after = {}
            integrity_verified = 0
            integrity_failed = 0
            corrupted_files = []
            
            for i, file_info in enumerate(files_data):
                filepath = file_info.get('path', '')
                
                file_hash = self.integrity_manager.calculate_sha256(filepath)
                if file_hash:
                    hashes_after[filepath] = file_hash
                    
                    hash_before = self._hashes_before.get(filepath)
                    
                    if hash_before and hash_before != file_hash:
                        if filepath not in self._encrypted_files:
                            corrupted_files.append(filepath)
                            integrity_failed += 1
                            self.integrity_manager.log_audit_event(
                                action_type='data_corruption_detected',
                                file_path=filepath,
                                details=f"Hash mismatch: before={hash_before[:16]}... after={file_hash[:16]}...",
                                severity='critical'
                            )
                        else:
                            integrity_verified += 1
                    elif os.access(filepath, os.R_OK):
                        integrity_verified += 1
                    else:
                        integrity_failed += 1
                
                progress = int((i + 1) / len(files_data) * 100)
                self._notify_progress(progress, f"Verifying: {os.path.basename(filepath)}")
            
            hash_file = os.path.join(
                self.backup_dir,
                f"hashes_after_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(hash_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'after_changes',
                    'hashes': hashes_after,
                    'corrupted_files': corrupted_files
                }, f, indent=2)
            
            if corrupted_files:
                return StepResult(
                    step=PipelineStep.HASH_AFTER,
                    success=False,
                    message=f"DATA CORRUPTION DETECTED in {len(corrupted_files)} file(s)",
                    error=f"Corrupted: {', '.join([os.path.basename(f) for f in corrupted_files[:3]])}{'...' if len(corrupted_files) > 3 else ''}"
                )
            
            if integrity_failed > 0:
                return StepResult(
                    step=PipelineStep.HASH_AFTER,
                    success=False,
                    message=f"Integrity check failed for {integrity_failed} files",
                    error="Some files may have been corrupted"
                )
            
            return StepResult(
                step=PipelineStep.HASH_AFTER,
                success=True,
                message=f"Verified integrity of {integrity_verified} files",
                data={'hashes': hashes_after, 'hash_file': hash_file}
            )
            
        except Exception as e:
            return StepResult(
                step=PipelineStep.HASH_AFTER,
                success=False,
                message="Integrity verification failed",
                error=str(e)
            )
    
    def _rollback(self, rollback_stack: List[StepResult], result: PipelineResult):
        """Rollback completed steps in reverse order."""
        self._notify_step(PipelineStep.ROLLED_BACK, "Rolling back changes...")
        
        for step_result in reversed(rollback_stack):
            rollback_info = self._rollback_step(step_result)
            result.rollback_results.append(rollback_info)
        
        result.rolled_back = True
    
    def _rollback_step(self, step_result: StepResult) -> Dict:
        """Rollback a single step."""
        rollback_info = {
            'step': step_result.step.value,
            'success': False,
            'message': ''
        }
        
        try:
            if step_result.step == PipelineStep.CHANGE_PERMISSION:
                changed_files = step_result.rollback_data.get('changed_files', [])
                
                for file_info in changed_files:
                    try:
                        os.chmod(file_info['path'], file_info['old_mode'])
                    except:
                        pass
                
                rollback_info['success'] = True
                rollback_info['message'] = f"Restored {len(changed_files)} file permissions"
                
            elif step_result.step == PipelineStep.ENCRYPT:
                enc_path = step_result.rollback_data.get('encrypted_path')
                if enc_path and os.path.exists(enc_path):
                    os.remove(enc_path)
                
                rollback_info['success'] = True
                rollback_info['message'] = "Removed encrypted backup"
                
            elif step_result.step == PipelineStep.BACKUP:
                rollback_info['success'] = True
                rollback_info['message'] = "Backup preserved for reference"
                
            else:
                rollback_info['success'] = True
                rollback_info['message'] = "No rollback needed"
                
        except Exception as e:
            rollback_info['message'] = f"Rollback failed: {str(e)}"
        
        return rollback_info
    
    def _finalize_result(self, result: PipelineResult) -> PipelineResult:
        """Finalize and return the pipeline result."""
        result.end_time = datetime.now().isoformat()
        
        self.integrity_manager.log_audit_event(
            action_type='pipeline_execution',
            details=f"Success: {result.success}, Files: {result.files_processed}/{result.total_files}, Rolled back: {result.rolled_back}",
            severity='info' if result.success else 'warning'
        )
        
        return result
    
    def _notify_progress(self, progress: int, message: str):
        """Notify progress callback if set."""
        if self.progress_callback:
            self.progress_callback(progress, message)
    
    def _notify_step(self, step: PipelineStep, message: str):
        """Notify step callback if set."""
        if self.step_callback:
            self.step_callback(step, message)
    
    def _log_step(self, step: PipelineStep, status: str, details: str = None):
        """Log step execution."""
        self.integrity_manager.log_audit_event(
            action_type=f'pipeline_step_{step.value}',
            details=f"Status: {status}. {details or ''}",
            severity='error' if status == 'Failed' else 'info'
        )


def run_permission_pipeline(
    files_data: List[Dict],
    backup_dir: str = "backups",
    enable_encryption: bool = False,
    encryption_password: str = None,
    custom_mode: int = None,
    progress_callback: Callable = None,
    step_callback: Callable = None
) -> PipelineResult:
    """
    Convenience function to run the full permission pipeline.
    
    Args:
        files_data: List of file data dicts
        backup_dir: Directory for backups
        enable_encryption: Whether to encrypt backups
        encryption_password: Password for encryption
        custom_mode: Optional custom permission mode
        progress_callback: Optional progress callback
        step_callback: Optional step completion callback
    
    Returns:
        PipelineResult with all step results
    """
    pipeline = PermissionPipeline(
        backup_dir=backup_dir,
        enable_encryption=enable_encryption,
        encryption_password=encryption_password
    )
    
    if progress_callback:
        pipeline.set_progress_callback(progress_callback)
    
    if step_callback:
        pipeline.set_step_callback(step_callback)
    
    return pipeline.execute(files_data, custom_mode)
