# Architecture Overview

Technical architecture documentation for the File Permission Checker application.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Main Application                          │
│                         (main.py)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    UI Layer                              │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │    │
│  │  │ Main Window  │ │   Dialogs    │ │   Widgets    │     │    │
│  │  └──────────────┘ └──────────────┘ └──────────────┘     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   Core Layer                             │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │    │
│  │  │ Scanner  │ │  Fixer   │ │ Security │ │  Backup  │    │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                 │    │
│  │  │Integrity │ │ Pipeline │ │ Database │                 │    │
│  │  └──────────┘ └──────────┘ └──────────┘                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  Utils Layer                             │    │
│  │  ┌──────────────┐ ┌──────────────┐                      │    │
│  │  │  Constants   │ │   Helpers    │                      │    │
│  │  └──────────────┘ └──────────────┘                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Module Descriptions

### UI Layer

#### main_window.py
- Main application window
- Tab management (Scanner, Encryption, Backups, Logs)
- Sidebar with statistics
- Header with quick actions

#### dialogs.py
- PasswordDialog: Password input with confirmation
- AdvancedPermissionDialog: Visual permission editor
- SettingsDialog: Application configuration

#### modern_widgets.py
- GlassCard: Container component
- ModernButton: Styled button variants
- ModernTableWidget: Enhanced table
- PillBadge: Risk level indicators
- ToastNotification: In-app notifications
- AnimatedProgressBar: Progress display
- LoadingSpinner: Loading indicator

### Core Layer

#### scanner.py
- ScanThread: Background file scanning
- Permission analysis
- Risk level determination
- Custom rule matching

#### permission_fixer.py
- PermissionFixer: Permission modification
- Automatic backup before changes
- Batch operations
- Error handling and rollback

#### security.py
- SecurityManager: Encryption operations
- AES-256 encryption
- Key derivation (PBKDF2)
- Password verification

#### backup.py
- BackupManager: File backup operations
- PermissionMetadata: Change tracking
- RestoreManager: Restore operations
- ZIP archive management

#### integrity.py
- IntegrityManager: Hash operations
- SHA-256 file hashing
- Audit logging
- Verification reports

#### pipeline.py
- PipelineOrchestrator: Workflow management
- Step execution with rollback
- Error handling
- Progress reporting

#### database.py
- Logging: SQLite logging
- Scan history
- Audit trails

### Utils Layer

#### constants.py
- CUSTOM_RULES: File-specific permissions
- RISK_TO_PERMISSION: Risk-based permissions
- RISK_COLORS: UI color mapping
- SENSITIVE_EXTENSIONS: High-risk file types

#### helpers.py
- File size formatting
- Path manipulation
- Permission conversion

## Threading Model

```
Main Thread (UI)
    │
    ├── ScanThread (Background)
    │   └── Emits: progress, file_found, finished
    │
    ├── EncryptionWorker (Background)
    │   └── Emits: progress, file_processed, finished
    │
    └── PipelineOrchestrator (Background)
        └── Emits: step_started, step_completed, pipeline_finished
```

## Data Flow

### Scanning Flow

```
User Input → ScanThread → File Analysis → Risk Classification → UI Update
```

### Permission Fix Flow

```
User Action → Backup Creation → Hash Generation → Permission Change → Verification
```

### Encryption Flow

```
File Selection → Password Input → Key Derivation → Encryption → Hash Storage
```

## Database Schema

### scan_logs

```sql
CREATE TABLE scan_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_date DATETIME,
    folder_path TEXT,
    total_files INTEGER,
    high_risk INTEGER,
    medium_risk INTEGER,
    low_risk INTEGER
);
```

### audit_log

```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME,
    file_path TEXT,
    operation TEXT,
    old_permission TEXT,
    new_permission TEXT,
    user TEXT,
    success BOOLEAN
);
```

## Configuration Files

### style.qss
Qt stylesheet defining the application theme.

### requirements.txt
Python package dependencies.

## Security Considerations

### Password Handling
- Passwords never stored in plain text
- Key derived using PBKDF2 with 100,000 iterations
- Salt stored with encrypted data

### File Operations
- Atomic operations where possible
- Backup before destructive changes
- Verification after modifications

### Audit Trail
- All operations logged
- Timestamps and user info recorded
- Success/failure status tracked

## Error Handling

### Permission Errors
- Graceful handling of access denied
- User notification with details
- Skip and continue for batch operations

### File System Errors
- Missing file handling
- Symbolic link handling
- Directory access issues

### Cryptographic Errors
- Invalid password detection
- Corrupted file handling
- Key derivation failures

## Performance Considerations

### Large Directories
- Background threading for scanning
- Progress reporting
- Incremental UI updates

### Memory Management
- Streaming for large files
- Efficient data structures
- Cleanup after operations

## Extension Points

### Custom Rules
Add entries to CUSTOM_RULES dictionary.

### New Risk Levels
Extend RISK_TO_PERMISSION mapping.

### Additional Export Formats
Implement new export methods in main_window.py.

### New Widgets
Add to modern_widgets.py following existing patterns.
