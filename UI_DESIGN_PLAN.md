# AasthaSathi Streamlit UI - Design Plan

## 🎨 UI Design Overview

A modern, user-friendly web interface for the AasthaSathi Banking Assistant that communicates with the REST API.

---

## 🎯 Design Principles

### 1. **User-Friendly**
- Clean, intuitive interface
- Minimal learning curve
- Clear visual hierarchy
- Responsive design

### 2. **Professional & Catchy**
- Banking-appropriate aesthetics
- Aastha brand colors (blues, cyans, whites)
- Modern card-based layout
- Smooth animations and transitions

### 3. **Conversational**
- Chat-style interface (WhatsApp/ChatGPT-like)
- Message history
- User and assistant avatars
- Real-time response feel

### 4. **Informative**
- Show routing decisions (API/RAG/Hybrid)
- Display sources and citations
- Execution metadata visualization
- Clear error messages

---

## 📐 UI Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│  🏦 AasthaSathi - AI Banking Assistant        [Settings ⚙️] │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│  SIDEBAR     │         MAIN CHAT AREA                       │
│              │                                              │
│ 🔐 Login     │  ┌────────────────────────────────────┐     │
│  Username    │  │ 👤 User: List branches in Patna   │     │
│  Password    │  └────────────────────────────────────┘     │
│  [Login]     │                                              │
│              │  ┌────────────────────────────────────┐     │
│ 📊 Status    │  │ 🤖 Assistant:                      │     │
│  ✓ Connected │  │ Here are the branches...           │     │
│              │  │ 📍 Sources: API Data               │     │
│ 💡 Examples  │  │ 🔄 Route: API                      │     │
│  ▶ API       │  └────────────────────────────────────┘     │
│    Queries   │                                              │
│  ▶ RAG       │                                              │
│    Queries   │         ⋮                                    │
│  ▶ Hybrid    │                                              │
│    Queries   │  ┌────────────────────────────────────┐     │
│              │  │ 💬 Type your question...           │     │
│ 🎨 Theme     │  │                            [Send 📤]│     │
│  □ Dark Mode │  └────────────────────────────────────┘     │
│              │                                              │
│ 📜 History   │  [Clear History] [Export Chat]               │
│  [Clear]     │                                              │
│              │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

---

## 🎨 Visual Design Mockup

### Color Scheme (Banking Professional):
```
Primary: #1E3A8A (Deep Blue)
Secondary: #0891B2 (Cyan)
Accent: #10B981 (Success Green)
Background: #F8FAFC (Light Gray)
Card: #FFFFFF (White)
Text: #1F2937 (Dark Gray)
User Message: #DBEAFE (Light Blue)
Assistant Message: #F3F4F6 (Light Gray)
```

### Typography:
- **Headings**: Inter, Sans-serif, Bold
- **Body**: Roboto, Sans-serif, Regular
- **Code/Tech**: Fira Code, Monospace

### Components:

#### 1. **Header Bar**
```
┌─────────────────────────────────────────────────────────┐
│ 🏦 AasthaSathi                              Settings ⚙️  │
│ AI-Powered Banking Assistant                            │
└─────────────────────────────────────────────────────────┘
```

#### 2. **Chat Message (User)**
```
┌──────────────────────────────────────────────┐
│                     👤 You          10:30 AM │
│                                              │
│  List all branches in Patna                  │
└──────────────────────────────────────────────┘
```

#### 3. **Chat Message (Assistant)**
```
┌──────────────────────────────────────────────┐
│ 🤖 AasthaSathi                      10:30 AM │
│                                              │
│ Here are the branches in Patna:              │
│ 1. Main Branch - Address...                 │
│ 2. City Center - Address...                 │
│                                              │
│ ┌──────────────────────────────────────┐    │
│ │ 🔄 Routing: API                      │    │
│ │ 📍 Sources: Banking API              │    │
│ │ ⚡ Response Time: 2.3s               │    │
│ └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

#### 4. **Example Queries Card**
```
┌─────────────────────────────────────────┐
│ 💡 Try these examples                   │
├─────────────────────────────────────────┤
│ 📊 API Queries                          │
│  → List branches in [city]              │
│  → What savings schemes available?      │
│  → Account balance for [number]         │
│                                         │
│ 📚 Knowledge Base                       │
│  → How to open an account?              │
│  → Loan application process             │
│  → Membership eligibility               │
│                                         │
│ 🔄 Hybrid Queries                       │
│  → Show RD schemes and explain them     │
│  → List loans and eligibility criteria  │
└─────────────────────────────────────────┘
```

#### 5. **Login Form**
```
┌─────────────────────────────────┐
│ 🔐 Authentication               │
├─────────────────────────────────┤
│ Username: [____________]        │
│ Password: [____________]        │
│                                 │
│        [Login] 🚀               │
│                                 │
│ Status: 🔴 Not Connected        │
│         🟢 Connected            │
└─────────────────────────────────┘
```

---

## 🏗️ Project Structure

```
ui/
├── __init__.py
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration (API URL, credentials)
├── api_client.py              # REST API client wrapper
├── theme.py                   # Theme configuration
├── requirements.txt           # UI-specific dependencies
│
├── components/
│   ├── __init__.py
│   ├── auth.py                # Authentication component
│   ├── chat.py                # Chat interface
│   ├── examples.py            # Example queries
│   ├── visualizer.py          # Response visualization
│   ├── settings.py            # Settings panel
│   └── sidebar.py             # Sidebar component
│
├── assets/
│   ├── logo.png               # AasthaSathi logo
│   ├── favicon.ico            # Browser favicon
│   └── styles.css             # Custom CSS
│
├── .streamlit/
│   └── config.toml            # Streamlit configuration
│
└── README.md                  # UI documentation
```

---

## 🔧 Technical Stack

### Core:
- **Streamlit** (1.30+) - UI framework
- **requests** - API communication
- **streamlit-chat** - Enhanced chat components

### Visualization:
- **plotly** - Interactive charts
- **streamlit-extras** - Additional UI components

### Utilities:
- **python-dotenv** - Environment management
- **Pillow** - Image handling

---

## 💻 Key Features

### 1. **Authentication Flow**
```python
# Sidebar Login
if not st.session_state.authenticated:
    with st.sidebar:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            # Verify credentials with API
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.password = password
                st.success("✓ Logged in successfully!")
            else:
                st.error("✗ Invalid credentials")
```

### 2. **Chat Interface**
```python
# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "metadata" in message:
            with st.expander("📊 Details"):
                st.json(message["metadata"])

# Input box
if prompt := st.chat_input("Ask me anything about banking..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Call API
    with st.spinner("Thinking..."):
        response = api_client.query(prompt)
    
    # Add assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response["answer"],
        "metadata": response.get("metadata")
    })
```

### 3. **API Client**
```python
class AasthaSathiAPIClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.auth = HTTPBasicAuth(username, password)
    
    def query(self, question, include_sources=True, include_metadata=True):
        response = requests.post(
            f"{self.base_url}/api/v1/query",
            auth=self.auth,
            json={
                "query": question,
                "include_sources": include_sources,
                "include_metadata": include_metadata
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self):
        response = requests.get(f"{self.base_url}/api/v1/health")
        return response.status_code == 200
```

### 4. **Response Visualization**
```python
def display_response_metadata(metadata):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Route", metadata["datasource"].upper())
    
    with col2:
        st.metric("Response Time", f"{metadata['processing_time_ms']/1000:.2f}s")
    
    with col3:
        st.metric("Documents", metadata.get("num_relevant", 0))
    
    # Execution path flowchart
    st.subheader("🔄 Execution Flow")
    flow = " → ".join(metadata["execution_path"])
    st.info(flow)
```

### 5. **Example Queries**
```python
EXAMPLES = {
    "📊 API Queries": [
        "List all branches in Kolkata",
        "What savings schemes are available?",
        "How many members joined in January 2025?"
    ],
    "📚 Knowledge Base": [
        "What are the membership eligibility criteria?",
        "Explain the loan application process",
        "How do I open an account?"
    ],
    "🔄 Hybrid": [
        "Show me all RD schemes and explain how they work",
        "List available loans and their eligibility criteria"
    ]
}

def display_examples():
    st.subheader("💡 Try these examples")
    for category, queries in EXAMPLES.items():
        with st.expander(category):
            for query in queries:
                if st.button(query, key=query):
                    st.session_state.selected_query = query
                    st.rerun()
```

---

## 🎨 Custom Styling

### `.streamlit/config.toml`
```toml
[theme]
primaryColor = "#0891B2"
backgroundColor = "#F8FAFC"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1F2937"
font = "sans serif"

[server]
headless = true
port = 8501
```

### Custom CSS
```python
def load_custom_css():
    st.markdown("""
    <style>
    /* Chat message styling */
    .user-message {
        background-color: #DBEAFE;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    
    .assistant-message {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
    
    /* Custom button styling */
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        padding: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)
```

---

## 📱 Responsive Design

### Mobile-Friendly Features:
- Collapsible sidebar on mobile
- Touch-friendly buttons (min 44x44px)
- Readable font sizes (16px+)
- Vertical layout for small screens

---

## 🚀 User Flow

```
1. User opens app
   ↓
2. Landing page with login form
   ↓
3. Enter credentials → Authenticate
   ↓
4. Main chat interface loads
   ↓
5. User sees:
   - Welcome message
   - Example queries
   - Empty chat area
   ↓
6. User types question OR clicks example
   ↓
7. Query sent to API (loading spinner)
   ↓
8. Response displayed with:
   - Answer text
   - Routing info
   - Sources
   - Metadata
   ↓
9. User can:
   - Ask follow-up
   - Clear history
   - Export chat
   - Logout
```

---

## 🎯 Success Metrics

### User Experience:
- ✅ Login in < 2 seconds
- ✅ Query response display in < 3 seconds (after API response)
- ✅ Smooth animations and transitions
- ✅ No page reloads for chat
- ✅ Clear error messages

### Visual Appeal:
- ✅ Professional banking aesthetic
- ✅ Consistent color scheme
- ✅ Readable typography
- ✅ Intuitive icons and labels
- ✅ Responsive on all devices

---

## 📋 Implementation Phases

### Phase 1: Core Setup (Tasks 1-3)
- Project structure
- Dependencies
- API client

### Phase 2: Authentication (Tasks 4, 6)
- Main layout
- Login form
- Session management

### Phase 3: Chat Interface (Tasks 5, 7)
- Message display
- Query input
- Example queries

### Phase 4: Enhancements (Tasks 8-10)
- Visualizations
- Settings
- Custom theme

### Phase 5: Polish & Testing (Tasks 11-14)
- Error handling
- Session management
- Testing
- Documentation

---

## 🔐 Security Considerations

1. **Credentials Storage**
   - Never store passwords in plain text
   - Use session state (memory only)
   - Clear on logout

2. **API Communication**
   - Use HTTPS in production
   - Timeout requests (60s)
   - Handle connection errors gracefully

3. **Input Validation**
   - Sanitize user inputs
   - Limit query length
   - Prevent injection attacks

---

## 📦 Deployment Options

### Local Development:
```bash
streamlit run ui/app.py
```

### Docker:
```dockerfile
FROM python:3.12-slim
COPY ui/ /app/ui/
WORKDIR /app
RUN pip install -r ui/requirements.txt
CMD ["streamlit", "run", "ui/app.py", "--server.port=8501"]
```

### Cloud Platforms:
- **Streamlit Cloud** - Free hosting
- **Heroku** - Container deployment
- **AWS/Azure** - Full control

---

## 🎉 Expected Result

A beautiful, professional web interface where users can:
- 🔐 Securely authenticate
- 💬 Have natural conversations
- 📊 Get banking information instantly
- 📈 See how queries are processed
- 💾 Manage chat history
- 🎨 Enjoy a modern, responsive design

**Estimated Development Time**: 2-3 days  
**Technologies**: Python, Streamlit, REST API  
**Target Users**: Bank employees, administrators, customers  

---

Ready to implement? Let's start with Phase 1! 🚀
