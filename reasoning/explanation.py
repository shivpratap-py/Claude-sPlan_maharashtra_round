from typing import Dict, Any

class ExplanationGenerator:
    def generate(self, evidence_results: dict, consistency_results: dict, fusion_result: dict, confidence_result: dict) -> dict:
        assessment = fusion_result.get('assessment', 'UNKNOWN')
        suspicion = fusion_result.get('suspicion_score', 0.0)
        
        summary = f"TrustLayer analysis indicates the claim is {assessment} with a suspicion score of {suspicion:.1f}/100. "
        summary += f"Confidence is {confidence_result.get('confidence_level', 'LOW')} ({confidence_result.get('overall_confidence', 0):.1f}%)."
        
        key_findings = []
        for mod, res in evidence_results.items():
            if res and res.get('status') == 'success':
                fp = res.get('fake_probability', 0.0)
                if fp > 0.7:
                    emoji = '🔴'
                    severity = 'high'
                elif fp > 0.4:
                    emoji = '🟠'
                    severity = 'medium'
                else:
                    emoji = '🟢'
                    severity = 'low'
                key_findings.append({'emoji': emoji, 'text': f"{mod.capitalize()} analysis shows {fp*100:.1f}% probability of manipulation.", 'severity': severity})
            else:
                key_findings.append({'emoji': '⚪', 'text': f"{mod.capitalize()} analysis unavailable.", 'severity': 'unknown'})
                
        contradictions = consistency_results.get('contradictions', [])
        
        supporting_evidence = []
        for k, v in fusion_result.get('score_breakdown', {}).items():
            supporting_evidence.append(f"{k}: {v}")
            
        uncertainty_notes = confidence_result.get('missing_evidence', []) + confidence_result.get('recommendations', [])
        
        conclusion = f"The assessment of {assessment} is made because "
        if suspicion > 50:
            conclusion += "multiple indicators point towards manipulation or synthetic generation."
        else:
            conclusion += "the available evidence aligns with the claim and shows little signs of tampering."
            
        disclaimer = "TrustLayer is an AI-assisted investigation system. Its output is an evidence-based assessment and should not be treated as definitive forensic proof."
        
        full_report_text = f"# TrustLayer Investigation Report\n\n**Summary:** {summary}\n\n## Key Findings\n"
        for kf in key_findings:
            full_report_text += f"- {kf['emoji']} {kf['text']}\n"
            
        if contradictions:
            full_report_text += "\n## Contradictions\n"
            for c in contradictions:
                full_report_text += f"- {c}\n"
                
        full_report_text += f"\n## Conclusion\n{conclusion}\n\n*Disclaimer: {disclaimer}*"
        
        return {
            'summary': summary,
            'key_findings': key_findings,
            'contradictions': contradictions,
            'supporting_evidence': supporting_evidence,
            'uncertainty_notes': uncertainty_notes,
            'conclusion': conclusion,
            'disclaimer': disclaimer,
            'full_report_text': full_report_text
        }
