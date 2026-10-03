import os
import subprocess
from typing import List, Tuple
import cv2
import numpy as np

def extract_audio_from_video(video_path: str, output_dir: str) -> str:
    """Use ffmpeg to extract audio as WAV."""
    os.makedirs(output_dir, exist_ok=True)
    basename = os.path.splitext(os.path.basename(video_path))[0]
    output_path = os.path.join(output_dir, f"{basename}.wav")
    try:
        subprocess.run(
            ['ffmpeg', '-y', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', output_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return output_path
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"ffmpeg extraction failed: {e}")
        return ""

def sample_video_frames(video_path: str, interval_seconds: float = 1.5) -> List[Tuple[int, np.ndarray]]:
    """Extract frames at interval using OpenCV, cap at 30 frames."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0
    
    frame_interval = int(fps * interval_seconds)
    frames = []
    frame_idx = 0
    
    while len(frames) < 30:
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
    
    duration = frame_count / fps if fps > 0 else 0
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
        y, sr = librosa.load(audio_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        # librosa standard load typically converts to mono unless mono=False
        # If mono is forced or y is 1D, channels is 1
        channels = 1 if y.ndim == 1 else y.shape[0]
        return {
            'duration': duration,
            'sample_rate': sr,
            'channels': channels
        }
    except Exception as e:
        print(f"Failed to get audio info: {e}")
        return {}
