from typing import Dict, Any

class EvidenceFusion:
    # Configurable weights - ALL IN ONE PLACE
    WEIGHTS = {
        'image_detector': 0.20,
        'audio_detector': 0.15,
        'video_frames': 0.20,
        'metadata_evidence': 0.05,
        'temporal_consistency': 0.12,
        'location_consistency': 0.10,
        'semantic_consistency': 0.08,
        'entity_consistency': 0.05,
        'cross_modal_agreement': 0.05,
    }
    
    def fuse_evidence(self, evidence_results: dict, consistency_results: dict) -> dict:
        score_breakdown = {}
        suspicion_score = 0.0
        available_sources = 0
        total_sources = len(self.WEIGHTS)
        
        # Calculate individual evidence scores
        if evidence_results.get('image', {}).get('status') == 'success':
            available_sources += 1
            prob = evidence_results['image'].get('fake_probability', 0.0) * 100
            w = self.WEIGHTS['image_detector']
            suspicion_score += prob * w
            score_breakdown['image_detector'] = f"Contributed {prob * w:.2f} based on fake_probability {prob:.2f}%"
            
        if evidence_results.get('audio', {}).get('status') == 'success':
            available_sources += 1
            prob = evidence_results['audio'].get('fake_probability', 0.0) * 100
            w = self.WEIGHTS['audio_detector']
            suspicion_score += prob * w
            score_breakdown['audio_detector'] = f"Contributed {prob * w:.2f} based on fake_probability {prob:.2f}%"
            
        if evidence_results.get('video', {}).get('status') == 'success':
            available_sources += 1
            prob = evidence_results['video'].get('fake_probability', 0.0) * 100
            w = self.WEIGHTS['video_frames']
            suspicion_score += prob * w
            score_breakdown['video_frames'] = f"Contributed {prob * w:.2f} based on fake_probability {prob:.2f}%"
            
        if evidence_results.get('metadata', {}).get('status') == 'success':
            available_sources += 1
            prob = evidence_results['metadata'].get('fake_probability', 0.0) * 100
            w = self.WEIGHTS['metadata_evidence']
            suspicion_score += prob * w
            score_breakdown['metadata_evidence'] = f"Contributed {prob * w:.2f} based on fake_probability {prob:.2f}%"
            
        # Consistency results
        for check, weight_key in [('temporal', 'temporal_consistency'), 
                                  ('location', 'location_consistency'), 
                                  ('entity', 'entity_consistency'), 
                                  ('semantic', 'semantic_consistency')]:
            res = consistency_results.get(check)
            if res:
                available_sources += 1
                # score is 0-1 where 1 is consistent. So 1 - score is suspicion.
                susp = (1.0 - res.get('score', 1.0)) * 100
                w = self.WEIGHTS[weight_key]
                suspicion_score += susp * w
                score_breakdown[weight_key] = f"Contributed {susp * w:.2f} (suspicion {susp:.2f}%)"
                
        # Cross-modal agreement
        det_agreement = consistency_results.get('detector_agreement', {})
        if det_agreement:
            available_sources += 1
            susp = (1.0 - det_agreement.get('score', 1.0)) * 100
            w = self.WEIGHTS['cross_modal_agreement']
            suspicion_score += susp * w
            score_breakdown['cross_modal_agreement'] = f"Contributed {susp * w:.2f} (suspicion {susp:.2f}%)"
            
        # Cross-modal contradiction bonuses
        inconsistencies = consistency_results.get('total_inconsistencies', 0)
        if inconsistencies > 0:
            bonus = min(inconsistencies * 5.0, 20.0)
            suspicion_score += bonus
            score_breakdown['contradiction_bonus'] = f"Added {bonus:.2f} due to {inconsistencies} contradictions"
            
        # normalize to 0-100 based on available sources
        # this is naive, but works for the prompt logic
        suspicion_score = min(suspicion_score, 100.0)
        evidence_completeness = (available_sources / total_sources) * 100 if total_sources > 0 else 0
        
        # Thresholds
        if evidence_completeness < 30:
            assessment = "INSUFFICIENT EVIDENCE"
        elif suspicion_score < 25:
            assessment = "AUTHENTIC"
        elif suspicion_score < 50:
            assessment = "AUTHENTIC_WITH_CONCERNS"
        elif suspicion_score < 70:
            assessment = "MANIPULATED"
        else:
            assessment = "COORDINATED SYNTHETIC"
            
        # Confidence
        confidence = min(evidence_completeness + (100 - abs(50 - suspicion_score)), 100)
        if confidence > 70:
            conf_level = "HIGH"
        elif confidence > 40:
            conf_level = "MEDIUM"
        else:
            conf_level = "LOW"
            
        return {
            'assessment': assessment,
            'confidence': float(confidence),
            'confidence_level': conf_level,
            'suspicion_score': float(suspicion_score),
            'evidence_completeness': float(evidence_completeness),
            'score_breakdown': score_breakdown,
            'weights_used': self.WEIGHTS,
        }
