# ============================ KONSTANTA ============================
CUSTOM_RULES = {
    '.env': '600',
    '.git': '700',
    'storage': '755',
    'config': '644',
    'private': '600',
}

MAX_FILE_SIZE_MB = 100  # Batas ukuran file untuk dipindai (MB)
BACKUP_HISTORY_LIMIT = 50  # Batas jumlah cadangan yang disimpan
SCAN_CACHE_DURATION = 300  # Durasi cache pemindaian (5 menit)

# Warna tingkat risiko
RISK_COLORS = {
    'High': '#FF4444',
    'Medium': '#FFAA00',
    'Low': '#44FF44'
}

# Ekstensi file yang dianggap sensitif
SENSITIVE_EXTENSIONS = [
    '.env', '.key', '.pem', '.conf', '.ini', '.sql', '.db', 
    '.pwd', '.secret', '.token', '.cred', '.cert'
]

# Ekstensi yang dapat dieksekusi
EXECUTABLE_EXTENSIONS = [
    '.sh', '.py', '.exe', '.bin', '.run', '.app', '.bat', 
    '.cmd', '.ps1', '.bash'
]

# Izin default
DEFAULT_PERMISSIONS = {
    'file': 0o644,
    'directory': 0o755,
    'executable': 0o755,
    'symlink': 0o777,
    'private': 0o600
}