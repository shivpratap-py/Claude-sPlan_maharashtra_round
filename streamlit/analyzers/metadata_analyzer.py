import os
from typing import Dict, Any
from utils.file_utils import get_file_stats
import exifread
from PIL import Image

class MetadataAnalyzer:
    def analyze(self, file_path: str, file_type: str) -> dict:
        result = {
            'modality': 'metadata',
            'status': 'success',
            'classification': 'metadata_only',
            'fake_probability': 0.0,
            'confidence': 0.5,
            'evidence': [],
            'metadata': {},
            'error': None,
            'file_metadata': {},
            'dates_found': [],
            'software_detected': [],
            'has_exif': False,
            'has_gps': False
        }
        
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            stats = get_file_stats(file_path)
            result['file_metadata'].update(stats)
            
            if stats.get('created'):
                result['dates_found'].append(stats['created'])
            if stats.get('modified'):
                result['dates_found'].append(stats['modified'])
                
            # Extractor based on type
            if file_type == 'image':
                try:
                    with Image.open(file_path) as img:
                        result['file_metadata']['dimensions'] = f"{img.width}x{img.height}"
                        result['file_metadata']['format'] = img.format
                        
                    with open(file_path, 'rb') as f:
                        tags = exifread.process_file(f, details=False)
                        if tags:
                            result['has_exif'] = True
                            
                        exif_dict = {}
                        for tag, val in tags.items():
                            if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
                                exif_dict[tag] = str(val)
                                
                                if 'Date' in tag:
                                    result['dates_found'].append(str(val))
                                if 'Software' in tag:
                                    result['software_detected'].append(str(val))
                                if 'GPS' in tag:
                                    result['has_gps'] = True
                                    
                        result['file_metadata']['exif'] = exif_dict
                except Exception as e:
                    result['evidence'].append(f"Image metadata extraction failed: {str(e)}")
                    
            elif file_type == 'audio':
                # Simplified mock for audio as librosa/pydub requires loading
                # actual implementation would use media_utils
                pass
            elif file_type == 'video':
                # Simplified mock for video, would use media_utils
                pass
            elif file_type == 'document':
                # Simplified mock for PyPDF2
                if file_path.lower().endswith('.pdf'):
                    try:
                        import PyPDF2
                        with open(file_path, 'rb') as f:
                            reader = PyPDF2.PdfReader(f)
                            result['file_metadata']['page_count'] = len(reader.pages)
                            info = reader.metadata
                            if info:
                                result['file_metadata']['creator'] = info.get('/Creator', '')
                                result['file_metadata']['producer'] = info.get('/Producer', '')
                                if info.get('/CreationDate'):
                                    result['dates_found'].append(info.get('/CreationDate'))
                                if info.get('/Producer'):
                                    result['software_detected'].append(info.get('/Producer'))
                    except Exception as e:
                        result['evidence'].append(f"PDF metadata extraction failed: {str(e)}")
            
            # Summarize Evidence
            if result['has_exif']:
                result['evidence'].append("EXIF metadata is present.")
            else:
                result['evidence'].append("No EXIF metadata found.")
                
            if result['software_detected']:
                result['evidence'].append(f"Software detected in metadata: {', '.join(result['software_detected'])}")
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            
        return result
