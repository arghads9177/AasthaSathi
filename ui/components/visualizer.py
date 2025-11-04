"""
Response Visualizer Component

Creates interactive visualizations for query responses:
- Routing decision flow diagrams
- Execution path timelines
- Performance metrics charts
- Source attribution visualizations
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional
from datetime import datetime


def create_routing_diagram(metadata: Dict[str, Any]) -> Optional[go.Figure]:
    """
    Create a flow diagram showing the routing decision.
    
    Args:
        metadata: Response metadata containing routing information
        
    Returns:
        Plotly figure object or None
    """
    route = metadata.get("route", "Unknown")
    query_type = metadata.get("query_type", "Unknown")
    
    # Define routing paths
    routing_paths = {
        "api": ["Query Input", "Router Analysis", "API Agent", "Response"],
        "rag": ["Query Input", "Router Analysis", "RAG Agent", "Vector Search", "Response"],
        "hybrid": ["Query Input", "Router Analysis", "Hybrid Agent", "API + RAG", "Response"],
        "unknown": ["Query Input", "Router Analysis", "Default Handler", "Response"]
    }
    
    path = routing_paths.get(route.lower(), routing_paths["unknown"])
    
    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=path,
            color=["#0891B2", "#06B6D4", "#22D3EE", "#67E8F9", "#A5F3FC"][:len(path)]
        ),
        link=dict(
            source=list(range(len(path) - 1)),
            target=list(range(1, len(path))),
            value=[1] * (len(path) - 1),
            color=["rgba(8, 145, 178, 0.4)"] * (len(path) - 1)
        )
    )])
    
    fig.update_layout(
        title=f"Query Routing Path: {route.upper()}",
        font=dict(size=12),
        height=300,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    return fig


def create_execution_timeline(metadata: Dict[str, Any]) -> Optional[go.Figure]:
    """
    Create a timeline visualization of execution steps.
    
    Args:
        metadata: Response metadata with timing information
        
    Returns:
        Plotly figure object or None
    """
    execution_time = metadata.get("execution_time", 0)
    route = metadata.get("route", "Unknown")
    
    # Estimate step times (in seconds)
    if route.lower() == "api":
        steps = [
            {"step": "Routing", "start": 0, "duration": 0.1},
            {"step": "API Call", "start": 0.1, "duration": execution_time * 0.8},
            {"step": "Processing", "start": 0.1 + execution_time * 0.8, "duration": execution_time * 0.1}
        ]
    elif route.lower() == "rag":
        steps = [
            {"step": "Routing", "start": 0, "duration": 0.1},
            {"step": "Embedding", "start": 0.1, "duration": execution_time * 0.2},
            {"step": "Vector Search", "start": 0.1 + execution_time * 0.2, "duration": execution_time * 0.3},
            {"step": "LLM Generation", "start": 0.1 + execution_time * 0.5, "duration": execution_time * 0.4}
        ]
    else:  # hybrid
        steps = [
            {"step": "Routing", "start": 0, "duration": 0.1},
            {"step": "Parallel Execution", "start": 0.1, "duration": execution_time * 0.7},
            {"step": "Merging Results", "start": 0.1 + execution_time * 0.7, "duration": execution_time * 0.2}
        ]
    
    # Create Gantt-style timeline
    fig = go.Figure()
    
    colors = ["#0891B2", "#06B6D4", "#22D3EE", "#67E8F9"]
    
    for idx, step in enumerate(steps):
        fig.add_trace(go.Bar(
            name=step["step"],
            x=[step["duration"]],
            y=[step["step"]],
            orientation='h',
            marker=dict(color=colors[idx % len(colors)]),
            text=[f"{step['duration']:.2f}s"],
            textposition='inside',
            hovertemplate=f"<b>{step['step']}</b><br>Duration: {step['duration']:.2f}s<extra></extra>"
        ))
    
    fig.update_layout(
        title=f"Execution Timeline (Total: {execution_time:.2f}s)",
        xaxis_title="Time (seconds)",
        yaxis_title="",
        showlegend=False,
        height=250,
        margin=dict(l=10, r=10, t=40, b=40),
        barmode='stack'
    )
    
    return fig


def create_metrics_chart(metadata: Dict[str, Any]) -> Optional[go.Figure]:
    """
    Create a metrics visualization showing performance stats.
    
    Args:
        metadata: Response metadata with performance metrics
        
    Returns:
        Plotly figure object or None
    """
    metrics = []
    values = []
    
    # Extract available metrics
    if "execution_time" in metadata:
        metrics.append("Execution Time (s)")
        values.append(metadata["execution_time"])
    
    if "tokens_used" in metadata:
        metrics.append("Tokens Used")
        values.append(metadata["tokens_used"])
    
    if "sources_count" in metadata:
        metrics.append("Sources Found")
        values.append(metadata["sources_count"])
    
    if "confidence_score" in metadata:
        metrics.append("Confidence (%)")
        values.append(metadata["confidence_score"] * 100)
    
    if not metrics:
        return None
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=metrics,
            y=values,
            marker_color=['#0891B2', '#06B6D4', '#22D3EE', '#67E8F9'][:len(metrics)],
            text=values,
            texttemplate='%{text:.2f}',
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Performance Metrics",
        xaxis_title="Metric",
        yaxis_title="Value",
        height=300,
        margin=dict(l=10, r=10, t=40, b=60),
        showlegend=False
    )
    
    return fig


def create_source_distribution(sources: List[Any]) -> Optional[go.Figure]:
    """
    Create a visualization of source distribution.
    
    Args:
        sources: List of source documents
        
    Returns:
        Plotly figure object or None
    """
    if not sources:
        return None
    
    # Count sources by type or document
    source_counts = {}
    
    for source in sources:
        if isinstance(source, dict):
            doc_name = source.get("document", "Unknown")
            source_counts[doc_name] = source_counts.get(doc_name, 0) + 1
        else:
            # If source is a string, try to extract document name
            doc_name = str(source)[:30] + "..." if len(str(source)) > 30 else str(source)
            source_counts[doc_name] = source_counts.get(doc_name, 0) + 1
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(source_counts.keys()),
        values=list(source_counts.values()),
        hole=0.3,
        marker=dict(colors=['#0891B2', '#06B6D4', '#22D3EE', '#67E8F9', '#A5F3FC'])
    )])
    
    fig.update_layout(
        title=f"Source Distribution ({len(sources)} total)",
        height=300,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    return fig


def create_confidence_gauge(metadata: Dict[str, Any]) -> Optional[go.Figure]:
    """
    Create a gauge chart for confidence score.
    
    Args:
        metadata: Response metadata with confidence score
        
    Returns:
        Plotly figure object or None
    """
    confidence = metadata.get("confidence_score", 0)
    
    if confidence == 0:
        return None
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=confidence * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Confidence Score"},
        delta={'reference': 80},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#0891B2"},
            'steps': [
                {'range': [0, 50], 'color': "#FEE2E2"},
                {'range': [50, 75], 'color': "#FEF3C7"},
                {'range': [75, 100], 'color': "#D1FAE5"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    return fig


def render_response_visualizations(
    metadata: Dict[str, Any],
    sources: List[Any],
    compact: bool = False,
    key_prefix: str = "viz"
) -> None:
    """
    Render all response visualizations.
    
    Args:
        metadata: Response metadata
        sources: List of source documents
        compact: If True, show compact view with fewer charts
        key_prefix: Unique prefix for chart keys
    """
    if not metadata and not sources:
        st.info("No visualization data available")
        return
    
    st.markdown("### 📊 Response Visualization")
    
    if compact:
        # Compact view - 2 columns
        col1, col2 = st.columns(2)
        
        with col1:
            # Routing diagram
            routing_fig = create_routing_diagram(metadata)
            if routing_fig:
                st.plotly_chart(routing_fig, use_container_width=True, key=f"{key_prefix}_routing_compact")
        
        with col2:
            # Metrics chart
            metrics_fig = create_metrics_chart(metadata)
            if metrics_fig:
                st.plotly_chart(metrics_fig, use_container_width=True, key=f"{key_prefix}_metrics_compact")
    
    else:
        # Full view - multiple sections
        
        # Row 1: Routing and Timeline
        col1, col2 = st.columns(2)
        
        with col1:
            routing_fig = create_routing_diagram(metadata)
            if routing_fig:
                st.plotly_chart(routing_fig, use_container_width=True, key=f"{key_prefix}_routing_full")
        
        with col2:
            timeline_fig = create_execution_timeline(metadata)
            if timeline_fig:
                st.plotly_chart(timeline_fig, use_container_width=True, key=f"{key_prefix}_timeline_full")
        
        # Row 2: Metrics and Sources
        col3, col4 = st.columns(2)
        
        with col3:
            metrics_fig = create_metrics_chart(metadata)
            if metrics_fig:
                st.plotly_chart(metrics_fig, use_container_width=True, key=f"{key_prefix}_metrics_full")
        
        with col4:
            if sources:
                source_fig = create_source_distribution(sources)
                if source_fig:
                    st.plotly_chart(source_fig, use_container_width=True, key=f"{key_prefix}_sources_full")
            else:
                confidence_fig = create_confidence_gauge(metadata)
                if confidence_fig:
                    st.plotly_chart(confidence_fig, use_container_width=True, key=f"{key_prefix}_confidence_full")


def render_metadata_summary(metadata: Dict[str, Any]) -> None:
    """
    Render a text summary of metadata.
    
    Args:
        metadata: Response metadata
    """
    if not metadata:
        return
    
    st.markdown("#### 📋 Metadata Summary")
    
    cols = st.columns(4)
    
    with cols[0]:
        route = metadata.get("route", "N/A")
        st.metric("Route", route.upper())
    
    with cols[1]:
        exec_time = metadata.get("execution_time", 0)
        st.metric("Execution Time", f"{exec_time:.2f}s")
    
    with cols[2]:
        provider = metadata.get("provider", "N/A")
        st.metric("Provider", provider.title())
    
    with cols[3]:
        model = metadata.get("model", "N/A")
        if len(model) > 15:
            model = model[:12] + "..."
        st.metric("Model", model)
