import os
import re
import datetime
from typing import Dict, Any
from utils.file_utils import get_file_stats
import exifread
from PIL import Image

_EXIF_DATE_RE = re.compile(r'^(\d{4}):(\d{2}):(\d{2})')


def _parse_exif_date(value: str) -> str:
    """Convert EXIF 'YYYY:MM:DD HH:MM:SS' to ISO 'YYYY-MM-DD HH:MM:SS'.
    Returns the original string unchanged when it does not match."""
    m = _EXIF_DATE_RE.match(str(value).strip())
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" + str(value).strip()[10:]
    return str(value)


class MetadataAnalyzer:
    def analyze(self, file_path: str, file_type: str) -> dict:
        result = {
            'modality': 'metadata',
            'status': 'success',
            'classification': 'metadata_only',
            'fake_probability': 0.0,
            'confidence': 0.0,
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

            suspicion = 0.0

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
                        if tag in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename',
                                   'EXIF MakerNote'):
                            continue
                        exif_dict[tag] = str(val)

                        if 'Date' in tag:
                            result['dates_found'].append(_parse_exif_date(str(val)))
                        if 'Software' in tag:
                            result['software_detected'].append(str(val))
                        if 'GPS' in tag:
                            result['has_gps'] = True

                    result['file_metadata']['exif'] = exif_dict

                    if not tags:
                        suspicion += 0.2  # stripped metadata is a mild indicator
                except Exception as e:
                    result['evidence'].append(f"Image metadata extraction failed: {str(e)}")

            elif file_type == 'audio':
                try:
                    from utils.media_utils import get_audio_info
                    info = get_audio_info(file_path)
                    if info:
                        result['file_metadata'].update(info)
                except Exception as e:
                    result['evidence'].append(f"Audio metadata extraction failed: {str(e)}")

            elif file_type == 'video':
                try:
                    from utils.media_utils import get_video_info
                    info = get_video_info(file_path)
                    if info:
                        result['file_metadata'].update(info)
                except Exception as e:
                    result['evidence'].append(f"Video metadata extraction failed: {str(e)}")

            elif file_type == 'document':
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
                                    result['dates_found'].append(str(info.get('/CreationDate')))
                                if info.get('/Producer'):
                                    result['software_detected'].append(str(info.get('/Producer')))
                    except Exception as e:
                        result['evidence'].append(f"PDF metadata extraction failed: {str(e)}")

            # Suspicious editing software in metadata
            editing_tools = ('photoshop', 'gimp', 'midjourney', 'stable diffusion',
                             'dall-e', 'canva')
            flagged = [s for s in result['software_detected']
                       if any(t in s.lower() for t in editing_tools)]
            if flagged:
                suspicion += 0.4
                result['evidence'].append(
                    f"Editing/generation software flagged in metadata: {', '.join(flagged)}"
                )
            elif result['software_detected']:
                result['evidence'].append(
                    f"Software detected in metadata: {', '.join(result['software_detected'])}"
                )

            if result['has_exif']:
                result['evidence'].append("EXIF metadata is present.")
            elif file_type == 'image':
                result['evidence'].append(
                    "No EXIF metadata found (could indicate stripping/re-encoding)."
                )

            result['fake_probability'] = min(suspicion, 1.0)
            # Metadata alone is never conclusive — keep confidence moderate
            result['confidence'] = 0.6 if (result['has_exif'] or result['software_detected']) else 0.3

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)

        return result
