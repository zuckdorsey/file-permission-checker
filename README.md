# File Permission Checker

A PyQt5 desktop application for scanning, analyzing, and securing file permissions on Unix-based systems.

## Overview

File Permission Checker provides a graphical interface for managing file permissions across directories. It identifies security risks, suggests fixes, and includes features for backup, encryption, and integrity verification.

## Features

- Permission scanning with risk analysis
- Automatic permission fixing based on configurable rules
- AES-256 file encryption with password protection
- Automatic backup before permission changes
- SHA-256 integrity verification
- Export to CSV and JSON formats
- SQLite audit logging

## Requirements

- Python 3.8 or higher
- PyQt5
- cryptography

## Installation

```bash
git clone https://github.com/zuckdorsey/file-permission-checker.git
cd file-permission-checker

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

### Scanning

1. Enter the folder path or use the browse button
2. Click Scan to analyze permissions
3. Results are displayed in the table with risk indicators

### Fixing Permissions

1. Click Fix Risky to fix all high-risk files
2. Or right-click specific files for individual actions
3. Use Advanced Settings for custom permission values

### Encryption

1. Navigate to the Encryption tab
2. Add files using the file browser
3. Enter a password and click Start Processing

### Backup

1. Navigate to the Backups tab
2. Select a folder and create a backup
3. Restore from backup history when needed

## Risk Classification

Files are classified based on sensitivity:

| Risk Level | Description | Recommended Permission |
|------------|-------------|------------------------|
| High | Sensitive files (keys, credentials, configs) | 600 (owner read/write only) |
| Medium | Configuration and script files | 640 (owner + group read) |
| Low | Standard files and documents | 644 (world readable) |

## Project Structure

```
file-permission-checker/
├── main.py                 # Application entry point
├── style.qss               # Qt stylesheet
├── core/
│   ├── scanner.py          # File scanning
│   ├── permission_fixer.py # Permission modification
│   ├── security.py         # Encryption/decryption
│   ├── backup.py           # Backup management
│   ├── integrity.py        # Hash verification
│   ├── pipeline.py         # Workflow orchestration
│   └── database.py         # SQLite logging
├── ui/
│   ├── main_window.py      # Main window
│   ├── dialogs.py          # Dialog windows
│   └── modern_widgets.py   # Custom widgets
├── utils/
│   ├── constants.py        # Configuration
│   └── helpers.py          # Utility functions
└── docs/
    ├── RISK_LEVEL_SPECIFICATION.md
    ├── RISK_TO_PERMISSION_MAPPING.md
    └── UI_DESIGN_SYSTEM.md
```

## Configuration

Custom permission rules can be defined in `utils/constants.py`:

```python
CUSTOM_RULES = {
    '.env': '600',
    '.pem': '600',
    '.key': '600',
    'id_rsa': '600',
    '.conf': '644',
    '.sh': '755',
}

RISK_TO_PERMISSION = {
    'High': {'file': '600', 'dir': '700'},
    'Medium': {'file': '640', 'dir': '750'},
    'Low': {'file': '644', 'dir': '755'},
}
```

## Security Pipeline

The application executes permission changes through a secure pipeline:

1. Scan files and determine risk levels
2. Create backup of current state
3. Generate hash of original files
4. Apply encryption if requested
5. Modify permissions
6. Verify integrity with new hash
7. Rollback on any failure

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+S | Start scan |
| Ctrl+F | Fix permissions |
| Ctrl+E | Export to CSV |
| F5 | Refresh view |

## Export Formats

### CSV

```csv
Filename,Path,Mode,Symbolic,Risk Level,Expected,Size,Modified
.env,config/.env,644,rw-r--r--,High,600,1.2 KB,2025-01-15
```

### JSON

```json
{
  "scan_date": "2025-01-15T10:30:00",
  "folder": "/path/to/project",
  "total_files": 500,
  "statistics": {
    "high_risk": 12,
    "medium_risk": 45,
    "low_risk": 443
  },
  "files": [...]
}
```

## Documentation

Additional documentation is available in the `docs/` directory:

- Risk Level Specification: Detailed risk classification criteria
- Risk to Permission Mapping: Permission recommendations by risk level
- UI Design System: Theme and component specifications

## License

MIT License

## Author

zuckdorsey - https://github.com/zuckdorsey
