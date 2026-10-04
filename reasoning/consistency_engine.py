"""Cross-modal consistency engine — compares evidence across modalities."""

import datetime
import re
from typing import Dict, Any, List


class ConsistencyEngine:
    def __init__(self):
        try:
            from models.model_manager import get_sentence_transformer
            self.sentence_model = get_sentence_transformer()
        except Exception:
            self.sentence_model = None

    # Backward-compatible alias expected by the evaluation harness
    def analyze(self, claim: str, evidence_results: dict) -> dict:
        return self.analyze_consistency(claim, evidence_results)

    def analyze_consistency(self, claim: str, evidence_results: dict) -> dict:
        """Main entry point. evidence_results keys: image, audio, video, text, document, metadata, claim."""
        temporal_result = self.check_temporal_consistency(claim, evidence_results)
        location_result = self.check_location_consistency(claim, evidence_results)
        entity_result = self.check_entity_consistency(claim, evidence_results)
        semantic_result = self.check_semantic_consistency(claim, evidence_results)
        detector_result = self.check_detector_agreement(evidence_results)

        contradictions = []
        checks_performed = 0
        for result in [temporal_result, location_result, entity_result, semantic_result]:
            contradictions.extend(result.get('conflicts', []))
            checks_performed += 1

        scores = [
            temporal_result['score'],
            location_result['score'],
            entity_result['score'],
            semantic_result['score'],
        ]
        overall_score = sum(scores) / len(scores) if scores else 1.0

        return {
            'temporal': temporal_result,
            'location': location_result,
            'entity': entity_result,
            'semantic': semantic_result,
            'detector_agreement': detector_result,
            'overall_consistency_score': float(overall_score),
            'contradictions': contradictions,
            'total_checks_performed': checks_performed,
            'total_inconsistencies': len(contradictions),
        }

    # ── Date extraction helpers ──────────────────────────────────────────

    def _extract_dates_from_text(self, text: str) -> List[datetime.datetime]:
        """Extract dates in common formats from free text."""
        dates = []
        if not text:
            return dates
        # YYYY-MM-DD
        for y, m, d in re.findall(r'\b(20\d\d)-(0?\d|1[0-2])-(0?\d|[12]\d|3[01])\b', text):
            try:
                dates.append(datetime.datetime(int(y), int(m), int(d)))
            except ValueError:
                pass
        # DD/MM/YYYY or MM/DD/YYYY (ambiguous — try both)
        for p1, p2, y in re.findall(r'\b(\d{1,2})/(\d{1,2})/(20\d\d)\b', text):
            try:
                dates.append(datetime.datetime(int(y), int(p2), int(p1)))
            except ValueError:
                try:
                    dates.append(datetime.datetime(int(y), int(p1), int(p2)))
                except ValueError:
                    pass
        # Month name patterns: "September 20, 2026"
        month_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        for match in re.finditer(
            r'\b(' + '|'.join(month_map.keys()) + r')\s+(\d{1,2}),?\s+(20\d\d)\b',
            text.lower()
        ):
            try:
                month = month_map[match.group(1)]
                day = int(match.group(2))
                year = int(match.group(3))
                dates.append(datetime.datetime(year, month, day))
            except ValueError:
                pass
        # Bare 4-digit year (e.g. "in 2026") — used only when no fuller date matched
        if not dates:
            for y in re.findall(r'\b(20\d\d)\b', text):
                try:
                    dates.append(datetime.datetime(int(y), 7, 1))  # mid-year anchor
                except ValueError:
                    pass
        return dates

    def _extract_locations_from_text(self, text: str) -> List[str]:
        """Extract location-like words from text using simple heuristics."""
        locations = []
        if not text:
            return locations
        # Look for capitalized words that might be places (simple heuristic)
        # Also look for common location indicators
        location_patterns = [
            r'\bat\s+(?:the\s+)?([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
            r'\bin\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
            r'\bfrom\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
        ]
        for pattern in location_patterns:
            for match in re.finditer(pattern, text):
                loc = match.group(1).strip()
                # Filter out common non-location words
                skip_words = {'The', 'This', 'That', 'Which', 'What', 'How', 'When',
                             'Where', 'Person', 'Company', 'Mr', 'Mrs', 'Dr', 'CEO'}
                if loc.split()[0] not in skip_words and len(loc) > 2:
                    locations.append(loc.lower())
        return list(set(locations))

    def _extract_entities_from_text(self, text: str) -> List[str]:
        """Extract person/organization-like names from text."""
        entities = []
        if not text:
            return entities
        # Simple: find sequences of capitalized words
        for match in re.finditer(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', text):
            entities.append(match.group(1))
        return list(set(entities))

    # ── Consistency checks ───────────────────────────────────────────────

    def check_temporal_consistency(self, claim: str, evidence_results: dict) -> dict:
        dates_found = {}
        conflicts = []

        # Dates from claim
        claim_dates = self._extract_dates_from_text(claim)
        if claim_dates:
            dates_found['claim'] = claim_dates[0]

        # Dates from text analysis
        text_res = evidence_results.get('text') or evidence_results.get('claim')
        if text_res and isinstance(text_res, dict):
            entities = text_res.get('entities', {})
            if isinstance(entities, dict):
                text_dates_raw = entities.get('dates', [])
                for d in text_dates_raw:
                    parsed = self._extract_dates_from_text(str(d))
                    if parsed and 'text' not in dates_found:
                        dates_found['text'] = parsed[0]

        # Dates from audio transcript
        audio_res = evidence_results.get('audio')
        if audio_res and isinstance(audio_res, dict):
            transcript = audio_res.get('transcript', '')
            if transcript:
                transcript_dates = self._extract_dates_from_text(transcript)
                if transcript_dates:
                    dates_found['transcript'] = transcript_dates[0]

        # Dates from media metadata (image/audio/video keep a nested 'metadata' dict;
        # the dedicated metadata analyzer uses 'file_metadata' + 'dates_found').
        for mod in ['image', 'audio', 'video']:
            res = evidence_results.get(mod)
            if isinstance(res, dict):
                md = res.get('metadata', {})
                if isinstance(md, dict):
                    for key in ['creation_date', 'Creation Date', 'EXIF DateTimeOriginal']:
                        val = md.get(key)
                        if val:
                            parsed = self._extract_dates_from_text(str(val))
                            if parsed and 'metadata' not in dates_found:
                                dates_found['metadata'] = parsed[0]
                                break

        meta_res = evidence_results.get('metadata')
        if isinstance(meta_res, dict):
            md = meta_res.get('file_metadata', {})
            if isinstance(md, dict):
                for key in ['creation_date', 'creation_time', 'Creation Date']:
                    val = md.get(key)
                    if val:
                        parsed = self._extract_dates_from_text(str(val))
                        if parsed and 'metadata' not in dates_found:
                            dates_found['metadata'] = parsed[0]
                            break
            meta_dates = meta_res.get('dates_found', [])
            if isinstance(meta_dates, list):
                for d in meta_dates:
                    parsed = self._extract_dates_from_text(str(d))
                    if parsed and 'metadata' not in dates_found:
                        dates_found['metadata'] = parsed[0]

        # Compare dates
        consistent = True
        score = 1.0
        if len(dates_found) > 1:
            all_keys = list(dates_found.keys())
            for i in range(len(all_keys)):
                for j in range(i + 1, len(all_keys)):
                    d1 = dates_found[all_keys[i]]
                    d2 = dates_found[all_keys[j]]
                    if isinstance(d1, datetime.datetime) and isinstance(d2, datetime.datetime):
                        diff = abs((d1 - d2).days)
                        if diff > 30:
                            consistent = False
                            score = 0.0
                            conflicts.append(
                                f"Temporal conflict: {all_keys[i]} date ({d1.strftime('%Y-%m-%d')}) "
                                f"differs from {all_keys[j]} date ({d2.strftime('%Y-%m-%d')}) "
                                f"by {diff} days."
                            )

        return {
            'consistent': consistent,
            'dates_found': {k: str(v) for k, v in dates_found.items()},
            'conflicts': list(set(conflicts)),
            'score': score,
        }

    def check_location_consistency(self, claim: str, evidence_results: dict) -> dict:
        locations_found = {}
        conflicts = []

        # Locations from claim
        claim_locs = self._extract_locations_from_text(claim)
        if claim_locs:
            locations_found['claim'] = claim_locs

        # Locations from text/claim analysis entities
        for source_key in ['text', 'claim']:
            res = evidence_results.get(source_key)
            if res and isinstance(res, dict):
                entities = res.get('entities', {})
                if isinstance(entities, dict):
                    locs = entities.get('locations', [])
                    if locs and source_key not in locations_found:
                        locations_found[source_key] = [l.lower() for l in locs]

        # Locations from audio transcript
        audio_res = evidence_results.get('audio')
        if audio_res and isinstance(audio_res, dict):
            transcript = audio_res.get('transcript', '')
            if transcript:
                transcript_locs = self._extract_locations_from_text(transcript)
                if transcript_locs:
                    locations_found['transcript'] = transcript_locs

        # GPS from metadata (has_gps lives at the top level of the metadata result)
        meta_res = evidence_results.get('metadata')
        if meta_res and isinstance(meta_res, dict) and meta_res.get('has_gps'):
            locations_found['gps'] = ['gps_coordinates_present']

        # Compare locations
        consistent = True
        score = 1.0
        if len(locations_found) > 1:
            all_locs = set()
            for loc_list in locations_found.values():
                if isinstance(loc_list, list):
                    all_locs.update(loc_list)

            # Check if any locations from different sources overlap
            sources = list(locations_found.keys())
            has_overlap = False
            for i in range(len(sources)):
                for j in range(i + 1, len(sources)):
                    s1 = set(locations_found[sources[i]]) if isinstance(locations_found[sources[i]], list) else set()
                    s2 = set(locations_found[sources[j]]) if isinstance(locations_found[sources[j]], list) else set()
                    if s1 & s2:
                        has_overlap = True

            if not has_overlap and len(all_locs) > 1:
                consistent = False
                score = 0.3
                loc_summary = {k: v for k, v in locations_found.items()}
                conflicts.append(
                    f"Location inconsistency: different locations mentioned across sources: {loc_summary}"
                )

        return {
            'consistent': consistent,
            'locations_found': locations_found,
            'conflicts': conflicts,
            'score': score,
        }

    def check_entity_consistency(self, claim: str, evidence_results: dict) -> dict:
        entities_found = {}
        conflicts = []

        # Entities from claim
        claim_entities = self._extract_entities_from_text(claim)
        if claim_entities:
            entities_found['claim'] = claim_entities

        # Entities from text analysis
        for source_key in ['text', 'claim']:
            res = evidence_results.get(source_key)
            if res and isinstance(res, dict):
                entities = res.get('entities', {})
                if isinstance(entities, dict):
                    persons = entities.get('persons', [])
                    orgs = entities.get('organizations', [])
                    combined = persons + orgs
                    if combined and source_key not in entities_found:
                        entities_found[source_key] = [e.lower() for e in combined]

        # Entities from transcript
        audio_res = evidence_results.get('audio')
        if audio_res and isinstance(audio_res, dict):
            transcript = audio_res.get('transcript', '')
            if transcript:
                transcript_entities = self._extract_entities_from_text(transcript)
                if transcript_entities:
                    entities_found['transcript'] = [e.lower() for e in transcript_entities]

        # Single capitalized words (e.g. a lone first name like 'John') are
        # often real entities but are missed by the multi-word pattern.
        stop_caps = {'This', 'That', 'The', 'A', 'An', 'In', 'On', 'At', 'With'}
        claim_tokens = {
            t.strip(',.!?;:').lower()
            for t in claim.split()
            if t[:1].isupper() and t.strip(',.!?;:') not in stop_caps
        }
        transcript_set = set(entities_found.get('transcript', []))
        if claim_tokens and transcript_set and 'claim' in entities_found:
            overlap = claim_tokens & transcript_set
            if overlap:
                entities_found['claim'] = list(
                    set(e.lower() for e in entities_found['claim']) | overlap
                )

        consistent = True
        score = 1.0
        if len(entities_found) > 1:
            sources = list(entities_found.keys())
            has_any_overlap = False
            for i in range(len(sources)):
                for j in range(i + 1, len(sources)):
                    s1 = set(entities_found[sources[i]])
                    s2 = set(entities_found[sources[j]])
                    if s1 & s2:
                        has_any_overlap = True

            if not has_any_overlap:
                all_entities = set()
                for v in entities_found.values():
                    all_entities.update(v)
                if len(all_entities) > 1:
                    consistent = False
                    score = 0.5
                    conflicts.append(
                        f"Entity inconsistency: no overlapping persons/organizations across sources."
                    )

        return {
            'consistent': consistent,
            'entities_found': entities_found,
            'conflicts': conflicts,
            'score': score,
        }

    def check_semantic_consistency(self, claim: str, evidence_results: dict) -> dict:
        conflicts = []
        similarity_scores = {}
        score = 1.0
        consistent = True

        if not self.sentence_model:
            # Skipped checks must NOT register as contradictions.
            return {
                'consistent': True,
                'similarity_scores': {},
                'conflicts': [],
                'skipped': True,
                'note': 'Sentence transformer unavailable; semantic check skipped.',
                'score': 1.0,
            }

        texts_to_compare = {}
        if claim and claim.strip():
            texts_to_compare['claim'] = claim

        # Audio transcript
        audio_res = evidence_results.get('audio')
        if audio_res and isinstance(audio_res, dict):
            transcript = audio_res.get('transcript')
            if transcript and transcript.strip():
                texts_to_compare['transcript'] = transcript

        # Text file content
        text_res = evidence_results.get('text')
        if text_res and isinstance(text_res, dict):
            extracted = text_res.get('extracted_text', '')
            if extracted and extracted.strip():
                texts_to_compare['text_file'] = extracted[:1000]  # cap length

        # Document text
        doc_res = evidence_results.get('document')
        if doc_res and isinstance(doc_res, dict):
            extracted = doc_res.get('extracted_text', '')
            if extracted and extracted.strip():
                texts_to_compare['document'] = extracted[:1000]

        keys = list(texts_to_compare.keys())
        if len(keys) >= 2:
            import numpy as np
            for i in range(len(keys)):
                for j in range(i + 1, len(keys)):
                    k1, k2 = keys[i], keys[j]
                    try:
                        emb1 = self.sentence_model.encode(texts_to_compare[k1])
                        emb2 = self.sentence_model.encode(texts_to_compare[k2])
                        sim = float(
                            np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2) + 1e-9)
                        )
                        similarity_scores[f"{k1}_vs_{k2}"] = round(sim, 3)

                        if sim < 0.3:
                            consistent = False
                            score = min(score, 0.2)
                            conflicts.append(
                                f"Semantic contradiction between {k1} and {k2} (similarity: {sim:.2f})"
                            )
                        elif sim < 0.5:
                            score = min(score, 0.6)
                    except Exception:
                        pass

        return {
            'consistent': consistent,
            'similarity_scores': similarity_scores,
            'conflicts': conflicts,
            'score': score,
        }

    def check_detector_agreement(self, evidence_results: dict) -> dict:
        probs = {}
        for mod in ['image', 'audio', 'video']:
            res = evidence_results.get(mod)
            if res and isinstance(res, dict) and res.get('status') == 'success':
                probs[mod] = res.get('fake_probability', 0.0)

        agreement = 'insufficient'
        score = 1.0

        if len(probs) >= 2:
            high_count = sum(1 for p in probs.values() if p > 0.6)
            low_count = sum(1 for p in probs.values() if p <= 0.4)

            if high_count >= 2:
                agreement = 'agreeing_suspicious'
                score = 0.0
            elif low_count >= 2:
                agreement = 'agreeing_authentic'
                score = 1.0
            elif high_count > 0 and low_count > 0:
                agreement = 'mixed'
                score = 0.5
            else:
                agreement = 'mixed'
                score = 0.6

        return {
            'agreement': agreement,
            'probabilities': probs,
            'score': score,
        }
