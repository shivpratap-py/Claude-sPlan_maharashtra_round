"""Visualization helpers for TrustLayer (Plotly + Streamlit)."""

from typing import Dict, Any, List

import networkx as nx
import plotly.graph_objects as go
import streamlit as st

_DARK_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'),
)

_ASSESSMENT_COLORS = {
    'AUTHENTIC': '#10b981',
    'AUTHENTIC_WITH_CONCERNS': '#a3e635',
    'MANIPULATED': '#f59e0b',
    'COORDINATED SYNTHETIC': '#ef4444',
    'INSUFFICIENT EVIDENCE': '#6b7280',
}


def _prob_color(p: float) -> str:
    if p < 0.3:
        return '#10b981'
    if p < 0.6:
        return '#f59e0b'
    return '#ef4444'


def create_evidence_graph(evidence_results: Dict[str, Any],
                          consistency_results: Dict[str, Any]) -> go.Figure:
    """Network graph of the evidence actually analyzed and the final flow."""
    G = nx.Graph()

    modality_nodes = []
    for mod in ['image', 'audio', 'video', 'text', 'document', 'metadata']:
        res = evidence_results.get(mod)
        if isinstance(res, dict) and res.get('status') == 'success':
            G.add_node(mod.upper(), prob=res.get('fake_probability', 0.0))
            modality_nodes.append(mod.upper())

    G.add_node('CLAIM', prob=None)
    G.add_node('CROSS-MODAL', prob=None)

    inconsistencies = consistency_results.get('total_inconsistencies', 0)
    assessment = 'ASSESSMENT'
    G.add_node(assessment, prob=None)

    for node in modality_nodes:
        G.add_edge('CLAIM', node)
        G.add_edge(node, 'CROSS-MODAL')
    if not modality_nodes:
        G.add_edge('CLAIM', 'CROSS-MODAL')
    G.add_edge('CROSS-MODAL', 'ASSESSMENT')

    pos = nx.spring_layout(G, seed=42)

    edge_x, edge_y = [], []
    for src, dst in G.edges():
        x0, y0 = pos[src]
        x1, y1 = pos[dst]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color='#4b5563'),
        hoverinfo='none',
        mode='lines',
    )

    node_x, node_y, node_text, node_color, node_hover = [], [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        prob = G.nodes[node].get('prob')
        if prob is None:
            node_color.append('#60a5fa' if node in ('CLAIM', 'CROSS-MODAL') else '#a78bfa')
            node_hover.append(node)
        else:
            node_color.append(_prob_color(prob))
            node_hover.append(f"{node}: fake probability {prob:.0%}")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition='bottom center',
        hovertext=node_hover,
        hoverinfo='text',
        marker=dict(color=node_color, size=26, line=dict(width=2, color='#e5e7eb')),
    )

    title = 'Evidence Graph'
    if inconsistencies:
        title += f' — {inconsistencies} contradiction(s) detected'

    fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
        title=dict(text=title, font=dict(color='white')),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        **_DARK_LAYOUT,
    ))
    return fig


def create_confidence_gauge(value: float, title: str) -> go.Figure:
    """Gauge chart for a 0-100 score."""
    value = max(0.0, min(float(value), 100.0))
    color = '#10b981' if value >= 70 else ('#f59e0b' if value >= 40 else '#ef4444')

    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=value,
        title={'text': title, 'font': {'color': 'white'}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': 'white'},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 40], 'color': 'rgba(239,68,68,0.15)'},
                {'range': [40, 70], 'color': 'rgba(245,158,11,0.15)'},
                {'range': [70, 100], 'color': 'rgba(16,185,129,0.15)'},
            ],
            'bgcolor': 'rgba(0,0,0,0)',
            'borderwidth': 2,
            'bordercolor': 'gray',
        },
        number={'font': {'color': 'white'}, 'suffix': '%'},
    ))
    fig.update_layout(**_DARK_LAYOUT, margin=dict(t=60, b=10, l=20, r=20))
    return fig


def create_evidence_summary_chart(results: Dict[str, Any]) -> go.Figure:
    """Horizontal bar chart of per-modality fake probabilities."""
    modalities, probs = [], []
    for mod, res in results.items():
        if isinstance(res, dict) and 'fake_probability' in res and res.get('status') == 'success':
            modalities.append(mod.upper())
            probs.append(res['fake_probability'] * 100)

    fig = go.Figure(go.Bar(
        x=probs,
        y=modalities,
        orientation='h',
        marker=dict(color=[_prob_color(p / 100) for p in probs]),
        text=[f'{p:.0f}%' for p in probs],
        textposition='auto',
    ))
    fig.update_layout(
        title=dict(text='Fake Probability by Modality', font=dict(color='white')),
        xaxis=dict(title='Probability (%)', range=[0, 100], showgrid=True, gridcolor='#374151'),
        yaxis=dict(title='Modality', showgrid=False),
        **_DARK_LAYOUT,
    )
    return fig


def render_assessment_card(assessment: str, confidence: float) -> None:
    """Render Streamlit HTML card with colored assessment badge.

    ``confidence`` is expected in the 0-100 range.
    """
    assessment = assessment.upper()
    color = _ASSESSMENT_COLORS.get(assessment, '#6b7280')
    conf = confidence if confidence > 1 else confidence * 100  # tolerate 0-1 inputs
    st.markdown(
        f'<div style="padding:15px; border-radius:8px; background-color:#111827; '
        f'border:1px solid {color}; color:white;">'
        f'<h3 style="margin:0;">Final Assessment: <span style="color:{color}">{assessment}</span></h3>'
        f'<p style="margin:0;">Confidence: {conf:.1f}%</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_evidence_card(modality: str, classification: str,
                         confidence: float, evidence: List[str]) -> None:
    """Render an individual evidence card."""
    conf = confidence if confidence > 1 else confidence * 100
    items = ''.join(f'<li>{e}</li>' for e in evidence) or '<li>No evidence items.</li>'
    st.markdown(
        f'<div style="padding:10px; margin-bottom:10px; border-left:5px solid #22d3ee; '
        f'background-color:#111827; color:white; border-radius:6px;">'
        f'<h4 style="margin:0;">Modality: {modality}</h4>'
        f'<p>Classification: <b>{classification}</b> | Confidence: {conf:.1f}%</p>'
        f'<ul>{items}</ul>'
        f'</div>',
        unsafe_allow_html=True,
    )
