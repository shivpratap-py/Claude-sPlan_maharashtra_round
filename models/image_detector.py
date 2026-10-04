import logging
from PIL import Image
from typing import Dict, Any
from .model_manager import get_image_classifier

logger = logging.getLogger(__name__)

class ImageDetector:
    def __init__(self):
        self.pipeline = get_image_classifier()
        self.model_name = 'umm-maybe/AI-image-detector'

    def analyze(self, image_path: str) -> dict:
        """Alias for detect."""
        return self.detect(image_path)

    def detect(self, image_path: str) -> dict:
        """Run deepfake/AI detection on image."""
        result = {
            'fake_probability': 0.0,
            'classification': 'unavailable',
            'confidence': 0.0,
            'raw_scores': {},
            'model_name': self.model_name,
            'available': False
        }

        if not self.pipeline:
            logger.warning("Image classifier unavailable.")
            return result
        
        try:
            image = Image.open(image_path).convert('RGB')
            outputs = self.pipeline(image)
            
            raw_scores = {out['label']: out['score'] for out in outputs}
            fake_prob = raw_scores.get('artificial', raw_scores.get('fake', 0.0))
            
            classification = 'suspicious' if fake_prob > 0.5 else 'likely_authentic'
            confidence = abs(fake_prob - 0.5) * 2.0
            
            result.update({
                'fake_probability': float(fake_prob),
                'classification': classification,
                'confidence': float(confidence),
                'raw_scores': raw_scores,
                'available': True
            })
            
        except Exception as e:
            logger.error(f"Error during image detection: {e}")
            
        return result
