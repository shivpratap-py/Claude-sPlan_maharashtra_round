import librosa
import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AudioDetector:
    def __init__(self):
        self.model_name = 'spectral_heuristics'

    def analyze(self, audio_path: str) -> dict:
        """Alias for detect."""
        return self.detect(audio_path)

    def detect(self, audio_path: str) -> dict:
        """Analyze audio using librosa for spectral heuristics."""
        result = {
            'fake_probability': 0.0,
            'classification': 'unavailable',
            'confidence': 0.0,
            'evidence': ["Audio analysis uses spectral heuristics (no dedicated deepfake model)"],
            'model_name': self.model_name,
            'available': True
        }

        try:
            y, sr = librosa.load(audio_path, sr=None)
            
            # Compute heuristics
            spectral_flatness = librosa.feature.spectral_flatness(y=y)[0]
            flatness_std = np.std(spectral_flatness)
            
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            zcr_std = np.std(zcr)
            
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            centroid_var = np.var(spectral_centroid)
            
            dynamic_range = np.max(y) - np.min(y)
            
            # Simple weighted rules
            suspicion = 0.0
            if flatness_std < 0.01:
                suspicion += 0.2
            if dynamic_range < 0.1:
                suspicion += 0.2
            if zcr_std > 0.1:
                suspicion += 0.1
                
            fake_prob = min(suspicion, 1.0)
            
            classification = 'suspicious' if fake_prob > 0.5 else 'likely_authentic'
            
            result.update({
                'fake_probability': float(fake_prob),
                'classification': classification,
                'confidence': 0.4, # Explicitly low confidence for heuristic fallback
            })
            
        except Exception as e:
            logger.error(f"Error during audio detection: {e}")
            result['classification'] = 'error'
            result['evidence'].append(f"Error processing audio: {e}")
            
        return result
