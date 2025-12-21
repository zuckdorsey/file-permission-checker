CUSTOM_RULES = {
    
    '.env': '600',
    '.key': '600',
    '.pem': '600',
    '.crt': '600',
    '.p12': '600',
    '.pfx': '600',
    '.pwd': '600',
    '.secret': '600',
    '.token': '600',
    'id_rsa': '600',
    'id_dsa': '600',
    'id_ecdsa': '600',
    'id_ed25519': '600',
    'authorized_keys': '600',
    '.htpasswd': '600',
    'master.key': '600',
    'credentials.yml': '600',
    'secrets.yaml': '600',
    'secrets.json': '600',
    'wp-config.php': '600',
    '.netrc': '600',
    '.pgpass': '600',
    '.git': '700',
    '.ssh': '700',
    '.gnupg': '700',
    'private': '700',
    'secrets': '700',
    'credentials': '700',
    
    
    'storage': '755',
    'config': '644',
    'logs': '755',
    'cache': '755',
}

MAX_FILE_SIZE_MB = 100  
BACKUP_HISTORY_LIMIT = 50  
SCAN_CACHE_DURATION = 300  

RISK_COLORS = {
    'High': '#FF4444',
    'Medium': '#FFAA00',
    'Low': '#44FF44'
}


RISK_TO_PERMISSION = {
    'High': {
        'file': ['700', '600', '400', '500'],
        'directory': ['700', '500'],
        'description': 'Sensitive files requiring owner-only access'
    },
    'Medium': {
        'file': ['640', '644', '755', '750'],
        'directory': ['755', '750'],
        'description': 'Moderately sensitive files with controlled sharing'
    },
    'Low': {
        'file': ['666', '777', '664', '757'],
        'directory': ['777', '757'],
        'description': 'Non-sensitive files that can have open access'
    }
}

SENSITIVE_EXTENSIONS = [
    '.env', '.key', '.pem', '.conf', '.ini', '.sql', '.db', 
    '.pwd', '.secret', '.token', '.cred', '.cert'
]

EXECUTABLE_EXTENSIONS = [
    '.sh', '.py', '.exe', '.bin', '.run', '.app', '.bat', 
    '.cmd', '.ps1', '.bash','appimage'
]

DEFAULT_PERMISSIONS = {
    'file': 0o644,
    'directory': 0o755,
    'executable': 0o755,
    'symlink': 0o777,
    'private': 0o600
}
