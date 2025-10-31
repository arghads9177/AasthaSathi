# REST API Development Plan for AasthaSathi Workflow

## 📋 Executive Summary

Create a production-ready FastAPI REST API that wraps the integrated workflow (Router + API Agent + RAG Agent), enabling external applications to leverage the intelligent banking assistant capabilities through standard HTTP endpoints.

---

## 🎯 Objectives

1. **Expose Workflow as API**: Make the integrated agent accessible via REST endpoints
2. **Session Management**: Support multi-turn conversations with persistent sessions
3. **Authentication & Security**: Implement API key-based authentication
4. **Rate Limiting**: Prevent abuse and manage resource usage
5. **Monitoring & Logging**: Track API usage, performance, and errors
6. **Documentation**: Auto-generated OpenAPI/Swagger documentation
7. **Deployment Ready**: Docker containerization and production configurations

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
│              (Web, Mobile, Desktop, Other APIs)              │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Layer (api/)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Endpoints  │  Auth  │  Rate Limit  │  Validation     │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Integrated Agent (agents/)                      │
│  Router → [API Agent | RAG Agent | Hybrid] → Answer        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
api/
├── __init__.py                 # Package initialization
├── main.py                     # FastAPI application entry point
├── dependencies.py             # Dependency injection (auth, rate limiting)
├── middleware.py               # Custom middleware (CORS, logging, timing)
├── models/
│   ├── __init__.py
│   ├── request.py             # Request models (Pydantic)
│   └── response.py            # Response models (Pydantic)
├── routes/
│   ├── __init__.py
│   ├── chat.py                # Chat/query endpoints
│   ├── session.py             # Session management endpoints
│   ├── health.py              # Health check endpoints
│   └── admin.py               # Admin endpoints (metrics, stats)
├── services/
│   ├── __init__.py
│   ├── agent_service.py       # Wrapper for IntegratedAgent
│   ├── session_service.py     # Session storage and management
│   └── auth_service.py        # API key validation
├── utils/
│   ├── __init__.py
│   ├── rate_limiter.py        # Rate limiting logic
│   ├── logger.py              # API-specific logging
│   └── validators.py          # Custom validators
└── config.py                   # API-specific configuration
```

---

## 🔌 API Endpoints Design

### 1. **Chat/Query Endpoints**

#### `POST /api/v1/chat/query`
Submit a query and get an answer.

**Request:**
```json
{
  "query": "What savings schemes are available?",
  "session_id": "optional-session-id",
  "include_sources": true,
  "include_metadata": true
}
```

**Response:**
```json
{
  "session_id": "generated-or-provided-session-id",
  "query": "What savings schemes are available?",
  "answer": "We offer a Savings Account scheme...",
  "datasource": "api",
  "routing_reasoning": "The query asks for current schemes...",
  "sources": ["API Data"],
  "metadata": {
    "execution_path": ["router", "api_call", "api_answer"],
    "retry_count": 0,
    "api_used": true,
    "num_retrieved": 0,
    "num_relevant": 0,
    "processing_time_ms": 2341
  },
  "timestamp": "2025-10-31T10:30:00Z"
}
```

#### `POST /api/v1/chat/stream`
Stream responses for real-time interaction (future enhancement).

**Request:** Same as `/query`

**Response:** Server-Sent Events (SSE) stream

---

### 2. **Session Management Endpoints**

#### `POST /api/v1/sessions`
Create a new session.

**Response:**
```json
{
  "session_id": "uuid-string",
  "created_at": "2025-10-31T10:30:00Z",
  "expires_at": "2025-10-31T12:30:00Z"
}
```

#### `GET /api/v1/sessions/{session_id}`
Get session details and history.

**Response:**
```json
{
  "session_id": "uuid-string",
  "created_at": "2025-10-31T10:30:00Z",
  "last_activity": "2025-10-31T10:35:00Z",
  "message_count": 5,
  "chat_history": [
    {
      "role": "user",
      "content": "What schemes do you offer?",
      "timestamp": "2025-10-31T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "We offer...",
      "timestamp": "2025-10-31T10:30:02Z"
    }
  ]
}
```

#### `DELETE /api/v1/sessions/{session_id}`
Delete a session.

**Response:**
```json
{
  "message": "Session deleted successfully",
  "session_id": "uuid-string"
}
```

#### `POST /api/v1/sessions/{session_id}/clear`
Clear chat history but keep session.

---

### 3. **Health & Monitoring Endpoints**

#### `GET /api/v1/health`
Basic health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-31T10:30:00Z",
  "version": "1.0.0"
}
```

#### `GET /api/v1/health/detailed`
Detailed health check with component status.

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "integrated_agent": "healthy",
    "chromadb": "healthy",
    "openai_api": "healthy",
    "banking_api": "healthy"
  },
  "uptime_seconds": 3600,
  "requests_processed": 1234,
  "timestamp": "2025-10-31T10:30:00Z"
}
```

---

### 4. **Admin Endpoints** (Protected)

#### `GET /api/v1/admin/metrics`
Get API usage metrics.

**Response:**
```json
{
  "total_requests": 5000,
  "requests_by_datasource": {
    "api": 2000,
    "rag": 1500,
    "hybrid": 1500
  },
  "avg_response_time_ms": 2500,
  "error_rate": 0.02,
  "active_sessions": 45
}
```

#### `GET /api/v1/admin/sessions`
List all active sessions (with pagination).

---

## 🔒 Security & Authentication

### API Key Authentication

**Implementation:**
- Header-based: `X-API-Key: your-api-key-here`
- Environment variable: `API_KEYS` (comma-separated list)
- Support for multiple API keys (for different clients)

**Example:**
```python
# In .env
API_KEYS=key1_abc123,key2_def456,admin_xyz789

# Usage
curl -H "X-API-Key: key1_abc123" \
     -X POST http://localhost:8000/api/v1/chat/query \
     -d '{"query": "List branches"}'
```

### Rate Limiting

**Strategy:**
- Per API key: 100 requests/minute
- Per IP: 20 requests/minute (fallback)
- Sliding window algorithm
- Return `429 Too Many Requests` when exceeded

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1698761400
```

### CORS Configuration

- Allow specific origins (configurable)
- Support for development (localhost) and production domains

---

## 📊 Data Models

### Request Models (`api/models/request.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="User query")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    include_sources: bool = Field(True, description="Include source attribution")
    include_metadata: bool = Field(True, description="Include execution metadata")

class SessionCreateRequest(BaseModel):
    metadata: Optional[dict] = Field(None, description="Custom session metadata")
```

### Response Models (`api/models/response.py`)

```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class QueryResponse(BaseModel):
    session_id: str
    query: str
    answer: str
    datasource: str
    routing_reasoning: Optional[str]
    sources: List[str]
    metadata: Optional[Dict[str, Any]]
    timestamp: datetime

class SessionResponse(BaseModel):
    session_id: str
    created_at: datetime
    expires_at: datetime
    message_count: int = 0

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
```

---

## 🛠️ Implementation Components

### 1. **Agent Service** (`api/services/agent_service.py`)

Wrapper around `IntegratedAgent` with:
- Singleton pattern for agent instance
- Error handling and retry logic
- Timeout management
- Performance monitoring

```python
class AgentService:
    def __init__(self):
        self.agent = get_integrated_agent()
        self.request_count = 0
        
    async def process_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        chat_history: Optional[List] = None
    ) -> Dict[str, Any]:
        """Process query through integrated agent."""
        # Implementation with error handling, timing, etc.
```

### 2. **Session Service** (`api/services/session_service.py`)

In-memory session storage with:
- TTL (Time To Live) - 2 hours default
- Automatic cleanup of expired sessions
- Thread-safe operations

```python
class SessionService:
    def __init__(self):
        self.sessions: Dict[str, SessionData] = {}
        
    def create_session(self) -> str:
        """Create new session with unique ID."""
        
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Retrieve session data."""
        
    def update_session(self, session_id: str, message: Dict):
        """Add message to session history."""
```

### 3. **Rate Limiter** (`api/utils/rate_limiter.py`)

Sliding window rate limiter:
```python
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        
    async def check_rate_limit(self, key: str) -> bool:
        """Check if request is within rate limit."""
```

### 4. **Middleware** (`api/middleware.py`)

Custom middleware for:
- Request logging (all incoming requests)
- Response timing
- Error handling and standardization
- CORS handling

---

## 🧪 Testing Strategy

### Unit Tests (`tests/api/`)

```
tests/api/
├── test_routes_chat.py        # Test chat endpoints
├── test_routes_session.py     # Test session management
├── test_services.py           # Test service layer
├── test_auth.py               # Test authentication
├── test_rate_limiter.py       # Test rate limiting
└── test_integration.py        # End-to-end API tests
```

### Test Coverage Goals
- **Routes**: 100% endpoint coverage
- **Services**: 90%+ business logic coverage
- **Integration**: All user flows tested

### Example Test:
```python
async def test_query_endpoint():
    response = await client.post(
        "/api/v1/chat/query",
        headers={"X-API-Key": "test-key"},
        json={"query": "List branches in Patna"}
    )
    assert response.status_code == 200
    assert "answer" in response.json()
```

---

## 📝 Configuration

### Environment Variables (`.env`)

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_KEYS=key1,key2,admin_key
API_TITLE="AasthaSathi Banking Assistant API"
API_VERSION=1.0.0

# Security
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
RATE_LIMIT_PER_MINUTE=100
SESSION_TTL_HOURS=2

# Agent Configuration (existing)
OPENAI_API_KEY=your_key
BANKING_AUTH_KEY=your_key
BANKING_OCODE=aastha

# Logging
API_LOG_LEVEL=INFO
API_LOG_FILE=/var/log/aasthasathi-api.log
```

---

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - BANKING_AUTH_KEY=${BANKING_AUTH_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

---

## 📈 Performance Considerations

### Optimization Strategies

1. **Async Operations**: Use async/await throughout
2. **Connection Pooling**: Reuse HTTP connections for external APIs
3. **Caching**: Cache frequent queries (optional)
4. **Background Tasks**: Process non-critical tasks asynchronously
5. **Resource Limits**: Set timeouts on agent queries (30s default)

### Expected Performance
- **Simple API queries**: 2-5 seconds
- **RAG queries**: 3-8 seconds
- **Hybrid queries**: 10-20 seconds
- **Concurrent requests**: Support 50+ simultaneous connections

---

## 📚 Documentation

### Auto-Generated Docs
- **Swagger UI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`
- **OpenAPI JSON**: Available at `/openapi.json`

### Additional Documentation
- API usage guide with examples
- Authentication setup guide
- Rate limiting policies
- Error codes reference
- Integration examples (Python, JavaScript, cURL)

---

## 🚀 Implementation Phases

### **Phase 1: Core API Structure** (Priority: High)
- [ ] Create API folder structure
- [ ] Setup FastAPI application (`api/main.py`)
- [ ] Define request/response models
- [ ] Implement basic health endpoint
- [ ] Setup CORS and middleware

### **Phase 2: Agent Integration** (Priority: High)
- [ ] Create agent service wrapper
- [ ] Implement `/api/v1/chat/query` endpoint
- [ ] Add error handling and validation
- [ ] Test basic query flow

### **Phase 3: Session Management** (Priority: Medium)
- [ ] Implement session service
- [ ] Create session endpoints (CRUD)
- [ ] Add session expiration logic
- [ ] Integrate sessions with chat endpoint

### **Phase 4: Security** (Priority: High)
- [ ] Implement API key authentication
- [ ] Add rate limiting
- [ ] Setup CORS properly
- [ ] Add request validation

### **Phase 5: Monitoring & Admin** (Priority: Medium)
- [ ] Implement detailed health checks
- [ ] Add metrics endpoint
- [ ] Create admin dashboard endpoints
- [ ] Setup comprehensive logging

### **Phase 6: Testing & Documentation** (Priority: High)
- [ ] Write unit tests for all endpoints
- [ ] Create integration tests
- [ ] Add API documentation
- [ ] Write usage examples

### **Phase 7: Deployment** (Priority: Medium)
- [ ] Create Dockerfile
- [ ] Setup docker-compose
- [ ] Add production configurations
- [ ] Create deployment guide

---

## 🔍 Example Usage

### Python Client
```python
import requests

API_URL = "http://localhost:8000/api/v1"
API_KEY = "your-api-key"

headers = {"X-API-Key": API_KEY}

# Create session
session_response = requests.post(f"{API_URL}/sessions", headers=headers)
session_id = session_response.json()["session_id"]

# Query
query_data = {
    "query": "What savings schemes are available?",
    "session_id": session_id
}
response = requests.post(f"{API_URL}/chat/query", headers=headers, json=query_data)
print(response.json()["answer"])
```

### cURL
```bash
# Query
curl -X POST "http://localhost:8000/api/v1/chat/query" \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"query": "List branches in Patna"}'
```

### JavaScript/Fetch
```javascript
const API_URL = 'http://localhost:8000/api/v1';
const API_KEY = 'your-api-key';

async function query(text) {
  const response = await fetch(`${API_URL}/chat/query`, {
    method: 'POST',
    headers: {
      'X-API-Key': API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ query: text })
  });
  
  return await response.json();
}
```

---

## ⚠️ Error Handling

### Standard Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Query cannot be empty",
    "details": {
      "field": "query",
      "constraint": "min_length"
    }
  },
  "timestamp": "2025-10-31T10:30:00Z"
}
```

### HTTP Status Codes
- `200`: Success
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid API key)
- `429`: Too Many Requests (rate limit exceeded)
- `500`: Internal Server Error
- `503`: Service Unavailable (agent timeout)

---

## 📦 Dependencies to Add

```txt
# Already have FastAPI in requirements.txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
slowapi>=0.1.9  # Rate limiting
python-multipart  # Already in requirements
```

---

## 🎯 Success Criteria

1. ✅ All endpoints functional and tested
2. ✅ Response times under 30 seconds for complex queries
3. ✅ API key authentication working
4. ✅ Rate limiting prevents abuse
5. ✅ Sessions persist across multiple queries
6. ✅ Error handling returns helpful messages
7. ✅ Documentation complete and accurate
8. ✅ Docker deployment working
9. ✅ 90%+ test coverage
10. ✅ Ready for production use

---

## 🔮 Future Enhancements

1. **Streaming Responses**: Server-Sent Events for real-time answers
2. **WebSocket Support**: Bi-directional communication
3. **Persistent Sessions**: Database-backed session storage
4. **Caching Layer**: Redis for frequent queries
5. **Multi-tenancy**: Support for multiple organizations
6. **Advanced Analytics**: Query patterns, user behavior
7. **A/B Testing**: Compare different routing strategies
8. **Webhook Support**: Notify external systems on events
9. **GraphQL API**: Alternative to REST
10. **SDK Libraries**: Python, JavaScript, Java client libraries

---

## 📋 Summary

This plan provides a comprehensive roadmap for building a production-ready REST API on top of the AasthaSathi integrated workflow. The API will:

- ✅ Expose all workflow capabilities via clean REST endpoints
- ✅ Support conversational interactions with session management
- ✅ Implement robust security with API keys and rate limiting
- ✅ Provide excellent developer experience with auto-generated docs
- ✅ Be production-ready with Docker deployment
- ✅ Include comprehensive testing and error handling

**Estimated Development Time**: 3-5 days for core functionality + testing

**Ready to proceed with implementation?**
