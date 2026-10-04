"""Evidence fusion: combines per-modality detector outputs and cross-modal
consistency scores into a single suspicion score and assessment."""

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

    # Modality keys that count toward evidence completeness
    MODALITY_KEYS = ['image', 'audio', 'video', 'metadata']

    # Decision thresholds (suspicion score 0-100)
    T_AUTHENTIC = 15.0
    T_CONCERNS = 40.0
    T_MANIPULATED = 70.0

    def fuse_evidence(self, evidence_results: Dict[str, Any],
                      consistency_results: Dict[str, Any]) -> dict:
        score_breakdown: Dict[str, dict] = {}
        suspicion_weighted = 0.0   # weighted suspicion in 0-1 space
        available_weight = 0.0

        modality_hits = 0
        strong_detector_count = 0  # detectors with fake_probability >= 0.7

        detector_map = [
            ('image', 'image_detector'),
            ('audio', 'audio_detector'),
            ('video', 'video_frames'),
            ('metadata', 'metadata_evidence'),
        ]

        for mod, weight_key in detector_map:
            res = evidence_results.get(mod)
            if isinstance(res, dict) and res.get('status') == 'success':
                modality_hits += 1
                prob = float(res.get('fake_probability', 0.0))
                if prob >= 0.7:
                    strong_detector_count += 1
                w = self.WEIGHTS[weight_key]
                suspicion_weighted += prob * w
                available_weight += w
                score_breakdown[weight_key] = {
                    'weighted_score': round(prob * w * 100, 2),
                    'explanation': f'{mod.title()} detector fake probability {prob:.0%} '
                                   f'(weight {w:.0%})',
                }

        # Consistency checks (1 - score = suspicion)
        consistency_map = [
            ('temporal', 'temporal_consistency'),
            ('location', 'location_consistency'),
            ('entity', 'entity_consistency'),
            ('semantic', 'semantic_consistency'),
        ]
        for check, weight_key in consistency_map:
            res = consistency_results.get(check)
            if res:
                susp = 1.0 - float(res.get('score', 1.0))
                w = self.WEIGHTS[weight_key]
                suspicion_weighted += susp * w
                available_weight += w
                score_breakdown[weight_key] = {
                    'weighted_score': round(susp * w * 100, 2),
                    'explanation': f'{check.title()} consistency suspicion {susp:.0%} '
                                   f'(weight {w:.0%})',
                }

        # Cross-modal detector agreement
        det_agreement = consistency_results.get('detector_agreement', {})
        if det_agreement:
            susp = 1.0 - float(det_agreement.get('score', 1.0))
            w = self.WEIGHTS['cross_modal_agreement']
            suspicion_weighted += susp * w
            available_weight += w
            score_breakdown['cross_modal_agreement'] = {
                'weighted_score': round(susp * w * 100, 2),
                'explanation': f"Detector agreement: {det_agreement.get('agreement', 'n/a')}",
            }

        # Normalize to 0-100 by the weight actually available
        if available_weight > 0:
            suspicion_score = (suspicion_weighted / available_weight) * 100.0
        else:
            suspicion_score = 0.0

        # Cross-modal contradiction bonus
        inconsistencies = consistency_results.get('total_inconsistencies', 0)
        if inconsistencies > 0:
            bonus = min(inconsistencies * 5.0, 20.0)
            suspicion_score += bonus
            score_breakdown['contradiction_bonus'] = {
                'weighted_score': round(bonus, 2),
                'explanation': f'{inconsistencies} cross-modal contradiction(s) detected',
            }

        # ── Decision rules ────────────────────────────────────────────────
        # A single very strong detector signal means the content itself is
        # manipulated even if other evidence agrees with the claim.
        max_detector_prob = max(
            (float(evidence_results.get(m, {}).get('fake_probability', 0.0))
             for m in self.MODALITY_KEYS
             if isinstance(evidence_results.get(m), dict)
             and evidence_results[m].get('status') == 'success'),
            default=0.0,
        )
        if max_detector_prob >= 0.75:
            suspicion_score = max(suspicion_score, 50.0)
            score_breakdown['strong_signal_rule'] = {
                'weighted_score': 50.0,
                'explanation': 'Strong manipulation signal (>=75%) in at least one modality',
            }

        # A hard cross-modal contradiction (dates/locations/entities that do
        # not line up) is itself evidence of contextual manipulation.
        if inconsistencies >= 1:
            suspicion_score = max(suspicion_score, 50.0)

        # Multiple strong detectors + contradiction = coordinated campaign.
        if strong_detector_count >= 2 and inconsistencies >= 1:
            suspicion_score = max(suspicion_score, 70.0)
            score_breakdown['coordinated_rule'] = {
                'weighted_score': 70.0,
                'explanation': 'Multiple strong detector signals plus cross-modal '
                               'contradiction indicate coordinated manipulation',
            }

        suspicion_score = min(max(suspicion_score, 0.0), 100.0)

        # Evidence completeness is based on how many real modalities succeeded
        evidence_completeness = (modality_hits / len(self.MODALITY_KEYS)) * 100.0

        if evidence_completeness < 30:
            assessment = 'INSUFFICIENT EVIDENCE'
        elif suspicion_score < self.T_AUTHENTIC:
            assessment = 'AUTHENTIC'
        elif suspicion_score < self.T_CONCERNS:
            assessment = 'AUTHENTIC_WITH_CONCERNS'
        elif suspicion_score < self.T_MANIPULATED:
            assessment = 'MANIPULATED'
        else:
            assessment = 'COORDINATED SYNTHETIC'

        confidence = min(evidence_completeness + (100 - abs(50 - suspicion_score)), 100.0)
        if confidence > 70:
            conf_level = 'HIGH'
        elif confidence > 40:
            conf_level = 'MEDIUM'
        else:
            conf_level = 'LOW'

        return {
            'assessment': assessment,
            'confidence': float(confidence),
            'confidence_level': conf_level,
            'suspicion_score': float(suspicion_score),
            'evidence_completeness': float(evidence_completeness),
            'score_breakdown': score_breakdown,
            'weights_used': self.WEIGHTS,
        }
