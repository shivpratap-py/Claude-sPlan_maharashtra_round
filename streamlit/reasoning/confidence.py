from typing import Dict, Any, List

class ConfidenceEstimator:
    def estimate(self, evidence_results: dict, consistency_results: dict, fusion_result: dict) -> dict:
        modalities = ['image', 'audio', 'video', 'text', 'metadata']
        success_count = sum(1 for m in modalities if evidence_results.get(m, {}).get('status') == 'success')
        evidence_completeness = (success_count / len(modalities)) * 100
        
        det_conf = []
        for m in modalities:
            res = evidence_results.get(m)
            if res and res.get('status') == 'success':
                det_conf.append(res.get('confidence', 0.5))
        detector_confidence = (sum(det_conf) / len(det_conf) * 100) if det_conf else 0.0
        
        # consistency confidence
        consistency_confidence = consistency_results.get('overall_consistency_score', 0.5) * 100
        
        overall_confidence = (evidence_completeness * 0.3) + (detector_confidence * 0.4) + (consistency_confidence * 0.3)
        overall_confidence = min(max(overall_confidence, 0.0), 100.0)
        
        if overall_confidence > 70:
            confidence_level = 'HIGH'
        elif overall_confidence >= 40:
            confidence_level = 'MEDIUM'
        else:
            confidence_level = 'LOW'
            
        missing_evidence = []
        recommendations = []
        for m in modalities:
            if evidence_results.get(m, {}).get('status') != 'success':
                missing_evidence.append(f"Missing {m} analysis")
                recommendations.append(f"Upload {m} data to enable cross-modal analysis.")
                
        return {
            'overall_confidence': float(overall_confidence),
            'confidence_level': confidence_level,
            'evidence_completeness': float(evidence_completeness),
            'detector_confidence': float(detector_confidence),
            'consistency_confidence': float(consistency_confidence),
            'missing_evidence': missing_evidence,
            'recommendations': recommendations
        }
