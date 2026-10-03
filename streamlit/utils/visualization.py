import plotly.graph_objects as go
import networkx as nx
import streamlit as st
from typing import dict, Any, List

def create_evidence_graph(evidence_results: dict, consistency_results: dict) -> go.Figure:
    """Create a network graph showing evidence relationships."""
    G = nx.Graph()
    
    # Adding nodes (simplified placeholder implementation for required nodes)
    nodes = ['CLAIM', 'IMAGE', 'AUDIO', 'VIDEO', 'TEXT', 'CROSS-MODAL', 'ASSESSMENT']
    for node in nodes:
        G.add_node(node)
        
    G.add_edge('CLAIM', 'TEXT', color='gray')
    G.add_edge('CLAIM', 'IMAGE', color='green')
    G.add_edge('CLAIM', 'ASSESSMENT', color='gray')
    
    pos = nx.spring_layout(G)
    
    edge_x = []
    edge_y = []
    edge_colors = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_colors.append(edge[2].get('color', 'gray'))
        
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='gray'),
        hoverinfo='none',
        mode='lines')
        
    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=list(G.nodes()),
        textposition="bottom center",
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color='lightblue',
            size=20,
            line_width=2))
            
    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='Evidence Graph',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
    return fig

def create_confidence_gauge(confidence: float, label: str) -> go.Figure:
    """Circular gauge 0-100."""
    val = confidence * 100
    color = "red" if val < 34 else "yellow" if val < 67 else "green"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        title={'text': label, 'font': {'color': 'white'}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "gray",
        },
        number={'font': {'color': 'white'}}
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    return fig

def create_evidence_summary_chart(results: dict) -> go.Figure:
    """Horizontal bar chart of per-modality fake probabilities."""
    modalities = []
    probs = []
    
    for mod, res in results.items():
        if isinstance(res, dict) and 'fake_probability' in res:
            modalities.append(mod)
            probs.append(res['fake_probability'] * 100)
            
    fig = go.Figure(go.Bar(
        x=probs,
        y=modalities,
        orientation='h',
        marker=dict(color=['red' if p > 50 else 'green' for p in probs])
    ))
    
    fig.update_layout(
        title='Fake Probabilities by Modality',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(title='Probability (%)', range=[0, 100], showgrid=True, gridcolor='gray'),
        yaxis=dict(title='Modality', showgrid=False)
    )
    return fig

def render_assessment_card(assessment: str, confidence: float):
    """Render Streamlit HTML card with colored assessment badge."""
    colors = {
        'AUTHENTIC': 'green',
        'MANIPULATED': 'orange',
        'COORDINATED SYNTHETIC': 'red',
        'INSUFFICIENT EVIDENCE': 'gray'
    }
    color = colors.get(assessment.upper(), 'gray')
    
    html = f"""
    <div style="padding:15px; border-radius:5px; background-color: #333; color: white;">
        <h3>Final Assessment: <span style="color:{color}">{assessment.upper()}</span></h3>
        <p>Confidence: {confidence*100:.1f}%</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_evidence_card(modality: str, classification: str, confidence: float, evidence: List[str]):
    """Render individual evidence card."""
    html = f"""
    <div style="padding:10px; margin-bottom: 10px; border-left: 5px solid cyan; background-color: #222; color: white;">
        <h4>Modality: {modality}</h4>
        <p>Classification: <b>{classification}</b> | Confidence: {confidence*100:.1f}%</p>
        <ul>
            {"".join(f"<li>{e}</li>" for e in evidence)}
        </ul>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
