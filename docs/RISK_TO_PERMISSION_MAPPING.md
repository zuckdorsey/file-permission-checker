# 🔐 Risk Level to UNIX Permission Mapping

## Overview

Dokumen ini mendefinisikan **mapping antara Risk Level dengan permission UNIX yang valid** untuk setiap kategori. Risk Level menunjukkan tingkat sensitivitas file, sehingga:

- **High Risk** = File sangat sensitif → memerlukan permission **paling ketat**
- **Medium Risk** = File cukup sensitif → memerlukan permission **seimbang**
- **Low Risk** = File tidak sensitif → dapat menggunakan permission **lebih longgar**

---

## 📊 Quick Reference Table

| Risk Level | Valid Permissions | Karakteristik | Contoh File |
|:----------:|:-----------------:|:--------------|:------------|
| 🔴 **High** | 700, 600, 400, 500 | Owner-only access | .env, private keys, passwords |
| 🟠 **Medium** | 640, 644, 755, 750 | Controlled sharing | configs, scripts, logs |
| 🟢 **Low** | 666, 777, 664, 757 | Open access | public assets, temp files |

---

## 🔴 HIGH RISK → Restrictive Permissions

### Filosofi
File dengan sensitivitas tinggi harus memiliki **permission paling ketat**. Hanya owner yang boleh mengakses, tanpa akses untuk group atau world.

### Daftar Permission Valid

| Permission | Symbolic | Owner | Group | Others | Use Case |
|:----------:|:--------:|:-----:|:-----:|:------:|:---------|
| **700** | `rwx------` | rwx | --- | --- | Private directories |
| **600** | `rw-------` | rw- | --- | --- | Sensitive files |
| **400** | `r--------` | r-- | --- | --- | Read-only secrets |
| **500** | `r-x------` | r-x | --- | --- | Read-only executables |

---

### 📁 Permission 700 (`rwx------`)

#### Breakdown Akses
```
Owner:  r (read) + w (write) + x (execute) = FULL ACCESS
Group:  - (none) + - (none) + - (none)     = NO ACCESS
Others: - (none) + - (none) + - (none)     = NO ACCESS
```

#### Kenapa Digunakan?
- **Maximum Protection untuk Directories**: Hanya owner yang dapat masuk, list, dan modifikasi isi directory
- **Prevent Traversal**: Group/world tidak dapat `cd` ke dalam directory
- **Ideal untuk Private Folders**: Melindungi seluruh konten di dalamnya

#### Contoh Penggunaan
```bash
# SSH directory
chmod 700 ~/.ssh

# Private application data
chmod 700 /opt/myapp/secrets/

# User-specific config directory
chmod 700 ~/.config/credentials/
```

#### File Types yang Sesuai
- `~/.ssh/` - SSH configuration directory
- `~/.gnupg/` - GPG keys directory
- `/root/` - Root home directory
- Private backup directories
- Encrypted vault directories

---

### 📄 Permission 600 (`rw-------`)

#### Breakdown Akses
```
Owner:  r (read) + w (write) + - (no exec) = READ + WRITE
Group:  - (none) + - (none) + - (none)     = NO ACCESS
Others: - (none) + - (none) + - (none)     = NO ACCESS
```

#### Kenapa Digunakan?
- **Standard untuk Sensitive Files**: Best practice untuk credentials dan secrets
- **Read-Write untuk Owner Only**: Memungkinkan update tanpa expose ke users lain
- **SSH Key Requirement**: SSH daemon akan reject keys dengan permission lebih longgar

#### Contoh Penggunaan
```bash
# Environment files
chmod 600 .env
chmod 600 .env.production

# SSH private keys
chmod 600 ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_ed25519

# SSL/TLS private keys
chmod 600 /etc/ssl/private/server.key

# Database credentials
chmod 600 /etc/myapp/db.conf
```

#### File Types yang Sesuai
- `.env` files (environment variables)
- `id_rsa`, `id_ed25519` (SSH private keys)
- `*.key`, `*.pem` (encryption keys & certificates)
- `wp-config.php` (WordPress with DB creds)
- `*.pwd`, `*.secret` (password files)
- Database connection configs

---

### 📖 Permission 400 (`r--------`)

#### Breakdown Akses
```
Owner:  r (read) + - (no write) + - (no exec) = READ ONLY
Group:  - (none) + - (none) + - (none)        = NO ACCESS
Others: - (none) + - (none) + - (none)        = NO ACCESS
```

#### Kenapa Digunakan?
- **Immutable Secrets**: File yang tidak boleh diubah setelah dibuat
- **Extra Protection**: Bahkan owner harus explicitly chmod untuk edit
- **Audit Trail**: Perubahan memerlukan conscious action
- **Compliance Requirements**: Beberapa standar keamanan memerlukan read-only secrets

#### Contoh Penggunaan
```bash
# Read-only certificates
chmod 400 /etc/ssl/certs/ca-bundle.crt

# Master encryption keys
chmod 400 /etc/myapp/master.key

# License files
chmod 400 /opt/software/license.key

# Backup encryption keys
chmod 400 /backup/keys/master.gpg
```

#### File Types yang Sesuai
- CA certificates (read-only after install)
- Master encryption keys
- Software license keys
- HSM export keys
- Archived credentials

---

### ⚙️ Permission 500 (`r-x------`)

#### Breakdown Akses
```
Owner:  r (read) + - (no write) + x (execute) = READ + EXECUTE
Group:  - (none) + - (none) + - (none)        = NO ACCESS
Others: - (none) + - (none) + - (none)        = NO ACCESS
```

#### Kenapa Digunakan?
- **Protected Executables**: Script yang hanya owner boleh run, tidak boleh modify
- **Security Tools**: Utilities yang perlu protected dari tampering
- **Integrity Protection**: Mencegah modification tanpa explicit permission change

#### Contoh Penggunaan
```bash
# Security audit scripts
chmod 500 /root/security-audit.sh

# Backup automation (protected)
chmod 500 /usr/local/sbin/secure-backup.sh

# Key rotation scripts
chmod 500 /opt/security/rotate-keys.sh
```

#### File Types yang Sesuai
- Security audit scripts
- Credential rotation utilities
- Private automation scripts
- System hardening tools
- Forensic collection scripts

---

## 🟠 MEDIUM RISK → Balanced Permissions

### Filosofi
File dengan sensitivitas sedang memerlukan **keseimbangan antara keamanan dan fungsionalitas**. Group access mungkin diperlukan untuk collaboration, tapi world access tetap dibatasi.

### Daftar Permission Valid

| Permission | Symbolic | Owner | Group | Others | Use Case |
|:----------:|:--------:|:-----:|:-----:|:------:|:---------|
| **640** | `rw-r-----` | rw- | r-- | --- | Shared configs |
| **644** | `rw-r--r--` | rw- | r-- | r-- | Standard files |
| **755** | `rwxr-xr-x` | rwx | r-x | r-x | Executables/dirs |
| **750** | `rwxr-x---` | rwx | r-x | --- | Group-shared dirs |

---

### 📄 Permission 640 (`rw-r-----`)

#### Breakdown Akses
```
Owner:  r (read) + w (write) + - (no exec) = READ + WRITE
Group:  r (read) + - (no write) + - (no exec) = READ ONLY
Others: - (none) + - (none) + - (none)        = NO ACCESS
```

#### Kenapa Digunakan?
- **Team Collaboration**: Group members dapat read, hanya owner yang write
- **Controlled Sharing**: Lebih aman dari 644 karena block world access
- **Service Accounts**: Apps running as group member dapat read configs

#### Contoh Penggunaan
```bash
# Application config readable by app group
chmod 640 /etc/myapp/config.yaml
chown root:myapp-group /etc/myapp/config.yaml

# Log files for monitoring group
chmod 640 /var/log/myapp/application.log

# SSL cert readable by web server group
chmod 640 /etc/ssl/certs/mysite.crt
chown root:www-data /etc/ssl/certs/mysite.crt
```

#### File Types yang Sesuai
- Application configuration files
- Service-specific log files
- SSL certificates (public cert, bukan private key)
- Shared team documentation
- Internal API documentation

---

### 📄 Permission 644 (`rw-r--r--`)

#### Breakdown Akses
```
Owner:  r (read) + w (write) + - (no exec) = READ + WRITE
Group:  r (read) + - (no write) + - (no exec) = READ ONLY
Others: r (read) + - (no write) + - (no exec) = READ ONLY
```

#### Kenapa Digunakan?
- **Default untuk Regular Files**: Standard UNIX permission untuk files
- **Public Readable**: Semua user dapat baca, hanya owner yang edit
- **Web Assets**: Ideal untuk static files yang perlu served ke users

#### Contoh Penggunaan
```bash
# Standard web files
chmod 644 /var/www/html/index.html
chmod 644 /var/www/html/style.css

# Public configuration
chmod 644 /etc/hosts
chmod 644 /etc/resolv.conf

# Documentation
chmod 644 README.md
chmod 644 /usr/share/doc/package/manual.txt
```

#### File Types yang Sesuai
- HTML, CSS, JavaScript files
- README dan documentation
- Public configuration files
- Images dan static assets
- Package manifests (package.json, requirements.txt)

---

### 📁 Permission 755 (`rwxr-xr-x`)

#### Breakdown Akses
```
Owner:  r (read) + w (write) + x (execute) = FULL ACCESS
Group:  r (read) + - (no write) + x (execute) = READ + EXECUTE
Others: r (read) + - (no write) + x (execute) = READ + EXECUTE
```

#### Kenapa Digunakan?
- **Standard untuk Executables**: Default untuk scripts dan binaries
- **Directory Access**: Allows `cd` dan listing untuk all users
- **Shared Utilities**: System-wide tools yang semua user perlu akses

#### Contoh Penggunaan
```bash
# System executables
chmod 755 /usr/local/bin/mytool

# Web directories
chmod 755 /var/www/html/

# Application directories
chmod 755 /opt/myapp/

# Shared scripts
chmod 755 /usr/local/bin/common-script.sh
```

#### File Types yang Sesuai
- Binary executables
- Shell scripts (shared)
- Directories yang perlu traversed
- Application root directories
- CGI scripts

---

### 📁 Permission 750 (`rwxr-x---`)

#### Breakdown Akses
```
Owner:  r (read) + w (write) + x (execute) = FULL ACCESS
Group:  r (read) + - (no write) + x (execute) = READ + EXECUTE
Others: - (none) + - (none) + - (none)        = NO ACCESS
```

#### Kenapa Digunakan?
- **Group-Exclusive Access**: Team members dapat access, others tidak
- **Security + Collaboration**: Balance antara team needs dan security
- **Service Isolation**: App group dapat access, other services tidak

#### Contoh Penggunaan
```bash
# Application home directory
chmod 750 /opt/myapp/
chown appuser:appgroup /opt/myapp/

# Team project directory
chmod 750 /home/projects/team-alpha/

# Log directory for monitoring team
chmod 750 /var/log/application/
chown root:monitoring /var/log/application/
```

#### File Types yang Sesuai
- Application home directories
- Team project folders
- Log directories dengan restricted access
- Deployment directories
- Build output directories

---

## 🟢 LOW RISK → Permissive Permissions

### Filosofi
File dengan sensitivitas rendah dapat memiliki **permission lebih longgar** untuk memudahkan akses dan kolaborasi. Hanya gunakan untuk file yang memang intended untuk public access.

> ⚠️ **Warning**: Permission ini HANYA untuk file yang benar-benar non-sensitif. Jangan gunakan untuk production systems tanpa justifikasi jelas.

### Daftar Permission Valid

| Permission | Symbolic | Owner | Group | Others | Use Case |
|:----------:|:--------:|:-----:|:-----:|:------:|:---------|
| **666** | `rw-rw-rw-` | rw- | rw- | rw- | Shared temp files |
| **777** | `rwxrwxrwx` | rwx | rwx | rwx | Public directories |
| **664** | `rw-rw-r--` | rw- | rw- | r-- | Collaborative files |
| **757** | `rwxr-xrwx` | rwx | r-x | rwx | Mixed access dirs |

---

### 📄 Permission 666 (`rw-rw-rw-`)

#### Breakdown Akses
```
Owner:  r (read) + w (write) + - (no exec) = READ + WRITE
Group:  r (read) + w (write) + - (no exec) = READ + WRITE
Others: r (read) + w (write) + - (no exec) = READ + WRITE
```

#### Kenapa Digunakan?
- **Fully Collaborative Files**: Semua users dapat edit
- **Temporary Processing**: Files yang di-process oleh multiple services
- **Development Only**: Quick collaboration tanpa permission management

#### Contoh Penggunaan
```bash
# Shared temp files (development only)
chmod 666 /tmp/shared-data.txt

# Inter-process communication files
chmod 666 /var/run/myapp/shared.sock

# Public upload staging (dengan sandboxing)
chmod 666 /var/spool/uploads/incoming/*
```

#### File Types yang Sesuai
- Temporary processing files
- IPC (Inter-Process Communication) files
- Development shared files
- Public writable logs (sandboxed)
- Collaborative editing buffers

#### ⚠️ Security Considerations
```
RISIKO:
- Any user dapat modify → potential for malicious changes
- No accountability → sulit trace siapa yang modify
- Data integrity issues → race conditions

MITIGASI:
- Gunakan hanya di sandboxed environments
- Limit ke specific use cases
- Implement application-level validation
- Regular cleanup/rotation
```

---

### 📁 Permission 777 (`rwxrwxrwx`)

#### Breakdown Akses
```
Owner:  r (read) + w (write) + x (execute) = FULL ACCESS
Group:  r (read) + w (write) + x (execute) = FULL ACCESS
Others: r (read) + w (write) + x (execute) = FULL ACCESS
```

#### Kenapa Digunakan?
- **Maximum Accessibility**: Tidak ada restriction sama sekali
- **Public Directories**: Upload folders, temp directories
- **Development Convenience**: Testing dan rapid prototyping

#### Contoh Penggunaan
```bash
# Temporary directory (system default)
chmod 777 /tmp

# Public upload directory (with proper app validation)
chmod 777 /var/www/uploads/

# Shared development workspace
chmod 777 /home/shared/dev-playground/

# Cache directories
chmod 777 /var/cache/public/
```

#### File Types yang Sesuai
- `/tmp` dan temporary directories
- Public upload folders (dengan app-level security)
- Shared development directories
- Cache directories
- Public spool directories

#### ⚠️ Security Considerations
```
RISIKO:
- HIGHEST RISK permission
- Any user dapat create, modify, delete, execute
- Potential for privilege escalation
- Malware deposit point

MITIGASI:
- NEVER use di production untuk sensitive data
- Implement sticky bit (+t) untuk shared dirs
- Regular security audits
- Application-level access controls
- Filesystem quotas
```

---

### 📄 Permission 664 (`rw-rw-r--`)

#### Breakdown Akses
```
Owner:  r (read) + w (write) + - (no exec) = READ + WRITE
Group:  r (read) + w (write) + - (no exec) = READ + WRITE
Others: r (read) + - (no write) + - (no exec) = READ ONLY
```

#### Kenapa Digunakan?
- **Team Editable, Public Readable**: Group collaboration dengan public visibility
- **Documentation**: Files yang team maintain, public dapat baca
- **Moderate Collaboration**: Lebih aman dari 666

#### Contoh Penggunaan
```bash
# Team-edited documentation
chmod 664 /var/www/docs/manual.html
chown www-data:editors /var/www/docs/manual.html

# Shared content files
chmod 664 /home/projects/articles/*.md

# Public data files
chmod 664 /var/lib/myapp/public-data.json
```

#### File Types yang Sesuai
- Collaborative documentation
- Shared content management files
- Public data exports
- Team-maintained static content
- Version-controlled files (with proper git setup)

---

### 📁 Permission 757 (`rwxr-xrwx`)

#### Breakdown Akses
```
Owner:  r (read) + w (write) + x (execute) = FULL ACCESS
Group:  r (read) + - (no write) + x (execute) = READ + EXECUTE
Others: r (read) + w (write) + x (execute) = READ + WRITE + EXECUTE
```

#### Kenapa Digunakan?
- **Public Writable Directory dengan Group Read**: Unusual case untuk specific workflows
- **Mixed Access Scenarios**: Owner full, group read/exec, public full
- **Legacy Compatibility**: Some older systems require this pattern

#### Contoh Penggunaan
```bash
# Public contribution directory
chmod 757 /var/www/public-contributions/

# Mixed-access spool
chmod 757 /var/spool/public-jobs/
```

#### File Types yang Sesuai
- Public contribution directories
- Legacy application requirements
- Special workflow directories
- Rarely used - prefer alternatives

#### ⚠️ Security Note
```
Permission 757 adalah unusual dan jarang digunakan.
Biasanya indicate misconfiguration atau legacy requirement.
Prefer 755 atau 777 dengan proper controls.
```

---

## 📋 Complete Mapping Summary

### Risk Level → Permission Matrix

```
┌─────────────────────────────────────────────────────────────────────┐
│                    RISK LEVEL TO PERMISSION MAPPING                  │
├──────────┬──────────────┬───────────────┬───────────────────────────┤
│ RISK     │ PERMISSION   │ SYMBOLIC      │ PRIMARY USE CASE          │
├──────────┼──────────────┼───────────────┼───────────────────────────┤
│          │ 700          │ rwx------     │ Private directories       │
│ 🔴 HIGH  │ 600          │ rw-------     │ Sensitive files           │
│          │ 400          │ r--------     │ Read-only secrets         │
│          │ 500          │ r-x------     │ Protected executables     │
├──────────┼──────────────┼───────────────┼───────────────────────────┤
│          │ 640          │ rw-r-----     │ Group-readable configs    │
│ 🟠 MEDIUM│ 644          │ rw-r--r--     │ Standard files            │
│          │ 755          │ rwxr-xr-x     │ Standard executables/dirs │
│          │ 750          │ rwxr-x---     │ Group-accessible dirs     │
├──────────┼──────────────┼───────────────┼───────────────────────────┤
│          │ 666          │ rw-rw-rw-     │ Shared temp files         │
│ 🟢 LOW   │ 777          │ rwxrwxrwx     │ Public directories        │
│          │ 664          │ rw-rw-r--     │ Collaborative files       │
│          │ 757          │ rwxr-xrwx     │ Mixed access (rare)       │
└──────────┴──────────────┴───────────────┴───────────────────────────┘
```

### Decision Flowchart

```
                    ┌──────────────────────┐
                    │ Apakah file berisi   │
                    │ credentials/secrets? │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │ YES            │                │ NO
              ▼                │                ▼
    ┌─────────────────┐        │     ┌─────────────────────┐
    │ 🔴 HIGH RISK    │        │     │ Apakah file perlu   │
    │ Use: 600/700    │        │     │ group collaboration?│
    └─────────────────┘        │     └──────────┬──────────┘
                               │                │
                               │    ┌───────────┼───────────┐
                               │    │ YES       │           │ NO
                               │    ▼           │           ▼
                               │  ┌────────────────┐  ┌────────────────┐
                               │  │🟠 MEDIUM RISK  │  │ Apakah public  │
                               │  │Use: 640/750    │  │ writable OK?   │
                               │  └────────────────┘  └───────┬────────┘
                               │                              │
                               │                    ┌─────────┼─────────┐
                               │                    │ YES     │         │ NO
                               │                    ▼         │         ▼
                               │           ┌──────────────┐   │  ┌──────────────┐
                               │           │ 🟢 LOW RISK  │   │  │🟠 MEDIUM RISK│
                               │           │Use: 666/777  │   │  │Use: 644/755  │
                               │           └──────────────┘   │  └──────────────┘
                               │                              │
                               └──────────────────────────────┘
```

---

## ✅ Acceptance Criteria Checklist

- [x] **High Risk permissions terdaftar**: 700, 600, 400, 500
- [x] **Medium Risk permissions terdaftar**: 640, 644, 755, 750
- [x] **Low Risk permissions terdaftar**: 666, 777, 664, 757
- [x] **Penjelasan per permission**: Breakdown akses dan alasan penggunaan
- [x] **Use case examples**: Contoh file dan command untuk setiap permission
- [x] **Security considerations**: Warning untuk permission berbahaya

---

**Document Version**: 1.0  
**Created**: 2025-12-21  
**Last Updated**: 2025-12-21  
**Related**: [RISK_LEVEL_SPECIFICATION.md](./RISK_LEVEL_SPECIFICATION.md)
