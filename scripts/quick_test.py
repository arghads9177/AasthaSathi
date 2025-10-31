"""
Quick test of provider fallback system.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 80)
print("QUICK PROVIDER FALLBACK TEST")
print("=" * 80)

# Test 1: Import all modules
print("\n[1/4] Testing imports...")
try:
    from core.config import get_provider_manager, Settings
    from agents.router import QueryRouter
    from agents.api_agent import APIAgent
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Provider Manager initialization
print("\n[2/4] Testing Provider Manager initialization...")
try:
    settings = Settings()
    print(f"  - Fallback enabled: {settings.enable_llm_fallback}")
    print(f"  - Fallback provider: {settings.fallback_llm_provider}")
    
    provider_manager = get_provider_manager()
    print(f"  - Providers loaded: {len(provider_manager.providers)}")
    
    for provider in provider_manager.providers:
        print(f"    • {provider.name} (priority={provider.priority}, model={provider.model})")
    
    print("✓ Provider Manager initialized")
except Exception as e:
    print(f"✗ Provider Manager initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Simple invocation
print("\n[3/4] Testing simple LLM invocation...")
try:
    messages = [{"role": "user", "content": "Say 'Hello' in one word"}]
    result = provider_manager.invoke_with_fallback(messages, temperature=0)
    
    print(f"  - Provider used: {result['provider']}")
    print(f"  - Model: {result['model']}")
    print(f"  - Response: {result['response'][:50]}...")
    print("✓ Simple invocation successful")
except Exception as e:
    print(f"✗ Invocation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Statistics
print("\n[4/4] Testing statistics...")
try:
    stats = provider_manager.get_manager_stats()
    print(f"  - Total requests: {stats['total_requests']}")
    print(f"  - Successful: {stats['successful_requests']}")
    print(f"  - Failed: {stats['failed_requests']}")
    print(f"  - Fallbacks: {stats['fallback_count']}")
    print(f"  - Success rate: {stats['success_rate']:.1%}")
    print("✓ Statistics working")
except Exception as e:
    print(f"✗ Statistics failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("ALL TESTS PASSED! ✓")
print("=" * 80)
