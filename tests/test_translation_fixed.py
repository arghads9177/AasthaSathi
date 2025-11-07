"""
Quick Test: Translation Service with deep-translator

Tests the updated translation service to verify it works with deep-translator.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.translation_service import TranslationService


def print_separator(title: str):
    """Print a formatted separator."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_translation_basic():
    """Test basic translation functionality."""
    print_separator("BASIC TRANSLATION TEST")
    
    service = TranslationService(enable_cache=False, retry_attempts=2)
    
    test_cases = [
        ("Hello", "en", "hi", "नमस्ते"),
        ("Hello", "en", "bn", "হ্যালো"),
        ("बैलेंस क्या है?", "hi", "en", "What is the balance?"),
        ("আস্থা র উদ্যোগ কি কি?", "bn", "en", "What are the initiatives of Aastha?"),
    ]
    
    for text, src, tgt, expected_pattern in test_cases:
        print(f"Translating: '{text}'")
        print(f"From: {src} → To: {tgt}")
        
        try:
            result = service.translate(text, src, tgt)
            
            if result:
                print(f"Result: '{result}'")
                print(f"Status: ✓ SUCCESS")
            else:
                print(f"Result: None")
                print(f"Status: ✗ FAILED - Translation returned None")
        except Exception as e:
            print(f"Status: ✗ ERROR - {str(e)}")
        
        print("-" * 60)


def test_your_bengali_query():
    """Test the specific Bengali query from user."""
    print_separator("USER'S BENGALI QUERY TEST")
    
    query = "আস্থা র উদ্যোগ কি কি?"
    print(f"Original Query (Bengali): {query}")
    
    service = TranslationService(enable_cache=False)
    
    try:
        # Translate Bengali to English
        english_query = service.translate_to_english(query, "bn")
        
        if english_query:
            print(f"Translated Query (English): {english_query}")
            print(f"\nStatus: ✓ Translation successful")
            print(f"This query should now route to RAG and retrieve documents")
        else:
            print(f"Translation failed - returned None")
            print(f"Status: ✗ FAILED")
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Status: ✗ ERROR")


def test_hindi_queries():
    """Test Hindi queries."""
    print_separator("HINDI QUERY TEST")
    
    service = TranslationService(enable_cache=False)
    
    queries = [
        "मेरा खाता शेष क्या है?",  # What is my account balance? (API)
        "ऋण के प्रकार क्या हैं?",    # What are the types of loans? (RAG)
    ]
    
    for query in queries:
        print(f"\nHindi Query: {query}")
        
        try:
            english = service.translate_to_english(query, "hi")
            
            if english:
                print(f"English: {english}")
                print(f"Status: ✓ SUCCESS")
            else:
                print(f"Status: ✗ FAILED")
        except Exception as e:
            print(f"Error: {str(e)}")
            print(f"Status: ✗ ERROR")


def test_full_workflow_with_translation():
    """Test full workflow with translated Bengali query."""
    print_separator("FULL WORKFLOW TEST - BENGALI RAG QUERY")
    
    print("Testing Bengali query through complete workflow...")
    print("Query: 'আস্থা র উদ্যোগ কি কি?' (What are the initiatives of Aastha?)")
    print("-" * 60)
    
    try:
        from agents.integrated_agent import get_integrated_agent
        
        agent = get_integrated_agent()
        result = agent.query("আস্থা র উদ্যোগ কি কি?", language="bn")
        
        print(f"\nQuery Language: {result.get('query_language', 'N/A')}")
        print(f"Query Language Confidence: {result.get('query_language_confidence', 0):.2%}")
        print(f"Datasource: {result.get('datasource', 'N/A')}")
        print(f"Routing Reasoning: {result.get('routing_reasoning', 'N/A')[:150]}...")
        print(f"\nDocs Retrieved: {result.get('num_retrieved', 0)}")
        print(f"Docs Relevant: {result.get('num_relevant', 0)}")
        print(f"\nAnswer Preview: {result.get('answer', 'N/A')[:200]}...")
        print(f"\nExecution Path: {' → '.join(result.get('execution_path', [])[:10])}")
        
        # Validate result
        datasource = result.get('datasource', '')
        answer = result.get('answer', '')
        
        if datasource in ['rag', 'hybrid'] and 'Bengali' not in answer:
            print(f"\n✓ SUCCESS - Query processed correctly through RAG")
        elif 'Bengali' in answer or "can't understand" in answer.lower():
            print(f"\n✗ FAILED - Translation did not work, model couldn't understand")
        else:
            print(f"\n⚠ PARTIAL - Check answer to verify correctness")
            
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Run all translation tests."""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "  TRANSLATION SERVICE TEST (deep-translator)".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    
    try:
        # Test basic translation
        test_translation_basic()
        
        # Test user's specific Bengali query
        test_your_bengali_query()
        
        # Test Hindi queries
        test_hindi_queries()
        
        # Test full workflow
        test_full_workflow_with_translation()
        
        print_separator("ALL TESTS COMPLETED")
        print("\nIf all tests passed, the translation service is working correctly.")
        print("Your Bengali query should now work through the UI/API!")
        
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
