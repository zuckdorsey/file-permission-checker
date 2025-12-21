# 📋 Risk Level Specification Document

## File Permission Risk Level Analysis

Dokumen ini mendefinisikan kategori tingkat risiko untuk file permission dalam konteks **File Permission Checker** application. Setiap level risiko menggambarkan potensi dampak jika file dengan permission berbahaya disalahgunakan oleh pihak tidak bertanggung jawab.

---

## 🎯 Ringkasan Kategori Risk Level

| Level | Warna | Permission Examples | Dampak Potensial |
|:-----:|:-----:|:-------------------:|:-----------------|
| **High** | 🔴 Merah | 777, 666, 767, 676 | Kritikal - Akses penuh oleh siapapun |
| **Medium** | 🟠 Oranye | 775, 664, 755 (pada sensitive files) | Moderat - Group/World dapat membaca/exec |
| **Low** | 🟢 Hijau | 644, 600, 755 (standar) | Minimal - Permission sesuai standar keamanan |

---

## 🔴 Level 1: HIGH RISK (Risiko Tinggi)

### Definisi
File dengan permission yang memungkinkan **siapa saja** (other/world) untuk membaca, menulis, dan/atau mengeksekusi file tanpa batasan. Ini adalah kondisi paling berbahaya karena tidak ada kontrol akses yang efektif.

### Permission Patterns yang Termasuk High Risk

| Permission Octal | Symbolic | Penjelasan |
|:----------------:|:--------:|:-----------|
| `777` | `rwxrwxrwx` | Semua user dapat read, write, execute |
| `666` | `rw-rw-rw-` | Semua user dapat read dan write |
| `767` | `rwxrw-rwx` | Owner dan World full access |
| `676` | `rw-rwxrw-` | Group full access, owner/world read-write |

### Sensitive Files dengan Group/World Write Permission
Ekstensi file sensitif yang secara otomatis dikategorikan **High Risk** jika memiliki group/world access:

- `.env` - Environment variables (API keys, credentials)
- `.key` - Encryption keys
- `.pem` - SSL/TLS certificates & private keys
- `.conf` - Configuration files
- `.ini` - Configuration files
- `.sql` - Database scripts/dumps
- `.db` - Database files
- `.pwd` - Password files

### Dampak Jika Disalahgunakan

#### 🚨 Confidentiality Impact (CRITICAL)
- **Data Exposure**: File credentials (.env, .key) dapat dibaca oleh any user di sistem
- **Credential Theft**: API keys, database passwords, encryption keys terekspos
- **Sensitive Data Leak**: Informasi pribadi, konfigurasi sistem bocor

#### 🚨 Integrity Impact (CRITICAL)
- **Malicious Modification**: Attacker dapat mengubah isi file secara bebas
- **Code Injection**: Script/executable dapat dimodifikasi untuk malicious purposes
- **Configuration Tampering**: Settings diubah untuk memfasilitasi attack lebih lanjut

#### 🚨 Availability Impact (HIGH)
- **File Corruption**: Data dapat rusak/dihapus secara sengaja
- **Service Disruption**: Config files diubah menyebabkan service crash
- **Ransomware Entry Point**: Files dapat di-encrypt oleh malicious actors

### Use Case Examples

#### Use Case 1: Exposed API Keys
```
Skenario: File .env dengan permission 666
Path: /var/www/myapp/.env
Content: 
  DATABASE_URL=postgres://admin:secret123@db.example.com/prod
  STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxx

Dampak:
  ✗ Any user di server dapat membaca database credentials
  ✗ Payment gateway keys terekspos → financial fraud
  ✗ Attacker dapat memodifikasi credentials untuk redirect data
```

#### Use Case 2: World-Writable Script
```
Skenario: Cron script dengan permission 777
Path: /opt/scripts/daily_backup.sh

Dampak:
  ✗ Attacker inject malicious code ke script
  ✗ Code dieksekusi sebagai root (jika cron runs as root)
  ✗ Full system compromise via privilege escalation
```

#### Use Case 3: Exposed SSL Private Key
```
Skenario: SSL private key dengan permission 666
Path: /etc/ssl/private/server.key

Dampak:
  ✗ Attacker dapat decrypt HTTPS traffic
  ✗ Man-in-the-middle attacks menjadi mungkin
  ✗ Impersonation attacks dengan certificate yang valid
```

### Recommended Actions
- **Immediate Fix Required**: Permission harus segera diperbaiki
- **Standard Safe Permission**: `600` (rw-------)
- **Action**: Use "Fix Risky Permissions" feature

---

## 🟠 Level 2: MEDIUM RISK (Risiko Sedang)

### Definisi
File dengan permission yang memungkinkan **group** atau **other/world** memiliki akses lebih dari yang diperlukan, namun tidak sepenuhnya terbuka. Ini memerlukan perhatian tetapi tidak sekritis High Risk.

### Permission Patterns yang Termasuk Medium Risk

| Permission Octal | Symbolic | Penjelasan |
|:----------------:|:--------:|:-----------|
| `775` | `rwxrwxr-x` | Group write + world execute |
| `664` | `rw-rw-r--` | Group write + world read |
| `755` (sensitive) | `rwxr-xr-x` | World execute pada sensitive file |
| Symlinks | Any | Symbolic links (pointer risks) |

### Kondisi Medium Risk
1. **Group-Writable Files** (mode[1] = 6 atau 7)
2. **World-Executable Non-Standard Files**
3. **Symbolic Links** (inherent redirection risk)
4. **Sensitive Extensions dengan Group/World Read**

### Dampak Jika Disalahgunakan

#### ⚠️ Confidentiality Impact (MODERATE)
- **Limited Exposure**: Hanya user dalam group tertentu yang dapat akses
- **Information Leakage**: Config files readable oleh unintended users
- **Reconnaissance**: Attacker dapat gather system information

#### ⚠️ Integrity Impact (MODERATE)
- **Group-Level Modification**: Members of same group dapat modify
- **Symlink Attacks**: Redirect files ke malicious targets
- **Subtle Tampering**: Perubahan kecil yang sulit dideteksi

#### ⚠️ Availability Impact (LOW-MODERATE)
- **Service Instability**: Config changes menyebabkan unexpected behavior
- **Resource Manipulation**: Shared files dapat di-lock atau di-modify

### Use Case Examples

#### Use Case 1: Group-Writable Config
```
Skenario: Nginx config dengan permission 664
Path: /etc/nginx/sites-available/mysite.conf
Group: www-data

Dampak:
  ⚠ Any user dalam www-data group dapat modify config
  ⚠ Web developer yang tidak authorized dapat mengubah routing
  ⚠ Potential for internal misuse atau accidental changes
```

#### Use Case 2: Symbolic Link Vulnerability
```
Skenario: Symlink ke sensitive file
Path: /var/log/app/current.log → /etc/passwd

Dampak:
  ⚠ Log reading operations might expose passwd file
  ⚠ Log writing dengan elevated privileges bisa overwrite passwd
  ⚠ Symlink race conditions mungkin terjadi
```

#### Use Case 3: Executable Log File
```
Skenario: Log file dengan execute permission (755)
Path: /var/log/application.log

Dampak:
  ⚠ Jika attacker dapat inject code ke log
  ⚠ Executed via path traversal atau log inclusion attacks
  ⚠ Unnecessary permission surface area
```

### Recommended Actions
- **Review Required**: Evaluate apakah permission memang diperlukan
- **Recommended Permission**: `644` untuk files, `755` untuk directories
- **Action**: Consider tightening jika tidak ada justifikasi bisnis

---

## 🟢 Level 3: LOW RISK (Risiko Rendah)

### Definisi
File dengan permission yang mengikuti **best practices keamanan standar**. Owner memiliki kontrol penuh, sementara group dan world memiliki akses minimal atau tidak ada sama sekali.

### Permission Patterns yang Termasuk Low Risk

| Permission Octal | Symbolic | Typical Use |
|:----------------:|:--------:|:------------|
| `644` | `rw-r--r--` | Regular files (default) |
| `600` | `rw-------` | Private/sensitive files |
| `755` | `rwxr-xr-x` | Executable/directories (standar) |
| `700` | `rwx------` | Private directories |
| `640` | `rw-r-----` | Shared read within group |
| `750` | `rwxr-x---` | Group-accessible directories |

### Karakteristik Low Risk
1. **Owner-Centric Access**: Hanya owner yang dapat write
2. **Principle of Least Privilege**: Minimal access untuk others
3. **Industry Standard Permissions**: Mengikuti UNIX best practices
4. **No Write for Group/Others**: Mencegah unauthorized modification

### Dampak Jika Disalahgunakan

#### ✅ Confidentiality Impact (MINIMAL)
- **Controlled Access**: Data hanya accessible oleh owner
- **Read-Only for Others**: Informasi non-sensitif dapat dibaca
- **Standard Exposure**: Normal operation, no unexpected leaks

#### ✅ Integrity Impact (MINIMAL)
- **Owner-Only Modification**: Perubahan memerlukan owner privileges
- **Audit Trail**: Easier to track siapa yang modify
- **Change Control**: Unauthorized writes akan fail

#### ✅ Availability Impact (MINIMAL)
- **Stable Operation**: Standard permissions = predictable behavior
- **Protected Resources**: Files aman dari accidental deletion
- **Normal Service**: No unexpected permission-related issues

### Use Case Examples

#### Use Case 1: Standard Configuration File
```
Skenario: Application config dengan permission 644
Path: /etc/myapp/config.yaml

Status:
  ✓ Owner (root) dapat read/write
  ✓ Others dapat read (necessary untuk app operation)
  ✓ No write access untuk unauthorized users
  → Permission SESUAI dengan kebutuhan operasional
```

#### Use Case 2: Private Credentials File
```
Skenario: SSH private key dengan permission 600
Path: /home/user/.ssh/id_rsa

Status:
  ✓ Hanya owner yang dapat access
  ✓ SSH daemon akan reject jika permission lebih loose
  ✓ Industry standard untuk private keys
  → Permission OPTIMAL untuk sensitive file
```

#### Use Case 3: Executable Script
```
Skenario: Deployment script dengan permission 755
Path: /usr/local/bin/deploy.sh

Status:
  ✓ Owner dapat modify script
  ✓ All users dapat execute (intended behavior)
  ✓ No unauthorized modification possible
  → Permission SESUAI untuk shared executable
```

### Recommended Actions
- **No Action Required**: Permission sudah sesuai standar
- **Monitoring**: Tetap monitor untuk perubahan
- **Documentation**: Document jika ada custom requirements

---

## 📊 Risk Level → Sensitivity Mapping

### Mapping Matrix

| Risk Level | Data Sensitivity | Action Priority | Fix Urgency | Review Cycle |
|:----------:|:----------------:|:---------------:|:-----------:|:------------:|
| 🔴 **High** | Critical / Confidential | P1 - Immediate | ASAP (< 24h) | Real-time |
| 🟠 **Medium** | Sensitive / Internal | P2 - High | Soon (< 1 week) | Weekly |
| 🟢 **Low** | Public / Normal | P3 - Low | Routine | Monthly |

### Sensitivity Classification

#### Critical Data (High Risk Files)
- Encryption keys & certificates
- Database credentials
- API secrets & tokens
- Payment gateway keys
- Personal Identifiable Information (PII)

#### Sensitive Data (Medium Risk Files)
- Application configurations
- Internal documentation
- Log files dengan business data
- Non-production credentials
- User-generated content

#### Normal Data (Low Risk Files)
- Public web assets (HTML, CSS, JS)
- Documentation files
- Open-source code
- Static resources
- Compiled binaries

---

## 🛡️ CIA Triad Impact Summary

| Aspect | High Risk | Medium Risk | Low Risk |
|:------:|:---------:|:-----------:|:--------:|
| **Confidentiality** | 🔴 Critical - Full exposure | 🟠 Moderate - Group exposure | 🟢 Minimal - Controlled access |
| **Integrity** | 🔴 Critical - Anyone can modify | 🟠 Moderate - Group can modify | 🟢 Minimal - Owner-only modify |
| **Availability** | 🔴 High - Service disruption | 🟠 Moderate - Instability risk | 🟢 Minimal - Stable operations |

---

## 📝 Quick Reference Card

### Dangerous Permissions (AVOID)
```
777 - World writable & executable  → NEVER USE
666 - World readable & writable    → NEVER USE  
755 on .env files                  → AVOID
644 on private keys                → AVOID
```

### Safe Defaults
```
Files:       644 (rw-r--r--)
Sensitive:   600 (rw-------)
Scripts:     755 (rwxr-xr-x)
Directories: 755 (rwxr-xr-x)
Private Dir: 700 (rwx------)
```

### Application-Specific Rules
```python
CUSTOM_RULES = {
    '.env': '600',          # Environment files - owner only
    '.git': '700',          # Git directory - owner only
    'storage': '755',       # Storage directories
    'config': '644',        # Config files - readable
    'private': '600',       # Private files - owner only
    'id_rsa': '600',        # SSH keys - strict
    'authorized_keys': '600', # SSH authorized
    '*.key': '600',         # Any key files
    '*.pem': '600',         # SSL certificates
}
```

---

## ✅ Acceptance Criteria Checklist

- [x] **High Risk terdefinisi jelas**: Permission 777, 666, dan sensitive files dengan excessive access
- [x] **Medium Risk terdefinisi jelas**: Group-writable, symbolic links, dan moderate exposure  
- [x] **Low Risk terdefinisi jelas**: Standard safe permissions 644, 600, 755 sesuai konteks
- [x] **Dampak per level didokumentasikan**: CIA Triad impact untuk setiap level
- [x] **Use case examples disediakan**: 3 contoh real-world per kategori
- [x] **Mapping risk → sensitivity**: Matrix korelasi risk level dengan data sensitivity
- [x] **Actionable recommendations**: Safe defaults dan remediation steps

---

## 📚 References

1. [Linux File Permissions - Red Hat](https://www.redhat.com/sysadmin/linux-file-permissions-explained)
2. [CIS Benchmarks - File Permissions](https://www.cisecurity.org/benchmark)
3. [OWASP - File Upload Security](https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload)
4. [NIST SP 800-123 - Guide to General Server Security](https://csrc.nist.gov/publications/detail/sp/800-123/final)

---

**Document Version**: 1.0  
**Created**: 2025-12-21  
**Last Updated**: 2025-12-21  
**Author**: File Permission Checker Team
