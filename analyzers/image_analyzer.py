import os
from typing import Dict, Any
from PIL import Image
import exifread
from models.image_detector import ImageDetector
from utils.file_utils import get_file_stats

class ImageAnalyzer:
    def __init__(self):
        self.detector = ImageDetector()

    def analyze(self, image_path: str) -> dict:
        result = {
            'modality': 'image',
            'status': 'success',
            'classification': 'unavailable',
            'fake_probability': 0.0,
            'confidence': 0.0,
            'evidence': [],
            'metadata': {},
            'error': None
        }
        
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # File stats
            stats = get_file_stats(image_path)
            
            # Image Dimensions
            try:
                with Image.open(image_path) as img:
                    dimensions = f"{img.width}x{img.height}"
            except Exception as e:
                raise ValueError(f"Corrupt or unreadable image: {str(e)}")

            # EXIF Data
            exif_data = {}
            try:
                with open(image_path, 'rb') as f:
                    tags = exifread.process_file(f, details=False)
                    for tag in tags.keys():
                        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
                            exif_data[tag] = str(tags[tag])
            except Exception:
                pass
                
            camera_info = exif_data.get('Image Make', '') + ' ' + exif_data.get('Image Model', '')
            software_used = exif_data.get('Image Software', '')
            
            result['metadata'] = {
                'exif': exif_data,
                'dimensions': dimensions,
                'file_size': stats.get('size'),
                'creation_date': stats.get('created'),
                'modification_date': stats.get('modified'),
                'camera_info': camera_info.strip(),
                'software_used': software_used
            }
            
            # Evidence from EXIF
            if software_used:
                software_lower = software_used.lower()
                if 'photoshop' in software_lower or 'gimp' in software_lower:
                    result['evidence'].append(f"Suspicious software detected in metadata: {software_used}")
                else:
                    result['evidence'].append(f"Image software: {software_used}")
                    
            if not exif_data:
                result['evidence'].append("No EXIF metadata found (could indicate stripping/re-encoding).")
            else:
                result['evidence'].append("EXIF metadata present.")
            
            # Detector
            detector_result = self.detector.analyze(image_path)
            
            result['fake_probability'] = detector_result.get('fake_probability', 0.0)
            result['confidence'] = detector_result.get('confidence', 0.0)
            result['classification'] = detector_result.get('classification', 'unavailable')
            
            if 'evidence' in detector_result and detector_result['evidence']:
                if isinstance(detector_result['evidence'], list):
                    result['evidence'].extend(detector_result['evidence'])
                else:
                    result['evidence'].append(str(detector_result['evidence']))
            
            result['evidence'].append(f"Detector classified as {result['classification']} with probability {result['fake_probability']:.2f}.")

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            
        return result
