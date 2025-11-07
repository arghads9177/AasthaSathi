"""
Tests for multilingual workflow integration.

This module tests the complete multilingual workflow including:
- Language detection
- Query translation
- Response translation
- Integration with router and RAG nodes
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.models import AgentState
from agents.integration_nodes import (
    language_detection_node,
    query_translation_node,
    response_translation_node
)


def test_language_detection_workflow():
    """Test language detection in workflow."""
    print("\n" + "="*60)
    print("TEST: Language Detection Workflow")
    print("="*60)
    
    # Test cases
    test_cases = [
        ("What is the interest rate?", "en"),
        ("ब्याज दर क्या है?", "hi"),
        ("সুদের হার কত?", "bn"),
    ]
    
    for query, expected_lang in test_cases:
        state: AgentState = {
            "user_query": query,
            "chat_history": [],
            "execution_path": []
        }
        
        result = language_detection_node(state)
        
        detected_lang = result.get("query_language", "unknown")
        confidence = result.get("query_language_confidence", 0.0)
        
        print(f"\nQuery: '{query}'")
        print(f"Expected: {expected_lang}, Detected: {detected_lang}, Confidence: {confidence:.2f}")
        print(f"✓ PASS" if detected_lang == expected_lang else f"✗ FAIL")


def test_query_translation_workflow():
    """Test query translation in workflow."""
    print("\n" + "="*60)
    print("TEST: Query Translation Workflow")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            "query": "What is the interest rate?",
            "language": "en",
            "should_translate": False
        },
        {
            "query": "ब्याज दर क्या है?",
            "language": "hi",
            "should_translate": True
        },
        {
            "query": "সুদের হার কত?",
            "language": "bn",
            "should_translate": True
        },
    ]
    
    for test_case in test_cases:
        state: AgentState = {
            "user_query": test_case["query"],
            "query_language": test_case["language"],
            "original_query": test_case["query"],
            "chat_history": [],
            "execution_path": []
        }
        
        result = query_translation_node(state)
        
        translated = result.get("translated_query")
        
        print(f"\nOriginal Query: '{test_case['query']}'")
        print(f"Language: {test_case['language']}")
        print(f"Should Translate: {test_case['should_translate']}")
        print(f"Translated Query: '{translated}'")
        
        if test_case["should_translate"]:
            if translated and translated != test_case["query"]:
                print(f"✓ PASS - Query was translated")
            else:
                print(f"✗ FAIL - Query should have been translated")
        else:
            if not translated:
                print(f"✓ PASS - English query, no translation needed")
            else:
                print(f"✗ FAIL - English query should not be translated")


def test_response_translation_workflow():
    """Test response translation in workflow."""
    print("\n" + "="*60)
    print("TEST: Response Translation Workflow")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            "answer": "The interest rate is 5% per annum.",
            "response_language": "en",
            "should_translate": False
        },
        {
            "answer": "The interest rate is 5% per annum.",
            "response_language": "hi",
            "should_translate": True
        },
        {
            "answer": "The interest rate is 5% per annum.",
            "response_language": "bn",
            "should_translate": True
        },
    ]
    
    for test_case in test_cases:
        state: AgentState = {
            "user_query": "test",
            "answer": test_case["answer"],
            "response_language": test_case["response_language"],
            "chat_history": [],
            "execution_path": []
        }
        
        result = response_translation_node(state)
        
        translated_answer = result.get("answer")
        
        print(f"\nOriginal Answer: '{test_case['answer']}'")
        print(f"Response Language: {test_case['response_language']}")
        print(f"Should Translate: {test_case['should_translate']}")
        print(f"Translated Answer: '{translated_answer}'")
        
        if test_case["should_translate"]:
            if translated_answer != test_case["answer"]:
                print(f"✓ PASS - Answer was translated")
            else:
                print(f"✗ FAIL - Answer should have been translated")
        else:
            if translated_answer == test_case["answer"]:
                print(f"✓ PASS - English answer, no translation needed")
            else:
                print(f"✗ FAIL - English answer should not change")


def test_complete_multilingual_flow():
    """Test complete multilingual flow: detection → translation → processing."""
    print("\n" + "="*60)
    print("TEST: Complete Multilingual Flow")
    print("="*60)
    
    # Hindi query
    hindi_query = "ब्याज दर क्या है?"
    
    print(f"\nProcessing Hindi query: '{hindi_query}'")
    
    # Step 1: Language Detection
    state: AgentState = {
        "user_query": hindi_query,
        "chat_history": [],
        "execution_path": []
    }
    
    state = language_detection_node(state)
    print(f"\n1. Language Detected: {state.get('query_language')} "
          f"(confidence: {state.get('query_language_confidence', 0):.2f})")
    
    # Step 2: Query Translation
    state = query_translation_node(state)
    print(f"2. Query Translated: '{state.get('translated_query')}'")
    
    # Step 3: Mock processing (would be router → retrieve → generate)
    state["answer"] = "The interest rate is 5% per annum."
    print(f"3. Answer Generated (in English): '{state['answer']}'")
    
    # Step 4: Response Translation
    state = response_translation_node(state)
    print(f"4. Answer Translated (to Hindi): '{state['answer']}'")
    
    print(f"\n✓ Complete multilingual flow executed successfully")


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# MULTILINGUAL WORKFLOW INTEGRATION TESTS")
    print("#"*60)
    
    try:
        test_language_detection_workflow()
        test_query_translation_workflow()
        test_response_translation_workflow()
        test_complete_multilingual_flow()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
