# 📋 Advanced File Permission Checker

Aplikasi PyQt5 yang canggih untuk memeriksa, menganalisis, dan memperbaiki izin file secara otomatis dengan berbagai fitur enterprise-level.

## ✨ Fitur Lengkap

### 1. **Risk Level Analysis** 🎯

- Analisis otomatis tingkat risiko: **Low**, **Medium**, **High**
- Color-coded display untuk identifikasi cepat
- Deteksi permission berbahaya (777, 666, dll)

### 2. **Auto Color Highlighting** 🎨

- 🔴 **Merah**: High risk files (world-writable)
- 🟠 **Orange**: Medium risk files
- 🟢 **Hijau**: Safe/Low risk files

### 3. **Auto Fix Permissions** 🔧

- Perbaikan otomatis dengan satu klik
- Menggunakan custom rules untuk file spesifik
- Default safe permissions (644 untuk files)

### 4. **Statistics Dashboard** 📊

- Total file count
- Breakdown berdasarkan risk level
- Real-time updates saat scanning

### 5. **Export Capabilities** 💾

- **CSV Export**: Untuk analisis di Excel/spreadsheet
- **JSON Export**: Untuk integrasi dengan sistem lain
- Includes metadata lengkap dan timestamp

### 6. **Advanced Filtering** 🔍

- Filter by risk level
- Search by filename
- Real-time table filtering

### 7. **Progress Bar** ⏳

- Visual feedback saat scanning
- Percentage completion
- Non-blocking UI (background thread)

### 8. **Status Bar** 📢

- Real-time status messages
- Operation feedback
- Error notifications

### 9. **Custom Rule Engine** 📜

File-specific permission rules:

```python
CUSTOM_RULES = {
    '.env': '600',      # Environment files
    '.git': '700',      # Git directory
    'storage': '755',   # Storage directories
    'config': '644',    # Config files
    'private': '600',   # Private files
}
```

### 10. **Dark Mode** 🌙

- Eye-friendly dark theme
- Toggle dengan checkbox
- Persistent across sessions

### 11. **SQLite Logging** 💿

- Automatic scan logging
- Historical data tracking
- Query past scans

### 12. **Drag & Drop Support** 🖱️

- Drag folder directly ke window
- Instant path population
- User-friendly interface

### 13. **Multi-threading** ⚡

- Non-blocking UI
- Responsive during long scans
- Progress updates in real-time

### 14. **Detailed Information** 📝

- Octal permissions (644, 755)
- Symbolic permissions (rwxr-xr-x)
- File size (formatted)
- Last modified date
- Relative path

## 🚀 Installation

```bash
# Install dependencies
pip install PyQt5

# Run the application
python main.py
```

## 📖 Usage Guide

### Basic Scan

1. Click **"Browse..."** atau drag & drop folder
2. Click **"Scan Folder"**
3. Wait for progress bar to complete
4. Review results in table

### Fix Risky Permissions

1. After scan, click **"Fix Risky Permissions"**
2. Confirm the action
3. Application will auto-fix based on rules

### Export Results

1. Click **"Export CSV"** or **"Export JSON"**
2. Choose save location
3. File will be saved with timestamp

### Apply Filters

1. Use **"Filter"** dropdown untuk risk level
2. Use **"Search"** box untuk cari file specific
3. Table updates automatically

## 🛡️ CIA Triad Implementation

Aplikasi ini menerapkan prinsip **Confidentiality, Integrity, dan Availability (CIA)** untuk keamanan data:

### 1. Confidentiality (Kerahasiaan) 🔒
- **Secure Logs**: Database log (`scan_logs.db`) otomatis di-set ke permission `600` (hanya owner yang bisa baca/tulis).
- **Secure Exports**: File hasil export (CSV/JSON) juga otomatis di-set ke permission `600` untuk mencegah akses tidak sah.

### 2. Integrity (Integritas) ✅
- **Checksum Verification**: Setiap kali melakukan export, aplikasi akan membuat file checksum `.sha256`.
- **Tamper Detection**: User bisa memverifikasi bahwa file report tidak dimodifikasi dengan membandingkan hash-nya.

### 3. Availability (Ketersediaan) 🛡️
- **Robust Scanning**: Scanner menangani error permission (`PermissionError`) dengan graceful.
- **Error Reporting**: File yang tidak bisa diakses akan ditandai sebagai "Permission Denied" di tabel, bukan crash atau di-skip diam-diam.

## 🔒 Permission Analysis

### Risk Levels

#### High Risk 🔴

- **777**: World writable (anyone can modify)
- **666**: World readable/writable
- **Sensitive files** with group/world permissions (.env, .key, .pem)

#### Medium Risk 🟠

- Group or other writable permissions
- Executable permissions on non-executable files
- Public readable sensitive files

#### Low Risk 🟢

- Standard safe permissions
- 644 for regular files
- 755 for directories
- 600 for private files

### Permission Format Examples

**Octal Format:**

- `644` = rw-r--r-- (owner: read+write, group/others: read)
- `755` = rwxr-xr-x (owner: all, group/others: read+execute)
- `600` = rw------- (owner: read+write only)
- `777` = rwxrwxrwx (everyone: all permissions) ⚠️ DANGEROUS

**Symbolic Format:**

```
rwxrwxrwx
│││││││││
││││││││└─ Others execute
│││││││└── Others write
││││││└─── Others read
│││││└──── Group execute
││││└───── Group write
│││└────── Group read
││└─────── Owner execute
│└──────── Owner write
└───────── Owner read
```

## 📊 Statistics Examples

After scanning:

```
Total File: 1247
✅ Aman: 1156
⚠️ Medium Risk: 67
🔴 High Risk: 24
```

## 🗃️ Database Schema

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

## 🎨 Dark Mode

Toggle dengan checkbox **"🌙 Dark Mode"** di header.

Dark mode menggunakan QPalette dengan color scheme:

- Background: #353535
- Text: White
- Alternate rows: Auto-colored
- Highlight: #2A82DA

## 📤 Export Formats

### CSV Format

```csv
Filename,Path,Mode,Symbolic,Risk Level,Expected,Size,Modified
.env,config/.env,644,rw-r--r--,Low,600,1.2 KB,2025-11-20 10:30
```

### JSON Format

```json
{
  "scan_date": "2025-11-20T10:30:00",
  "folder": "/home/user/project",
  "total_files": 1247,
  "statistics": {
    "high_risk": 24,
    "medium_risk": 67,
    "low_risk": 1156
  },
  "files": [...]
}
```

## 🛠️ Technical Details

### Threading Architecture

- **Main Thread**: UI updates
- **Scan Thread**: File scanning
- **Signals**: progress, file_found, finished

### Permission Detection

```python
# Get file stats
file_stat = os.stat(filepath)

# Check owner permissions
is_readable = bool(file_stat.st_mode & stat.S_IRUSR)
is_writable = bool(file_stat.st_mode & stat.S_IWUSR)
is_executable = bool(file_stat.st_mode & stat.S_IXUSR)

# Get octal representation
mode_octal = oct(file_stat.st_mode)[-3:]

# Get symbolic representation
mode_symbolic = stat.filemode(file_stat.st_mode)
```

### Auto-Fix Logic

```python
# For risky files
if file_data['expected']:
    # Use custom rule
    new_mode = int(file_data['expected'], 8)
else:
    # Use safe default
    new_mode = 0o644

os.chmod(filepath, new_mode)
```

## 🎯 Use Cases

1. **Security Audit**: Scan project directories untuk security issues
2. **DevOps**: Pre-deployment permission checks
3. **Compliance**: Ensure files meet security standards
4. **Cleanup**: Batch fix permissions after git clone
5. **Education**: Learn about file permissions

## ⚠️ Important Notes

- **Backup**: Always backup before mass permission changes
- **Root Access**: Some files may require sudo
- **Testing**: Test on non-critical folders first
- **Symbolic Links**: Application follows symlinks

## 🔧 Customization

Edit `CUSTOM_RULES` dictionary untuk menambah rules:

```python
CUSTOM_RULES = {
    '.env': '600',
    'id_rsa': '600',
    'authorized_keys': '600',
    'nginx.conf': '644',
    'ssl': '700',
}
```

## 📝 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions welcome! Areas to improve:

- PDF export functionality
- More custom rules
- Permission templates
- Recursive directory permissions
- Undo functionality

## 🐛 Known Issues

- PDF export not yet implemented (CSV/JSON available)
- Large folders (10k+ files) may take time
- Requires appropriate permissions to modify files

## 📧 Support

For issues or questions, please open an issue on the repository.

---

**Made with ❤️ using PyQt5**
