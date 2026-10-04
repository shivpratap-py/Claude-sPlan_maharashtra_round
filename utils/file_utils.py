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
    ext = file_path.rsplit('.', 1)[-1].lower() if '.' in file_path else ''
    for category, exts in SUPPORTED_EXTENSIONS.items():
        if ext in exts:
            return category
    return 'unknown'

def save_uploaded_file(uploaded_file: Any, temp_dir: str) -> str:
    """Save a Streamlit UploadedFile to temp dir, return path."""
    # Sanitize filename to avoid path traversal
    safe_name = os.path.basename(uploaded_file.name) or "uploaded_file"
    file_path = os.path.join(temp_dir, safe_name)
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def create_temp_dir() -> str:
    """Create and return a temp directory path."""
    return tempfile.mkdtemp(prefix="trustlayer_")

def cleanup_temp_dir(temp_dir: str) -> None:
    """Safely remove temp directory."""
    if temp_dir and os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error removing temp directory {temp_dir}: {e}")

def get_file_stats(file_path: str) -> dict:
    """Return file size, creation time, modification time.

    Includes both descriptive keys and the short aliases
    (``size``, ``created``, ``modified``) used by analyzers.
    """
    stats = os.stat(file_path)
    created = time.ctime(stats.st_ctime)
    modified = time.ctime(stats.st_mtime)
    return {
        'size_bytes': stats.st_size,
        'size_human': format_file_size(stats.st_size),
        'creation_time': created,
        'modification_time': modified,
        # Aliases kept for backward compatibility with analyzers
        'size': stats.st_size,
        'created': created,
        'modified': modified,
    }

def format_file_size(size_bytes: float) -> str:
    """Human readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
