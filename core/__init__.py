"""
Core Module - FilePermissionChecker
Focused on: Scanning, Permission Fixing, Integrity, and Database Logging
"""

from core.scanner import ScanThread
from core.permission_fixer import PermissionFixer
from core.integrity import IntegrityManager
from core.database import init_database, log_scan, log_permission_change

__all__ = [
    # Scanner
    'ScanThread',
    
    # Permission
    'PermissionFixer',
    
    # Integrity (CIA - for audit logging)
    'IntegrityManager',
    
    # Database
    'init_database',
    'log_scan',
    'log_permission_change',
]