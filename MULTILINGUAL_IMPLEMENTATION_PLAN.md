# AasthaSathi - Multilingual Support Implementation Plan

**Feature:** Multilingual Query Processing (English/Hindi/Bengali)  
**Date:** November 5, 2025  
**Status:** 📋 Planning Phase

---

## 🎯 Objective

Enable users to interact with AasthaSathi AI assistant in multiple languages (English, Hindi, Bengali). The system should:
1. **Detect** the language of user queries automatically
2. **Process** queries in the detected language
3. **Respond** in the same language as the query
4. **Maintain** context across multilingual conversations
5. **Translate** API responses and document sources when needed

---

## 🏗️ Architecture Overview

### Current Architecture
```
User Query (English only)
    ↓
Router → Classify (API/RAG/Hybrid)
    ↓
API Agent / RAG Agent
    ↓
LLM Processing (English prompts)
    ↓
Response (English only)
```

### New Multilingual Architecture
```
User Query (English/Hindi/Bengali)
    ↓
Language Detection Layer ← NEW
    ↓
Router → Classify (API/RAG/Hybrid) + Language Context
    ↓
API Agent / RAG Agent (with language-aware prompts)
    ↓
Translation Layer (if needed) ← NEW
    ↓
LLM Processing (multilingual prompts)
    ↓
Response (same language as query)
```

---

## 📦 Phase 1: Infrastructure Setup

### 1.1 Language Detection Module

**File:** `core/language_detector.py`

**Components:**
- **Library:** Use `langdetect` or `fasttext-langdetect` for fast detection
- **Fallback:** Default to English if detection uncertain
- **Confidence threshold:** Minimum 0.8 confidence for non-English

**Functions:**
```python
def detect_language(text: str) -> tuple[str, float]
    # Detect language and return (lang_code, confidence)
    # Returns: ("en", 0.95), ("hi", 0.89), ("bn", 0.92)

def is_supported_language(lang_code: str) -> bool
    # Check if language is in supported list

def get_language_name(lang_code: str) -> str
    # Convert "en" → "English", "hi" → "Hindi", "bn" → "Bengali"
```

**Dependencies to add:**
```bash
langdetect==1.0.9
# OR
fasttext-langdetect==1.0.5
```

---

### 1.2 Translation Service Module

**File:** `core/translation_service.py`

**Options:**

#### Option A: Google Translate API (Recommended)
- **Pros:** High accuracy, official support, reliable
- **Cons:** Paid service (but free tier available)
- **Library:** `googletrans==4.0.0-rc1` or Google Cloud Translation API

#### Option B: IndicTrans2 (Open Source)
- **Pros:** Free, optimized for Indian languages, offline
- **Cons:** Requires model download (~2GB), slower
- **Library:** `indictrans` from AI4Bharat

#### Option C: MarianMT (Hugging Face)
- **Pros:** Free, good quality, moderate size
- **Cons:** Need separate models per language pair
- **Library:** `transformers` with `Helsinki-NLP/opus-mt-*` models

**Recommended:** Start with **Option A (Google Translate)** for MVP, add Option B for production cost optimization.

**Functions:**
```python
class TranslationService:
    def translate(self, text: str, source_lang: str, target_lang: str) -> str
        # Translate text from source to target language
    
    def translate_to_english(self, text: str, source_lang: str) -> str
        # Convenience method for query translation
    
    def translate_from_english(self, text: str, target_lang: str) -> str
        # Convenience method for response translation
    
    def batch_translate(self, texts: list[str], source_lang: str, target_lang: str) -> list[str]
        # Translate multiple texts efficiently
```

---

### 1.3 Multilingual Prompts Module

**File:** `agents/prompts_multilingual.py`

**Structure:**
```python
# Prompt templates for each language
PROMPTS = {
    "en": {
        "router_system": "...",
        "answer_generation": "...",
        # ... all prompts in English
    },
    "hi": {
        "router_system": "...",  # Hindi translation
        "answer_generation": "...",
        # ... all prompts in Hindi
    },
    "bn": {
        "router_system": "...",  # Bengali translation
        "answer_generation": "...",
        # ... all prompts in Bengali
    }
}

def get_prompt(prompt_name: str, language: str = "en") -> str:
    """Get prompt template for specific language."""
    return PROMPTS.get(language, PROMPTS["en"]).get(prompt_name)
```

**Prompts to translate:**
1. `ROUTER_SYSTEM_PROMPT` - Query classification
2. `RELEVANCY_CHECK_PROMPT` - Document relevance
3. `QUERY_REFORMULATION_PROMPT` - Query rewriting
4. `ANSWER_GENERATION_PROMPT` - Final answer generation
5. `API_ONLY_PROMPT` - API-only response generation

---

## 📝 Phase 2: Core System Modifications

### 2.1 Update Agent State Model

**File:** `agents/models.py`

**Changes:**
```python
class AgentState(TypedDict):
    # ... existing fields ...
    
    # NEW: Multilingual fields
    query_language: str              # Detected language code ("en", "hi", "bn")
    query_language_confidence: float # Detection confidence (0.0-1.0)
    original_query: str              # Original query in user's language
    translated_query: Optional[str]  # English translation (if needed)
    response_language: str           # Language for response (same as query)
```

---

### 2.2 Language Detection Node

**File:** `agents/integration_nodes.py`

**New Node:**
```python
def language_detection_node(state: AgentState) -> dict:
    """
    Detect language of user query and update state.
    
    Args:
        state: Current agent state with query
        
    Returns:
        Updated state with language information
    """
    from core.language_detector import detect_language
    
    query = state["query"]
    lang_code, confidence = detect_language(query)
    
    logger.info(f"Detected language: {lang_code} (confidence: {confidence:.2f})")
    
    return {
        "query_language": lang_code,
        "query_language_confidence": confidence,
        "original_query": query,
        "response_language": lang_code
    }
```

**Integration:** Add as first node in workflow graph

---

### 2.3 Query Translation Node

**File:** `agents/integration_nodes.py`

**New Node:**
```python
def query_translation_node(state: AgentState) -> dict:
    """
    Translate non-English queries to English for processing.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with translated query
    """
    from core.translation_service import TranslationService
    
    lang = state["query_language"]
    original_query = state["original_query"]
    
    if lang == "en":
        # No translation needed
        logger.info("Query is in English, skipping translation")
        return {"translated_query": None}
    
    # Translate to English for router and retrieval
    translator = TranslationService()
    translated = translator.translate_to_english(original_query, lang)
    
    logger.info(f"Translated query: {original_query} → {translated}")
    
    # Update query field for processing
    return {
        "translated_query": translated,
        "query": translated  # Use translated query for processing
    }
```

---

### 2.4 Response Translation Node

**File:** `agents/integration_nodes.py`

**New Node:**
```python
def response_translation_node(state: AgentState) -> dict:
    """
    Translate English responses back to user's language.
    
    Args:
        state: Current agent state with answer
        
    Returns:
        Updated state with translated answer
    """
    from core.translation_service import TranslationService
    
    response_lang = state["response_language"]
    answer = state["answer"]
    
    if response_lang == "en":
        # No translation needed
        logger.info("Response is already in English")
        return {}
    
    # Translate answer to target language
    translator = TranslationService()
    translated_answer = translator.translate_from_english(answer, response_lang)
    
    logger.info(f"Translated answer to {response_lang}")
    
    return {"answer": translated_answer}
```

---

### 2.5 Update Router Node

**File:** `agents/integration_nodes.py`

**Modifications:**
```python
def router_node(state: AgentState) -> dict:
    """Route query with language context."""
    from agents.prompts_multilingual import get_prompt
    
    # Get language-specific router prompt
    lang = state.get("query_language", "en")
    router_prompt = get_prompt("router_system", lang)
    
    # Use language-aware router
    router = RouterAgent(system_prompt=router_prompt)
    
    # ... rest of routing logic ...
```

---

### 2.6 Update Answer Generation Node

**File:** `agents/nodes.py`

**Modifications:**
```python
def generate_answer_node(state: AgentState) -> dict:
    """Generate answer with language-aware prompt."""
    from agents.prompts_multilingual import get_prompt
    
    lang = state.get("response_language", "en")
    answer_prompt = get_prompt("answer_generation", lang)
    
    # Include language instruction in prompt
    context = format_docs_for_llm(state["retrieved_documents"])
    history = format_history(state.get("chat_history", []))
    
    prompt_with_language = f"""
{answer_prompt}

IMPORTANT: Respond in {get_language_name(lang)} language.

Query: {state["original_query"]}

{context}

{history}
"""
    
    # ... rest of generation logic ...
```

---

### 2.7 Update Integrated Agent Workflow

**File:** `agents/integrated_agent.py`

**Modifications:**
```python
def create_graph() -> StateGraph:
    """Create integrated workflow with multilingual support."""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("language_detection", language_detection_node)  # NEW
    workflow.add_node("query_translation", query_translation_node)    # NEW
    workflow.add_node("router", router_node)
    workflow.add_node("api_call", api_call_node)
    workflow.add_node("retrieve", retrieve_node)
    # ... existing nodes ...
    workflow.add_node("response_translation", response_translation_node)  # NEW
    
    # Set entry point
    workflow.set_entry_point("language_detection")  # CHANGED from "router"
    
    # Add edges
    workflow.add_edge("language_detection", "query_translation")  # NEW
    workflow.add_edge("query_translation", "router")  # NEW
    
    # ... existing conditional edges ...
    
    # Add final translation before END
    workflow.add_conditional_edges(
        "generate_answer",
        lambda s: "response_translation" if s.get("response_language") != "en" else "end",
        {
            "response_translation": "response_translation",
            "end": END
        }
    )
    workflow.add_edge("response_translation", END)  # NEW
    
    # ... rest of workflow ...
```

---

## 🎨 Phase 3: UI Modifications

### 3.1 Language Selector Component

**File:** `ui/components/language_selector.py`

**New Component:**
```python
import streamlit as st

SUPPORTED_LANGUAGES = {
    "en": "🇬🇧 English",
    "hi": "🇮🇳 हिंदी (Hindi)",
    "bn": "🇧🇩 বাংলা (Bengali)"
}

def render_language_selector():
    """Render language selection dropdown."""
    
    # Initialize language in session state
    if "preferred_language" not in st.session_state:
        st.session_state.preferred_language = "en"
    
    # Language selector
    selected = st.selectbox(
        "🌐 Language / भाषा / ভাষা",
        options=list(SUPPORTED_LANGUAGES.keys()),
        format_func=lambda x: SUPPORTED_LANGUAGES[x],
        index=list(SUPPORTED_LANGUAGES.keys()).index(
            st.session_state.preferred_language
        ),
        key="language_selector"
    )
    
    st.session_state.preferred_language = selected
    
    return selected
```

---

### 3.2 Update Main App

**File:** `ui/app.py`

**Changes:**
```python
from components.language_selector import render_language_selector, SUPPORTED_LANGUAGES

def render_sidebar():
    """Render sidebar with language selector."""
    with st.sidebar:
        # ... existing login/profile ...
        
        st.divider()
        
        # Language selection
        st.subheader("🌐 Language Preferences")
        selected_lang = render_language_selector()
        
        if selected_lang != "en":
            st.info(f"Queries will be processed in {SUPPORTED_LANGUAGES[selected_lang]}")
        
        # ... rest of sidebar ...

def render_chat_interface():
    """Render chat interface with language context."""
    
    # Get user query
    user_query = st.chat_input("Ask me anything... / कुछ भी पूछें... / কিছু জিজ্ঞাসা করুন...")
    
    if user_query:
        # Add language preference to API call
        preferred_lang = st.session_state.preferred_language
        
        # ... submit query with language context ...
```

---

### 3.3 Update API Client

**File:** `ui/api_client.py`

**Changes:**
```python
def query(self, question: str, query_type: str = "hybrid", 
          include_sources: bool = True, include_metadata: bool = True,
          language: str = "en") -> tuple[bool, dict, str]:  # NEW parameter
    """
    Submit query with language preference.
    
    Args:
        question: User query
        query_type: Type of query routing
        include_sources: Include source documents
        include_metadata: Include execution metadata
        language: Preferred language code (NEW)
    """
    # ... existing code ...
    
    payload = {
        "query": question,
        "query_type": query_type,
        "include_sources": include_sources,
        "include_metadata": include_metadata,
        "language": language  # NEW field
    }
    
    # ... rest of API call ...
```

---

### 3.4 Update Example Queries

**File:** `ui/app.py`

**Changes:**
```python
EXAMPLE_QUERIES = {
    "en": [
        "What are the different types of loans available?",
        "How can I open a Recurring Deposit (RD) account?",
        "What are the current Fixed Deposit (FD) interest rates?",
        "Explain the KYC process for new members",
        "What are the bank's operating hours?",
        "How do I become a member of the bank?"
    ],
    "hi": [
        "कितने प्रकार के ऋण उपलब्ध हैं?",
        "मैं आवर्ती जमा (RD) खाता कैसे खोल सकता हूँ?",
        "वर्तमान सावधि जमा (FD) ब्याज दरें क्या हैं?",
        "नए सदस्यों के लिए KYC प्रक्रिया समझाएं",
        "बैंक के कार्य समय क्या हैं?",
        "मैं बैंक का सदस्य कैसे बन सकता हूँ?"
    ],
    "bn": [
        "কত ধরনের ঋণ উপলব্ধ আছে?",
        "আমি কীভাবে একটি আবর্তক আমানত (RD) অ্যাকাউন্ট খুলতে পারি?",
        "বর্তমান স্থির আমানত (FD) সুদের হার কত?",
        "নতুন সদস্যদের জন্য KYC প্রক্রিয়া ব্যাখ্যা করুন",
        "ব্যাংকের কার্যকরী সময় কী?",
        "আমি কীভাবে ব্যাংকের সদস্য হতে পারি?"
    ]
}

def render_example_queries():
    """Render language-specific example queries."""
    lang = st.session_state.preferred_language
    queries = EXAMPLE_QUERIES.get(lang, EXAMPLE_QUERIES["en"])
    
    for query in queries:
        if st.button(query, key=f"ex_{hash(query)}"):
            # Submit query
            submit_query(query)
```

---

## 🔧 Phase 4: API Modifications

### 4.1 Update API Schema

**File:** `api/main.py`

**Changes:**
```python
from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    query_type: str = "hybrid"
    include_sources: bool = True
    include_metadata: bool = True
    language: str = "en"  # NEW field

class QueryResponse(BaseModel):
    answer: str
    sources: Optional[List[SourceDocument]] = None
    metadata: Optional[Dict[str, Any]] = None
    language: str  # NEW field - language of response
    original_language: Optional[str] = None  # NEW field - if translated
```

---

### 4.2 Update Query Endpoint

**File:** `api/main.py`

**Changes:**
```python
@app.post("/api/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Process query with language support."""
    
    # Validate language
    supported_languages = ["en", "hi", "bn"]
    if request.language not in supported_languages:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language. Supported: {supported_languages}"
        )
    
    # Process with language context
    result = await agent_service.process_query(
        query=request.query,
        query_type=request.query_type,
        language=request.language,  # Pass language
        include_sources=request.include_sources,
        include_metadata=request.include_metadata
    )
    
    # Return with language info
    return QueryResponse(
        answer=result["answer"],
        sources=result.get("sources"),
        metadata=result.get("metadata"),
        language=result.get("response_language", request.language),
        original_language=result.get("query_language")
    )
```

---

## 📊 Phase 5: Vector Store & RAG Modifications

### 5.1 Multilingual Document Embedding

**Challenge:** ChromaDB currently stores English documents only.

**Solutions:**

#### Option A: Translate-Then-Retrieve (Recommended for MVP)
1. Translate non-English queries to English
2. Retrieve from existing English vector store
3. Translate retrieved documents to user's language
4. Generate answer in user's language

**Pros:** No need to re-embed documents, works with existing vector DB  
**Cons:** Translation overhead, potential accuracy loss

#### Option B: Multilingual Embeddings
1. Use multilingual embedding model (e.g., `multilingual-e5-large`)
2. Re-embed all documents with multilingual model
3. Store in new collection
4. Retrieve directly in user's language

**Pros:** Better semantic search, no translation needed  
**Cons:** Need to re-process all documents, larger model

**Recommendation:** Start with **Option A**, migrate to **Option B** in production.

---

### 5.2 Update Retriever

**File:** `agents/retriever.py`

**Changes (for Option A):**
```python
def retrieve_documents(query: str, k: int = 5, language: str = "en") -> list:
    """
    Retrieve documents with language support.
    
    Args:
        query: Search query (should be in English after translation)
        k: Number of documents to retrieve
        language: Target language for documents (if translation needed)
    """
    from core.translation_service import TranslationService
    
    # Retrieve from vector store (English)
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=k)
    
    # Translate document content if needed
    if language != "en":
        translator = TranslationService()
        for doc in results:
            doc.page_content = translator.translate_from_english(
                doc.page_content, language
            )
    
    return results
```

---

## 🧪 Phase 6: Testing Strategy

### 6.1 Unit Tests

**File:** `tests/test_language_detector.py`
- Test language detection accuracy
- Test confidence thresholds
- Test edge cases (mixed language, short text)

**File:** `tests/test_translation_service.py`
- Test translation accuracy
- Test batch translation
- Test error handling

**File:** `tests/test_multilingual_prompts.py`
- Test prompt loading for each language
- Test fallback to English

---

### 6.2 Integration Tests

**File:** `tests/test_multilingual_workflow.py`
- Test end-to-end Hindi query → English processing → Hindi response
- Test end-to-end Bengali query → English processing → Bengali response
- Test language switching in conversation
- Test API agent with non-English queries
- Test RAG agent with non-English queries
- Test hybrid mode with non-English queries

---

### 6.3 UI Tests

**File:** `ui/test_multilingual_ui.py`
- Test language selector
- Test example queries in each language
- Test response display in each language
- Test language persistence across session

---

## 📈 Phase 7: Configuration & Settings

### 7.1 Update Config

**File:** `core/config.py`

**New Settings:**
```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Multilingual settings
    enable_multilingual: bool = Field(default=True, env="ENABLE_MULTILINGUAL")
    supported_languages: list = Field(default=["en", "hi", "bn"], env="SUPPORTED_LANGUAGES")
    default_language: str = Field(default="en", env="DEFAULT_LANGUAGE")
    translation_service: str = Field(default="google", env="TRANSLATION_SERVICE")  # google/indictrans/marian
    
    # Translation API keys
    google_translate_api_key: Optional[str] = Field(default=None, env="GOOGLE_TRANSLATE_API_KEY")
    
    # Language detection
    language_detection_confidence_threshold: float = Field(default=0.8, env="LANG_DETECT_CONFIDENCE")
    
    # Caching
    enable_translation_cache: bool = Field(default=True, env="ENABLE_TRANSLATION_CACHE")
```

---

### 7.2 Environment Variables

**File:** `.env`

**New Variables:**
```bash
# Multilingual Support
ENABLE_MULTILINGUAL=true
SUPPORTED_LANGUAGES=["en", "hi", "bn"]
DEFAULT_LANGUAGE="en"
TRANSLATION_SERVICE="google"

# Translation API (if using Google Translate)
GOOGLE_TRANSLATE_API_KEY="your_api_key_here"

# Language Detection
LANG_DETECT_CONFIDENCE=0.8

# Performance
ENABLE_TRANSLATION_CACHE=true
```

---

## 🚀 Phase 8: Deployment & Optimization

### 8.1 Translation Caching

**File:** `core/translation_cache.py`

**Purpose:** Cache translations to reduce API calls and improve performance

```python
import hashlib
from functools import lru_cache

class TranslationCache:
    def __init__(self):
        self.cache = {}
    
    def get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key from translation parameters."""
        content = f"{text}|{source_lang}|{target_lang}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Get cached translation."""
        key = self.get_cache_key(text, source_lang, target_lang)
        return self.cache.get(key)
    
    def set(self, text: str, source_lang: str, target_lang: str, translation: str):
        """Cache translation."""
        key = self.get_cache_key(text, source_lang, target_lang)
        self.cache[key] = translation
```

---

### 8.2 Performance Optimizations

1. **Batch Translation:** Translate multiple documents in single API call
2. **Lazy Loading:** Only translate when user requests specific language
3. **Streaming:** Stream translated responses token by token
4. **Model Quantization:** Use quantized translation models for faster inference

---

### 8.3 Monitoring & Metrics

**Metrics to track:**
- Language distribution (% queries in each language)
- Translation latency
- Translation cache hit rate
- Language detection accuracy
- User satisfaction by language

---

## 📋 Implementation Checklist

### Phase 1: Infrastructure ✅
- [ ] Install language detection library (`langdetect`)
- [ ] Install translation library (`googletrans` or alternatives)
- [ ] Create `core/language_detector.py`
- [ ] Create `core/translation_service.py`
- [ ] Create `core/translation_cache.py`
- [ ] Create `agents/prompts_multilingual.py`
- [ ] Translate all prompts to Hindi
- [ ] Translate all prompts to Bengali

### Phase 2: Core System ✅
- [ ] Update `agents/models.py` with language fields
- [ ] Create `language_detection_node` in `agents/integration_nodes.py`
- [ ] Create `query_translation_node` in `agents/integration_nodes.py`
- [ ] Create `response_translation_node` in `agents/integration_nodes.py`
- [ ] Update `router_node` for language awareness
- [ ] Update `generate_answer_node` for language awareness
- [ ] Update `agents/integrated_agent.py` workflow
- [ ] Update `agents/retriever.py` for multilingual retrieval

### Phase 3: UI ✅
- [ ] Create `ui/components/language_selector.py`
- [ ] Update `ui/app.py` with language selector
- [ ] Update `ui/api_client.py` to pass language parameter
- [ ] Create multilingual example queries
- [ ] Update chat input placeholder with multilingual text
- [ ] Update UI labels and messages for multilingual support

### Phase 4: API ✅
- [ ] Update `api/main.py` schema with language fields
- [ ] Update query endpoint to accept language parameter
- [ ] Update response model with language metadata
- [ ] Add language validation

### Phase 5: RAG ✅
- [ ] Update retriever for multilingual documents
- [ ] Add document translation logic
- [ ] Consider multilingual embeddings (future)

### Phase 6: Testing ✅
- [ ] Write unit tests for language detection
- [ ] Write unit tests for translation service
- [ ] Write unit tests for multilingual prompts
- [ ] Write integration tests for full workflow
- [ ] Write UI tests for language selector
- [ ] Manual testing with real users

### Phase 7: Configuration ✅
- [ ] Update `core/config.py` with multilingual settings
- [ ] Update `.env` with new variables
- [ ] Update documentation

### Phase 8: Deployment ✅
- [ ] Set up translation caching
- [ ] Configure monitoring
- [ ] Performance testing
- [ ] Production deployment

---

## 📊 Effort Estimation

| Phase | Tasks | Estimated Time | Priority |
|-------|-------|----------------|----------|
| Phase 1: Infrastructure | 8 tasks | 2-3 days | High |
| Phase 2: Core System | 8 tasks | 3-4 days | High |
| Phase 3: UI | 6 tasks | 2-3 days | High |
| Phase 4: API | 4 tasks | 1-2 days | High |
| Phase 5: RAG | 3 tasks | 2-3 days | Medium |
| Phase 6: Testing | 6 tasks | 2-3 days | High |
| Phase 7: Configuration | 3 tasks | 1 day | Medium |
| Phase 8: Deployment | 4 tasks | 1-2 days | Medium |
| **TOTAL** | **42 tasks** | **14-23 days** | - |

---

## 🎯 Success Criteria

1. ✅ Users can type queries in English, Hindi, or Bengali
2. ✅ System automatically detects query language (≥80% accuracy)
3. ✅ Responses are returned in the same language as query
4. ✅ Translation latency < 2 seconds per query
5. ✅ Language context maintained across conversation
6. ✅ All UI elements support language switching
7. ✅ API responses include language metadata
8. ✅ RAG retrieval works with multilingual queries
9. ✅ 100% test coverage for multilingual features
10. ✅ Documentation updated for multilingual support

---

## 🚧 Known Challenges & Mitigations

| Challenge | Mitigation |
|-----------|------------|
| Translation accuracy | Use high-quality services (Google Translate), validate with native speakers |
| Translation latency | Implement caching, batch translation, consider local models |
| Context preservation | Maintain original query, use language-aware prompts |
| Technical terminology | Build custom glossary for banking terms |
| Mixed language queries | Set confidence threshold, fallback to English |
| Document translation cost | Cache translations, consider pre-translating common documents |
| Embedding model limitations | Use multilingual models or translate-then-retrieve approach |

---

## 🔄 Future Enhancements

1. **Additional Languages:** Add more Indian languages (Tamil, Telugu, Marathi, Gujarati)
2. **Voice Input:** Speech-to-text in multiple languages
3. **Voice Output:** Text-to-speech responses
4. **Language Learning Mode:** Help users learn banking terms in different languages
5. **Transliteration:** Support for typing Hindi/Bengali in English script
6. **Document Translation:** Translate source documents on-demand
7. **Cultural Adaptation:** Culturally appropriate responses and examples
8. **Multilingual Analytics:** Language usage dashboards

---

## 📚 Dependencies & Libraries

### Required Packages
```bash
# Language Detection
langdetect==1.0.9

# Translation (choose one or more)
googletrans==4.0.0-rc1          # Google Translate (free, unofficial)
google-cloud-translate==3.12.1   # Google Cloud Translation API (official, paid)
indictrans==1.0.0               # IndicTrans2 (free, for Indian languages)
transformers==4.35.0            # For Marian/Helsinki-NLP models

# Multilingual Embeddings (future)
sentence-transformers==2.2.2    # For multilingual-e5-large

# Utilities
langcodes==3.3.0               # Language code handling
pycountry==22.3.5              # Language name mapping
```

---

## 📖 Documentation Updates Needed

1. **README.md** - Add multilingual features section
2. **UI README** - Document language selector usage
3. **API Documentation** - Document language parameter
4. **Configuration Guide** - Document multilingual settings
5. **User Guide** - How to use multilingual features
6. **Developer Guide** - How to add new languages

---

## 🎓 Training & Rollout

### Phase 1: Internal Testing (1 week)
- Test with team members who speak Hindi/Bengali
- Gather feedback on translation quality
- Fix critical issues

### Phase 2: Beta Release (2 weeks)
- Release to select users
- Monitor usage and errors
- Collect user feedback

### Phase 3: Production Release
- Full rollout with monitoring
- User training materials
- Support documentation

---

**Next Steps:** 
1. Review and approve this plan
2. Set up development environment
3. Begin Phase 1 implementation
4. Schedule regular check-ins for progress updates

---

**Document Version:** 1.0  
**Last Updated:** November 5, 2025  
**Owner:** AasthaSathi Development Team
