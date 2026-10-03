import os
import subprocess
from typing import List, Tuple
import cv2
import numpy as np

MAX_FRAMES = 30

def extract_audio_from_video(video_path: str, output_dir: str) -> str:
    """Use ffmpeg to extract audio as WAV. Returns '' on failure."""
    os.makedirs(output_dir, exist_ok=True)
    basename = os.path.splitext(os.path.basename(video_path))[0]
    output_path = os.path.join(output_dir, f"{basename}.wav")
    try:
        subprocess.run(
            ['ffmpeg', '-y', '-i', video_path, '-vn', '-acodec', 'pcm_s16le',
             '-ar', '44100', '-ac', '2', output_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return output_path if os.path.exists(output_path) else ""
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"ffmpeg extraction failed: {e}")
        return ""

def sample_video_frames(video_path: str, interval_seconds: float = 1.5) -> List[Tuple[int, np.ndarray]]:
    """Sample up to MAX_FRAMES frames spread across the video.

    Uses timestamp seeking (CAP_PROP_POS_MSEC) instead of decoding every
    frame, which is dramatically faster for long videos.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = frame_count / fps if frame_count > 0 else 0.0

    frames: List[Tuple[int, np.ndarray]] = []

    if duration > 0:
        # Spread samples evenly across the whole video
        n_samples = min(MAX_FRAMES, max(1, int(duration / max(interval_seconds, 0.1))))
        step_ms = (duration * 1000.0) / (n_samples + 1)
        for i in range(1, n_samples + 1):
            ms = i * step_ms
            cap.set(cv2.CAP_PROP_POS_MSEC, ms)
            ret, frame = cap.read()
            if ret and frame is not None:
                frames.append((int(round(ms * fps / 1000.0)), frame))
    else:
        # Fallback: sequential read with skipping
        frame_interval = max(1, int(fps * interval_seconds))
        frame_idx = 0
        while len(frames) < MAX_FRAMES:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % frame_interval == 0:
                frames.append((frame_idx, frame))
            frame_idx += 1

    cap.release()
    return frames

def get_video_info(video_path: str) -> dict:
    """Return video metadata."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {}

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])

    duration = frame_count / fps if fps and fps > 0 else 0
    cap.release()

    return {
        'duration': duration,
        'fps': fps,
        'frame_count': int(frame_count),
        'width': int(width),
        'height': int(height),
        'codec': codec
    }

def convert_audio_format(input_path: str, output_path: str) -> str:
    """Convert audio to WAV using pydub."""
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format="wav")
        return output_path
    except Exception as e:
        print(f"Failed to convert audio using pydub: {e}")
        return ""

def get_audio_info(audio_path: str) -> dict:
    """Return audio metadata using librosa."""
    try:
        import librosa
        y, sr = librosa.load(audio_path, sr=None, mono=False)
        duration = librosa.get_duration(y=y, sr=sr)
        channels = 1 if y.ndim == 1 else y.shape[0]
        return {
            'duration': duration,
            'sample_rate': sr,
            'channels': channels
        }
    except Exception as e:
        print(f"Failed to get audio info: {e}")
        return {}
