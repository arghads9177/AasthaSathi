# AasthaSathi UI - User Interface Documentation

**Version:** 1.0.0  
**Framework:** Streamlit 1.51.0  
**Status:** ✅ Production Ready (100% Tests Passed)

A modern, interactive web interface for the AasthaSathi multi-provider LLM fallback system with MyAastha banking integration.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Components](#-components)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Deployment](#-deployment)
- [API Reference](#-api-reference)

---

## ✨ Features

### Core Features
- 🔐 **MyAastha Authentication** - Secure login with banking credentials
- 💬 **Interactive Chat Interface** - Real-time conversations with AI assistant
- 📊 **Response Visualizations** - Interactive Plotly charts for metadata
- 🎯 **Query Type Selection** - API-only, RAG-only, or Hybrid routing
- 📚 **Source Citations** - Document sources displayed with responses
- 💾 **Export Chat History** - JSON, Text, and Markdown formats
- 🎨 **Custom Theme** - Aastha brand colors and professional design

### Advanced Features
- 👍👎 **Response Feedback** - Rate assistant responses
- 📋 **Copy to Clipboard** - Quick copy for any message
- 📈 **Chat Statistics** - Track conversations and response metrics
- 🔄 **Session Management** - Persistent chat history during session
- ⚡ **Error Handling** - Graceful degradation with user-friendly messages
- 🌐 **Multi-Provider LLM** - Fallback across OpenAI, Groq, Gemini

---

## 🏗️ Architecture

```
ui/
├── app.py                      # Main Streamlit application entry point
├── config.py                   # Configuration and environment variables
├── api_client.py              # API wrapper for backend communication
├── __init__.py
├── components/
│   ├── __init__.py
│   ├── chat.py                # Chat interface and message display
│   └── visualizer.py          # Plotly visualizations for metadata
├── .streamlit/
│   └── config.toml            # Streamlit theme and UI configuration
├── test_integration.py        # Integration test suite
├── INTEGRATION_TEST_REPORT.md # Test results and validation
└── README.md                  # This documentation file
```

### Data Flow

```
User Login (MyAastha) → Authentication → User Profile Stored
                                              ↓
User Query → API Client → AasthaSathi API → LLM Processing
                                              ↓
Response with Metadata → Visualizer → Display to User
```

---

## 📦 Prerequisites

### System Requirements
- **Python:** 3.12 or higher
- **Operating System:** Linux, macOS, or Windows
- **RAM:** Minimum 2GB available
- **Network:** Internet connection for API access

### Required Services
- **AasthaSathi API Server** running at `http://localhost:8000`
- **MyAastha Banking API** accessible at `https://web.myaastha.in`

### Environment Variables
```bash
# Required
BANKING_AUTH_KEY="QUFzdDhAOmNCMW5L"  # MyAastha Bearer token

# Optional (defaults provided)
AASTHASATHI_API_URL="http://localhost:8000"
AASTHASATHI_API_USERNAME="aastha_admin"
AASTHASATHI_API_PASSWORD="aastha_secure_2025"
MYAASTHA_LOGIN_URL="https://web.myaastha.in/cobankapi/api/user/signin"
```

---

## 🚀 Installation

### Step 1: Clone Repository
```bash
cd /path/to/AasthaSathi
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### Step 3: Install Dependencies

Using **uv** (recommended):
```bash
uv pip install streamlit plotly pandas requests streamlit-chat python-dotenv
```

Or using **pip**:
```bash
pip install streamlit plotly pandas requests streamlit-chat python-dotenv
```

### Step 4: Verify Installation
```bash
# Check Streamlit version
streamlit --version
# Should show: Streamlit, version 1.51.0

# Check Python version
python --version
# Should show: Python 3.12.x or higher
```

---

## ⚙️ Configuration

### Environment Setup

Create or update `.env` file in project root:
```bash
# MyAastha Authentication
BANKING_AUTH_KEY="QUFzdDhAOmNCMW5L"

# AasthaSathi API Configuration
AASTHASATHI_API_URL="http://localhost:8000"
AASTHASATHI_API_USERNAME="aastha_admin"
AASTHASATHI_API_PASSWORD="aastha_secure_2025"

# MyAastha Login Endpoint
MYAASTHA_LOGIN_URL="https://web.myaastha.in/cobankapi/api/user/signin"
```

### Theme Configuration

Theme is configured in `ui/.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#0891B2"      # Aastha cyan
backgroundColor = "#FFFFFF"    # White
secondaryBackgroundColor = "#F8FAFC"  # Light gray
textColor = "#1E293B"         # Dark slate
font = "sans serif"

[server]
port = 8501
headless = false
```

### API Client Configuration

Configuration in `ui/config.py`:
- **API Timeout:** 30 seconds
- **Request Timeout:** 30 seconds
- **Retry Logic:** Automatic connection retries
- **Error Handling:** Graceful degradation

---

## 🎯 Usage

### Starting the Application

#### Method 1: Start Both Servers (Recommended)

**Terminal 1 - Start API Server:**
```bash
cd /path/to/AasthaSathi
source .venv/bin/activate
python main.py
# API will run at http://localhost:8000
```

**Terminal 2 - Start Streamlit UI:**
```bash
cd /path/to/AasthaSathi
source .venv/bin/activate
streamlit run ui/app.py
# UI will open at http://localhost:8501
```

#### Method 2: Background API Server
```bash
cd /path/to/AasthaSathi
source .venv/bin/activate

# Start API in background
nohup python main.py > api.log 2>&1 &

# Start Streamlit UI
streamlit run ui/app.py
```

### First Time Setup

1. **Open Browser** - Navigate to `http://localhost:8501`
2. **Login** - Enter MyAastha credentials in sidebar
   - User ID: Your 10-digit mobile number
   - Password: Your MyAastha password
3. **Verify Connection** - Check for green "Connected" indicator
4. **Start Chatting** - Ask questions or use example queries

### Using the Interface

#### 1. Authentication
```
Sidebar → Enter User ID → Enter Password → Click "Login"
```
- **Success:** User profile displays with name and email
- **Failure:** Error message shown with details

#### 2. Asking Questions

**Quick Start with Examples:**
- Click any example query button
- Questions are pre-filled in input box
- Press Enter or click submit

**Custom Questions:**
- Type your question in the chat input
- Press Enter or click send button
- Wait for response (typically 10-15 seconds)

**Example Queries:**
- "What are the different types of loans available?"
- "How can I open a Recurring Deposit (RD) account?"
- "What are the current Fixed Deposit (FD) interest rates?"
- "Explain the KYC process for new members"
- "What are the bank's operating hours?"
- "How do I become a member of the bank?"

#### 3. Response Features

**Copy Message:**
- Click 📋 icon next to any message
- Content copied to clipboard

**Provide Feedback:**
- Click 👍 for helpful responses
- Click 👎 for unhelpful responses

**View Sources:**
- Expand "Sources" section below response
- See document names and relevance scores

**View Metadata:**
- Click "Show Metadata" (if enabled in settings)
- See routing decision, execution time, token usage

**Visualizations:**
- Interactive Plotly charts appear below responses
- Routing diagram shows decision flow
- Timeline shows execution steps
- Metrics show performance data

#### 4. Settings Configuration

**Query Type:**
- **API Only:** Direct LLM responses (fastest)
- **RAG Only:** Document-based answers (most accurate)
- **Hybrid:** Intelligent routing (recommended)

**Display Options:**
- ☑️ Include Sources - Show document citations
- ☑️ Include Metadata - Show execution details

#### 5. Session Management

**Export Chat History:**
1. Click "Export Chat" button
2. Select format:
   - **JSON:** Structured data with metadata
   - **Text:** Plain text conversation
   - **Markdown:** Formatted for documentation
3. Download file automatically

**Clear Chat:**
- Click "Clear Chat" button
- Confirms before deleting
- Resets conversation history

**Chat Statistics:**
- Total messages count
- User vs Assistant message breakdown
- Average response length

---

## 🧩 Components

### 1. Main Application (`app.py`)

**Key Functions:**
- `initialize_session_state()` - Set up session variables
- `render_sidebar()` - Display login/profile and settings
- `render_chat_interface()` - Main chat area with messages
- `main()` - Entry point and page configuration

**Session State Variables:**
```python
st.session_state.messages         # Chat history
st.session_state.user_info        # Logged-in user data
st.session_state.api_client       # API client instance
st.session_state.query_type       # Current query routing
st.session_state.include_sources  # Display sources toggle
st.session_state.include_metadata # Display metadata toggle
```

### 2. API Client (`api_client.py`)

**Class: `AasthaSathiAPIClient`**

**Methods:**
```python
login_myaastha(userid, password)
    # Login to MyAastha banking system
    # Returns: (success, user_data, error)

query(question, query_type, include_sources, include_metadata)
    # Submit query to AasthaSathi API
    # Returns: (success, response_data, error)

logout()
    # Clear authentication state

health_check()
    # Check API server status
    # Returns: (is_healthy, health_data, error)

get_connection_status()
    # Get current connection state
    # Returns: dict with connection info
```

### 3. Chat Component (`components/chat.py`)

**Functions:**
```python
render_message(message, idx, key_prefix)
    # Display single chat message with copy/feedback

render_chat_history(messages)
    # Display all messages with avatars

render_chat_controls()
    # Export and clear chat buttons

render_chat_stats(messages)
    # Display conversation statistics

export_chat_history(messages, format)
    # Export chat in JSON/Text/Markdown
```

### 4. Visualizer Component (`components/visualizer.py`)

**Functions:**
```python
create_routing_diagram(metadata)
    # Sankey flow diagram for routing decision

create_execution_timeline(metadata)
    # Gantt-style timeline for execution steps

create_metrics_chart(metadata)
    # Bar chart for performance metrics

create_source_distribution(sources)
    # Pie chart for source documents

create_confidence_gauge(confidence)
    # Gauge chart for confidence score

render_response_visualizations(response, key_prefix)
    # Main function to display all visualizations
```

---

## 🧪 Testing

### Running Integration Tests

```bash
cd /path/to/AasthaSathi
source .venv/bin/activate
python ui/test_integration.py
```

**Test Credentials:**
- User ID: `9614108399`
- Password: `123456`

### Test Coverage

The test suite validates:

1. ✅ **API Connectivity** (2 tests)
   - Health check endpoint
   - Connection status

2. ✅ **Authentication** (4 tests)
   - Valid login
   - User info extraction
   - Logout functionality
   - Invalid credentials handling

3. ✅ **Query Submission** (6 tests)
   - Banking queries
   - Procedure queries
   - Rate queries
   - Response structure validation

4. ✅ **Error Handling** (3 tests)
   - Empty queries
   - Long queries (>1000 chars)
   - Special characters

5. ✅ **Session Features** (2 tests)
   - Multiple client instances
   - State isolation

6. ✅ **UI Integration** (2 tests)
   - Configuration loading
   - Component imports

**Total:** 19 individual tests across 6 test suites

### Test Results

Latest test run (November 5, 2025):
```
✅ 6/6 test suites passed (100%)
🎉 All tests passed! UI is ready for production.
```

See `INTEGRATION_TEST_REPORT.md` for detailed results.

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. "Could not connect to AasthaSathi API"

**Problem:** API server not running or wrong URL

**Solution:**
```bash
# Check if API is running
curl http://localhost:8000/api/v1/health

# If not running, start API server
python main.py

# Check if port is in use
netstat -tuln | grep 8000
```

#### 2. "ModuleNotFoundError: No module named 'streamlit'"

**Problem:** Dependencies not installed

**Solution:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install streamlit plotly pandas requests streamlit-chat

# Verify installation
python -c "import streamlit; print(streamlit.__version__)"
```

#### 3. "MyAastha login failed: 404"

**Problem:** Invalid credentials or missing auth token

**Solution:**
1. Verify credentials are correct
2. Check `BANKING_AUTH_KEY` in `.env` file
3. Ensure Bearer token is set: `QUFzdDhAOmNCMW5L`
4. Verify MyAastha API is accessible

#### 4. "StreamlitDuplicateElementId"

**Problem:** Multiple Plotly charts with same ID

**Solution:** This is fixed in current version. If you see it:
```bash
# Update to latest code
git pull origin master

# Or manually update visualizer.py
# Ensure key_prefix is used in render_response_visualizations()
```

#### 5. "Query failed with status 422"

**Problem:** Invalid query format

**Solution:**
- Ensure query is not empty
- Keep queries under 1000 characters
- Check query contains valid text

#### 6. Port 8501 Already in Use

**Problem:** Streamlit already running or port blocked

**Solution:**
```bash
# Find process using port 8501
lsof -i :8501

# Kill existing Streamlit
pkill -f streamlit

# Or use different port
streamlit run ui/app.py --server.port 8502
```

#### 7. Slow Response Times (>30 seconds)

**Problem:** Network latency or LLM processing time

**Solution:**
1. Check internet connection
2. Verify API server performance
3. Consider using "API Only" mode for faster responses
4. Increase timeout in `config.py` if needed

#### 8. Chat History Not Persisting

**Problem:** Session state cleared on page refresh

**Solution:**
- Expected behavior - Streamlit clears state on refresh
- Export chat before refreshing if you need to save it
- For persistent storage, implement database backend

### Debug Mode

Enable debug logging:
```bash
# Set log level to DEBUG
export LOG_LEVEL=DEBUG

# Run with verbose output
streamlit run ui/app.py --logger.level=debug
```

### Getting Help

If issues persist:
1. Check `INTEGRATION_TEST_REPORT.md` for known issues
2. Review error logs in terminal
3. Verify all environment variables are set
4. Test API endpoints directly with curl
5. Check Streamlit version compatibility

---

## 🚢 Deployment

### Production Checklist

Before deploying to production:

- [ ] **Security**
  - [ ] Enable HTTPS/SSL certificates
  - [ ] Store credentials in secure vault (not .env)
  - [ ] Implement rate limiting
  - [ ] Add CORS configuration
  - [ ] Enable authentication tokens with expiry

- [ ] **Performance**
  - [ ] Load test with concurrent users
  - [ ] Configure caching for static content
  - [ ] Optimize query response times
  - [ ] Set up CDN for assets

- [ ] **Monitoring**
  - [ ] Set up logging infrastructure
  - [ ] Configure error tracking (Sentry, etc.)
  - [ ] Monitor API health checks
  - [ ] Track user analytics

- [ ] **Scalability**
  - [ ] Configure auto-scaling for API server
  - [ ] Set up load balancer
  - [ ] Implement connection pooling
  - [ ] Database backup strategy

- [ ] **Testing**
  - [ ] Run full integration test suite
  - [ ] Perform security audit
  - [ ] Test mobile responsiveness
  - [ ] Validate all edge cases

### Deployment Options

#### Option 1: Streamlit Cloud (Easiest)

```bash
# 1. Push code to GitHub
git push origin master

# 2. Visit Streamlit Cloud
# https://streamlit.io/cloud

# 3. Connect repository and deploy
# Set environment variables in dashboard
```

#### Option 2: Docker Deployment

```dockerfile
# Dockerfile (create in ui/ directory)
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Build and run
docker build -t aasthasathi-ui .
docker run -p 8501:8501 --env-file .env aasthasathi-ui
```

#### Option 3: Traditional Server

```bash
# Install as systemd service
sudo nano /etc/systemd/system/aasthasathi-ui.service
```

```ini
[Unit]
Description=AasthaSathi UI Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/AasthaSathi
Environment="PATH=/opt/AasthaSathi/.venv/bin"
ExecStart=/opt/AasthaSathi/.venv/bin/streamlit run ui/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable aasthasathi-ui
sudo systemctl start aasthasathi-ui
```

### Production Environment Variables

```bash
# Production .env
BANKING_AUTH_KEY="<production_token>"
AASTHASATHI_API_URL="https://api.aasthasathi.com"
AASTHASATHI_API_USERNAME="<prod_username>"
AASTHASATHI_API_PASSWORD="<secure_password>"
MYAASTHA_LOGIN_URL="https://web.myaastha.in/cobankapi/api/user/signin"

# Additional production settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

---

## 📚 API Reference

### AasthaSathi REST API

**Base URL:** `http://localhost:8000/api/v1`

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-05T10:30:00Z"
}
```

#### Submit Query
```http
POST /query
Authorization: Basic <base64(username:password)>
Content-Type: application/json

{
  "query": "What are the loan types?",
  "query_type": "hybrid",
  "include_sources": true,
  "include_metadata": true
}
```

**Response:**
```json
{
  "answer": "The bank offers the following loan types...",
  "sources": [
    {
      "document": "User Manual.pdf",
      "score": 0.89
    }
  ],
  "metadata": {
    "route": "hybrid",
    "execution_time": 12.5,
    "tokens_used": 450
  }
}
```

### MyAastha Login API

**Base URL:** `https://web.myaastha.in/cobankapi/api`

#### User Sign In
```http
POST /user/signin
Authorization: Bearer QUFzdDhAOmNCMW5L
Content-Type: application/json

{
  "userid": "9614108399",
  "password": "123456"
}
```

**Response:**
```json
{
  "success": 1,
  "userid": "9614108399",
  "usertoken": "abc123...",
  "name": "User Name",
  "email": "user@example.com",
  "role": "member",
  "imageUrl": "https://..."
}
```

---

## 📄 License

This project is part of the AasthaSathi system. See main repository LICENSE file for details.

---

## 👥 Contributing

For contributions, please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run integration tests
5. Submit a pull request

---

## 📞 Support

For issues or questions:
- Create an issue in GitHub repository
- Check troubleshooting section above
- Review integration test report for known issues

---

**Last Updated:** November 5, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅
