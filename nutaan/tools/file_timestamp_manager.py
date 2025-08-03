"""
Shared timestamp manager for file operations across tools.
"""

import os
from typing import Dict


class FileTimestampManager:
    """Singleton class to manage file read timestamps across all tools."""
    
    _instance = None
    _timestamps: Dict[str, float] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FileTimestampManager, cls).__new__(cls)
        return cls._instance
    
    def mark_file_as_read(self, file_path: str) -> bool:
        """Mark a file as read with current timestamp."""
        try:
            full_path = os.path.abspath(file_path)
            if os.path.exists(full_path):
                stat = os.stat(full_path)
                self._timestamps[full_path] = stat.st_mtime * 1000
                return True
            return False
        except OSError:
            return False
    
    def get_read_timestamp(self, file_path: str) -> float:
        """Get the read timestamp for a file."""
        full_path = os.path.abspath(file_path)
        return self._timestamps.get(full_path, 0)
    
    def is_file_stale(self, file_path: str) -> bool:
        """Check if file has been modified since last read."""
        try:
            full_path = os.path.abspath(file_path)
            read_timestamp = self.get_read_timestamp(file_path)
            if read_timestamp == 0:
                return True  # Never read
            
            stat = os.stat(full_path)
            file_timestamp = stat.st_mtime * 1000
            return file_timestamp > read_timestamp
        except OSError:
            return True
    
    def is_file_ready_for_edit(self, file_path: str) -> bool:
        """Check if file has been read and is ready for editing."""
        read_timestamp = self.get_read_timestamp(file_path)
        return read_timestamp > 0 and not self.is_file_stale(file_path)
    
    def clear_timestamp(self, file_path: str):
        """Clear the read timestamp for a file."""
        full_path = os.path.abspath(file_path)
        self._timestamps.pop(full_path, None)
    
    def clear_all_timestamps(self):
        """Clear all timestamps."""
        self._timestamps.clear()
