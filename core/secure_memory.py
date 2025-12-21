import ctypes
import sys
import os
import platform
import subprocess
from typing import Optional

if platform.system() == 'Linux':
    LIBC = ctypes.CDLL('libc.so.6')
    M_LOCKALL = 1
    M_UNLOCKALL = 2


class SecureString:
    
    def __init__(self, value: str):
        self._value = value
        self._length = len(value)
        self._cleared = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()
    
    def __del__(self):
        self.clear()
    
    def value(self) -> str:
        if self._cleared:
            raise ValueError("Memory has been cleared")
        return self._value
    
    def clear(self):
        if not self._cleared and hasattr(self, '_value'):
            try:
                self._value = '0' * self._length
                self._value = None
            except:
                pass
            self._cleared = True
    
    def __len__(self):
        return self._length


class SecureBuffer:
    
    def __init__(self, data: bytes):
        self._buffer = bytearray(data)
        self._length = len(data)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()
        
    def __bytes__(self):
        return bytes(self._buffer)
        
    def clear(self):
        for i in range(self._length):
            self._buffer[i] = 0


def secure_delete_file(path: str, passes: int = 1) -> bool:
    if not os.path.exists(path):
        return False
        
    try:
        file_size = os.path.getsize(path)
        
        with open(path, 'wb') as f:
            f.write(b'\x00' * file_size)
            f.flush()
            os.fsync(f.fileno())
            
            if passes > 1:
                f.seek(0)
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())
        
        os.remove(path)
        return True
    except Exception as e:
        print(f"Secure delete failed: {e}")
        return False
