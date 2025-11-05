"""
Translation Cache Module for Performance Optimization

Caches translation results to reduce API calls and improve response times.
Uses in-memory caching with LRU eviction policy.
"""

import logging
import hashlib
from typing import Optional, Dict
from functools import lru_cache
import json

logger = logging.getLogger(__name__)

# Default cache size (number of translations to cache)
DEFAULT_CACHE_SIZE = 1000


class TranslationCache:
    """
    In-memory cache for translation results.
    
    Stores translation mappings to avoid redundant API calls.
    Uses MD5 hashing for cache keys and LRU eviction policy.
    """
    
    def __init__(self, max_size: int = DEFAULT_CACHE_SIZE):
        """
        Initialize translation cache.
        
        Args:
            max_size: Maximum number of translations to cache
        """
        self.cache: Dict[str, str] = {}
        self.max_size = max_size
        self.hit_count = 0
        self.miss_count = 0
        
        logger.info(f"TranslationCache initialized (max_size: {max_size})")
    
    def _generate_cache_key(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        Generate unique cache key for translation.
        
        Args:
            text: Original text
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            MD5 hash as cache key
        """
        # Create key from text and language pair
        key_content = f"{text}|{source_lang}|{target_lang}"
        
        # Generate MD5 hash
        cache_key = hashlib.md5(key_content.encode('utf-8')).hexdigest()
        
        return cache_key
    
    def get(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """
        Get cached translation if available.
        
        Args:
            text: Original text
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Cached translation or None if not found
        """
        cache_key = self._generate_cache_key(text, source_lang, target_lang)
        
        if cache_key in self.cache:
            self.hit_count += 1
            translation = self.cache[cache_key]
            logger.debug(
                f"Cache HIT: {source_lang}→{target_lang} "
                f"(hits: {self.hit_count}, misses: {self.miss_count})"
            )
            return translation
        else:
            self.miss_count += 1
            logger.debug(
                f"Cache MISS: {source_lang}→{target_lang} "
                f"(hits: {self.hit_count}, misses: {self.miss_count})"
            )
            return None
    
    def set(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        translation: str
    ) -> None:
        """
        Cache a translation result.
        
        Args:
            text: Original text
            source_lang: Source language code
            target_lang: Target language code
            translation: Translated text
        """
        cache_key = self._generate_cache_key(text, source_lang, target_lang)
        
        # Check if cache is full
        if len(self.cache) >= self.max_size and cache_key not in self.cache:
            # Evict oldest entry (simple FIFO for now)
            # In production, consider using LRU with OrderedDict or cachetools
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.debug(f"Cache full, evicted entry (size: {len(self.cache)})")
        
        self.cache[cache_key] = translation
        logger.debug(
            f"Cached translation: {source_lang}→{target_lang} "
            f"(cache size: {len(self.cache)}/{self.max_size})"
        )
    
    def clear(self) -> None:
        """Clear all cached translations."""
        size_before = len(self.cache)
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0
        logger.info(f"Cache cleared ({size_before} entries removed)")
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache metrics
        """
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "utilization_percent": round(len(self.cache) / self.max_size * 100, 2)
        }
    
    def print_stats(self) -> None:
        """Print cache statistics to console."""
        stats = self.get_stats()
        
        print("=" * 70)
        print("Translation Cache Statistics")
        print("=" * 70)
        print(f"Cache Size: {stats['cache_size']}/{stats['max_size']} "
              f"({stats['utilization_percent']}% utilized)")
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Cache Hits: {stats['hit_count']}")
        print(f"Cache Misses: {stats['miss_count']}")
        print(f"Hit Rate: {stats['hit_rate_percent']}%")
        print("=" * 70)
    
    def export_to_file(self, filepath: str) -> bool:
        """
        Export cache to JSON file.
        
        Args:
            filepath: Path to save cache
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert cache to exportable format
            cache_data = {
                "cache": self.cache,
                "stats": self.get_stats()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Cache exported to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export cache: {e}")
            return False
    
    def import_from_file(self, filepath: str) -> bool:
        """
        Import cache from JSON file.
        
        Args:
            filepath: Path to load cache from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            self.cache = cache_data.get("cache", {})
            logger.info(f"Cache imported from {filepath} ({len(self.cache)} entries)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import cache: {e}")
            return False


# Global cache instance
_global_cache = None


def get_cache(max_size: int = DEFAULT_CACHE_SIZE) -> TranslationCache:
    """
    Get or create global translation cache instance.
    
    Args:
        max_size: Maximum cache size
        
    Returns:
        TranslationCache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = TranslationCache(max_size)
    return _global_cache


# LRU cache decorator for frequently used translations
@lru_cache(maxsize=100)
def cached_translate_key(text: str, source_lang: str, target_lang: str) -> str:
    """
    LRU cached function for generating cache keys.
    
    This provides an additional layer of caching for key generation.
    """
    return f"{text}|{source_lang}|{target_lang}"


if __name__ == "__main__":
    # Test the translation cache
    print("=" * 70)
    print("Translation Cache Test")
    print("=" * 70)
    
    cache = TranslationCache(max_size=5)
    
    # Test cache operations
    print("\n1. Testing cache SET and GET:")
    cache.set("Hello", "en", "hi", "नमस्ते")
    cache.set("Thank you", "en", "hi", "धन्यवाद")
    cache.set("Good morning", "en", "hi", "सुप्रभात")
    
    # Test cache hit
    result = cache.get("Hello", "en", "hi")
    print(f"   Cache GET 'Hello': {result}")
    
    # Test cache miss
    result = cache.get("Goodbye", "en", "hi")
    print(f"   Cache GET 'Goodbye': {result}")
    
    # Add more to test eviction
    print("\n2. Testing cache eviction:")
    for i in range(3, 8):
        cache.set(f"Text {i}", "en", "hi", f"अनुवाद {i}")
        print(f"   Added 'Text {i}' (cache size: {len(cache.cache)}/5)")
    
    # Print statistics
    print("\n3. Cache Statistics:")
    cache.print_stats()
    
    # Test export/import
    print("\n4. Testing export/import:")
    cache.export_to_file("/tmp/translation_cache_test.json")
    
    new_cache = TranslationCache()
    new_cache.import_from_file("/tmp/translation_cache_test.json")
    print(f"   Imported cache size: {len(new_cache.cache)}")
    
    # Test clear
    print("\n5. Testing cache clear:")
    cache.clear()
    print(f"   Cache size after clear: {len(cache.cache)}")
    
    print("\n" + "=" * 70)
