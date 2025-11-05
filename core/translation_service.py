"""
Translation Service Module for Multilingual Support

Provides translation capabilities for converting text between
English, Hindi, and Bengali languages.
"""

import logging
from typing import List, Optional, Dict
from googletrans import Translator
import time

logger = logging.getLogger(__name__)

# Language codes
SUPPORTED_LANGUAGES = ["en", "hi", "bn"]

# Language names for logging
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali"
}


class TranslationService:
    """
    Translation service for multilingual text conversion.
    
    Uses Google Translate API for high-quality translations
    between English, Hindi, and Bengali.
    """
    
    def __init__(self, enable_cache: bool = True, retry_attempts: int = 3):
        """
        Initialize translation service.
        
        Args:
            enable_cache: Enable translation caching (from translation_cache module)
            retry_attempts: Number of retry attempts for failed translations
        """
        self.translator = Translator()
        self.enable_cache = enable_cache
        self.retry_attempts = retry_attempts
        
        # Import cache if enabled
        if enable_cache:
            try:
                from core.translation_cache import TranslationCache
                self.cache = TranslationCache()
                logger.info("TranslationService initialized with caching enabled")
            except ImportError:
                logger.warning("TranslationCache not available, caching disabled")
                self.cache = None
                self.enable_cache = False
        else:
            self.cache = None
            logger.info("TranslationService initialized without caching")
    
    def translate(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        use_cache: bool = True
    ) -> Optional[str]:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code (en, hi, bn)
            target_lang: Target language code (en, hi, bn)
            use_cache: Whether to use cache for this translation
            
        Returns:
            Translated text or None if translation fails
            
        Examples:
            >>> service = TranslationService()
            >>> service.translate("Hello", "en", "hi")
            'नमस्ते'
            >>> service.translate("बैंक", "hi", "en")
            'Bank'
        """
        # Validate inputs
        if not text or not text.strip():
            logger.warning("Empty text provided for translation")
            return text
        
        # Check if translation is needed
        if source_lang == target_lang:
            logger.debug(f"Source and target languages are same ({source_lang}), skipping translation")
            return text
        
        # Validate languages
        if source_lang not in SUPPORTED_LANGUAGES or target_lang not in SUPPORTED_LANGUAGES:
            logger.error(
                f"Unsupported language pair: {source_lang} → {target_lang}. "
                f"Supported: {SUPPORTED_LANGUAGES}"
            )
            return None
        
        # Check cache first
        if use_cache and self.enable_cache and self.cache:
            cached = self.cache.get(text, source_lang, target_lang)
            if cached:
                logger.debug(f"Cache hit for translation: {source_lang} → {target_lang}")
                return cached
        
        # Perform translation with retries
        for attempt in range(1, self.retry_attempts + 1):
            try:
                logger.info(
                    f"Translating: {LANGUAGE_NAMES[source_lang]} → "
                    f"{LANGUAGE_NAMES[target_lang]} (attempt {attempt}/{self.retry_attempts})"
                )
                
                result = self.translator.translate(
                    text,
                    src=source_lang,
                    dest=target_lang
                )
                
                translated_text = result.text
                
                # Cache the result
                if self.enable_cache and self.cache:
                    self.cache.set(text, source_lang, target_lang, translated_text)
                
                logger.info(f"Translation successful: '{text[:50]}...' → '{translated_text[:50]}...'")
                return translated_text
                
            except Exception as e:
                logger.error(f"Translation attempt {attempt} failed: {e}")
                
                if attempt < self.retry_attempts:
                    # Wait before retry with exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Translation failed after {self.retry_attempts} attempts")
                    return None
        
        return None
    
    def translate_to_english(self, text: str, source_lang: str) -> Optional[str]:
        """
        Convenience method to translate to English.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            
        Returns:
            English translation or None if translation fails
        """
        if source_lang == "en":
            return text
        
        return self.translate(text, source_lang, "en")
    
    def translate_from_english(self, text: str, target_lang: str) -> Optional[str]:
        """
        Convenience method to translate from English.
        
        Args:
            text: English text to translate
            target_lang: Target language code
            
        Returns:
            Translated text or None if translation fails
        """
        if target_lang == "en":
            return text
        
        return self.translate(text, "en", target_lang)
    
    def batch_translate(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str,
        use_cache: bool = True
    ) -> List[Optional[str]]:
        """
        Translate multiple texts efficiently.
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            use_cache: Whether to use cache
            
        Returns:
            List of translated texts (None for failed translations)
        """
        if not texts:
            return []
        
        logger.info(
            f"Batch translating {len(texts)} texts: "
            f"{LANGUAGE_NAMES[source_lang]} → {LANGUAGE_NAMES[target_lang]}"
        )
        
        results = []
        for i, text in enumerate(texts):
            logger.debug(f"Translating text {i+1}/{len(texts)}")
            translated = self.translate(text, source_lang, target_lang, use_cache)
            results.append(translated)
        
        successful = sum(1 for r in results if r is not None)
        logger.info(f"Batch translation completed: {successful}/{len(texts)} successful")
        
        return results
    
    def detect_and_translate_to_english(self, text: str) -> tuple[Optional[str], str, float]:
        """
        Detect language and translate to English if needed.
        
        Args:
            text: Input text in any supported language
            
        Returns:
            Tuple of (translated_text, detected_lang, confidence)
        """
        from core.language_detector import detect_language
        
        # Detect language
        lang_code, confidence = detect_language(text)
        
        # Translate if not English
        if lang_code != "en":
            translated = self.translate_to_english(text, lang_code)
            return (translated, lang_code, confidence)
        else:
            return (text, lang_code, confidence)
    
    def get_translation_info(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Dict[str, any]:
        """
        Get detailed translation information.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Dictionary with translation details including timing
        """
        start_time = time.time()
        
        translated = self.translate(text, source_lang, target_lang)
        
        elapsed_time = time.time() - start_time
        
        return {
            "original_text": text,
            "translated_text": translated,
            "source_language": LANGUAGE_NAMES[source_lang],
            "target_language": LANGUAGE_NAMES[target_lang],
            "translation_time_seconds": round(elapsed_time, 3),
            "success": translated is not None,
            "cached": False  # TODO: Implement cache hit detection
        }


# Convenience functions for quick access
_default_service = None


def get_translation_service(enable_cache: bool = True) -> TranslationService:
    """
    Get or create default translation service instance.
    
    Args:
        enable_cache: Enable caching
        
    Returns:
        TranslationService instance
    """
    global _default_service
    if _default_service is None:
        _default_service = TranslationService(enable_cache=enable_cache)
    return _default_service


def translate(text: str, source_lang: str, target_lang: str) -> Optional[str]:
    """
    Quick translation using default service.
    
    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
        
    Returns:
        Translated text
    """
    service = get_translation_service()
    return service.translate(text, source_lang, target_lang)


def translate_to_english(text: str, source_lang: str) -> Optional[str]:
    """
    Quick translation to English.
    
    Args:
        text: Text to translate
        source_lang: Source language code
        
    Returns:
        English translation
    """
    service = get_translation_service()
    return service.translate_to_english(text, source_lang)


def translate_from_english(text: str, target_lang: str) -> Optional[str]:
    """
    Quick translation from English.
    
    Args:
        text: English text
        target_lang: Target language code
        
    Returns:
        Translated text
    """
    service = get_translation_service()
    return service.translate_from_english(text, target_lang)


if __name__ == "__main__":
    # Test the translation service
    print("=" * 70)
    print("Translation Service Test")
    print("=" * 70)
    
    service = TranslationService(enable_cache=False)
    
    test_cases = [
        ("Hello, how are you?", "en", "hi"),
        ("What are the loan types?", "en", "bn"),
        ("बैंक के कार्य समय क्या हैं?", "hi", "en"),
        ("ব্যাংকের কার্যকরী সময় কী?", "bn", "en"),
        ("Fixed Deposit", "en", "hi"),
        ("Recurring Deposit", "en", "bn"),
    ]
    
    for text, src, tgt in test_cases:
        print(f"\n{'-' * 70}")
        print(f"Original ({LANGUAGE_NAMES[src]}): {text}")
        translated = service.translate(text, src, tgt)
        if translated:
            print(f"Translated ({LANGUAGE_NAMES[tgt]}): {translated}")
        else:
            print(f"Translation failed!")
    
    print("\n" + "=" * 70)
    
    # Test batch translation
    print("\nBatch Translation Test:")
    texts = ["Hello", "Thank you", "Good morning"]
    results = service.batch_translate(texts, "en", "hi")
    for orig, trans in zip(texts, results):
        print(f"  {orig} → {trans}")
    
    print("\n" + "=" * 70)
