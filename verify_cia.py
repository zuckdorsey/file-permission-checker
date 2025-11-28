import os
import sqlite3
import hashlib
import sys

def verify_cia():
    print("Memverifikasi Implementasi CIA...")
    
    # 1. Cek Permission Database (Confidentiality)
    db_path = 'scan_logs.db'
    if os.path.exists(db_path):
        mode = os.stat(db_path).st_mode
        perms = oct(mode)[-3:]
        print(f"Permission database: {perms}")
        if perms == '600':
            print("✅ Confidentiality: Permission database aman (600).")
        else:
            print(f"❌ Confidentiality: Permission database TIDAK aman ({perms}). Seharusnya 600.")
    else:
        print("⚠️ Database tidak ditemukan. Jalankan aplikasi terlebih dahulu.")

    # 2. Cek Integritas Export (Integrity)
    # Kita cek apakah logika kode ada di main.py menggunakan grep
    with open('main.py', 'r') as f:
        content = f.read()
        
    if 'hashlib.sha256()' in content and '.sha256' in content:
         print("✅ Integrity: Kode pembuatan checksum ditemukan.")
    else:
         print("❌ Integrity: Kode pembuatan checksum TIDAK ditemukan.")

    if 'os.chmod(filename, 0o600)' in content:
         print("✅ Confidentiality: Kode pembatasan permission file export ditemukan.")
    else:
         print("❌ Confidentiality: Kode pembatasan permission file export TIDAK ditemukan.")

    # 3. Cek Availability (Error Handling)
    if "except PermissionError:" in content and "return {'error': 'Permission Denied'}" in content:
        print("✅ Availability: Penanganan PermissionError ditemukan.")
    else:
        print("❌ Availability: Penanganan PermissionError TIDAK ditemukan.")

if __name__ == "__main__":
    verify_cia()
