"""TrustLayer design system: CSS injection + HTML helpers.
Preserves original color palette (navy/slate dark theme with standard status colors)
while expanding visual depth, typography, card elevation, and contrast.
"""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  /* Core Original Dark Palette Expanded */
  --bg-deep: #080d18;
  --bg: #0c1220;
  --surface: #131b2e;
  --surface-2: #1a2440;
  --surface-hover: #222f52;
  --line: #26314d;
  --line-glow: rgba(124, 156, 255, 0.25);
  
  /* Text & Typography */
  --text: #f0f4fc;
  --muted: #8b97b5;
  --muted-dark: #5c6885;
  
  /* Accent Colors */
  --accent: #7c9cff;
  --accent-glow: rgba(124, 156, 255, 0.15);
  --accent-bright: #9bb5ff;
  
  /* Status Indicators (Preserved Original Scheme) */
  --ok: #34d399;
  --ok-glow: rgba(52, 211, 153, 0.15);
  --warn: #fbbf24;
  --warn-glow: rgba(251, 191, 36, 0.15);
  --bad: #f87171;
  --bad-glow: rgba(248, 113, 113, 0.15);
  --neutral: #94a3b8;
  --neutral-glow: rgba(148, 163, 184, 0.12);
}

/* Global Reset & Typography */
html, body, .stApp, [class*="css"] { 
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif; 
}

code, kbd, pre, .stCode {
  font-family: 'JetBrains Mono', monospace !important;
}

.stApp { 
  background: radial-gradient(circle at 50% 0%, #151e36 0%, var(--bg-deep) 70%);
  background-attachment: fixed;
  color: var(--text); 
}

header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

.block-container { 
  max-width: 1180px; 
  padding-top: 2rem; 
  padding-bottom: 4rem; 
}

/* Typography Hierarchy */
h1, h2, h3, h4 { 
  letter-spacing: -0.02em; 
  font-weight: 700; 
  color: var(--text); 
}

h1 { font-size: 2.2rem; }
h2 { font-size: 1.6rem; margin-bottom: 0.75rem; } 
h3 { font-size: 1.25rem; margin-top: 0.75rem; }
hr { border: none; border-top: 1px solid var(--line); margin: 1.75rem 0; }
[data-testid="stCaptionContainer"] { color: var(--muted); }

/* Custom Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--line); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted-dark); }

/* Hero Section */
.hero { 
  padding: 1rem 0 2rem; 
  background: linear-gradient(180deg, rgba(26,36,64,0.4) 0%, rgba(12,18,32,0) 100%);
  border-radius: 16px;
  margin-bottom: 1rem;
}
.hero h1 { 
  font-size: 2.8rem; 
  font-weight: 800; 
  margin: 0.2rem 0 0.5rem; 
  background: linear-gradient(135deg, #ffffff 0%, #a5bbfd 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero p { 
  color: var(--muted); 
  font-size: 1.05rem; 
  max-width: 38rem; 
  margin: 0; 
  line-height: 1.6; 
}
.pill { 
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem; 
  font-weight: 700; 
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--accent);
  background: rgba(124, 156, 255, 0.1); 
  border: 1px solid rgba(124, 156, 255, 0.25);
  padding: 0.3rem 0.8rem; 
  border-radius: 999px; 
  box-shadow: 0 0 12px rgba(124, 156, 255, 0.15);
}

/* Sidebar Navigation Styling */
section[data-testid="stSidebar"] { 
  background: var(--surface); 
  border-right: 1px solid var(--line); 
}

/* Hide radio circles completely across all Streamlit versions */
section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label > div:first-child,
section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label div[class*="st-ae"],
section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label div[class*="st-af"],
section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label input,
section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] label svg {
  display: none !important;
  visibility: hidden !important;
  width: 0 !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

section[data-testid="stSidebar"] [role="radiogroup"] {
  gap: 0.35rem;
}

/* Navigation items container */
section[data-testid="stSidebar"] [role="radiogroup"] label {
  padding: 0.75rem 1rem !important;
  border-radius: 8px !important;
  width: 100% !important;
  cursor: pointer !important;
  border: 1px solid transparent !important;
  border-left: 3px solid transparent !important; /* Space reserved for indicator bar */
  transition: all 0.2s ease !important;
  background: transparent !important;
  margin: 0 !important;
}

/* Hover state */
section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
  background: var(--surface-2) !important;
  color: var(--text) !important;
}

/* Active selected item with single colored indicator bar */
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
  background: var(--surface-2) !important;
  border-left: 3px solid var(--accent) !important;
  border-top-left-radius: 2px !important;
  border-bottom-left-radius: 2px !important;
  box-shadow: none !important;
}

/* Ensure text spans fill the item container cleanly */
section[data-testid="stSidebar"] [role="radiogroup"] label p,
section[data-testid="stSidebar"] [role="radiogroup"] label span {
  color: var(--text) !important;
  font-weight: 600 !important;
  font-size: 0.95rem !important;
  margin: 0 !important;
}

/* Cards (Evidence & Metrics) */
.evidence-card, .metric-card {
  background: linear-gradient(145deg, var(--surface) 0%, var(--surface-2) 100%); 
  border: 1px solid var(--line); 
  border-radius: 14px; 
  padding: 1.25rem; 
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}
.evidence-card:hover, .metric-card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(124, 156, 255, 0.12);
}
.evidence-card { margin-bottom: 0.9rem; }
.evidence-card h4 { font-size: 0.95rem; margin: 0 0 0.4rem; word-break: break-all; }
.evidence-card p { color: var(--muted); font-size: 0.82rem; margin: 0; }
.metric-card { text-align: left; }
.metric-value { 
  font-size: 2.2rem; 
  font-weight: 800; 
  letter-spacing: -0.03em; 
  line-height: 1.1; 
}
.metric-label { 
  color: var(--muted); 
  font-size: 0.82rem; 
  font-weight: 600; 
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.4rem; 
}
.confidence-high { color: var(--ok); text-shadow: 0 0 10px rgba(52, 211, 153, 0.3); } 
.confidence-medium { color: var(--warn); text-shadow: 0 0 10px rgba(251, 191, 36, 0.3); } 
.confidence-low { color: var(--bad); text-shadow: 0 0 10px rgba(248, 113, 113, 0.3); }

/* Verdict Panel */
.verdict { 
  display: flex; 
  align-items: center; 
  gap: 2rem; 
  flex-wrap: wrap;
  background: linear-gradient(135deg, var(--surface) 0%, #17223b 100%); 
  border: 1px solid var(--line); 
  border-radius: 20px;
  padding: 2rem; 
  margin: 1rem 0 1.5rem; 
  border-left: 6px solid var(--tone); 
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
  position: relative;
  overflow: hidden;
}
.verdict::after {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 200%;
  background: radial-gradient(circle, var(--tone) 0%, transparent 70%);
  opacity: 0.06;
  pointer-events: none;
}
.verdict .ring { 
  --p: 0; 
  width: 120px; 
  height: 120px; 
  border-radius: 50%; 
  flex: none;
  background: conic-gradient(var(--tone) calc(var(--p) * 1%), var(--line) 0);
  display: grid; 
  place-items: center; 
  box-shadow: 0 0 20px rgba(0,0,0,0.4);
}
.verdict .ring span { 
  width: 96px; 
  height: 96px; 
  border-radius: 50%; 
  background: var(--bg-deep);
  display: grid; 
  place-items: center; 
  font-size: 1.75rem; 
  font-weight: 800; 
  color: var(--text);
}
.verdict .label { 
  color: var(--muted); 
  font-size: 0.9rem; 
  margin-bottom: 0.5rem; 
}
.verdict .label b { color: var(--text); font-weight: 600; }

/* Assessment Badges */
[class^="assessment-"] { 
  display: inline-block; 
  padding: 0.5rem 1.25rem; 
  border-radius: 999px;
  font-weight: 800; 
  font-size: 1.25rem; 
  letter-spacing: 0.02em;
  border: 1px solid; 
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.assessment-authentic { 
  color: var(--ok); 
  background: var(--ok-glow); 
  border-color: rgba(52, 211, 153, 0.4); 
}
.assessment-manipulated { 
  color: var(--warn); 
  background: var(--warn-glow); 
  border-color: rgba(251, 191, 36, 0.4); 
}
.assessment-coordinated { 
  color: var(--bad); 
  background: var(--bad-glow); 
  border-color: rgba(248, 113, 113, 0.4); 
}
.assessment-insufficient { 
  color: var(--neutral); 
  background: var(--neutral-glow); 
  border-color: rgba(148, 163, 184, 0.4); 
}

/* Disclaimer Box */
.disclaimer { 
  background: rgba(26, 36, 64, 0.6); 
  border-left: 3px solid var(--accent); 
  color: var(--muted);
  padding: 0.9rem 1.1rem; 
  border-radius: 0 10px 10px 0; 
  font-size: 0.85rem; 
  line-height: 1.5; 
}

/* Streamlit Native Widgets Styling Overrides */
[data-testid="stFileUploaderDropzone"] { 
  background: var(--surface); 
  border: 1.5px dashed var(--line);
  border-radius: 14px; 
  transition: all 0.2s ease; 
}
[data-testid="stFileUploaderDropzone"]:hover { 
  border-color: var(--accent); 
  background: var(--surface-2); 
  box-shadow: 0 0 15px rgba(124, 156, 255, 0.1);
}

.stTextArea textarea { 
  background: var(--surface); 
  border: 1px solid var(--line); 
  border-radius: 14px;
  padding: 1rem; 
  font-size: 0.98rem; 
  color: var(--text);
}
.stTextArea textarea:focus { 
  border-color: var(--accent); 
  box-shadow: 0 0 0 3px var(--accent-glow); 
}

[data-testid="stExpander"] { 
  background: var(--surface); 
  border: 1px solid var(--line); 
  border-radius: 14px; 
  overflow: hidden;
}
[data-testid="stExpander"] summary { 
  font-weight: 600; 
  color: var(--text);
  padding: 0.8rem 1rem;
}

[data-testid="stMetric"] { 
  background: var(--surface); 
  border: 1px solid var(--line);
  border-radius: 14px; 
  padding: 1rem 1.2rem; 
}
[data-testid="stMetricLabel"] { color: var(--muted); }

[data-testid="stAlert"] { border-radius: 12px; }

/* Progress bar */
.stProgress > div > div > div > div { 
  background: linear-gradient(90deg, var(--accent) 0%, var(--accent-bright) 100%); 
}

/* Tabs */
button[data-baseweb="tab"] { 
  font-weight: 600; 
  color: var(--muted);
  border-radius: 8px;
  padding: 0.5rem 1rem;
}
button[data-baseweb="tab"][aria-selected="true"] { 
  color: var(--text) !important;
  background: var(--surface-2);
}

/* Buttons */
.stButton > button, .stDownloadButton > button { 
  border-radius: 12px; 
  font-weight: 600;
  border: 1px solid var(--line); 
  background: var(--surface-2); 
  color: var(--text);
  padding: 0.65rem 1.25rem; 
  transition: all 0.2s ease; 
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.stButton > button:hover, .stDownloadButton > button:hover { 
  border-color: var(--accent); 
  background: var(--surface-hover);
  color: #ffffff; 
  box-shadow: 0 4px 15px rgba(124, 156, 255, 0.2);
}
.stButton > button:active { transform: translateY(1px); }

/* Primary Accent Buttons */
.stButton > button[kind="primary"] { 
  background: linear-gradient(135deg, #7c9cff 0%, #587bf6 100%); 
  color: #080d18; 
  font-weight: 700;
  border-color: #8daaff; 
  box-shadow: 0 4px 18px rgba(124, 156, 255, 0.3);
}
.stButton > button[kind="primary"]:hover { 
  filter: brightness(1.1); 
  color: #080d18; 
  box-shadow: 0 6px 22px rgba(124, 156, 255, 0.45);
}
.stButton > button:disabled { opacity: 0.45; cursor: not-allowed; }

:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

@media (max-width: 640px) {
  .hero h1 { font-size: 2.1rem; }
  .verdict { padding: 1.25rem; gap: 1.25rem; }
}
</style>
"""

TONES = {
    'AUTHENTIC': ('var(--ok)', 'assessment-authentic'),
    'MANIPULATED': ('var(--warn)', 'assessment-manipulated'),
    'COORDINATED SYNTHETIC': ('var(--bad)', 'assessment-coordinated'),
    'INSUFFICIENT EVIDENCE': ('var(--neutral)', 'assessment-insufficient'),
}


def inject_theme():
    st.markdown(CSS, unsafe_allow_html=True)


def header_html() -> str:
    return (
        '<div class="hero">'
        '<span class="pill">🔍 Digital Authenticity & Forensic Engine</span>'
        '<h1>TrustLayer</h1>'
        '<p>Submit an investigation claim with multi-modal evidence files. TrustLayer evaluates cross-modal consistency, metadata integrity, and synthetic manipulation signals.</p>'
        '</div>'
    )


def verdict_html(assessment: str, confidence: float, level: str) -> str:
    tone, cls = TONES.get(assessment, TONES['INSUFFICIENT EVIDENCE'])
    return (
        f'<div class="verdict" style="--tone:{tone}">'
        f'<div class="ring" style="--p:{max(0, min(confidence, 100)):.0f}"><span>{confidence:.0f}%</span></div>'
        f'<div><div class="label">System Verdict · <b>{level.title()} Confidence</b></div>'
        f'<div class="{cls}">{assessment.title()}</div></div></div>'
    )


def metric_html(label: str, value: str, caption: str = "", color: str = "var(--text)") -> str:
    cap = f'<div class="metric-label" style="margin:.3rem 0 0; text-transform:none;">{caption}</div>' if caption else ''
    return (
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value" style="color:{color}">{value}</div>{cap}</div>'
    )