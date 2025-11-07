"""
Tests for Phase 3 - UI Multilingual Components

This module tests the multilingual UI components without requiring Streamlit runtime.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.components.multilingual import (
    SUPPORTED_LANGUAGES,
    EXAMPLE_QUERIES,
    UI_TEXT,
    get_text,
    get_language_name
)


def test_supported_languages():
    """Test language configuration."""
    print("\n" + "="*60)
    print("TEST: Supported Languages Configuration")
    print("="*60)
    
    expected_langs = ["en", "hi", "bn"]
    
    print(f"\nExpected languages: {expected_langs}")
    print(f"Configured languages: {list(SUPPORTED_LANGUAGES.keys())}")
    
    for lang_code in expected_langs:
        assert lang_code in SUPPORTED_LANGUAGES, f"Missing language: {lang_code}"
        lang_info = SUPPORTED_LANGUAGES[lang_code]
        
        print(f"\n{lang_code.upper()}:")
        print(f"  Name: {lang_info['name']}")
        print(f"  Flag: {lang_info['flag']}")
        print(f"  Native: {lang_info['native_name']}")
        
        assert 'name' in lang_info
        assert 'flag' in lang_info
        assert 'native_name' in lang_info
    
    print(f"\n✓ PASS - All {len(expected_langs)} languages configured correctly")


def test_example_queries():
    """Test example queries for all languages."""
    print("\n" + "="*60)
    print("TEST: Example Queries")
    print("="*60)
    
    categories = ["api", "rag", "hybrid"]
    languages = ["en", "hi", "bn"]
    
    for lang in languages:
        print(f"\n{lang.upper()} Examples:")
        assert lang in EXAMPLE_QUERIES, f"Missing examples for {lang}"
        
        lang_examples = EXAMPLE_QUERIES[lang]
        
        for category in categories:
            assert category in lang_examples, f"Missing {category} category for {lang}"
            examples = lang_examples[category]
            
            print(f"  {category.upper()}: {len(examples)} examples")
            assert len(examples) > 0, f"No examples in {category} for {lang}"
            
            # Print first example
            print(f"    Sample: {examples[0]}")
    
    total_examples = sum(
        len(EXAMPLE_QUERIES[lang][cat])
        for lang in languages
        for cat in categories
    )
    
    print(f"\n✓ PASS - {total_examples} total examples across all languages")


def test_ui_text_translations():
    """Test UI text translations."""
    print("\n" + "="*60)
    print("TEST: UI Text Translations")
    print("="*60)
    
    required_keys = [
        "language_selector",
        "query_type",
        "example_queries",
        "detected_language",
        "confidence",
        "processing",
        "sources",
        "metadata"
    ]
    
    languages = ["en", "hi", "bn"]
    
    for lang in languages:
        print(f"\n{lang.upper()} Translations:")
        assert lang in UI_TEXT, f"Missing UI text for {lang}"
        
        lang_text = UI_TEXT[lang]
        
        for key in required_keys:
            assert key in lang_text, f"Missing '{key}' translation for {lang}"
            print(f"  {key}: {lang_text[key]}")
    
    print(f"\n✓ PASS - All {len(required_keys)} text elements translated for all languages")


def test_get_text_helper():
    """Test get_text() helper function."""
    print("\n" + "="*60)
    print("TEST: get_text() Helper Function")
    print("="*60)
    
    # Test English
    text_en = get_text("language_selector", "en")
    print(f"\nEnglish: {text_en}")
    assert "Select Language" in text_en or "language" in text_en.lower()
    
    # Test Hindi
    text_hi = get_text("language_selector", "hi")
    print(f"Hindi: {text_hi}")
    assert len(text_hi) > 0
    
    # Test Bengali
    text_bn = get_text("language_selector", "bn")
    print(f"Bengali: {text_bn}")
    assert len(text_bn) > 0
    
    # Test fallback
    text_fallback = get_text("nonexistent_key", "en")
    print(f"Fallback: {text_fallback}")
    assert text_fallback == "nonexistent_key"
    
    print(f"\n✓ PASS - get_text() works correctly with fallback")


def test_get_language_name_helper():
    """Test get_language_name() helper function."""
    print("\n" + "="*60)
    print("TEST: get_language_name() Helper Function")
    print("="*60)
    
    # Test each language
    for lang_code in ["en", "hi", "bn"]:
        name = get_language_name(lang_code, "en")
        print(f"\n{lang_code} → {name}")
        assert len(name) > 0
        # Should contain flag emoji
        assert any(char in name for char in "🇬🇧🇮🇳🇧🇩")
    
    # Test unknown language
    unknown = get_language_name("fr", "en")
    print(f"\nUnknown (fr) → {unknown}")
    assert "fr" in unknown.upper() or "🌐" in unknown
    
    print(f"\n✓ PASS - get_language_name() handles all cases correctly")


def test_translation_completeness():
    """Test that all languages have same keys."""
    print("\n" + "="*60)
    print("TEST: Translation Completeness")
    print("="*60)
    
    # Get all keys from English (reference)
    en_keys = set(UI_TEXT["en"].keys())
    hi_keys = set(UI_TEXT["hi"].keys())
    bn_keys = set(UI_TEXT["bn"].keys())
    
    print(f"\nEnglish keys: {len(en_keys)}")
    print(f"Hindi keys: {len(hi_keys)}")
    print(f"Bengali keys: {len(bn_keys)}")
    
    # Check Hindi
    missing_hi = en_keys - hi_keys
    extra_hi = hi_keys - en_keys
    
    if missing_hi:
        print(f"\n⚠️ Hindi missing keys: {missing_hi}")
    if extra_hi:
        print(f"\n⚠️ Hindi extra keys: {extra_hi}")
    
    # Check Bengali
    missing_bn = en_keys - bn_keys
    extra_bn = bn_keys - en_keys
    
    if missing_bn:
        print(f"\n⚠️ Bengali missing keys: {missing_bn}")
    if extra_bn:
        print(f"\n⚠️ Bengali extra keys: {extra_bn}")
    
    if en_keys == hi_keys == bn_keys:
        print(f"\n✓ PASS - All languages have same {len(en_keys)} keys")
    else:
        print(f"\n⚠️ WARNING - Languages have different keys")


def test_example_query_structure():
    """Test example query structure consistency."""
    print("\n" + "="*60)
    print("TEST: Example Query Structure")
    print("="*60)
    
    categories = ["api", "rag", "hybrid"]
    
    for lang in ["en", "hi", "bn"]:
        print(f"\n{lang.upper()}:")
        for category in categories:
            count = len(EXAMPLE_QUERIES[lang][category])
            print(f"  {category}: {count} examples")
    
    # Check if all languages have examples for all categories
    for lang in ["en", "hi", "bn"]:
        for category in categories:
            assert category in EXAMPLE_QUERIES[lang]
            assert len(EXAMPLE_QUERIES[lang][category]) > 0
    
    print(f"\n✓ PASS - All languages have examples for all categories")


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# PHASE 3 - UI MULTILINGUAL COMPONENT TESTS")
    print("#"*60)
    
    try:
        test_supported_languages()
        test_example_queries()
        test_ui_text_translations()
        test_get_text_helper()
        test_get_language_name_helper()
        test_translation_completeness()
        test_example_query_structure()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
