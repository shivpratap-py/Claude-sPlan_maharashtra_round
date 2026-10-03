import os
from typing import Dict, Any
import PyPDF2
from analyzers.text_analyzer import TextAnalyzer

class DocumentAnalyzer:
    def __init__(self):
        self.text_analyzer = TextAnalyzer()

    def analyze(self, file_path: str) -> dict:
        result = {
            'modality': 'document',
            'status': 'success',
            'classification': 'unavailable',
            'fake_probability': 0.0,
            'confidence': 0.0,
            'evidence': [],
            'metadata': {},
            'error': None,
            'document_type': None,
            'page_count': 0,
            'document_metadata': {},
            'text_analysis': {},
            'extracted_text': ""
        }
        
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Document not found: {file_path}")
                
            ext = file_path.lower().split('.')[-1]
            if ext not in ['pdf', 'txt']:
                raise ValueError(f"Unsupported document type: {ext}")
                
            result['document_type'] = ext
            extracted_text = ""
            
            if ext == 'pdf':
                try:
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        result['page_count'] = len(reader.pages)
                        info = reader.metadata
                        if info:
                            result['document_metadata'] = {
                                'creator': info.get('/Creator', ''),
                                'producer': info.get('/Producer', ''),
                                'creation_date': info.get('/CreationDate', '')
                            }
                            
                        for page in reader.pages:
                            text = page.extract_text()
                            if text:
                                extracted_text += text + "\n"
                                
                    if not extracted_text.strip():
                        result['evidence'].append("OCR not performed, text extraction failed (possibly a scanned document).")
                except Exception as e:
                    result['evidence'].append(f"Error reading PDF: {str(e)}")
                    
            elif ext == 'txt':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    extracted_text = f.read()
                    
            result['extracted_text'] = extracted_text.strip()
            
            # Text Analysis
            if result['extracted_text']:
                text_res = self.text_analyzer.analyze(result['extracted_text'], source=f"document_{ext}")
                result['text_analysis'] = text_res
                if 'evidence' in text_res and text_res['evidence']:
                    result['evidence'].extend(text_res['evidence'])
            
            # Metadata evidence
            if result['document_metadata'].get('producer'):
                result['evidence'].append(f"Document produced by: {result['document_metadata']['producer']}")
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            
        return result
