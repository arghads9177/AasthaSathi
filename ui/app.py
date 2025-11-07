"""
AasthaSathi - AI Banking Assistant
Main Streamlit Application

Provides an intelligent chat interface for banking queries with authentication,
multi-modal responses (API/RAG/Hybrid), and comprehensive visualizations.
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from config import (
    APP_TITLE,
    APP_ICON,
    PAGE_LAYOUT,
    AASTHASATHI_API_URL,
    AASTHASATHI_API_USERNAME,
    AASTHASATHI_API_PASSWORD,
    MYAASTHA_LOGIN_URL,
    MYAASTHA_AUTH_TOKEN,
    REQUEST_TIMEOUT
)
from api_client import AasthaSathiAPIClient
from components.chat import (
    render_chat_history,
    render_chat_input,
    render_chat_controls,
    render_chat_stats,
    render_typing_indicator
)
from components.multilingual import (
    render_language_selector,
    render_language_detection_indicator,
    render_multilingual_examples,
    get_text,
    get_language_name
)

# Configure page - MUST be first Streamlit command
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=PAGE_LAYOUT,
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize all session state variables."""
    
    # API Client
    if "api_client" not in st.session_state:
        st.session_state.api_client = AasthaSathiAPIClient(
            api_base_url=AASTHASATHI_API_URL,
            api_username=AASTHASATHI_API_USERNAME,
            api_password=AASTHASATHI_API_PASSWORD,
            myaastha_login_url=MYAASTHA_LOGIN_URL,
            myaastha_auth_token=MYAASTHA_AUTH_TOKEN,
            timeout=REQUEST_TIMEOUT
        )
    
    # Authentication state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    
    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Settings
    if "show_sources" not in st.session_state:
        st.session_state.show_sources = True
    
    if "show_metadata" not in st.session_state:
        st.session_state.show_metadata = False
    
    if "query_type" not in st.session_state:
        st.session_state.query_type = "Auto"  # Auto, API, RAG, Hybrid
    
    # Multilingual settings (Phase 3)
    if "preferred_language" not in st.session_state:
        st.session_state.preferred_language = "en"  # Default to English
    
    if "last_detected_language" not in st.session_state:
        st.session_state.last_detected_language = None
    
    if "last_detection_confidence" not in st.session_state:
        st.session_state.last_detection_confidence = None
    
    # Connection status
    if "api_connected" not in st.session_state:
        st.session_state.api_connected = None


def render_sidebar():
    """Render the sidebar with branding, authentication, and navigation."""
    
    with st.sidebar:
        # Header with branding
        st.markdown(f"# {APP_ICON} AasthaSathi")
        st.markdown("### AI Banking Assistant")
        st.markdown("---")
        
        # Authentication Section
        if not st.session_state.authenticated:
            st.markdown("### 🔐 Login")
            
            with st.form("login_form"):
                userid = st.text_input("User ID", placeholder="Enter your user ID")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submit_button = st.form_submit_button("Login", use_container_width=True)
                
                if submit_button:
                    if userid and password:
                        with st.spinner("Authenticating..."):
                            success, user_data, error = st.session_state.api_client.login_myaastha(
                                userid, password
                            )
                            
                            if success:
                                st.session_state.authenticated = True
                                st.session_state.user_info = user_data
                                st.success(f"Welcome, {user_data['name']}!")
                                st.rerun()
                            else:
                                st.error(f"❌ {error}")
                    else:
                        st.warning("Please enter both User ID and Password")
        
        else:
            # User Profile
            user = st.session_state.user_info
            st.markdown("### 👤 User Profile")
            
            # Display profile image if available
            if user.get("imageUrl"):
                st.image(user["imageUrl"], width=100)
            
            st.markdown(f"**Name:** {user['name']}")
            st.markdown(f"**User ID:** {user['userid']}")
            st.markdown(f"**Role:** {user['role']}")
            
            if user.get("userat"):
                st.markdown(f"**Location:** {user['userat']}")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.api_client.logout()
                st.session_state.authenticated = False
                st.session_state.user_info = None
                st.session_state.messages = []
                st.success("Logged out successfully!")
                st.rerun()
            
            st.markdown("---")
            
            # Language Settings (Phase 3 - Multilingual)
            st.markdown(f"### {get_text('language_selector', st.session_state.preferred_language)}")
            new_language = render_language_selector(st.session_state.preferred_language)
            
            # Update language preference if changed
            if new_language != st.session_state.preferred_language:
                st.session_state.preferred_language = new_language
                st.success(f"Language changed to {get_language_name(new_language, new_language)}")
                st.rerun()
            
            st.markdown("---")
            
            # Query Settings
            st.markdown("### ⚙️ Query Settings")
            
            st.session_state.query_type = st.selectbox(
                "Query Type",
                ["Auto", "API", "RAG", "Hybrid"],
                help="Auto: Let system decide | API: Code-based | RAG: Document-based | Hybrid: Both"
            )
            
            st.session_state.show_sources = st.checkbox(
                "Show Sources",
                value=st.session_state.show_sources,
                help="Display source documents for RAG responses"
            )
            
            st.session_state.show_metadata = st.checkbox(
                "Show Metadata",
                value=st.session_state.show_metadata,
                help="Display routing and execution metadata"
            )
            
            st.markdown("---")
            
            # Multilingual Example Queries (Phase 3)
            selected_example = render_multilingual_examples(st.session_state.preferred_language)
            if selected_example:
                # Store selected example in session state for the chat input
                st.session_state.example_query = selected_example
                st.rerun()
            
            st.markdown("---")
            
            # Chat Statistics
            render_chat_stats(st.session_state.messages)
            
            st.markdown("---")
            
            # Chat Controls
            render_chat_controls(st.session_state.messages)
        
        st.markdown("---")
        
        # API Connection Status
        st.markdown("### 🔌 Connection Status")
        check_connection_status()


def check_connection_status():
    """Check and display API connection status."""
    
    if st.button("🔄 Check Connection", use_container_width=True):
        with st.spinner("Checking..."):
            is_healthy, health_data, error = st.session_state.api_client.health_check()
            st.session_state.api_connected = is_healthy
            
            if is_healthy:
                st.success("✅ API Connected")
                with st.expander("Health Details"):
                    st.json(health_data)
            else:
                st.error(f"❌ API Disconnected\n\n{error}")
    
    # Display cached status
    if st.session_state.api_connected is not None:
        if st.session_state.api_connected:
            st.success("✅ Connected")
        else:
            st.error("❌ Disconnected")


def render_main_area():
    """Render the main chat area."""
    
    # Page title
    st.title(f"{APP_ICON} AasthaSathi AI Assistant")
    
    # Check authentication
    if not st.session_state.authenticated:
        # Welcome screen for unauthenticated users
        st.markdown("""
        ## Welcome to AasthaSathi! 👋
        
        **AasthaSathi** is your intelligent AI banking assistant powered by advanced language models.
        
        ### Features:
        - 🤖 **Smart Query Routing**: Automatically determines the best way to answer your question
        - 📚 **Document Search**: Access information from banking manuals and documentation
        - 💻 **API Integration**: Real-time data from banking systems
        - 🔄 **Hybrid Responses**: Combines multiple sources for comprehensive answers
        - 📊 **Visualizations**: Interactive charts and insights
        
        ### Getting Started:
        1. **Login** using your MyAastha credentials in the sidebar
        2. **Ask questions** about banking operations, procedures, or policies
        3. **View sources** and metadata to understand how answers are generated
        
        ---
        
        **Please login to continue →**
        """)
        
        # Display connection status
        st.info("💡 **Tip**: Check the connection status in the sidebar before logging in")
        
    else:
        # Chat interface for authenticated users
        render_chat_interface()


def render_chat_interface():
    """Render the chat interface with message history and input."""
    
    # Example queries for first-time users
    example_queries = [
        "What are the loan types available?",
        "What are the steps to create an RD account?",
        "What is the interest rate for fixed deposits?",
        "Explain the KYC process",
        "What are the banking hours?",
        "How can I apply for membership?"
    ]
    
    # Check if we need to process the last user message
    if (st.session_state.messages and 
        st.session_state.messages[-1]["role"] == "user" and
        not st.session_state.get("processing_response", False)):
        
        # Set processing flag
        st.session_state.processing_response = True
        
        # Get the last user message
        user_message = st.session_state.messages[-1]
        prompt = user_message["content"]
        
        # Display chat history up to user message
        render_chat_history(
            st.session_state.messages,
            show_sources=st.session_state.show_sources,
            show_metadata=st.session_state.show_metadata,
            enable_feedback=True
        )
        
        # Show typing indicator
        with st.spinner("🤔 Thinking..."):
            # Determine query type
            query_type = None if st.session_state.query_type == "Auto" else st.session_state.query_type.lower()
            
            # Query the API with language preference
            success, response, error = st.session_state.api_client.query(
                question=prompt,
                query_type=query_type,
                language=st.session_state.preferred_language,  # Phase 3 - Multilingual
                metadata={
                    "user_id": st.session_state.user_info["userid"],
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            if success:
                # Extract response data
                answer = response.get("answer", "No answer available")
                sources = response.get("sources", [])
                metadata = response.get("metadata", {})
                
                # Store language detection info (Phase 3 - Multilingual)
                if "detected_language" in metadata:
                    st.session_state.last_detected_language = metadata["detected_language"]
                    st.session_state.last_detection_confidence = metadata.get("detection_confidence", 0.0)
                
                # Add assistant message to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "metadata": metadata,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                # Add error message to chat
                error_msg = f"❌ **Error**: {error}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Clear processing flag
        st.session_state.processing_response = False
        
        # Rerun to display assistant response
        st.rerun()
    
    else:
        # Display normal chat history
        render_chat_history(
            st.session_state.messages,
            show_sources=st.session_state.show_sources,
            show_metadata=st.session_state.show_metadata,
            enable_feedback=True
        )
        
        # Show language detection indicator if available (Phase 3 - Multilingual)
        if (st.session_state.last_detected_language and 
            st.session_state.last_detection_confidence and
            len(st.session_state.messages) > 0):
            render_language_detection_indicator(
                detected_language=st.session_state.last_detected_language,
                confidence=st.session_state.last_detection_confidence,
                user_language=st.session_state.preferred_language
            )
    
    # Chat input with examples
    # Check if an example query was selected (Phase 3 - Multilingual)
    input_value = st.session_state.pop("example_query", None)
    
    prompt = render_chat_input(
        placeholder="Ask me anything about banking operations...",
        disabled=st.session_state.get("processing_response", False),
        examples=example_queries if len(st.session_state.messages) == 0 else None,
        value=input_value
    )
    
    # Process user input
    if prompt:
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })
        
        # Rerun to display user message before processing
        st.rerun()


def main():
    """Main application entry point."""
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render main area
    render_main_area()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "AasthaSathi v1.0 | Powered by Advanced AI | "
        f"© {datetime.now().year} MyAastha"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
