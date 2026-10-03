import os
from typing import Dict, Any
from utils.media_utils import get_audio_info
from models.audio_detector import AudioDetector


class AudioAnalyzer:
    def __init__(self):
        self.detector = AudioDetector()
        # Whisper is loaded lazily — loading it here once caused it to be
        # downloaded/loaded twice when a VideoAnalyzer was also constructed.
        self._whisper = None

    def _get_whisper(self):
        if self._whisper is None:
            from models.model_manager import get_whisper_model
            self._whisper = get_whisper_model()
        return self._whisper

    def analyze(self, audio_path: str) -> dict:
        result = {
            'modality': 'audio',
            'status': 'success',
            'classification': 'unavailable',
            'fake_probability': 0.0,
            'confidence': 0.0,
            'evidence': [],
            'metadata': {},
            'error': None,
            'transcript': None,
            'language': None,
            'segments': [],
            'audio_info': {}
        }

        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio not found: {audio_path}")

            # Audio info
            audio_info = get_audio_info(audio_path)
            result['audio_info'] = audio_info

            if not audio_info:
                raise ValueError("Could not read audio info, file may be corrupt or unreadable.")

            result['evidence'].append(
                f"Audio properties: {audio_info.get('sample_rate', 'unknown')} Hz, "
                f"{audio_info.get('channels', 'unknown')} channels, "
                f"{audio_info.get('duration', 0):.1f}s."
            )

            # Spoof detection
            detector_result = self.detector.analyze(audio_path)
            result['fake_probability'] = detector_result.get('fake_probability', 0.0)
            result['confidence'] = detector_result.get('confidence', 0.0)
            result['classification'] = detector_result.get('classification', 'unavailable')

            det_evidence = detector_result.get('evidence')
            if det_evidence:
                if isinstance(det_evidence, list):
                    result['evidence'].extend(det_evidence)
                else:
                    result['evidence'].append(str(det_evidence))

            result['evidence'].append(
                f"Detector classified as {result['classification']} "
                f"with probability {result['fake_probability']:.2f}."
            )

            # Transcription (lazy model load)
            whisper = self._get_whisper()
            if whisper:
                try:
                    transcription = whisper.transcribe(audio_path)
                    result['transcript'] = transcription.get('text')
                    result['language'] = transcription.get('language')
                    result['segments'] = transcription.get('segments', [])
                    result['evidence'].append("Transcription successful.")
                except Exception as e:
                    result['evidence'].append(f"Transcription failed: {str(e)}")
            else:
                result['evidence'].append("Whisper model unavailable for transcription.")

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)

        return result
