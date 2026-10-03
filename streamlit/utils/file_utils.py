import os
import shutil
import tempfile
import time
from typing import Any

SUPPORTED_EXTENSIONS = {
    'image': ['jpg', 'jpeg', 'png', 'webp'],
    'audio': ['mp3', 'wav', 'm4a'],
    'video': ['mp4', 'mov'],
    'document': ['pdf'],
    'text': ['txt']
}

def get_file_type(file_path: str) -> str:
    """Detect file type from extension, return category."""
    ext = file_path.split('.')[-1].lower() if '.' in file_path else ''
    for category, exts in SUPPORTED_EXTENSIONS.items():
        if ext in exts:
            return category
    return 'unknown'

def save_uploaded_file(uploaded_file: Any, temp_dir: str) -> str:
    """Save a Streamlit UploadedFile to temp dir, return path."""
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def create_temp_dir() -> str:
    """Create and return a temp directory path."""
    return tempfile.mkdtemp(prefix="trustlayer_")

def cleanup_temp_dir(temp_dir: str) -> None:
    """Safely remove temp directory."""
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error removing temp directory {temp_dir}: {e}")

def get_file_stats(file_path: str) -> dict:
    """Return file size, creation time, modification time."""
    stats = os.stat(file_path)
    return {
        'size_bytes': stats.st_size,
        'creation_time': time.ctime(stats.st_ctime),
        'modification_time': time.ctime(stats.st_mtime)
    }

def format_file_size(size_bytes: int) -> str:
    """Human readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
