# Risk Level Specification

## Overview

This document defines the risk level categories for file permissions in the File Permission Checker application. Each risk level describes the potential impact if files with dangerous permissions are exploited.

## Risk Level Summary

| Level | Permission Examples | Potential Impact |
|-------|---------------------|------------------|
| High | 777, 666, 767, 676 | Critical - Full access by anyone |
| Medium | 775, 664, 755 (on sensitive files) | Moderate - Group/World can read/execute |
| Low | 644, 600, 755 (standard) | Minimal - Permissions follow security standards |

## High Risk

### Definition

Files with permissions that allow anyone (other/world) to read, write, and/or execute without restrictions. This is the most dangerous condition because there is no effective access control.

### Permission Patterns

| Octal | Symbolic | Description |
|-------|----------|-------------|
| 777 | rwxrwxrwx | All users can read, write, execute |
| 666 | rw-rw-rw- | All users can read and write |
| 767 | rwxrw-rwx | Owner and World full access |
| 676 | rw-rwxrw- | Group full access, owner/world read-write |

### Sensitive File Extensions

Files with these extensions are automatically categorized as High Risk if they have group/world access:

- .env - Environment variables
- .key - Encryption keys
- .pem - SSL/TLS certificates and private keys
- .conf - Configuration files
- .ini - Configuration files
- .sql - Database scripts/dumps
- .db - Database files
- .pwd - Password files

### Impact Analysis

**Confidentiality**
- Credential files can be read by any user on the system
- API keys, database passwords, encryption keys exposed
- Sensitive configuration data leaked

**Integrity**
- Attackers can modify file contents freely
- Scripts and executables can be altered for malicious purposes
- Configuration tampering to facilitate further attacks

**Availability**
- Data can be corrupted or deleted intentionally
- Configuration changes causing service crashes
- Entry point for ransomware attacks

### Recommended Actions

- Immediate fix required
- Standard safe permission: 600 (rw-------)
- Use "Fix Risky Permissions" feature

## Medium Risk

### Definition

Files with permissions that allow group or other/world to have more access than necessary, but not completely open. This requires attention but is not as critical as High Risk.

### Permission Patterns

| Octal | Symbolic | Description |
|-------|----------|-------------|
| 775 | rwxrwxr-x | Group write + world execute |
| 664 | rw-rw-r-- | Group write + world read |
| 755 (sensitive) | rwxr-xr-x | World execute on sensitive file |
| Symlinks | Any | Symbolic links (pointer risks) |

### Conditions

1. Group-writable files (mode[1] = 6 or 7)
2. World-executable non-standard files
3. Symbolic links (inherent redirection risk)
4. Sensitive extensions with group/world read

### Impact Analysis

**Confidentiality**
- Limited exposure to users in specific groups
- Configuration files readable by unintended users
- Information gathering for reconnaissance

**Integrity**
- Members of same group can modify files
- Symlink attacks redirecting to malicious targets
- Subtle tampering that is difficult to detect

**Availability**
- Configuration changes causing unexpected behavior
- Shared files can be locked or modified

### Recommended Actions

- Review required
- Recommended permission: 644 for files, 755 for directories
- Consider tightening if no business justification

## Low Risk

### Definition

Files with permissions that follow security best practices. Owner has full control while group and world have minimal or no access.

### Permission Patterns

| Octal | Symbolic | Typical Use |
|-------|----------|-------------|
| 644 | rw-r--r-- | Regular files (default) |
| 600 | rw------- | Private/sensitive files |
| 755 | rwxr-xr-x | Executables/directories (standard) |
| 700 | rwx------ | Private directories |
| 640 | rw-r----- | Shared read within group |
| 750 | rwxr-x--- | Group-accessible directories |

### Characteristics

1. Owner-centric access: Only owner can write
2. Principle of least privilege: Minimal access for others
3. Industry standard permissions: Following UNIX best practices
4. No write for group/others: Prevents unauthorized modification

### Impact Analysis

**Confidentiality**
- Data only accessible by owner
- Read-only for others on non-sensitive information
- Standard exposure with no unexpected leaks

**Integrity**
- Changes require owner privileges
- Easier to track modifications
- Unauthorized writes will fail

**Availability**
- Standard permissions provide predictable behavior
- Files protected from accidental deletion
- No unexpected permission-related issues

### Recommended Actions

- No action required
- Continue monitoring for changes
- Document any custom requirements

## Sensitivity Mapping

### Priority Matrix

| Risk Level | Data Sensitivity | Action Priority | Fix Urgency | Review Cycle |
|------------|------------------|-----------------|-------------|--------------|
| High | Critical / Confidential | P1 - Immediate | Within 24 hours | Real-time |
| Medium | Sensitive / Internal | P2 - High | Within 1 week | Weekly |
| Low | Public / Normal | P3 - Low | Routine | Monthly |

### Data Classification

**Critical Data (High Risk Files)**
- Encryption keys and certificates
- Database credentials
- API secrets and tokens
- Payment gateway keys
- Personal Identifiable Information (PII)

**Sensitive Data (Medium Risk Files)**
- Application configurations
- Internal documentation
- Log files with business data
- Non-production credentials
- User-generated content

**Normal Data (Low Risk Files)**
- Public web assets (HTML, CSS, JS)
- Documentation files
- Open-source code
- Static resources
- Compiled binaries

## CIA Triad Summary

| Aspect | High Risk | Medium Risk | Low Risk |
|--------|-----------|-------------|----------|
| Confidentiality | Critical - Full exposure | Moderate - Group exposure | Minimal - Controlled access |
| Integrity | Critical - Anyone can modify | Moderate - Group can modify | Minimal - Owner-only modify |
| Availability | High - Service disruption | Moderate - Instability risk | Minimal - Stable operations |

## Quick Reference

### Dangerous Permissions (Avoid)

```
777 - World writable and executable (never use)
666 - World readable and writable (never use)
755 on .env files (avoid)
644 on private keys (avoid)
```

### Safe Defaults

```
Files:       644 (rw-r--r--)
Sensitive:   600 (rw-------)
Scripts:     755 (rwxr-xr-x)
Directories: 755 (rwxr-xr-x)
Private Dir: 700 (rwx------)
```

## References

1. Linux File Permissions - Red Hat Documentation
2. CIS Benchmarks - File Permissions
3. OWASP - File Upload Security
4. NIST SP 800-123 - Guide to General Server Security

---

Version: 1.0
Last Updated: 2025-12-21
