"""╔══════════════════════════════════════════════════════════════════╗
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

from core.scanner import ScanThread
from core.permission_fixer import PermissionFixer
from core.integrity import IntegrityManager
from core.database import init_database, log_scan, log_permission_change
from core.security import SecurityManager
from core.encryption_manager import EncryptionWorker
from core.backup import BackupManager
from core.secure_memory import SecureString, secure_delete_file

__all__ = [
    'ScanThread',
    'PermissionFixer',
    'IntegrityManager',
    'SecurityManager',
    'EncryptionWorker',
    'SecureString',
    'secure_delete_file',
    'BackupManager',
    'init_database',
    'log_scan',
    'log_permission_change',
]