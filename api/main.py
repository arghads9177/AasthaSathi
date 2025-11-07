"""
FastAPI application for AasthaSathi Banking Assistant.

Simple REST API that exposes the integrated agent workflow with Basic Authentication.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from api.models import QueryRequest, QueryResponse, ErrorResponse
from api.services.agent_service import get_agent_service
from api.auth import get_current_user

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AasthaSathi Banking Assistant API",
    description="""
    AI-powered banking assistant with intelligent routing (API + RAG + Hybrid) and **multilingual support**.
    
    ## 🌐 Multilingual Support (Phase 4)
    
    The API now supports **English**, **Hindi (हिंदी)**, and **Bengali (বাংলা)**:
    
    - **Auto-Detection**: Language automatically detected from query
    - **Manual Selection**: Specify preferred language with `language` parameter
    - **Response Translation**: Answers provided in detected/preferred language
    - **Confidence Score**: Detection confidence included in response
    
    ### Example (Hindi Query):
    ```json
    {
        "query": "कौन सी बचत योजनाएं उपलब्ध हैं?",
        "language": "hi"
    }
    ```
    
    ### Response includes:
    ```json
    {
        "answer": "हमारे पास...",
        "detected_language": "hi",
        "detection_confidence": 1.0,
        "response_language": "hi"
    }
    ```
    
    ## 🔐 Authentication
    
    This API uses **HTTP Basic Authentication**. Include credentials in the Authorization header:
    
    ```
    Authorization: Basic <base64-encoded-username:password>
    ```
    
    Most HTTP clients handle this automatically when you provide username and password.
    
    ## 📍 Endpoints
    
    - **POST /api/v1/query** - Process banking queries (requires auth)
    - **GET /api/v1/health** - Health check (public)
    - **GET /** - API information (public)
    
    ## 🔒 Security Note
    
    ⚠️ Always use HTTPS in production to encrypt credentials during transmission.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - Allow all origins for now (will restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "AasthaSathi Banking Assistant API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "query": "POST /api/v1/query",
            "health": "GET /api/v1/health"
        }
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AasthaSathi API"
    }


@app.post(
    "/api/v1/query",
    response_model=QueryResponse,
    responses={
        200: {"description": "Successful query response"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        401: {"description": "Unauthorized - Invalid credentials"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def query(request: QueryRequest, username: str = Depends(get_current_user)):
    """
    Process a user query through the integrated agent.
    
    **Authentication Required**: HTTP Basic Auth
    - Send credentials in Authorization header: `Basic <base64-encoded-username:password>`
    - Most HTTP clients handle this automatically
    
    This endpoint accepts a natural language query and returns an AI-generated
    answer using intelligent routing (API, RAG, or Hybrid).
    
    **Multilingual Support**: (Phase 4)
    - Supports English (en), Hindi (hi), and Bengali (bn)
    - Language auto-detected from query if not specified
    - Response translated to detected/preferred language
    
    **Example (English):**
    ```json
    {
        "query": "What savings schemes are available?",
        "language": "en",
        "session_id": null,
        "include_sources": true,
        "include_metadata": true
    }
    ```
    
    **Example (Hindi):**
    ```json
    {
        "query": "कौन सी बचत योजनाएं उपलब्ध हैं?",
        "language": "hi",
        "session_id": null,
        "include_sources": true,
        "include_metadata": true
    }
    ```
    
    **Response includes:**
    - AI-generated answer (in requested/detected language)
    - Data source used (api/rag/hybrid)
    - Language detection info (detected_language, confidence)
    - Source attribution
    - Execution metadata (timing, path, etc.)
    """
    try:
        logger.info(f"[User: {username}] Received query: '{request.query[:50]}...'")
        if request.language:
            logger.info(f"[User: {username}] Preferred language: {request.language}")
        
        # Get agent service
        agent_service = get_agent_service()
        
        # Process query with language parameter
        result = await agent_service.process_query(
            query=request.query,
            session_id=request.session_id,
            chat_history=None,  # Will add session support later
            language=request.language,  # Phase 4 - Pass language preference
            include_sources=request.include_sources,
            include_metadata=request.include_metadata
        )
        
        # Build response
        response = QueryResponse(
            session_id=result["session_id"],
            query=result["query"],
            answer=result["answer"],
            datasource=result["datasource"],
            routing_reasoning=result.get("routing_reasoning"),
            detected_language=result.get("detected_language"),  # Phase 4
            detection_confidence=result.get("detection_confidence"),  # Phase 4
            response_language=result.get("response_language"),  # Phase 4
            sources=result.get("sources", []),
            metadata=result.get("metadata"),
            timestamp=datetime.now()
        )
        
        logger.info(f"✓ Query processed successfully - Route: {response.datasource}")
        
        return response
        
    except Exception as e:
        logger.error(f"✗ Error in query endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("🚀 AasthaSathi API starting up...")
    logger.info("📚 API Documentation available at /docs")
    logger.info("✅ API is ready to accept requests")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("👋 AasthaSathi API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
