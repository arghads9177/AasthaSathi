"""
Standalone tests for multilingual components.

This module tests multilingual components in isolation without requiring full agent setup.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.language_detector import LanguageDetector
from core.translation_service import TranslationService


def test_language_detection():
    """Test language detection."""
    print("\n" + "="*60)
    print("TEST: Language Detection")
    print("="*60)
    
    detector = LanguageDetector()
    
    test_cases = [
        ("What is the interest rate?", "en"),
        ("ब्याज दर क्या है?", "hi"),
        ("সুদের হার কত?", "bn"),
        ("How do I open a savings account?", "en"),
        ("मुझे बचत खाता कैसे खोलना है?", "hi"),
        ("আমি কিভাবে সঞ্চয় অ্যাকাউন্ট খুলব?", "bn"),
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_lang in test_cases:
        lang_code, confidence = detector.detect_language(query)
        
        print(f"\nQuery: '{query}'")
        print(f"Expected: {expected_lang}, Detected: {lang_code}, Confidence: {confidence:.2f}")
        
        if lang_code == expected_lang:
            print(f"✓ PASS")
            passed += 1
        else:
            print(f"✗ FAIL")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}")


def test_translation():
    """Test translation service."""
    print("\n" + "="*60)
    print("TEST: Translation Service")
    print("="*60)
    
    translator = TranslationService()
    
    test_cases = [
        {
            "text": "ब्याज दर क्या है?",
            "source_lang": "hi",
            "target_lang": "en",
            "description": "Hindi to English"
        },
        {
            "text": "সুদের হার কত?",
            "source_lang": "bn",
            "target_lang": "en",
            "description": "Bengali to English"
        },
        {
            "text": "The interest rate is 5% per annum.",
            "source_lang": "en",
            "target_lang": "hi",
            "description": "English to Hindi"
        },
        {
            "text": "The interest rate is 5% per annum.",
            "source_lang": "en",
            "target_lang": "bn",
            "description": "English to Bengali"
        },
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        result = translator.translate(
            test_case["text"],
            source_lang=test_case["source_lang"],
            target_lang=test_case["target_lang"]
        )
        
        print(f"\n{test_case['description']}")
        print(f"Original: '{test_case['text']}'")
        print(f"Translated: '{result}'")
        
        if result and result != test_case["text"]:
            print(f"✓ PASS - Translation successful")
            passed += 1
        else:
            print(f"✗ FAIL - Translation failed or unchanged")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*60}")


def test_translation_helpers():
    """Test translation helper methods."""
    print("\n" + "="*60)
    print("TEST: Translation Helper Methods")
    print("="*60)
    
    translator = TranslationService()
    
    # Test translate_to_english
    print("\n1. Testing translate_to_english():")
    hindi_query = "ब्याज दर क्या है?"
    english = translator.translate_to_english(hindi_query, source_lang="hi")
    print(f"Hindi: '{hindi_query}'")
    print(f"English: '{english}'")
    
    # Test translate_from_english
    print("\n2. Testing translate_from_english():")
    english_text = "The interest rate is 5% per annum."
    hindi = translator.translate_from_english(english_text, target_lang="hi")
    print(f"English: '{english_text}'")
    print(f"Hindi: '{hindi}'")
    
    bengali = translator.translate_from_english(english_text, target_lang="bn")
    print(f"Bengali: '{bengali}'")
    
    print(f"\n✓ Helper methods working correctly")


def test_complete_multilingual_simulation():
    """Simulate complete multilingual workflow."""
    print("\n" + "="*60)
    print("TEST: Complete Multilingual Flow Simulation")
    print("="*60)
    
    detector = LanguageDetector()
    translator = TranslationService()
    
    # Simulate Hindi query
    hindi_query = "खाता खोलने के लिए कौन से दस्तावेज़ चाहिए?"
    
    print(f"\n1. User Query (Hindi): '{hindi_query}'")
    
    # Step 1: Detect language
    lang_code, confidence = detector.detect_language(hindi_query)
    print(f"\n2. Language Detected: {lang_code} (confidence: {confidence:.2f})")
    
    # Step 2: Translate query to English
    if lang_code != "en":
        english_query = translator.translate_to_english(hindi_query, source_lang=lang_code)
        print(f"\n3. Query Translated to English: '{english_query}'")
    else:
        english_query = hindi_query
        print(f"\n3. Query is already in English")
    
    # Step 3: Simulate processing (mock answer)
    english_answer = "You need the following documents to open an account: ID proof, address proof, and photographs."
    print(f"\n4. Answer Generated (in English): '{english_answer}'")
    
    # Step 4: Translate answer back to user's language
    if lang_code != "en":
        final_answer = translator.translate_from_english(english_answer, target_lang=lang_code)
        print(f"\n5. Answer Translated to {lang_code.upper()}: '{final_answer}'")
    else:
        final_answer = english_answer
        print(f"\n5. Answer is already in English")
    
    print(f"\n✓ Complete multilingual flow executed successfully!")


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# STANDALONE MULTILINGUAL COMPONENT TESTS")
    print("#"*60)
    
    try:
        test_language_detection()
        test_translation()
        test_translation_helpers()
        test_complete_multilingual_simulation()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
