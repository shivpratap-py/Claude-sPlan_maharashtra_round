"""Video analyzer: extracts frames and audio, delegates to image and audio analyzers."""

import os
import tempfile
import cv2
from typing import Callable, Optional
from utils.media_utils import get_video_info, sample_video_frames, extract_audio_from_video
from analyzers.image_analyzer import ImageAnalyzer
from analyzers.audio_analyzer import AudioAnalyzer


class VideoAnalyzer:
    def __init__(self):
        self.image_analyzer = ImageAnalyzer()
        self.audio_analyzer = AudioAnalyzer()

    def analyze(self, video_path: str, progress_callback: Optional[Callable] = None) -> dict:
        result = {
            'modality': 'video',
            'status': 'success',
            'classification': 'unavailable',
            'fake_probability': 0.0,
            'confidence': 0.0,
            'evidence': [],
            'metadata': {},
            'error': None,
            'video_info': {},
            'frame_analysis': {
                'total_frames_analyzed': 0,
                'suspicious_frames': 0,
                'mean_fake_probability': 0.0,
                'frame_results': []
            },
            'audio_analysis': None,
            'visual_classification': 'unavailable',
            'audio_classification': 'unavailable'
        }

        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video not found: {video_path}")

            video_info = get_video_info(video_path)
            result['video_info'] = video_info
            result['evidence'].append(
                f"Video: {video_info.get('duration', 0):.1f}s, "
                f"{video_info.get('fps', 0):.0f} fps, "
                f"{video_info.get('width', 0)}x{video_info.get('height', 0)}"
            )

            with tempfile.TemporaryDirectory(prefix="tl_video_") as temp_dir:
                # Extract frames as numpy arrays from media_utils
                frame_tuples = sample_video_frames(video_path, interval_seconds=1.5)

                if not frame_tuples:
                    raise ValueError("Could not extract any frames from video.")

                total_frames = len(frame_tuples)
                result['frame_analysis']['total_frames_analyzed'] = total_frames

                total_fake_prob = 0.0
                suspicious_count = 0

                for idx, (frame_num, frame_array) in enumerate(frame_tuples):
                    # Save frame to temp file for image analyzer
                    frame_path = os.path.join(temp_dir, f"frame_{frame_num:06d}.jpg")
                    cv2.imwrite(frame_path, frame_array)

                    frame_res = self.image_analyzer.analyze(frame_path)

                    if frame_res.get('status') == 'success':
                        prob = frame_res.get('fake_probability', 0.0)
                        total_fake_prob += prob

                        if frame_res.get('classification') == 'suspicious':
                            suspicious_count += 1

                        result['frame_analysis']['frame_results'].append({
                            'frame_index': idx,
                            'frame_number': frame_num,
                            'fake_probability': prob,
                            'classification': frame_res.get('classification', 'unavailable')
                        })

                    if progress_callback:
                        progress_callback(idx + 1, total_frames)

                mean_fake_prob = total_fake_prob / total_frames if total_frames > 0 else 0.0
                result['frame_analysis']['mean_fake_probability'] = mean_fake_prob
                result['frame_analysis']['suspicious_frames'] = suspicious_count

                suspicious_ratio = suspicious_count / total_frames if total_frames > 0 else 0
                if mean_fake_prob > 0.5 or suspicious_ratio > 0.3:
                    result['visual_classification'] = 'suspicious'
                else:
                    result['visual_classification'] = 'likely_authentic'

                result['evidence'].append(
                    f"Visual analysis: {suspicious_count}/{total_frames} frames suspicious "
                    f"(mean fake prob: {mean_fake_prob:.2f})."
                )

                # Audio extraction and analysis
                audio_path = extract_audio_from_video(video_path, temp_dir)
                if audio_path and os.path.exists(audio_path):
                    audio_res = self.audio_analyzer.analyze(audio_path)
                    result['audio_analysis'] = audio_res
                    result['audio_classification'] = audio_res.get('classification', 'unavailable')
                    result['evidence'].append(
                        f"Audio analysis: {result['audio_classification']} "
                        f"(fake prob: {audio_res.get('fake_probability', 0.0):.2f})."
                    )
                else:
                    result['evidence'].append("No audio track extracted or available.")

            # Aggregate classification
            vis_suspicious = result['visual_classification'] == 'suspicious'
            aud_suspicious = result['audio_classification'] == 'suspicious'

            if vis_suspicious and aud_suspicious:
                result['classification'] = 'suspicious'
                result['evidence'].append("Both visual and audio modalities show suspicious indicators.")
            elif vis_suspicious or aud_suspicious:
                result['classification'] = 'suspicious'
                result['evidence'].append(
                    "Disagreement: only one modality (visual or audio) is suspicious."
                )
            else:
                result['classification'] = 'likely_authentic'

            # Compute overall probability and confidence
            audio_prob = (result['audio_analysis'] or {}).get('fake_probability', 0.0)
            if result['audio_analysis']:
                result['fake_probability'] = (mean_fake_prob + audio_prob) / 2
                result['confidence'] = 0.8
            else:
                result['fake_probability'] = mean_fake_prob
                result['confidence'] = 0.7

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            result['evidence'].append(f"Video analysis error: {e}")

        return result
