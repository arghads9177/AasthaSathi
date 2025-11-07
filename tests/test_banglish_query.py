"""
Test Banglish (Bengali written in English script) query handling.

Issue: "Amar member number SM-1388. amar ki ki running account ache?" 
       returns "member not found" even though member exists.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.translation_service import TranslationService
from core.language_detector import LanguageDetector

def test_banglish_detection():
    """Test what language is detected for Banglish text."""
    query = "Amar member number SM-1388. amar ki ki running account ache?"
    
    detector = LanguageDetector()
    lang_code, confidence = detector.detect_language(query)
    
    print("=" * 80)
    print("TEST 1: Language Detection for Banglish")
    print("=" * 80)
    print(f"Query: {query}")
    print(f"Detected Language: {lang_code}")
    print(f"Confidence: {confidence:.2%}")
    print()

def test_banglish_translation():
    """Test what translation service returns for Banglish."""
    query = "Amar member number SM-1388. amar ki ki running account ache?"
    
    service = TranslationService()
    detector = LanguageDetector()
    
    # Detect language first
    detected_lang, confidence = detector.detect_language(query)
    
    print("=" * 80)
    print("TEST 2: Translation of Banglish")
    print("=" * 80)
    print(f"Original Query: {query}")
    print(f"Detected as: {detected_lang} (confidence: {confidence:.2%})")
    
    if detected_lang != 'en':
        translated = service.translate(query, source_lang=detected_lang, target_lang='en')
        print(f"Translated Query: {translated}")
    else:
        print(f"No translation needed (detected as English)")
        print(f"Query remains: {query}")
    print()

def test_member_id_extraction():
    """Test if member ID SM-1388 is preserved in translation."""
    queries = [
        "Amar member number SM-1388. amar ki ki running account ache?",
        "My member number is SM-1388. What running accounts do I have?",
        "মেম্বার নম্বর SM-1388. আমার কি কি রানিং একাউন্ট আছে?"
    ]
    
    service = TranslationService()
    detector = LanguageDetector()
    
    print("=" * 80)
    print("TEST 3: Member ID Preservation in Translation")
    print("=" * 80)
    
    for query in queries:
        detected_lang, confidence = detector.detect_language(query)
        
        print(f"\nOriginal: {query}")
        print(f"Language: {detected_lang} (confidence: {confidence:.2%})")
        
        if detected_lang != 'en':
            translated = service.translate(query, source_lang=detected_lang, target_lang='en')
            print(f"Translated: {translated}")
            
            # Check if SM-1388 is preserved
            if 'SM-1388' in translated or 'SM-1388' in query:
                print(f"✓ Member ID preserved: SM-1388 found")
            else:
                print(f"✗ Member ID LOST: SM-1388 not found in translated text")
        else:
            print(f"Stays: {query}")
            print(f"✓ Member ID preserved: SM-1388 found")
        print("-" * 80)

def test_full_workflow_simulation():
    """Simulate the full workflow to see where the issue occurs."""
    from agents.integration_nodes import language_detection_node, query_translation_node
    from core.state import InputState
    
    query = "Amar member number SM-1388. amar ki ki running account ache?"
    
    print("=" * 80)
    print("TEST 4: Full Workflow Simulation")
    print("=" * 80)
    print(f"Input Query: {query}")
    print()
    
    # Step 1: Language Detection
    state = {"original_query": query}
    state = language_detection_node(state)
    print(f"Step 1 - Language Detection:")
    print(f"  Detected Language: {state['detected_language']}")
    print(f"  Confidence: {state.get('language_confidence', 'N/A')}")
    print()
    
    # Step 2: Query Translation
    state = query_translation_node(state)
    print(f"Step 2 - Query Translation:")
    print(f"  Translated Query: {state.get('translated_query')}")
    print(f"  Translation Success: {state.get('translation_success')}")
    print()
    
    # Check if member ID is in translated query
    translated = state.get('translated_query', '')
    if 'SM-1388' in translated:
        print(f"✓ Member ID SM-1388 preserved in translated query")
    else:
        print(f"✗ WARNING: Member ID SM-1388 NOT found in translated query!")
        print(f"  This will cause API to look for wrong member!")
    print()

if __name__ == "__main__":
    test_banglish_detection()
    test_banglish_translation()
    test_member_id_extraction()
    test_full_workflow_simulation()
    
    print("\n" + "=" * 80)
    print("DIAGNOSIS SUMMARY")
    print("=" * 80)
    print("If member ID is lost in translation, the API will fail.")
    print("If language is detected as English, no translation happens (good).")
    print("If detected as Hindi/Bengali, translation may corrupt member ID.")
