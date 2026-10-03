"""TrustLayer design system: one CSS injection + small HTML helpers.
Class names from the original app (.evidence-card, .metric-card, .disclaimer,
.assessment-*, .confidence-*) are kept so existing markup picks up the new look."""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

:root{
  --bg:#0c1220; --surface:#131b2e; --surface-2:#1a2440; --line:#26314d;
  --text:#e8ecf8; --muted:#8b97b5; --accent:#7c9cff;
  --ok:#34d399; --warn:#fbbf24; --bad:#f87171; --neutral:#94a3b8;
}
html, body, .stApp, [class*="css"]{ font-family:'Manrope',system-ui,sans-serif; }
.stApp{ background:var(--bg); color:var(--text); }
header[data-testid="stHeader"]{ background:transparent; }
#MainMenu, footer{ visibility:hidden; }
.block-container{ max-width:1100px; padding-top:2.5rem; padding-bottom:4rem; }

h1,h2,h3,h4{ letter-spacing:-0.02em; font-weight:700; color:var(--text); }
h2{ font-size:1.6rem; } h3{ font-size:1.2rem; margin-top:.5rem; }
hr{ border:none; border-top:1px solid var(--line); margin:1.75rem 0; }
[data-testid="stCaptionContainer"]{ color:var(--muted); }

/* Hero */
.hero{ padding:.5rem 0 1.5rem; }
.hero h1{ font-size:2.8rem; font-weight:800; margin:0 0 .4rem; }
.hero p{ color:var(--muted); font-size:1.1rem; max-width:34rem; margin:0; line-height:1.5; }
.pill{ display:inline-block; font-size:.78rem; font-weight:600; color:var(--accent);
  background:rgba(124,156,255,.12); border:1px solid rgba(124,156,255,.3);
  padding:.25rem .7rem; border-radius:999px; margin-bottom:1rem; }

/* Sidebar */
section[data-testid="stSidebar"]{ background:var(--surface); border-right:1px solid var(--line); }
section[data-testid="stSidebar"] [role="radiogroup"]{ gap:.25rem; }
section[data-testid="stSidebar"] [role="radiogroup"] label{
  padding:.55rem .8rem; border-radius:10px; width:100%; cursor:pointer;
  transition:background .15s; }
section[data-testid="stSidebar"] [role="radiogroup"] label:hover{ background:var(--surface-2); }
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){
  background:var(--surface-2); box-shadow:inset 3px 0 0 var(--accent); }
section[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child{ display:none; }

/* Cards */
.evidence-card, .metric-card{
  background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:1.1rem 1.2rem; }
.evidence-card{ margin-bottom:.9rem; }
.evidence-card h4{ font-size:.95rem; margin:0 0 .3rem; word-break:break-all; }
.evidence-card p{ color:var(--muted); font-size:.82rem; margin:0; }
.metric-card{ text-align:left; }
.metric-value{ font-size:2rem; font-weight:800; letter-spacing:-0.03em; line-height:1.1; }
.metric-label{ color:var(--muted); font-size:.85rem; font-weight:500; margin-bottom:.35rem; }
.confidence-high{ color:var(--ok); } .confidence-medium{ color:var(--warn); } .confidence-low{ color:var(--bad); }

/* Verdict */
.verdict{ display:flex; align-items:center; gap:2rem; flex-wrap:wrap;
  background:var(--surface); border:1px solid var(--line); border-radius:20px;
  padding:1.75rem 2rem; margin:1rem 0 1.5rem; border-left:5px solid var(--tone); }
.verdict .ring{ --p:0; width:116px; height:116px; border-radius:50%; flex:none;
  background:conic-gradient(var(--tone) calc(var(--p)*1%), var(--line) 0);
  display:grid; place-items:center; }
.verdict .ring span{ width:92px; height:92px; border-radius:50%; background:var(--surface);
  display:grid; place-items:center; font-size:1.7rem; font-weight:800; }
.verdict .label{ color:var(--muted); font-size:.9rem; margin-bottom:.4rem; }
.verdict .label b{ color:var(--text); font-weight:600; }

/* Assessment badges */
[class^="assessment-"]{ display:inline-block; padding:.45rem 1.1rem; border-radius:999px;
  font-weight:700; font-size:1.25rem; border:1px solid; }
.assessment-authentic{ color:var(--ok); background:rgba(52,211,153,.12); border-color:rgba(52,211,153,.4); }
.assessment-manipulated{ color:var(--warn); background:rgba(251,191,36,.12); border-color:rgba(251,191,36,.4); }
.assessment-coordinated{ color:var(--bad); background:rgba(248,113,113,.12); border-color:rgba(248,113,113,.4); }
.assessment-insufficient{ color:var(--neutral); background:rgba(148,163,184,.12); border-color:rgba(148,163,184,.4); }

/* Disclaimer */
.disclaimer{ background:var(--surface-2); border-left:3px solid var(--accent); color:var(--muted);
  padding:.8rem 1rem; border-radius:0 10px 10px 0; font-size:.85rem; line-height:1.5; }

/* Streamlit widgets */
[data-testid="stFileUploaderDropzone"]{ background:var(--surface); border:1.5px dashed var(--line);
  border-radius:14px; transition:border-color .15s, background .15s; }
[data-testid="stFileUploaderDropzone"]:hover{ border-color:var(--accent); background:var(--surface-2); }
.stTextArea textarea{ background:var(--surface); border:1px solid var(--line); border-radius:14px;
  padding:1rem; font-size:1rem; }
.stTextArea textarea:focus{ border-color:var(--accent); box-shadow:0 0 0 3px rgba(124,156,255,.2); }
[data-testid="stExpander"]{ background:var(--surface); border:1px solid var(--line); border-radius:14px; }
[data-testid="stExpander"] summary{ font-weight:600; }
[data-testid="stMetric"]{ background:var(--surface); border:1px solid var(--line);
  border-radius:14px; padding:1rem 1.2rem; }
[data-testid="stMetricLabel"]{ color:var(--muted); }
[data-testid="stAlert"]{ border-radius:12px; }
.stProgress > div > div > div > div{ background:var(--accent); }
button[data-baseweb="tab"]{ font-weight:600; }

.stButton > button, .stDownloadButton > button{ border-radius:12px; font-weight:600;
  border:1px solid var(--line); background:var(--surface-2); color:var(--text);
  padding:.65rem 1.2rem; transition:border-color .15s, transform .1s; }
.stButton > button:hover, .stDownloadButton > button:hover{ border-color:var(--accent); color:var(--text); }
.stButton > button:active{ transform:translateY(1px); }
.stButton > button[kind="primary"]{ background:var(--accent); color:#0c1220; border-color:var(--accent); }
.stButton > button[kind="primary"]:hover{ filter:brightness(1.08); color:#0c1220; }
.stButton > button:disabled{ opacity:.45; }
:focus-visible{ outline:2px solid var(--accent); outline-offset:2px; }

@media (max-width:640px){
  .hero h1{ font-size:2.1rem; }
  .verdict{ padding:1.25rem; gap:1.25rem; }
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
        '<div class="hero"><span class="pill">Digital authenticity investigation</span>'
        '<h1>TrustLayer</h1>'
        '<p>Add a claim and the evidence behind it. TrustLayer checks whether the files '
        'agree with each other and with the claim.</p></div>'
    )


def verdict_html(assessment: str, confidence: float, level: str) -> str:
    tone, cls = TONES.get(assessment, TONES['INSUFFICIENT EVIDENCE'])
    return (
        f'<div class="verdict" style="--tone:{tone}">'
        f'<div class="ring" style="--p:{max(0, min(confidence, 100)):.0f}"><span>{confidence:.0f}%</span></div>'
        f'<div><div class="label">Assessment · <b>{level.title()} confidence</b></div>'
        f'<div class="{cls}">{assessment.title()}</div></div></div>'
    )


def metric_html(label: str, value: str, caption: str = "", color: str = "var(--text)") -> str:
    cap = f'<div class="metric-label" style="margin:.3rem 0 0">{caption}</div>' if caption else ''
    return (
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value" style="color:{color}">{value}</div>{cap}</div>'
    )
