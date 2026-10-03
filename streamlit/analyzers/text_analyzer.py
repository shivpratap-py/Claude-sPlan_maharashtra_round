import re
from typing import Dict, Any
from models.model_manager import get_spacy_model

class TextAnalyzer:
    def __init__(self):
        self.nlp = get_spacy_model()

    def analyze(self, text: str, source: str = 'text_file') -> dict:
        result = {
            'modality': 'text',
            'status': 'success',
            'classification': 'text_only',
            'fake_probability': 0.0,
            'confidence': 1.0,
            'evidence': [],
            'metadata': {},
            'error': None,
            'extracted_text': text,
            'entities': {
                'persons': [],
                'organizations': [],
                'locations': [],
                'dates': [],
                'other': []
            },
            'key_claims': [],
            'word_count': 0,
            'source': source
        }
        
        try:
            if not text:
                return result
                
            result['word_count'] = len(text.split())
            
            # Common Date Regex Extraction
            date_patterns = [
                r'\b\d{4}-\d{2}-\d{2}\b',
                r'\b\d{2}/\d{2}/\d{4}\b',
                r'\b\d{2}-\d{2}-\d{4}\b'
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if match not in result['entities']['dates']:
                        result['entities']['dates'].append(match)
            
            # Spacy NER
            if self.nlp:
                doc = self.nlp(text)
                
                for ent in doc.ents:
                    if ent.label_ == 'PERSON':
                        result['entities']['persons'].append(ent.text)
                    elif ent.label_ == 'ORG':
                        result['entities']['organizations'].append(ent.text)
                    elif ent.label_ in ['GPE', 'LOC']:
                        result['entities']['locations'].append(ent.text)
                    elif ent.label_ == 'DATE':
                        result['entities']['dates'].append(ent.text)
                    else:
                        result['entities']['other'].append(ent.text)
                
                # Deduplicate
                for key in result['entities']:
                    result['entities'][key] = list(set(result['entities'][key]))
                
                # Key claims (sentences with entities or first 5 sentences)
                sentences = list(doc.sents)
                claims = []
                for idx, sent in enumerate(sentences):
                    if len(sent.ents) > 0 or idx < 5:
                        claims.append(sent.text.strip())
                result['key_claims'] = list(set(claims))[:10]
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            
        return result
