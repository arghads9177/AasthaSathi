"""
Chat Interface Component

Advanced chat interface with enhanced features:
- Message rendering with avatars and timestamps
- Source citations with expandable details
- Metadata visualization
- Message feedback and rating
- Copy to clipboard functionality
- Export chat history
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

# Import visualizer
try:
    from components.visualizer import render_response_visualizations, render_metadata_summary
    VISUALIZER_AVAILABLE = True
except ImportError:
    VISUALIZER_AVAILABLE = False


def render_message_avatar(role: str) -> str:
    """
    Get emoji avatar for message role.
    
    Args:
        role: Message role ('user' or 'assistant')
        
    Returns:
        Emoji string for avatar
    """
    avatars = {
        "user": "👤",
        "assistant": "🤖",
        "system": "⚙️"
    }
    return avatars.get(role, "💬")


def format_timestamp(timestamp: str) -> str:
    """
    Format ISO timestamp to readable format.
    
    Args:
        timestamp: ISO format timestamp string
        
    Returns:
        Formatted time string (HH:MM AM/PM)
    """
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%I:%M %p")
    except:
        return ""


def render_message(
    message: Dict[str, Any],
    show_sources: bool = True,
    show_metadata: bool = False,
    enable_feedback: bool = True
) -> None:
    """
    Render a single message with enhanced features.
    
    Args:
        message: Message dictionary with role, content, timestamp, etc.
        show_sources: Whether to show source citations
        show_metadata: Whether to show metadata
        enable_feedback: Whether to enable feedback buttons
    """
    role = message.get("role", "user")
    content = message.get("content", "")
    timestamp = message.get("timestamp", "")
    sources = message.get("sources", [])
    metadata = message.get("metadata", {})
    message_id = message.get("id", timestamp)
    
    with st.chat_message(role):
        # Header with timestamp
        if timestamp:
            time_str = format_timestamp(timestamp)
            if time_str:
                st.caption(f"🕒 {time_str}")
        
        # Main content
        st.markdown(content)
        
        # Additional features for assistant messages
        if role == "assistant":
            col1, col2, col3, col4 = st.columns([1, 1, 1, 8])
            
            # Copy button
            with col1:
                if st.button("📋", key=f"copy_{message_id}", help="Copy response"):
                    st.session_state[f"copied_{message_id}"] = True
                    st.toast("Copied to clipboard!", icon="✅")
            
            # Feedback buttons
            if enable_feedback:
                with col2:
                    if st.button("👍", key=f"like_{message_id}", help="Helpful"):
                        if "feedback" not in st.session_state:
                            st.session_state.feedback = {}
                        st.session_state.feedback[message_id] = "positive"
                        st.toast("Thank you for your feedback!", icon="👍")
                
                with col3:
                    if st.button("👎", key=f"dislike_{message_id}", help="Not helpful"):
                        if "feedback" not in st.session_state:
                            st.session_state.feedback = {}
                        st.session_state.feedback[message_id] = "negative"
                        st.toast("Thank you for your feedback!", icon="👎")
            
            # Show sources if available
            if show_sources and sources:
                with st.expander(f"📚 Sources ({len(sources)})"):
                    for idx, source in enumerate(sources, 1):
                        st.markdown(f"**Source {idx}:**")
                        if isinstance(source, dict):
                            # If source is a dictionary with details
                            st.markdown(f"- **Document:** {source.get('document', 'N/A')}")
                            st.markdown(f"- **Content:** {source.get('content', 'N/A')}")
                            if source.get('score'):
                                st.markdown(f"- **Relevance:** {source['score']:.2%}")
                        else:
                            # If source is a string
                            st.markdown(f"- {source}")
                        st.markdown("---")
            
            # Show metadata if enabled
            if show_metadata and metadata:
                with st.expander("📊 Response Metadata"):
                    # Show visualizations if available
                    if VISUALIZER_AVAILABLE:
                        render_metadata_summary(metadata)
                        st.markdown("---")
                        render_response_visualizations(
                            metadata,
                            sources,
                            compact=True,
                            key_prefix=f"msg_{message_id}"
                        )
                    else:
                        # Fallback to JSON view
                        st.json(metadata)
                    
                    # Full metadata JSON
                    with st.expander("🔍 Raw Metadata"):
                        st.json(metadata)


def render_chat_history(
    messages: List[Dict[str, Any]],
    show_sources: bool = True,
    show_metadata: bool = False,
    enable_feedback: bool = True
) -> None:
    """
    Render complete chat history with all messages.
    
    Args:
        messages: List of message dictionaries
        show_sources: Whether to show source citations
        show_metadata: Whether to show metadata
        enable_feedback: Whether to enable feedback buttons
    """
    for idx, message in enumerate(messages):
        # Add unique ID if not present
        if "id" not in message:
            message["id"] = f"{message.get('timestamp', '')}_{idx}"
        
        render_message(
            message,
            show_sources=show_sources,
            show_metadata=show_metadata,
            enable_feedback=enable_feedback
        )


def render_chat_input(
    placeholder: str = "Type your message...",
    disabled: bool = False,
    examples: Optional[List[str]] = None,
    value: Optional[str] = None,
) -> Optional[str]:
    """
    Render chat input with optional example prompts.
    
    Args:
        placeholder: Input placeholder text
        disabled: Whether input is disabled
        examples: Optional list of example prompts to show
        
    Returns:
        User input text or None
    """
    # If a value is provided (for example: selected example query), return it immediately
    if value:
        return value

    # Show example prompts if provided
    if examples and not st.session_state.messages:
        st.markdown("### 💡 Try asking:")
        cols = st.columns(min(len(examples), 3))

        for idx, example in enumerate(examples[:6]):  # Limit to 6 examples
            col_idx = idx % 3
            with cols[col_idx]:
                if st.button(
                    example,
                    key=f"example_{idx}",
                    use_container_width=True,
                    disabled=disabled
                ):
                    return example

    # Main chat input
    return st.chat_input(placeholder, disabled=disabled)


def export_chat_history(messages: List[Dict[str, Any]], format: str = "json") -> str:
    """
    Export chat history to various formats.
    
    Args:
        messages: List of message dictionaries
        format: Export format ('json', 'text', 'markdown')
        
    Returns:
        Formatted chat history string
    """
    if format == "json":
        return json.dumps(messages, indent=2)
    
    elif format == "text":
        lines = []
        for msg in messages:
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            timestamp = format_timestamp(msg.get("timestamp", ""))
            lines.append(f"[{timestamp}] {role}: {content}\n")
        return "\n".join(lines)
    
    elif format == "markdown":
        lines = ["# Chat History\n"]
        for msg in messages:
            role = msg.get("role", "unknown").title()
            content = msg.get("content", "")
            timestamp = format_timestamp(msg.get("timestamp", ""))
            lines.append(f"## {role} ({timestamp})\n")
            lines.append(f"{content}\n")
            
            # Add sources if available
            if msg.get("sources"):
                lines.append("\n**Sources:**\n")
                for idx, source in enumerate(msg["sources"], 1):
                    lines.append(f"{idx}. {source}\n")
            
            lines.append("\n---\n")
        
        return "\n".join(lines)
    
    else:
        return json.dumps(messages, indent=2)


def render_chat_controls(messages: List[Dict[str, Any]]) -> None:
    """
    Render chat control buttons (clear, export, etc.).
    
    Args:
        messages: Current chat messages
    """
    if not messages:
        return
    
    st.markdown("### 🎛️ Chat Controls")
    
    col1, col2, col3 = st.columns(3)
    
    # Clear chat button
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            if "feedback" in st.session_state:
                st.session_state.feedback = {}
            st.success("Chat cleared!")
            st.rerun()
    
    # Export buttons
    with col2:
        export_format = st.selectbox(
            "Export Format",
            ["JSON", "Text", "Markdown"],
            label_visibility="collapsed"
        )
    
    with col3:
        if st.button("💾 Export", use_container_width=True):
            format_map = {"JSON": "json", "Text": "text", "Markdown": "markdown"}
            exported = export_chat_history(messages, format_map[export_format])
            
            # Trigger download
            st.download_button(
                label=f"📥 Download {export_format}",
                data=exported,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_map[export_format]}",
                mime="application/json" if export_format == "JSON" else "text/plain",
                use_container_width=True
            )


def render_typing_indicator():
    """Display a typing indicator for assistant responses."""
    with st.chat_message("assistant"):
        st.markdown("💭 *Thinking...*")


def get_message_stats(messages: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Get statistics about messages.
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        Dictionary with message statistics
    """
    stats = {
        "total": len(messages),
        "user": sum(1 for m in messages if m.get("role") == "user"),
        "assistant": sum(1 for m in messages if m.get("role") == "assistant"),
        "with_sources": sum(1 for m in messages if m.get("sources")),
        "with_metadata": sum(1 for m in messages if m.get("metadata"))
    }
    
    # Calculate average response length
    assistant_messages = [m for m in messages if m.get("role") == "assistant"]
    if assistant_messages:
        total_length = sum(len(m.get("content", "")) for m in assistant_messages)
        stats["avg_response_length"] = total_length // len(assistant_messages)
    else:
        stats["avg_response_length"] = 0
    
    return stats


def render_chat_stats(messages: List[Dict[str, Any]]) -> None:
    """
    Display chat statistics in sidebar.
    
    Args:
        messages: List of message dictionaries
    """
    if not messages:
        return
    
    stats = get_message_stats(messages)
    
    st.markdown("### 📊 Chat Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Messages", stats["total"])
        st.metric("User Messages", stats["user"])
    
    with col2:
        st.metric("AI Responses", stats["assistant"])
        st.metric("Avg Length", f"{stats['avg_response_length']} chars")
    
    if stats["with_sources"] > 0:
        st.info(f"📚 {stats['with_sources']} responses with sources")
