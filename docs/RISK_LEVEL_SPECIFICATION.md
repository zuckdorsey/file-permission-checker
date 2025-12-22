# Risk Level Specification

## Overview

This document defines the risk level categories for the File Permission Checker application. **Risk is determined by a matrix of file sensitivity AND current permissions.**

## Risk Matrix

| File Sensitivity | Current Permission | Result |
|:-----------------|:-------------------|:-------|
| **High** (e.g., `.env`, `.key`) | > 600 (loose) | **High Risk** |
| **High** | ≤ 600 (strict) | **Low Risk** (Secure) |
| **Medium** (e.g., `.conf`, `.sh`) | Group/World writable | **Medium Risk** |
| **Medium** | ≤ 644 (proper) | **Low Risk** |
| **Low** | Any | **Low Risk** |

> **Key Change (v2.0):** Risk now reflects security posture, not just file sensitivity. A sensitive file with proper permissions is "Low Risk" (secure).

## High Sensitivity Files

These files contain secrets and must have strict permissions (600 or stricter):

**Extensions:**
- `.env`, `.key`, `.pem`, `.crt`, `.p12`, `.pfx`
- `.pwd`, `.password`, `.secret`, `.token`
- `.credentials`, `.auth`

**Patterns:**
- `id_rsa`, `id_dsa`, `id_ecdsa`, `id_ed25519`
- `authorized_keys`, `known_hosts`
- `.htpasswd`, `.htaccess`
- `shadow`, `passwd`, `sudoers`
- `master.key`, `credentials.yml`, `secrets.yaml`

**Directories:**
- `.ssh/`, `.gnupg/`, `private/`, `secrets/`, `credentials/`

## Medium Sensitivity Files

Configuration and script files that should be protected from group/world write:

**Extensions:**
- `.conf`, `.config`, `.cfg`, `.ini`, `.yaml`, `.yml`
- `.sql`, `.db`, `.sqlite`, `.sqlite3`
- `.sh`, `.bash`, `.zsh`, `.py`, `.rb`, `.pl`
- `.log`

**Patterns:**
- `config`, `settings`, `database`
- `nginx`, `apache`, `httpd`
- `docker-compose`, `dockerfile`

## Risk Level Actions

| Risk Level | Action Required | Recommended Permission |
|:-----------|:----------------|:-----------------------|
| **High** | Immediate fix | 600 (rw-------) |
| **Medium** | Review needed | 644 (rw-r--r--) |
| **Low** | None | Current is acceptable |

## Permission Quick Reference

### Sensitive Files (Must be 600)
```
600 (rw-------)  → .env, .key, .pem, id_rsa
400 (r--------)  → Read-only secrets
```

### Config/Scripts (Should be 644/755)
```
644 (rw-r--r--)  → Config files (.conf, .yaml)
755 (rwxr-xr-x)  → Executables (.sh, .py)
```

### Standard Files (Flexible)
```
644 (rw-r--r--)  → Regular files
755 (rwxr-xr-x)  → Directories
```

## CIA Triad Impact

| Aspect | High Risk | Medium Risk | Low Risk |
|:-------|:----------|:------------|:---------|
| **Confidentiality** | Critical - Full exposure | Moderate - Group exposure | Minimal |
| **Integrity** | Critical - Anyone can modify | Moderate - Group can modify | Owner-only |
| **Availability** | High - Service disruption | Moderate - Instability | Stable |

---

Version: 2.0
Last Updated: 2025-12-23
