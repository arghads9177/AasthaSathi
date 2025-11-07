# Multilingual Query Improvement Plan

## Problem Analysis

### Your Test Case
**Query (Bengali)**: "আস্থা র উদ্যোগ কি কি?"  
**Translation**: "What are the initiatives of Aastha?" or "What are Aastha's schemes?"  
**Expected**: Should query RAG knowledge base (documents about schemes/initiatives)  
**Actual Result**: Model responded saying it can't understand Bengali

### Root Cause
1. Translation service fails (httpcore dependency conflict)
2. Query remains in Bengali: "আস্থা র উদ্যোগ কি কি?"
3. Router receives Bengali text (can't process non-English)
4. Router defaults to explaining it can't understand Bengali
5. Result: No translation → No proper routing → No answer

### Why One Bengali Query Worked
If one Bengali query about API worked, it might be because:
- The model recognized patterns/keywords even in Bengali
- Or it was routed to API by chance/default behavior
- But this is unreliable without proper translation

## Solution Plan

### Phase 1: Fix Translation Service (CRITICAL)
**Replace googletrans with deep-translator**

#### Step 1: Install deep-translator
```bash
pip install deep-translator
```

#### Step 2: Update core/translation_service.py
Replace GoogleTranslator import and implementation:
```python
from deep_translator import GoogleTranslator

# Old: from googletrans import Translator
# New: Use GoogleTranslator from deep-translator
```

**Advantages of deep-translator**:
- ✅ No httpcore dependency conflict
- ✅ Actively maintained (2024 updates)
- ✅ Supports 100+ languages including Hindi/Bengali
- ✅ Simple API, similar to googletrans
- ✅ Better error handling
- ✅ Can use multiple translation engines (Google, Microsoft, etc.)

#### Step 3: Update Translation Methods
```python
# Old googletrans API:
result = self.translator.translate(text, src=source_lang, dest=target_lang)
translated_text = result.text

# New deep-translator API:
translator = GoogleTranslator(source=source_lang, target=target_lang)
translated_text = translator.translate(text)
```

### Phase 2: Improve Translation Error Handling

#### Current Behavior on Translation Failure
- Retries 3 times
- Falls back to original query
- Continues processing (may fail downstream)

#### Improved Behavior
1. **Attempt Translation**: Try with retry logic
2. **On Failure**: Log detailed error
3. **Fallback Options**:
   - Option A: Use original query + add note in response
   - Option B: Return error asking for English query
   - Option C: Use keyword extraction for basic routing
4. **User Notification**: Inform that translation failed, answer may be limited

### Phase 3: Enhance Routing for Non-English Queries

#### Current Flow
```
Bengali Query → Translation FAILS → Router gets Bengali → ???
```

#### Improved Flow
```
Bengali Query → Translation SUCCESS → Router gets English → Correct routing
              ↓ (if fails)
              Use language-aware router with Bengali support
```

#### Implementation
1. **Multilingual Router Prompts**: Already implemented ✓
2. **Language Detection First**: Already working ✓
3. **Translation Before Routing**: Needs fixing (Phase 1)
4. **Fallback Router**: Add router that can handle non-English queries

### Phase 4: Testing Strategy

#### Test Scenarios
1. **English API Query**: "What is my account balance?" → Should work ✓
2. **English RAG Query**: "What are the loan types?" → Should work ✓
3. **Hindi API Query**: "मेरा खाता शेष क्या है?" → Should translate & work
4. **Hindi RAG Query**: "ऋण के प्रकार क्या हैं?" → Should translate & work
5. **Bengali API Query**: "আমার একাউন্ট ব্যালেন্স কত?" → Should translate & work
6. **Bengali RAG Query**: "আস্থা র উদ্যোগ কি কি?" → Should translate & work (YOUR CASE)

#### Test Cases for Your Specific Query
```python
Query: "আস্থা র উদ্যোগ কি কি?"
Expected Translation: "What are the initiatives of Aastha?" 
                      or "What are Aastha's schemes?"
Expected Route: RAG (knowledge base query)
Expected Result: List of schemes/initiatives from documents
```

## Implementation Steps

### Step 1: Install and Configure deep-translator
```bash
# In virtualenv
source .venv/bin/activate
pip uninstall googletrans googletrans-py -y
pip install deep-translator
```

### Step 2: Update core/translation_service.py
Changes needed:
1. Import: `from deep_translator import GoogleTranslator`
2. Remove lazy import complexity (no httpcore issues)
3. Update `_get_translator()` method
4. Update `translate()` method API calls
5. Add better error messages

### Step 3: Update agents/integration_nodes.py
Enhancements:
1. Better error logging when translation fails
2. Add fallback query text in state
3. Pass translation status to downstream nodes

### Step 4: Testing
```bash
# Run updated diagnostic tests
python tests/test_workflow_diagnostics.py

# Test your specific Bengali query
python -c "
from agents.integrated_agent import get_integrated_agent
agent = get_integrated_agent()
result = agent.query('আস্থা র উদ্যোগ কি কি?', language='bn')
print(result['answer'])
"
```

### Step 5: Validate UI/API
1. Restart API server
2. Test through Streamlit UI
3. Try all three languages
4. Verify routing decisions

## Expected Outcomes After Fix

### Your Bengali Query Flow
```
Input: "আস্থা র উদ্যোগ কি কি?"
  ↓
Language Detection: Bengali (bn) - 100% confidence ✓
  ↓
Translation: "What are the initiatives of Aastha?" ✓
  ↓
Router: RAG (knowledge base query) ✓
  ↓
Retrieval: Documents about Aastha schemes ✓
  ↓
Generation: Answer in English ✓
  ↓
Response Translation: Back to Bengali ✓
  ↓
Final Answer: "আস্থার উদ্যোগ হলো..." ✓
```

## Risk Mitigation

### If deep-translator Also Fails
**Fallback Plan**:
1. Use `py-googletrans` (different package, more maintained)
2. Use `translate` library (simple, lightweight)
3. Implement basic keyword translation dictionary
4. Use Azure Translator or Google Cloud Translation API

### Temporary Workaround for Demo
Create a translation dictionary for common queries:
```python
COMMON_TRANSLATIONS = {
    'bn': {
        'আস্থা র উদ্যোগ কি কি?': 'What are the initiatives of Aastha?',
        'আমার একাউন্ট ব্যালেন্স কত?': 'What is my account balance?',
    },
    'hi': {
        'आस्था की पहल क्या हैं?': 'What are the initiatives of Aastha?',
        'मेरा खाता शेष क्या है?': 'What is my account balance?',
    }
}
```

## Timeline

1. **Immediate** (15 minutes): Install deep-translator, update translation_service.py
2. **Short-term** (30 minutes): Test and validate all language combinations
3. **Medium-term** (1 hour): Full regression testing, UI validation
4. **Long-term**: Consider Google Cloud Translation for production

## Success Criteria

✅ Bengali query "আস্থা র উদ্যোগ কি কি?" returns information about Aastha schemes  
✅ All Hindi queries work (API and RAG types)  
✅ All Bengali queries work (API and RAG types)  
✅ English queries continue to work  
✅ Responses translated back to query language  
✅ No httpcore dependency conflicts  
✅ All diagnostic tests pass  

## Next Actions

1. **IMPLEMENT**: Replace googletrans with deep-translator
2. **TEST**: Run diagnostic suite
3. **VALIDATE**: Test your specific Bengali query
4. **DEPLOY**: Update API and UI servers
5. **DOCUMENT**: Update requirements.txt and README

Would you like me to proceed with implementing the deep-translator solution now?
