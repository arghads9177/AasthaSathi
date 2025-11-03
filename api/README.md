# AasthaSathi API - Quick Start Guide

## � Authentication

The API uses **HTTP Basic Authentication** to secure endpoints. You must provide valid credentials with each request.

### Default Credentials
- **Username**: `aastha_admin`
- **Password**: `aastha_secure_2025`

⚠️ **Security Note**: Change these credentials in production by updating the `.env` file. Always use HTTPS in production to encrypt credentials during transmission.

---

## �🚀 Running the API

### 1. Start the API Server

```bash
# From project root
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the Python executable from virtual environment:

```bash
/home/argha-ds/datascience/ai-assistant/AasthaSathi/.venv/bin/python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Interactive Swagger UI with auth)
- **ReDoc**: http://localhost:8000/redoc (Alternative documentation)

---

## 📡 API Endpoints

### 1. Health Check (Public - No Auth Required)
```bash
curl http://localhost:8000/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "AasthaSathi API"
}
```

### 2. Query Endpoint (Requires Authentication)

**Using cURL with Basic Auth:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
     -u aastha_admin:aastha_secure_2025 \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What savings schemes are available?",
       "include_sources": true,
       "include_metadata": true
     }'
```

**Using Python requests:**
```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.post(
    "http://localhost:8000/api/v1/query",
    auth=HTTPBasicAuth('aastha_admin', 'aastha_secure_2025'),
    json={
        "query": "List all branches in Patna",
        "include_sources": True,
        "include_metadata": True
    }
)

print(response.json())
```

**Using JavaScript/Fetch:**
```javascript
// Encode credentials to Base64
const credentials = btoa('aastha_admin:aastha_secure_2025');

fetch('http://localhost:8000/api/v1/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Basic ${credentials}`
  },
  body: JSON.stringify({
    query: 'How do I open an account?',
    include_sources: true,
    include_metadata: true
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

### Authentication Errors

**401 Unauthorized** - Invalid or missing credentials:
```json
{
  "detail": "Invalid authentication credentials"
}
```

To test authentication:
```bash
# Without auth (should fail with 401)
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "test"}'

# With correct auth (should succeed with 200)
curl -X POST "http://localhost:8000/api/v1/query" \
     -u aastha_admin:aastha_secure_2025 \
     -H "Content-Type: application/json" \
     -d '{"query": "test"}'
```

---

## 🧪 Testing

Run the test script:
```bash
python scripts/test_api_endpoint.py
```

This will test:
- API queries (branches, schemes)
- RAG queries (procedures)
- Hybrid queries (combined data)

---

## 📝 Request Format

```json
{
  "query": "Your question here",
  "session_id": "optional-session-id",
  "include_sources": true,
  "include_metadata": true
}
```

**Fields:**
- `query` (required): Your question (1-1000 characters)
- `session_id` (optional): For conversation continuity
- `include_sources` (optional, default: true): Include source attribution
- `include_metadata` (optional, default: true): Include execution details

---

## 📤 Response Format

```json
{
  "session_id": "generated-uuid",
  "query": "What savings schemes are available?",
  "answer": "We offer a Savings Account scheme with 4% interest...",
  "datasource": "api",
  "routing_reasoning": "Query asks for current schemes...",
  "sources": ["API Data"],
  "metadata": {
    "execution_path": ["router", "api_call", "api_answer"],
    "processing_time_ms": 2341,
    "retry_count": 0,
    "api_used": true,
    "num_retrieved": 0,
    "num_relevant": 0
  },
  "timestamp": "2025-10-31T10:30:00Z"
}
```

---

## 🎯 Example Queries

### API Queries (Real-time Data)
```bash
# Branches
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "List all branches in Patna"}'

# Schemes
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What loan schemes are available?"}'

# Members
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "How many members joined in January 2025?"}'
```

### RAG Queries (Knowledge Base)
```bash
# Procedures
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "How do I open an account?"}'

# Policies
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the membership eligibility criteria?"}'
```

### Hybrid Queries (Combined)
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Show me all RD schemes and explain how they work"}'
```

---

## 📊 Interactive Documentation

Visit http://localhost:8000/docs for:
- Interactive API testing
- Request/response schemas
- Example values
- Try it out directly in browser

---

## 🔧 Troubleshooting

### API not starting?
1. Check if port 8000 is available
2. Verify virtual environment is activated
3. Ensure all dependencies are installed: `pip install -r requirements.txt`

### Connection refused?
- Make sure the API server is running
- Check the port number (default: 8000)

### Slow responses?
- First query takes longer (agent initialization)
- API queries: ~2-5 seconds
- RAG queries: ~3-8 seconds
- Hybrid queries: ~10-20 seconds

---

## 🎉 What's Working

✅ FastAPI server with CORS enabled  
✅ POST /api/v1/query endpoint  
✅ Integrated agent (Router + API + RAG)  
✅ Request/response validation (Pydantic)  
✅ Auto-generated documentation  
✅ Error handling  
✅ Processing time tracking  
✅ Source attribution  

---

## 🚧 Coming Next

⏳ Session management  
⏳ API key authentication  
⏳ Rate limiting  
⏳ Streaming responses  
⏳ Docker deployment  

---

## 📞 Support

For issues or questions:
1. Check the logs in console
2. Visit /docs for API documentation
3. Review error messages in response
