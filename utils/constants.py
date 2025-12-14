# Constants for the file scanner application

# Custom rules for file scanning
CUSTOM_RULES = {
    'high_risk_extensions': ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com'],
    'medium_risk_extensions': ['.dll', '.sys', '.drv', '.ocx'],
    'suspicious_permissions': [0o777, 0o666],
    'max_file_age_days': 365
}

# Maximum file size to scan in MB
MAX_FILE_SIZE_MB = 100