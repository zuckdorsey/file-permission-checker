# Risk Level to UNIX Permission Mapping

## Overview

This document defines the mapping between Risk Levels and valid UNIX permissions. Risk Level indicates file sensitivity:

- **High Risk** = Highly sensitive files requiring strictest permissions
- **Medium Risk** = Moderately sensitive files requiring balanced permissions
- **Low Risk** = Non-sensitive files that can use more permissive access

## Quick Reference Table

| Risk Level | Valid Permissions | Characteristics | Example Files |
|------------|-------------------|-----------------|---------------|
| High | 700, 600, 400, 500 | Owner-only access | .env, private keys, passwords |
| Medium | 640, 644, 755, 750 | Controlled sharing | configs, scripts, logs |
| Low | 666, 777, 664, 757 | Open access | public assets, temp files |

## High Risk Permissions

### Philosophy

Highly sensitive files must have the strictest permissions. Only the owner should have access, with no access for group or world.

### Valid Permissions

| Permission | Symbolic | Owner | Group | Others | Use Case |
|------------|----------|-------|-------|--------|----------|
| 700 | rwx------ | rwx | --- | --- | Private directories |
| 600 | rw------- | rw- | --- | --- | Sensitive files |
| 400 | r-------- | r-- | --- | --- | Read-only secrets |
| 500 | r-x------ | r-x | --- | --- | Read-only executables |

### Permission 700

**Access Breakdown**
```
Owner:  r (read) + w (write) + x (execute) = FULL ACCESS
Group:  - (none) + - (none) + - (none)     = NO ACCESS
Others: - (none) + - (none) + - (none)     = NO ACCESS
```

**Usage**
```bash
chmod 700 ~/.ssh
chmod 700 /opt/myapp/secrets/
chmod 700 ~/.config/credentials/
```

**Applicable File Types**
- SSH configuration directory
- GPG keys directory
- Root home directory
- Private backup directories
- Encrypted vault directories

### Permission 600

**Access Breakdown**
```
Owner:  r (read) + w (write) + - (no exec) = READ + WRITE
Group:  - (none) + - (none) + - (none)     = NO ACCESS
Others: - (none) + - (none) + - (none)     = NO ACCESS
```

**Usage**
```bash
chmod 600 .env
chmod 600 ~/.ssh/id_rsa
chmod 600 /etc/ssl/private/server.key
chmod 600 /etc/myapp/db.conf
```

**Applicable File Types**
- Environment files (.env)
- SSH private keys (id_rsa, id_ed25519)
- Encryption keys and certificates (*.key, *.pem)
- Database connection configs
- Password files (*.pwd, *.secret)

### Permission 400

**Access Breakdown**
```
Owner:  r (read) + - (no write) + - (no exec) = READ ONLY
Group:  - (none) + - (none) + - (none)        = NO ACCESS
Others: - (none) + - (none) + - (none)        = NO ACCESS
```

**Usage**
```bash
chmod 400 /etc/ssl/certs/ca-bundle.crt
chmod 400 /etc/myapp/master.key
chmod 400 /opt/software/license.key
```

**Applicable File Types**
- CA certificates (read-only after install)
- Master encryption keys
- Software license keys
- Archived credentials

### Permission 500

**Access Breakdown**
```
Owner:  r (read) + - (no write) + x (execute) = READ + EXECUTE
Group:  - (none) + - (none) + - (none)        = NO ACCESS
Others: - (none) + - (none) + - (none)        = NO ACCESS
```

**Usage**
```bash
chmod 500 /root/security-audit.sh
chmod 500 /usr/local/sbin/secure-backup.sh
chmod 500 /opt/security/rotate-keys.sh
```

**Applicable File Types**
- Security audit scripts
- Credential rotation utilities
- Private automation scripts
- System hardening tools

## Medium Risk Permissions

### Philosophy

Moderately sensitive files require a balance between security and functionality. Group access may be necessary for collaboration, but world access should be limited.

### Valid Permissions

| Permission | Symbolic | Owner | Group | Others | Use Case |
|------------|----------|-------|-------|--------|----------|
| 640 | rw-r----- | rw- | r-- | --- | Shared configs |
| 644 | rw-r--r-- | rw- | r-- | r-- | Standard files |
| 755 | rwxr-xr-x | rwx | r-x | r-x | Executables/dirs |
| 750 | rwxr-x--- | rwx | r-x | --- | Group-shared dirs |

### Permission 640

**Access Breakdown**
```
Owner:  r (read) + w (write) + - (no exec) = READ + WRITE
Group:  r (read) + - (no write) + - (no exec) = READ ONLY
Others: - (none) + - (none) + - (none)        = NO ACCESS
```

**Usage**
```bash
chmod 640 /etc/myapp/config.yaml
chown root:myapp-group /etc/myapp/config.yaml

chmod 640 /var/log/myapp/application.log
```

**Applicable File Types**
- Application configuration files
- Service-specific log files
- SSL certificates (public cert, not private key)
- Shared team documentation

### Permission 644

**Access Breakdown**
```
Owner:  r (read) + w (write) + - (no exec) = READ + WRITE
Group:  r (read) + - (no write) + - (no exec) = READ ONLY
Others: r (read) + - (no write) + - (no exec) = READ ONLY
```

**Usage**
```bash
chmod 644 /var/www/html/index.html
chmod 644 /var/www/html/style.css
chmod 644 README.md
```

**Applicable File Types**
- HTML, CSS, JavaScript files
- README and documentation
- Public configuration files
- Images and static assets
- Package manifests (package.json, requirements.txt)

### Permission 755

**Access Breakdown**
```
Owner:  r (read) + w (write) + x (execute) = FULL ACCESS
Group:  r (read) + - (no write) + x (execute) = READ + EXECUTE
Others: r (read) + - (no write) + x (execute) = READ + EXECUTE
```

**Usage**
```bash
chmod 755 /usr/local/bin/mytool
chmod 755 /var/www/html/
chmod 755 /opt/myapp/
```

**Applicable File Types**
- Binary executables
- Shell scripts (shared)
- Directories that need to be traversed
- Application root directories
- CGI scripts

### Permission 750

**Access Breakdown**
```
Owner:  r (read) + w (write) + x (execute) = FULL ACCESS
Group:  r (read) + - (no write) + x (execute) = READ + EXECUTE
Others: - (none) + - (none) + - (none)        = NO ACCESS
```

**Usage**
```bash
chmod 750 /opt/myapp/
chown appuser:appgroup /opt/myapp/

chmod 750 /home/projects/team-alpha/
```

**Applicable File Types**
- Application home directories
- Team project folders
- Log directories with restricted access
- Deployment directories
- Build output directories

## Low Risk Permissions

### Philosophy

Low sensitivity files can have more permissive access for convenience and collaboration. Only use for files that are truly intended for public access.

**Warning**: These permissions should ONLY be used for genuinely non-sensitive files. Do not use on production systems without clear justification.

### Valid Permissions

| Permission | Symbolic | Owner | Group | Others | Use Case |
|------------|----------|-------|-------|--------|----------|
| 666 | rw-rw-rw- | rw- | rw- | rw- | Shared temp files |
| 777 | rwxrwxrwx | rwx | rwx | rwx | Public directories |
| 664 | rw-rw-r-- | rw- | rw- | r-- | Collaborative files |
| 757 | rwxr-xrwx | rwx | r-x | rwx | Mixed access dirs |

### Permission 666

**Access Breakdown**
```
Owner:  r (read) + w (write) + - (no exec) = READ + WRITE
Group:  r (read) + w (write) + - (no exec) = READ + WRITE
Others: r (read) + w (write) + - (no exec) = READ + WRITE
```

**Usage**
```bash
chmod 666 /tmp/shared-data.txt
chmod 666 /var/run/myapp/shared.sock
```

**Applicable File Types**
- Temporary processing files
- IPC (Inter-Process Communication) files
- Development shared files
- Public writable logs (sandboxed)

**Security Considerations**
- Any user can modify (potential for malicious changes)
- No accountability (difficult to trace who modified)
- Data integrity issues (race conditions)
- Use only in sandboxed environments with proper validation

### Permission 777

**Access Breakdown**
```
Owner:  r (read) + w (write) + x (execute) = FULL ACCESS
Group:  r (read) + w (write) + x (execute) = FULL ACCESS
Others: r (read) + w (write) + x (execute) = FULL ACCESS
```

**Usage**
```bash
chmod 777 /tmp
chmod 777 /var/www/uploads/
chmod 777 /home/shared/dev-playground/
```

**Applicable File Types**
- /tmp and temporary directories
- Public upload folders (with app-level security)
- Shared development directories
- Cache directories

**Security Considerations**
- HIGHEST RISK permission
- Any user can create, modify, delete, execute
- Potential for privilege escalation
- Malware deposit point
- NEVER use in production for sensitive data
- Implement sticky bit (+t) for shared directories

### Permission 664

**Access Breakdown**
```
Owner:  r (read) + w (write) + - (no exec) = READ + WRITE
Group:  r (read) + w (write) + - (no exec) = READ + WRITE
Others: r (read) + - (no write) + - (no exec) = READ ONLY
```

**Usage**
```bash
chmod 664 /var/www/docs/manual.html
chown www-data:editors /var/www/docs/manual.html
```

**Applicable File Types**
- Collaborative documentation
- Shared content management files
- Public data exports
- Team-maintained static content

## Complete Mapping Summary

```
RISK LEVEL TO PERMISSION MAPPING

| RISK   | PERMISSION | SYMBOLIC    | PRIMARY USE CASE           |
|--------|------------|-------------|----------------------------|
|        | 700        | rwx------   | Private directories        |
| HIGH   | 600        | rw-------   | Sensitive files            |
|        | 400        | r--------   | Read-only secrets          |
|        | 500        | r-x------   | Protected executables      |
|--------|------------|-------------|----------------------------|
|        | 640        | rw-r-----   | Group-readable configs     |
| MEDIUM | 644        | rw-r--r--   | Standard files             |
|        | 755        | rwxr-xr-x   | Standard executables/dirs  |
|        | 750        | rwxr-x---   | Group-accessible dirs      |
|--------|------------|-------------|----------------------------|
|        | 666        | rw-rw-rw-   | Shared temp files          |
| LOW    | 777        | rwxrwxrwx   | Public directories         |
|        | 664        | rw-rw-r--   | Collaborative files        |
|        | 757        | rwxr-xrwx   | Mixed access (rare)        |
```

## Decision Flowchart

```
Does file contain credentials/secrets?
    |
    +--YES--> HIGH RISK: Use 600 or 700
    |
    +--NO---> Does file need group collaboration?
                  |
                  +--YES--> MEDIUM RISK: Use 640 or 750
                  |
                  +--NO---> Is public writable access acceptable?
                                |
                                +--YES--> LOW RISK: Use 666 or 777
                                |
                                +--NO---> MEDIUM RISK: Use 644 or 755
```

---

Version: 1.0
Last Updated: 2025-12-21
Related: [RISK_LEVEL_SPECIFICATION.md](./RISK_LEVEL_SPECIFICATION.md)
