# Quick Fix: Update Provider Models

## Issue
Current provider models are outdated or incorrect:
- Groq: `llama-3.1-70b-versatile` (decommissioned)
- Gemini: `gemini-1.5-flash` (wrong API version)

## Solution

Update `core/config.py` with current model names:

### Step 1: Check Available Models

**Groq Models (as of Oct 2025):**
- `llama-3.3-70b-versatile` - Recommended (newest)
- `llama-3.1-8b-instant` - Fast & cheap
- `mixtral-8x7b-32768` - Good alternative

**Gemini Models:**
- `gemini-1.5-pro` - Recommended
- `gemini-pro` - Standard version

### Step 2: Update Config

Edit `core/config.py`:

```python
# Line ~40-50 - Update Groq settings
fallback_model: str = "llama-3.3-70b-versatile"  # Changed from llama-3.1-70b-versatile

# For get_provider_manager() function (around line 80):
groq_provider = GroqProvider(
    api_key=self.groq_api_key,
    model="llama-3.3-70b-versatile",  # Updated model
    priority=2
)

gemini_provider = GeminiProvider(
    api_key=self.google_api_key,
    model="gemini-1.5-pro",  # Changed from gemini-1.5-flash
    priority=3
)
```

### Step 3: Test Again

```bash
python scripts/quick_test.py
```

### Expected Result

✅ System should work with at least one provider:
- If OpenAI has quota → Fallback to Groq ✓
- If Groq fails → Fallback to Gemini ✓

## Alternative: Use Only Working Providers

If you want to temporarily disable problematic providers:

### Option A: OpenAI + Groq Only

In `core/config.py`, comment out Gemini:

```python
def get_provider_manager(self):
    providers = [
        OpenAIProvider(...),
        GroqProvider(...),
        # GeminiProvider(...),  # Disabled for now
    ]
```

### Option B: Use Environment Variable

Add to `.env`:
```bash
# Enable only specific providers
ENABLED_PROVIDERS=openai,groq
```

Then update `config.py` to read this setting.

## Quick Command Reference

```bash
# Test with updated config
python scripts/quick_test.py

# Test full API
./start_api.sh

# Check provider stats
python -c "from core.config import get_provider_manager; pm = get_provider_manager(); print(pm.get_manager_stats())"
```

## Recommended Configuration

For production use:

```python
# Primary: OpenAI (best quality)
openai_model: str = "gpt-4"  # or gpt-4-turbo-preview

# Fallback: Groq (fast, cheap)
fallback_model: str = "llama-3.3-70b-versatile"

# Final: Gemini (free tier)
gemini_model: str = "gemini-1.5-pro"
```

This gives you:
1. Best quality (OpenAI)
2. Fast fallback (Groq)
3. Free backup (Gemini)
