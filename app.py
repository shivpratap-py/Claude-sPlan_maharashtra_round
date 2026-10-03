"""
TrustLayer — AI-Powered Digital Authenticity & Trust Investigation Platform
Main Streamlit Application
"""

import streamlit as st
import os
import sys
import json
import tempfile
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Page config must be first Streamlit command
st.set_page_config(
    page_title="TrustLayer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS for dark forensics theme ───────────────────────────────────────

st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background-color: #0a0e17;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b2838 100%);
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 {
        color: #e0e7ff;
        font-size: 2.5rem;
        margin: 0;
        letter-spacing: 2px;
    }
    .main-header p {
        color: #8899aa;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Cards */
    .evidence-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .evidence-card h4 {
        color: #e0e7ff;
        margin: 0 0 0.5rem 0;
    }
    
    /* Assessment badges */
    .assessment-authentic {
        background: #064e3b;
        color: #6ee7b7;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.3rem;
        display: inline-block;
        border: 1px solid #10b981;
    }
    .assessment-concerns {
        background: #3f3d0f;
        color: #fde047;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.3rem;
        display: inline-block;
        border: 1px solid #eab308;
    }
    .assessment-manipulated {
        background: #78350f;
        color: #fbbf24;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.3rem;
        display: inline-block;
        border: 1px solid #f59e0b;
    }
    .assessment-coordinated {
        background: #7f1d1d;
        color: #fca5a5;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.3rem;
        display: inline-block;
        border: 1px solid #ef4444;
    }
    .assessment-insufficient {
        background: #1f2937;
        color: #9ca3af;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.3rem;
        display: inline-block;
        border: 1px solid #6b7280;
    }
    
    /* Confidence */
    .confidence-high { color: #6ee7b7; }
    .confidence-medium { color: #fbbf24; }
    .confidence-low { color: #fca5a5; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #1e3a5f;
    }
    
    /* Metric cards */
    .metric-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #e0e7ff;
    }
    .metric-label {
        color: #6b7280;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Disclaimer */
    .disclaimer {
        background: #1a1a2e;
        border-left: 3px solid #4a5568;
        padding: 0.8rem 1rem;
        margin-top: 1rem;
        border-radius: 0 6px 6px 0;
        color: #8899aa;
        font-size: 0.85rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* File uploader style */
    .stFileUploader {
        border: 1px dashed #1e3a5f;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ─── Lazy imports and initialization ───────────────────────────────────────────

def import_analyzers():
    """Lazy import analyzers to avoid loading models at startup."""
    from analyzers.image_analyzer import ImageAnalyzer
    from analyzers.audio_analyzer import AudioAnalyzer
    from analyzers.video_analyzer import VideoAnalyzer
    from analyzers.metadata_analyzer import MetadataAnalyzer
    from analyzers.text_analyzer import TextAnalyzer
    from analyzers.document_analyzer import DocumentAnalyzer
    return {
        'image': ImageAnalyzer(),
        'audio': AudioAnalyzer(),
        'video': VideoAnalyzer(),
        'metadata': MetadataAnalyzer(),
        'text': TextAnalyzer(),
        'document': DocumentAnalyzer(),
    }


def import_reasoning():
    """Lazy import reasoning modules."""
    from reasoning.consistency_engine import ConsistencyEngine
    from reasoning.evidence_fusion import EvidenceFusion
    from reasoning.confidence import ConfidenceEstimator
    from reasoning.explanation import ExplanationGenerator
    return {
        'consistency': ConsistencyEngine(),
        'fusion': EvidenceFusion(),
        'confidence': ConfidenceEstimator(),
        'explanation': ExplanationGenerator(),
    }


# ─── Session state initialization ─────────────────────────────────────────────

if 'investigation_results' not in st.session_state:
    st.session_state.investigation_results = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'New Investigation'
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'eval_results' not in st.session_state:
    st.session_state.eval_results = None


# ─── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🔍 TrustLayer")
    st.markdown("---")
    
    page = st.radio(
        "Investigation",
        ["New Investigation", "Evidence", "Analysis", "Results", "Evaluation"],
        index=["New Investigation", "Evidence", "Analysis", "Results", "Evaluation"].index(
            st.session_state.current_page
        ),
        key="nav_radio"
    )
    st.session_state.current_page = page
    
    st.markdown("---")
    st.markdown(
        '<div class="disclaimer">'
        'TrustLayer is an AI-assisted investigation system. '
        'Its output is an evidence-based assessment and should '
        'not be treated as definitive forensic proof.'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.caption("v1.1 — Hackathon Prototype")


# ─── Helper functions ──────────────────────────────────────────────────────────

def get_assessment_class(assessment: str) -> str:
    """Return CSS class for assessment badge."""
    mapping = {
        'AUTHENTIC': 'assessment-authentic',
        'AUTHENTIC_WITH_CONCERNS': 'assessment-concerns',
        'MANIPULATED': 'assessment-manipulated',
        'COORDINATED SYNTHETIC': 'assessment-coordinated',
        'INSUFFICIENT EVIDENCE': 'assessment-insufficient',
    }
    return mapping.get(assessment, 'assessment-insufficient')


def get_assessment_emoji(assessment: str) -> str:
    mapping = {
        'AUTHENTIC': '🟢',
        'AUTHENTIC_WITH_CONCERNS': '🟡',
        'MANIPULATED': '🟠',
        'COORDINATED SYNTHETIC': '🔴',
        'INSUFFICIENT EVIDENCE': '⚪',
    }
    return mapping.get(assessment, '⚪')


def classify_file(filename: str) -> str:
    """Classify uploaded file into modality category."""
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
    categories = {
        'image': ['jpg', 'jpeg', 'png', 'webp'],
        'audio': ['mp3', 'wav', 'm4a'],
        'video': ['mp4', 'mov'],
        'document': ['pdf'],
        'text': ['txt'],
    }
    for cat, exts in categories.items():
        if ext in exts:
            return cat
    return 'unknown'


def run_investigation(claim: str, uploaded_files: list, progress_container):
    """Run the full investigation pipeline."""
    from utils.file_utils import create_temp_dir, save_uploaded_file, cleanup_temp_dir
    
    temp_dir = create_temp_dir()
    evidence_results = {}
    
    try:
        # Initialize analyzers and reasoning
        progress_container.write("⏳ Loading AI models...")
        progress_bar = progress_container.progress(0, text="Initializing...")
        
        analyzers = import_analyzers()
        reasoning = import_reasoning()
        
        progress_bar.progress(10, text="Models loaded")
        
        # ── Save and categorize files ──
        saved_files = {}
        for uf in uploaded_files:
            file_path = save_uploaded_file(uf, temp_dir)
            file_type = classify_file(uf.name)
            if file_type not in saved_files:
                saved_files[file_type] = []
            saved_files[file_type].append((uf.name, file_path))
        
        progress_bar.progress(15, text="Files prepared")
        total_steps = len(uploaded_files) + 3  # +3 for reasoning steps
        current_step = 0
        
        # ── Analyze each file ──
        
        # Images
        if 'image' in saved_files:
            for name, path in saved_files['image']:
                current_step += 1
                pct = 15 + int((current_step / total_steps) * 60)
                progress_bar.progress(pct, text=f"Analyzing image: {name}")
                try:
                    result = analyzers['image'].analyze(path)
                    evidence_results['image'] = result
                except Exception as e:
                    evidence_results['image'] = {
                        'modality': 'image', 'status': 'error',
                        'error': str(e), 'classification': 'unavailable',
                        'fake_probability': 0.0, 'confidence': 0.0,
                        'evidence': [f'Image analysis failed: {e}'], 'metadata': {}
                    }
        
        # Audio
        if 'audio' in saved_files:
            for name, path in saved_files['audio']:
                current_step += 1
                pct = 15 + int((current_step / total_steps) * 60)
                progress_bar.progress(pct, text=f"Analyzing audio: {name}")
                try:
                    result = analyzers['audio'].analyze(path)
                    evidence_results['audio'] = result
                except Exception as e:
                    evidence_results['audio'] = {
                        'modality': 'audio', 'status': 'error',
                        'error': str(e), 'classification': 'unavailable',
                        'fake_probability': 0.0, 'confidence': 0.0,
                        'evidence': [f'Audio analysis failed: {e}'],
                        'metadata': {}, 'transcript': None
                    }
        
        # Video
        if 'video' in saved_files:
            for name, path in saved_files['video']:
                current_step += 1
                pct = 15 + int((current_step / total_steps) * 60)
                progress_bar.progress(pct, text=f"Analyzing video: {name} (this may take a moment)")
                try:
                    def video_progress(curr, total):
                        sub_pct = pct + int((curr / max(total, 1)) * 10)
                        progress_bar.progress(min(sub_pct, 95),
                                              text=f"Analyzing video frame {curr}/{total}")
                    result = analyzers['video'].analyze(path, progress_callback=video_progress)
                    evidence_results['video'] = result
                    # Also store video audio analysis separately if available
                    if result.get('audio_analysis') and not evidence_results.get('audio'):
                        evidence_results['audio'] = result['audio_analysis']
                except Exception as e:
                    evidence_results['video'] = {
                        'modality': 'video', 'status': 'error',
                        'error': str(e), 'classification': 'unavailable',
                        'fake_probability': 0.0, 'confidence': 0.0,
                        'evidence': [f'Video analysis failed: {e}'], 'metadata': {}
                    }
        
        # Documents
        if 'document' in saved_files:
            for name, path in saved_files['document']:
                current_step += 1
                pct = 15 + int((current_step / total_steps) * 60)
                progress_bar.progress(pct, text=f"Analyzing document: {name}")
                try:
                    result = analyzers['document'].analyze(path)
                    evidence_results['document'] = result
                    # Extract text analysis from document
                    if result.get('text_analysis'):
                        evidence_results['text'] = result['text_analysis']
                except Exception as e:
                    evidence_results['document'] = {
                        'modality': 'document', 'status': 'error',
                        'error': str(e), 'classification': 'unavailable',
                        'fake_probability': 0.0, 'confidence': 0.0,
                        'evidence': [f'Document analysis failed: {e}'], 'metadata': {}
                    }
        
        # Text files
        if 'text' in saved_files:
            for name, path in saved_files['text']:
                current_step += 1
                pct = 15 + int((current_step / total_steps) * 60)
                progress_bar.progress(pct, text=f"Analyzing text: {name}")
                try:
                    with open(path, 'r', encoding='utf-8', errors='replace') as f:
                        text_content = f.read()
                    result = analyzers['text'].analyze(text_content, source=name)
                    evidence_results['text'] = result
                except Exception as e:
                    evidence_results['text'] = {
                        'modality': 'text', 'status': 'error',
                        'error': str(e), 'classification': 'unavailable',
                        'fake_probability': 0.0, 'confidence': 0.0,
                        'evidence': [f'Text analysis failed: {e}'], 'metadata': {}
                    }
        
        # Metadata analysis for all files
        all_metadata = {}
        for file_type, files in saved_files.items():
            for name, path in files:
                try:
                    meta_result = analyzers['metadata'].analyze(path, file_type)
                    all_metadata[name] = meta_result
                except Exception:
                    pass
        if all_metadata:
            # Merge into a single metadata result
            first_meta = list(all_metadata.values())[0]
            combined_dates = []
            combined_software = []
            for m in all_metadata.values():
                combined_dates.extend(m.get('dates_found', []))
                combined_software.extend(m.get('software_detected', []))
            first_meta['dates_found'] = combined_dates
            first_meta['software_detected'] = combined_software
            first_meta['all_files_metadata'] = all_metadata
            evidence_results['metadata'] = first_meta
        
        # ── Claim text analysis ──
        if claim and claim.strip():
            try:
                claim_analysis = analyzers['text'].analyze(claim, source='investigation_claim')
                evidence_results['claim'] = claim_analysis
            except Exception:
                pass
        
        # ── Cross-modal reasoning ──
        progress_bar.progress(80, text="Running cross-modal consistency analysis...")
        
        consistency_results = reasoning['consistency'].analyze_consistency(
            claim or "", evidence_results
        )
        
        progress_bar.progress(85, text="Fusing evidence...")
        
        fusion_result = reasoning['fusion'].fuse_evidence(
            evidence_results, consistency_results
        )
        
        progress_bar.progress(90, text="Estimating confidence...")
        
        confidence_result = reasoning['confidence'].estimate(
            evidence_results, consistency_results, fusion_result
        )
        
        progress_bar.progress(95, text="Generating explanation...")
        
        explanation_result = reasoning['explanation'].generate(
            evidence_results, consistency_results, fusion_result, confidence_result
        )
        
        progress_bar.progress(100, text="Investigation complete!")
        time.sleep(0.5)
        
        # Store results
        investigation_data = {
            'investigation_id': f"TL-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'claim': claim,
            'files_analyzed': {k: [n for n, _ in v] for k, v in saved_files.items()},
            'evidence_results': evidence_results,
            'consistency_results': consistency_results,
            'fusion_result': fusion_result,
            'confidence_result': confidence_result,
            'explanation_result': explanation_result,
        }
        
        return investigation_data
        
    finally:
        cleanup_temp_dir(temp_dir)


def render_report_download(investigation_data: dict):
    """Generate and offer investigation report download."""
    try:
        report_lines = []
        report_lines.append("# TrustLayer Investigation Report\n")
        report_lines.append(f"**Investigation ID:** {investigation_data.get('investigation_id', 'N/A')}")
        report_lines.append(f"**Date:** {investigation_data.get('timestamp', 'N/A')}")
        report_lines.append(f"**Claim:** {investigation_data.get('claim', 'No claim provided')}\n")
        
        fusion = investigation_data.get('fusion_result', {})
        confidence = investigation_data.get('confidence_result', {})
        explanation = investigation_data.get('explanation_result', {})
        
        report_lines.append(f"## Assessment: {fusion.get('assessment', 'N/A')}")
        report_lines.append(f"**Confidence:** {fusion.get('confidence', 0):.0f}% ({confidence.get('confidence_level', 'N/A')})")
        report_lines.append(f"**Evidence Completeness:** {confidence.get('evidence_completeness', 0):.0f}%\n")
        
        # Evidence summary
        report_lines.append("## Evidence Summary\n")
        for modality, result in investigation_data.get('evidence_results', {}).items():
            if isinstance(result, dict) and result.get('status') == 'success':
                report_lines.append(
                    f"- **{modality.title()}**: {result.get('classification', 'N/A')} "
                    f"(Fake prob: {result.get('fake_probability', 0):.1%}, "
                    f"Confidence: {result.get('confidence', 0):.1%})"
                )
        
        # Key findings
        report_lines.append("\n## Key Findings\n")
        for finding in explanation.get('key_findings', []):
            if isinstance(finding, dict):
                report_lines.append(f"- {finding.get('emoji', '')} {finding.get('text', '')}")
            else:
                report_lines.append(f"- {finding}")
        
        # Contradictions
        contradictions = explanation.get('contradictions', [])
        if contradictions:
            report_lines.append("\n## Contradictions\n")
            for c in contradictions:
                report_lines.append(f"- {c}")
        
        # Conclusion
        report_lines.append(f"\n## Conclusion\n\n{explanation.get('conclusion', 'N/A')}")
        
        # Uncertainty
        uncertainty = explanation.get('uncertainty_notes', [])
        if uncertainty:
            report_lines.append("\n## Uncertainty Notes\n")
            for u in uncertainty:
                report_lines.append(f"- {u}")
        
        # Score breakdown
        report_lines.append("\n## Score Breakdown\n")
        for category, info in fusion.get('score_breakdown', {}).items():
            if isinstance(info, dict):
                report_lines.append(f"- **{category}**: {info.get('weighted_score', 0):.1f} — {info.get('explanation', '')}")
            else:
                report_lines.append(f"- **{category}**: {info}")
        
        # Disclaimer
        report_lines.append(f"\n---\n\n{explanation.get('disclaimer', '')}")
        
        report_text = "\n".join(report_lines)
        
        # Also generate JSON
        report_json = json.dumps(investigation_data, indent=2, default=str)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📄 Download Report (Markdown)",
                report_text,
                file_name=f"trustlayer_report_{investigation_data.get('investigation_id', 'report')}.md",
                mime="text/markdown"
            )
        with col2:
            st.download_button(
                "📊 Download Report (JSON)",
                report_json,
                file_name=f"trustlayer_report_{investigation_data.get('investigation_id', 'report')}.json",
                mime="application/json"
            )
            
    except Exception as e:
        st.error(f"Report generation error: {e}")


# ─── Page: New Investigation ───────────────────────────────────────────────────

def page_new_investigation():
    # Header
    st.markdown(
        '<div class="main-header">'
        '<h1>🔍 TRUSTLAYER</h1>'
        '<p>Multimodal Digital Authenticity &amp; Trust Investigation</p>'
        '</div>',
        unsafe_allow_html=True
    )
    
    # Investigation claim
    st.markdown("### 📝 Investigation Claim")
    st.caption("Describe the claim being investigated. Example: *'This video shows Person X at Location Y on Date Z.'*")
    claim = st.text_area(
        "Enter the claim to investigate:",
        placeholder="This video shows the CEO of Acme Corp giving a speech at the Delhi conference on September 20, 2026.",
        height=100,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # File upload
    st.markdown("### 📁 Upload Evidence")
    st.caption("Upload multiple evidence files for this investigation. Supported: JPG, PNG, WEBP, MP3, WAV, M4A, MP4, MOV, TXT, PDF")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**🖼️ Images**")
        image_files = st.file_uploader(
            "Upload images",
            type=['jpg', 'jpeg', 'png', 'webp'],
            accept_multiple_files=True,
            key="image_upload",
            label_visibility="collapsed"
        )
    with col2:
        st.markdown("**🔊 Audio**")
        audio_files = st.file_uploader(
            "Upload audio",
            type=['mp3', 'wav', 'm4a'],
            accept_multiple_files=True,
            key="audio_upload",
            label_visibility="collapsed"
        )
    with col3:
        st.markdown("**🎬 Video**")
        video_files = st.file_uploader(
            "Upload video",
            type=['mp4', 'mov'],
            accept_multiple_files=True,
            key="video_upload",
            label_visibility="collapsed"
        )
    with col4:
        st.markdown("**📄 Documents**")
        doc_files = st.file_uploader(
            "Upload documents",
            type=['txt', 'pdf'],
            accept_multiple_files=True,
            key="doc_upload",
            label_visibility="collapsed"
        )
    
    # Combine all files
    all_files = (image_files or []) + (audio_files or []) + (video_files or []) + (doc_files or [])
    
    if all_files:
        st.markdown("---")
        st.markdown(f"### 📋 Evidence Summary: **{len(all_files)} file(s)** uploaded")
        file_cols = st.columns(min(len(all_files), 4))
        for i, f in enumerate(all_files):
            with file_cols[i % len(file_cols)]:
                ftype = classify_file(f.name)
                emoji_map = {'image': '🖼️', 'audio': '🔊', 'video': '🎬', 
                            'document': '📄', 'text': '📝', 'unknown': '❓'}
                st.markdown(
                    f'<div class="evidence-card">'
                    f'<h4>{emoji_map.get(ftype, "❓")} {f.name}</h4>'
                    f'<p style="color: #6b7280; margin: 0;">{ftype.upper()} • {f.size / 1024:.1f} KB</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
    
    st.markdown("---")
    
    # Analyze button
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        analyze_clicked = st.button(
            "🔬 ANALYZE INVESTIGATION",
            type="primary",
            use_container_width=True,
            disabled=len(all_files) == 0
        )
    
    if analyze_clicked and all_files:
        progress_container = st.container()
        with progress_container:
            st.markdown("---")
            st.markdown("### ⚡ Analysis in Progress")
        
        try:
            results = run_investigation(claim, all_files, progress_container)
            st.session_state.investigation_results = results
            st.session_state.analysis_complete = True
            st.session_state.current_page = 'Results'
            st.rerun()
        except Exception as e:
            st.error(f"Investigation failed: {str(e)}")
            st.exception(e)
    
    elif analyze_clicked:
        st.warning("Please upload at least one evidence file.")


# ─── Page: Evidence ────────────────────────────────────────────────────────────

def page_evidence():
    st.markdown("## 📁 Evidence Details")
    
    results = st.session_state.investigation_results
    if not results:
        st.info("No investigation results yet. Start a new investigation first.")
        return
    
    st.markdown(f"**Investigation ID:** `{results.get('investigation_id', 'N/A')}`")
    st.markdown(f"**Claim:** {results.get('claim', 'No claim provided')}")
    st.markdown("---")
    
    evidence = results.get('evidence_results', {})
    
    for modality, result in evidence.items():
        if modality == 'claim':
            continue
        if not isinstance(result, dict):
            continue
            
        emoji_map = {'image': '🖼️', 'audio': '🔊', 'video': '🎬',
                    'document': '📄', 'text': '📝', 'metadata': '📋'}
        
        with st.expander(f"{emoji_map.get(modality, '📌')} {modality.upper()} Analysis", expanded=True):
            status = result.get('status', 'unknown')
            
            if status == 'error':
                st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
                continue
            
            col1, col2, col3 = st.columns(3)
            with col1:
                classification = result.get('classification', 'N/A')
                color = '#6ee7b7' if 'authentic' in str(classification).lower() else (
                    '#fca5a5' if 'suspicious' in str(classification).lower() else '#9ca3af'
                )
                st.markdown(f"**Classification:** <span style='color:{color}'>{classification}</span>",
                          unsafe_allow_html=True)
            with col2:
                st.metric("Fake Probability", f"{result.get('fake_probability', 0):.1%}")
            with col3:
                st.metric("Confidence", f"{result.get('confidence', 0):.1%}")
            
            # Evidence items
            evidence_items = result.get('evidence', [])
            if evidence_items:
                st.markdown("**Evidence:**")
                for item in evidence_items:
                    st.markdown(f"  - {item}")
            
            # Transcript (audio)
            transcript = result.get('transcript')
            if transcript:
                st.markdown("**Transcript:**")
                st.text_area("", transcript, height=100, disabled=True, 
                           key=f"transcript_{modality}")
            
            # Metadata
            metadata = result.get('metadata', {})
            if metadata:
                with st.expander("Technical Metadata"):
                    st.json(metadata)


# ─── Page: Analysis ────────────────────────────────────────────────────────────

def page_analysis():
    st.markdown("## 🔗 Cross-Modal Analysis")
    
    results = st.session_state.investigation_results
    if not results:
        st.info("No investigation results yet. Start a new investigation first.")
        return
    
    consistency = results.get('consistency_results', {})
    
    # Overview metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{consistency.get("total_checks_performed", 0)}</div>'
            f'<div class="metric-label">Checks Performed</div>'
            f'</div>', unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{consistency.get("total_inconsistencies", 0)}</div>'
            f'<div class="metric-label">Inconsistencies Found</div>'
            f'</div>', unsafe_allow_html=True
        )
    with col3:
        score = consistency.get('overall_consistency_score', 0)
        color_class = 'confidence-high' if score > 0.7 else ('confidence-medium' if score > 0.4 else 'confidence-low')
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value {color_class}">{score:.0%}</div>'
            f'<div class="metric-label">Consistency Score</div>'
            f'</div>', unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Individual consistency checks
    check_names = {
        'temporal': ('🕐 Temporal Consistency', 'Do dates and timestamps align?'),
        'location': ('📍 Location Consistency', 'Do locations mentioned match across sources?'),
        'entity': ('👤 Entity Consistency', 'Are the same people/organizations mentioned?'),
        'semantic': ('💬 Semantic Consistency', 'Do the sources describe the same event?'),
        'detector_agreement': ('🤖 Detector Agreement', 'Do independent detectors agree?'),
    }
    
    for key, (title, description) in check_names.items():
        check_result = consistency.get(key, {})
        if not check_result:
            continue
        
        with st.expander(title, expanded=True):
            st.caption(description)
            
            is_consistent = check_result.get('consistent', check_result.get('agreement', '') in ['agreeing_authentic', 'agreeing_suspicious'])
            score = check_result.get('score', 0)
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if isinstance(is_consistent, bool):
                    if is_consistent:
                        st.success(f"Consistent ({score:.0%})")
                    else:
                        st.error(f"Inconsistent ({score:.0%})")
                else:
                    st.info(f"Score: {score:.0%}")
            
            with col2:
                conflicts = check_result.get('conflicts', [])
                if conflicts:
                    for conflict in conflicts:
                        st.warning(conflict)
                else:
                    st.markdown("No conflicts detected.")
    
    # Contradictions summary
    contradictions = consistency.get('contradictions', [])
    if contradictions:
        st.markdown("---")
        st.markdown("### ⚠️ All Contradictions")
        for c in contradictions:
            st.error(c)


# ─── Page: Results ─────────────────────────────────────────────────────────────

def page_results():
    results = st.session_state.investigation_results
    if not results:
        st.info("No investigation results yet. Start a new investigation first.")
        return
    
    fusion = results.get('fusion_result', {})
    confidence = results.get('confidence_result', {})
    explanation = results.get('explanation_result', {})
    evidence = results.get('evidence_results', {})
    consistency = results.get('consistency_results', {})
    
    assessment = fusion.get('assessment', 'INSUFFICIENT EVIDENCE')
    conf_value = fusion.get('confidence', 0)
    conf_level = confidence.get('confidence_level', 'LOW')
    
    # ── Main assessment card ──
    st.markdown("## 🔍 Investigation Result")
    st.markdown(f"**ID:** `{results.get('investigation_id', 'N/A')}` | **Date:** {results.get('timestamp', 'N/A')}")
    
    assessment_class = get_assessment_class(assessment)
    assessment_emoji = get_assessment_emoji(assessment)
    
    st.markdown(
        f'<div style="text-align:center; padding: 2rem; background: #111827; '
        f'border-radius: 12px; border: 1px solid #1f2937; margin: 1rem 0;">'
        f'<div class="{assessment_class}">{assessment_emoji} {assessment}</div>'
        f'<p style="color: #e0e7ff; font-size: 1.5rem; margin-top: 1rem;">'
        f'Confidence: <strong>{conf_value:.0f}%</strong> ({conf_level})</p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # ── Evidence summary metrics ──
    st.markdown("### 📊 Evidence Summary")
    
    modality_cols = []
    for mod in ['image', 'audio', 'video', 'text', 'document']:
        if mod in evidence and isinstance(evidence[mod], dict) and evidence[mod].get('status') == 'success':
            modality_cols.append((mod, evidence[mod]))
    
    if modality_cols:
        cols = st.columns(len(modality_cols))
        for i, (mod, result) in enumerate(modality_cols):
            with cols[i]:
                classification = result.get('classification', 'N/A')
                fake_prob = result.get('fake_probability', 0)
                color = '#6ee7b7' if fake_prob < 0.3 else ('#fbbf24' if fake_prob < 0.6 else '#fca5a5')
                emoji_map = {'image': '🖼️', 'audio': '🔊', 'video': '🎬',
                            'text': '📝', 'document': '📄'}
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div style="font-size: 1.5rem;">{emoji_map.get(mod, "📌")}</div>'
                    f'<div class="metric-label">{mod.upper()}</div>'
                    f'<div style="color: {color}; font-weight: bold;">{classification}</div>'
                    f'<div class="metric-value" style="color: {color};">{fake_prob:.0%}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
    
    st.markdown("---")
    
    # ── Evidence graph ──
    st.markdown("### 🕸️ Evidence Graph")
    try:
        from utils.visualization import create_evidence_graph, create_confidence_gauge, create_evidence_summary_chart
        
        fig = create_evidence_graph(evidence, consistency)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.caption(f"Evidence graph unavailable: {e}")
        # Fallback: text-based evidence map
        st.code(
            "         CLAIM\n"
            "           │\n"
            "  ┌────────┼────────┐\n"
            "  ↓        ↓        ↓\n"
            "IMAGE    AUDIO     TEXT\n"
            "  │        │        │\n"
            "  └────┬───┴────────┘\n"
            "       ↓\n"
            "CROSS-MODAL ANALYSIS\n"
            "       ↓\n"
            f"  {assessment}",
            language=None
        )
    
    # ── Confidence gauge ──
    st.markdown("---")
    st.markdown("### 📈 Confidence & Completeness")
    
    col1, col2 = st.columns(2)
    with col1:
        try:
            gauge_fig = create_confidence_gauge(conf_value, "Investigation Confidence")
            st.plotly_chart(gauge_fig, use_container_width=True)
        except Exception:
            st.metric("Confidence", f"{conf_value:.0f}%")
    
    with col2:
        completeness = confidence.get('evidence_completeness', 0)
        try:
            gauge_fig = create_confidence_gauge(completeness, "Evidence Completeness")
            st.plotly_chart(gauge_fig, use_container_width=True)
        except Exception:
            st.metric("Evidence Completeness", f"{completeness:.0f}%")
    
    # Missing evidence recommendations
    missing = confidence.get('missing_evidence', [])
    recommendations = confidence.get('recommendations', [])
    if missing or recommendations:
        with st.expander("💡 Recommendations for Improving Confidence"):
            for m in missing:
                st.markdown(f"- ⚪ {m}")
            for r in recommendations:
                st.markdown(f"- 💡 {r}")
    
    # ── Key findings ──
    st.markdown("---")
    st.markdown("### 🔎 Key Findings")
    
    findings = explanation.get('key_findings', [])
    for finding in findings:
        if isinstance(finding, dict):
            emoji = finding.get('emoji', '•')
            text = finding.get('text', '')
            st.markdown(f"{emoji} {text}")
        else:
            st.markdown(f"• {finding}")
    
    # ── Contradictions ──
    contradictions = explanation.get('contradictions', [])
    if contradictions:
        st.markdown("---")
        st.markdown("### ⚠️ Contradictions Detected")
        for c in contradictions:
            st.error(c)
    
    # ── Why this decision? ──
    st.markdown("---")
    with st.expander("### 🧠 Why This Decision?", expanded=True):
        st.markdown(explanation.get('conclusion', 'No conclusion available.'))
        
        # Score breakdown
        st.markdown("#### Score Breakdown")
        breakdown = fusion.get('score_breakdown', {})
        if breakdown:
            for category, info in breakdown.items():
                if isinstance(info, dict):
                    score = info.get('weighted_score', 0)
                    exp = info.get('explanation', '')
                    bar_color = '#6ee7b7' if score < 10 else ('#fbbf24' if score < 25 else '#fca5a5')
                    st.markdown(
                        f"**{category}**: {score:.1f} — {exp}"
                    )
                    st.progress(min(score / 50, 1.0))
    
    # ── Uncertainty ──
    uncertainty = explanation.get('uncertainty_notes', [])
    if uncertainty:
        st.markdown("---")
        with st.expander("⚖️ Uncertainty & Limitations"):
            for note in uncertainty:
                st.info(note)
    
    # ── Disclaimer ──
    st.markdown("---")
    st.markdown(
        f'<div class="disclaimer">{explanation.get("disclaimer", "")}</div>',
        unsafe_allow_html=True
    )
    
    # ── Report download ──
    st.markdown("---")
    st.markdown("### 📋 Investigation Report")
    render_report_download(results)


# ─── Page: Evaluation ──────────────────────────────────────────────────────────

def page_evaluation():
    st.markdown("## 📊 Evaluation Mode")
    st.caption("Run predefined test cases to evaluate TrustLayer's cross-modal reasoning capabilities.")
    
    try:
        from evaluation.evaluator import Evaluator
        from evaluation.test_cases import get_test_cases
    except ImportError as e:
        st.error(f"Evaluation modules not available: {e}")
        return
    
    tab1, tab2 = st.tabs(["🧪 Test Cases", "🔬 Generalization Test"])
    
    with tab1:
        st.markdown("### Predefined Test Cases")
        
        test_cases = get_test_cases()
        
        # Show test case descriptions
        for i, tc in enumerate(test_cases):
            with st.expander(f"Case {i+1}: {tc.name}", expanded=False):
                st.markdown(f"**Description:** {tc.description}")
                st.markdown(f"**Claim:** {tc.claim}")
                st.markdown(f"**Expected:** `{tc.expected_assessment}`")
                st.markdown(f"**Category:** {tc.category}")
                if tc.expected_contradictions:
                    st.markdown(f"**Expected contradictions:** {', '.join(tc.expected_contradictions)}")
        
        st.markdown("---")
        
        if st.button("▶️ Run All Test Cases", type="primary", use_container_width=True):
            with st.spinner("Running evaluation..."):
                evaluator = Evaluator()
                eval_results = evaluator.run_all_tests()
            
            st.session_state.eval_results = eval_results
        
        # Display results if available
        if st.session_state.get('eval_results'):
            eval_results = st.session_state.eval_results
            
            st.markdown("### Results")
            
            # Metrics
            metrics = eval_results.get('metrics', {})
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Accuracy", f"{metrics.get('accuracy', 0):.1%}")
            with col2:
                st.metric("Precision", f"{metrics.get('precision', 0):.1%}")
            with col3:
                st.metric("Recall", f"{metrics.get('recall', 0):.1%}")
            with col4:
                st.metric("F1 Score", f"{metrics.get('f1', 0):.1%}")
            
            # Per-case results
            st.markdown("### Per-Case Results")
            for case_result in eval_results.get('results', []):
                name = case_result.get('name', 'Unknown')
                predicted = case_result.get('predicted', 'N/A')
                expected = case_result.get('expected', 'N/A')
                passed = case_result.get('passed', False)
                
                icon = "✅" if passed else "❌"
                st.markdown(
                    f"{icon} **{name}** — "
                    f"Predicted: `{predicted}` | Expected: `{expected}`"
                )
            
            # Confusion matrix
            st.markdown("### Confusion Matrix")
            try:
                from evaluation.metrics import MetricsCalculator
                mc = MetricsCalculator()
                cm = metrics.get('confusion_matrix', [])
                labels = metrics.get('labels', MetricsCalculator.ASSESSMENT_LABELS)
                if cm:
                    fig = mc.create_confusion_matrix_figure(cm, labels)
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.caption(f"Confusion matrix visualization unavailable: {e}")
    
    with tab2:
        st.markdown("### 🔬 Unseen Combination Test")
        st.markdown(
            "This test evaluates whether TrustLayer's cross-modal reasoning "
            "can identify manipulation in **combinations** that were not explicitly "
            "represented during calibration."
        )
        st.info(
            "**Note:** This is a prototype evaluation of combination-level generalization, "
            "not proof of universal generalization."
        )
        
        if st.button("▶️ Run Generalization Test", type="primary", key="gen_test"):
            with st.spinner("Running generalization test..."):
                evaluator = Evaluator()
                gen_results = evaluator.run_generalization_test()
            
            st.markdown("### Results")
            for result in gen_results.get('results', []):
                name = result.get('name', 'Unknown')
                predicted = result.get('predicted', 'N/A')
                expected = result.get('expected', 'N/A')
                passed = result.get('passed', False)
                
                icon = "✅" if passed else "❌"
                color = "green" if passed else "red"
                
                st.markdown(f"### {icon} {name}")
                st.markdown(f"**Predicted:** `{predicted}` | **Expected:** `{expected}`")
                
                # Show the reasoning
                fusion = result.get('fusion_result', {})
                if fusion:
                    st.markdown(f"**Confidence:** {fusion.get('confidence', 0):.0f}%")
                    st.markdown(f"**Suspicion Score:** {fusion.get('suspicion_score', 0):.0f}")
                
                explanation_result = result.get('explanation', {})
                if explanation_result:
                    findings = explanation_result.get('key_findings', [])
                    if findings:
                        st.markdown("**Key findings:**")
                        for f in findings:
                            if isinstance(f, dict):
                                st.markdown(f"  {f.get('emoji', '')} {f.get('text', '')}")
            
            st.markdown("---")
            st.markdown(f"**Summary:** {gen_results.get('summary', 'N/A')}")


# ─── Main routing ──────────────────────────────────────────────────────────────

def main():
    page = st.session_state.current_page
    
    if page == "New Investigation":
        page_new_investigation()
    elif page == "Evidence":
        page_evidence()
    elif page == "Analysis":
        page_analysis()
    elif page == "Results":
        page_results()
    elif page == "Evaluation":
        page_evaluation()
    else:
        page_new_investigation()


if __name__ == "__main__":
    main()
