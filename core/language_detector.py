"""
Language Detection Module for Multilingual Support

Automatically detects the language of user queries to enable multilingual processing.
Supports English, Hindi, and Bengali languages.
"""

import logging
from typing import Tuple, Optional
from langdetect import detect, detect_langs, LangDetectException
from langcodes import Language

logger = logging.getLogger(__name__)

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi", 
    "bn": "Bengali"
}

# Minimum confidence threshold for language detection
DEFAULT_CONFIDENCE_THRESHOLD = 0.8


class LanguageDetector:
    """
    Language detector for identifying query language.
    
    Uses langdetect library with confidence scoring to determine
    if a query is in English, Hindi, or Bengali.
    """
    
    def __init__(self, confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD):
        """
        Initialize language detector.
        
        Args:
            confidence_threshold: Minimum confidence (0.0-1.0) required for detection
        """
        self.confidence_threshold = confidence_threshold
        logger.info(f"LanguageDetector initialized (confidence threshold: {confidence_threshold})")
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of given text.
        
        Args:
            text: Input text to detect language
            
        Returns:
            Tuple of (language_code, confidence)
            - language_code: ISO 639-1 code (en, hi, bn)
            - confidence: Detection confidence (0.0-1.0)
            
        Examples:
            >>> detector = LanguageDetector()
            >>> detector.detect_language("What is your name?")
            ('en', 0.99)
            >>> detector.detect_language("आपका नाम क्या है?")
            ('hi', 0.95)
            >>> detector.detect_language("আপনার নাম কি?")
            ('bn', 0.92)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for language detection")
            return ("en", 0.0)
        
        try:
            # Get language probabilities
            lang_probs = detect_langs(text)
            
            if not lang_probs:
                logger.warning("No language detected, defaulting to English")
                return ("en", 0.0)
            
            # Get most probable language
            top_lang = lang_probs[0]
            lang_code = top_lang.lang
            confidence = top_lang.prob
            
            # Validate if detected language is supported
            if lang_code not in SUPPORTED_LANGUAGES:
                logger.info(
                    f"Detected unsupported language '{lang_code}' "
                    f"(confidence: {confidence:.2f}), defaulting to English"
                )
                return ("en", confidence)
            
            logger.info(
                f"Detected language: {SUPPORTED_LANGUAGES[lang_code]} "
                f"(code: {lang_code}, confidence: {confidence:.2f})"
            )
            
            return (lang_code, confidence)
            
        except LangDetectException as e:
            logger.error(f"Language detection failed: {e}, defaulting to English")
            return ("en", 0.0)
        except Exception as e:
            logger.error(f"Unexpected error in language detection: {e}")
            return ("en", 0.0)
    
    def detect_with_validation(self, text: str) -> Tuple[str, float, bool]:
        """
        Detect language with confidence validation.
        
        Args:
            text: Input text to detect language
            
        Returns:
            Tuple of (language_code, confidence, is_confident)
            - language_code: ISO 639-1 code
            - confidence: Detection confidence (0.0-1.0)
            - is_confident: True if confidence >= threshold
        """
        lang_code, confidence = self.detect_language(text)
        is_confident = confidence >= self.confidence_threshold
        
        if not is_confident:
            logger.warning(
                f"Low confidence detection: {lang_code} "
                f"({confidence:.2f} < {self.confidence_threshold})"
            )
        
        return (lang_code, confidence, is_confident)
    
    def is_supported_language(self, lang_code: str) -> bool:
        """
        Check if language code is supported.
        
        Args:
            lang_code: ISO 639-1 language code
            
        Returns:
            True if language is supported, False otherwise
        """
        return lang_code in SUPPORTED_LANGUAGES
    
    def get_language_name(self, lang_code: str) -> str:
        """
        Get full language name from code.
        
        Args:
            lang_code: ISO 639-1 language code
            
        Returns:
            Full language name or "Unknown" if not supported
            
        Examples:
            >>> detector = LanguageDetector()
            >>> detector.get_language_name("en")
            'English'
            >>> detector.get_language_name("hi")
            'Hindi'
            >>> detector.get_language_name("bn")
            'Bengali'
        """
        return SUPPORTED_LANGUAGES.get(lang_code, "Unknown")
    
    def get_supported_languages(self) -> dict:
        """
        Get dictionary of all supported languages.
        
        Returns:
            Dictionary mapping language codes to names
        """
        return SUPPORTED_LANGUAGES.copy()


# Convenience functions for quick access
_default_detector = None


def get_detector(confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD) -> LanguageDetector:
    """
    Get or create default language detector instance.
    
    Args:
        confidence_threshold: Minimum confidence threshold
        
    Returns:
        LanguageDetector instance
    """
    global _default_detector
    if _default_detector is None:
        _default_detector = LanguageDetector(confidence_threshold)
    return _default_detector


def detect_language(text: str) -> Tuple[str, float]:
    """
    Quick language detection using default detector.
    
    Args:
        text: Input text
        
    Returns:
        Tuple of (language_code, confidence)
    """
    detector = get_detector()
    return detector.detect_language(text)


def is_supported_language(lang_code: str) -> bool:
    """
    Quick check if language is supported.
    
    Args:
        lang_code: ISO 639-1 language code
        
    Returns:
        True if supported
    """
    return lang_code in SUPPORTED_LANGUAGES


def get_language_name(lang_code: str) -> str:
    """
    Quick get language name from code.
    
    Args:
        lang_code: ISO 639-1 language code
        
    Returns:
        Full language name
    """
    return SUPPORTED_LANGUAGES.get(lang_code, "Unknown")


if __name__ == "__main__":
    # Test the language detector
    print("=" * 70)
    print("Language Detector Test")
    print("=" * 70)
    
    detector = LanguageDetector()
    
    test_cases = [
        "What are the loan types available?",
        "बैंक के कार्य समय क्या हैं?",
        "ব্যাংকের কার্যকরী সময় কী?",
        "How to open a Fixed Deposit account?",
        "मैं आवर्ती जमा खाता कैसे खोल सकता हूँ?",
        "আমি কীভাবে একটি সঞ্চয়ী অ্যাকাউন্ট খুলতে পারি?",
        "KYC process",
        "12345",  # Edge case
        "",  # Empty
    ]
    
    for text in test_cases:
        if text:
            lang_code, confidence = detector.detect_language(text)
            lang_name = detector.get_language_name(lang_code)
            print(f"\nText: {text[:50]}...")
            print(f"  → Language: {lang_name} ({lang_code})")
            print(f"  → Confidence: {confidence:.2f}")
        else:
            print(f"\nText: (empty)")
            lang_code, confidence = detector.detect_language(text)
            print(f"  → Default: {detector.get_language_name(lang_code)}")
    
    print("\n" + "=" * 70)
    print(f"Supported languages: {list(SUPPORTED_LANGUAGES.values())}")
    print("=" * 70)
