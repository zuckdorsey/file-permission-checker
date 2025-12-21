import os
import hashlib
from datetime import datetime
from typing import Dict, Any

def format_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def get_file_hash(filepath: str) -> str:
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except:
        return "ERROR"

def format_timestamp(timestamp: datetime) -> str:
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def safe_chmod(filepath: str, mode: int) -> bool:
    try:
        os.chmod(filepath, mode)
        return True
    except:
        return False

def validate_path(path: str) -> Dict[str, Any]:
    result = {
        'exists': False,
        'is_dir': False,
        'is_file': False,
        'readable': False,
        'writable': False,
        'size': 0
    }
    
    try:
        if os.path.exists(path):
            result['exists'] = True
            result['is_dir'] = os.path.isdir(path)
            result['is_file'] = os.path.isfile(path)
            result['readable'] = os.access(path, os.R_OK)
            result['writable'] = os.access(path, os.W_OK)
            
            if result['is_file']:
                result['size'] = os.path.getsize(path)
    
    except:
        pass
    
    return result

def calculate_directory_size(path: str) -> int:
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except:
        pass
    
    return total_size
