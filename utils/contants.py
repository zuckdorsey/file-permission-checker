# ============================ CONSTANTS ============================
CUSTOM_RULES = {
    '.env': '600',
    '.git': '700',
    'storage': '755',
    'config': '644',
    'private': '600',
}

MAX_FILE_SIZE_MB = 100  # Batas file untuk di-scan
BACKUP_HISTORY_LIMIT = 50  # Batas jumlah backup yang disimpan
SCAN_CACHE_DURATION = 300  # Cache scan selama 5 menit

# Risk level colors
RISK_COLORS = {
    'High': '#FF4444',
    'Medium': '#FFAA00',
    'Low': '#44FF44'
}

# File extensions considered sensitive
SENSITIVE_EXTENSIONS = [
    '.env', '.key', '.pem', '.conf', '.ini', '.sql', '.db', 
    '.pwd', '.secret', '.token', '.cred', '.cert'
]

# Executable extensions
EXECUTABLE_EXTENSIONS = [
    '.sh', '.py', '.exe', '.bin', '.run', '.app', '.bat', 
    '.cmd', '.ps1', '.bash'
]

# Default permissions
DEFAULT_PERMISSIONS = {
    'file': 0o644,
    'directory': 0o755,
    'executable': 0o755,
    'symlink': 0o777,
    'private': 0o600
}