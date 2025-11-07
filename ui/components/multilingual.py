"""
Multilingual UI Components for AasthaSathi

This module provides reusable UI components for multilingual support:
- Language selector
- Language detection indicator
- Multilingual example queries
- Language-aware messages
"""

import streamlit as st
from typing import Dict, Optional, Tuple


# Language configuration
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "flag": "🇬🇧", "native_name": "English"},
    "hi": {"name": "Hindi", "flag": "🇮🇳", "native_name": "हिंदी"},
    "bn": {"name": "Bengali", "flag": "🇧🇩", "native_name": "বাংলা"}
}

# Multilingual example queries
EXAMPLE_QUERIES = {
    "en": {
        "api": [
            "List all branches in Patna",
            "What savings schemes are available?",
            "How many members joined in January 2025?",
            "Show me all SB accounts opened in 2024"
        ],
        "rag": [
            "What are the membership eligibility criteria?",
            "Explain the loan application process",
            "What documents are required for opening an account?",
            "What are the interest rates for different schemes?"
        ],
        "hybrid": [
            "Show me all RD schemes and explain how they work",
            "List branches in Gaya and their services",
            "What loan schemes are available and their eligibility criteria?"
        ]
    },
    "hi": {
        "api": [
            "पटना में सभी शाखाओं की सूची दिखाएं",
            "कौन सी बचत योजनाएं उपलब्ध हैं?",
            "जनवरी 2025 में कितने सदस्य शामिल हुए?",
            "2024 में खोले गए सभी SB खाते दिखाएं"
        ],
        "rag": [
            "सदस्यता पात्रता मानदंड क्या हैं?",
            "ऋण आवेदन प्रक्रिया को समझाएं",
            "खाता खोलने के लिए कौन से दस्तावेज़ आवश्यक हैं?",
            "विभिन्न योजनाओं के लिए ब्याज दरें क्या हैं?"
        ],
        "hybrid": [
            "सभी RD योजनाओं को दिखाएं और बताएं कि वे कैसे काम करती हैं",
            "गया में शाखाओं की सूची और उनकी सेवाएं दिखाएं",
            "कौन सी ऋण योजनाएं उपलब्ध हैं और उनके पात्रता मानदंड?"
        ]
    },
    "bn": {
        "api": [
            "পাটনার সমস্ত শাখার তালিকা দেখান",
            "কোন সঞ্চয় প্রকল্প উপলব্ধ আছে?",
            "জানুয়ারি 2025 এ কতজন সদস্য যোগ দিয়েছেন?",
            "2024 সালে খোলা সমস্ত SB অ্যাকাউন্ট দেখান"
        ],
        "rag": [
            "সদস্যপদের যোগ্যতার মানদণ্ড কী?",
            "ঋণ আবেদন প্রক্রিয়া ব্যাখ্যা করুন",
            "অ্যাকাউন্ট খোলার জন্য কোন নথি প্রয়োজন?",
            "বিভিন্ন প্রকল্পের সুদের হার কত?"
        ],
        "hybrid": [
            "সমস্ত RD প্রকল্প দেখান এবং ব্যাখ্যা করুন কিভাবে তারা কাজ করে",
            "গয়ার শাখাগুলি এবং তাদের সেবা তালিকা করুন",
            "কোন ঋণ প্রকল্প উপলব্ধ এবং তাদের যোগ্যতার মানদণ্ড?"
        ]
    }
}

# Multilingual UI text
UI_TEXT = {
    "en": {
        "language_selector": "🌐 Select Language",
        "query_type": "Query Type",
        "example_queries": "📖 Example Queries",
        "api_queries": "API Queries (Real-time Data)",
        "rag_queries": "RAG Queries (Knowledge Base)",
        "hybrid_queries": "Hybrid Queries (Combined)",
        "detected_language": "Detected Language",
        "confidence": "Confidence",
        "processing": "Processing your query...",
        "typing": "AasthaSathi is typing...",
        "chat_history": "Chat History",
        "clear_chat": "Clear Chat",
        "sources": "Sources",
        "metadata": "Metadata"
    },
    "hi": {
        "language_selector": "🌐 भाषा चुनें",
        "query_type": "क्वेरी प्रकार",
        "example_queries": "📖 उदाहरण प्रश्न",
        "api_queries": "API प्रश्न (रीयल-टाइम डेटा)",
        "rag_queries": "RAG प्रश्न (ज्ञान आधार)",
        "hybrid_queries": "हाइब्रिड प्रश्न (संयुक्त)",
        "detected_language": "पता लगाई गई भाषा",
        "confidence": "विश्वास",
        "processing": "आपकी क्वेरी संसाधित की जा रही है...",
        "typing": "आस्थासाथी टाइप कर रहा है...",
        "chat_history": "चैट इतिहास",
        "clear_chat": "चैट साफ़ करें",
        "sources": "स्रोत",
        "metadata": "मेटाडेटा"
    },
    "bn": {
        "language_selector": "🌐 ভাষা নির্বাচন করুন",
        "query_type": "কোয়েরির ধরন",
        "example_queries": "📖 উদাহরণ প্রশ্ন",
        "api_queries": "API প্রশ্ন (রিয়েল-টাইম ডেটা)",
        "rag_queries": "RAG প্রশ্ন (জ্ঞান ভিত্তি)",
        "hybrid_queries": "হাইব্রিড প্রশ্ন (সম্মিলিত)",
        "detected_language": "সনাক্তকৃত ভাষা",
        "confidence": "আত্মবিশ্বাস",
        "processing": "আপনার কোয়েরি প্রক্রিয়া করা হচ্ছে...",
        "typing": "আস্থাসাথী টাইপ করছে...",
        "chat_history": "চ্যাট ইতিহাস",
        "clear_chat": "চ্যাট পরিষ্কার করুন",
        "sources": "উৎস",
        "metadata": "মেটাডেটা"
    }
}


def get_text(key: str, language: str = "en") -> str:
    """
    Get translated UI text for a given key and language.
    
    Args:
        key: Text key to look up
        language: Language code (en, hi, bn)
        
    Returns:
        Translated text or key if not found
    """
    return UI_TEXT.get(language, UI_TEXT["en"]).get(key, key)


def render_language_selector(current_language: Optional[str] = None) -> str:
    """
    Render language selector component.
    
    Args:
        current_language: Currently selected language code
        
    Returns:
        Selected language code
    """
    # Default to English if not set
    if current_language is None:
        current_language = "en"
    
    # Get current index for selectbox
    lang_codes = list(SUPPORTED_LANGUAGES.keys())
    current_index = lang_codes.index(current_language) if current_language in lang_codes else 0
    
    # Create options with flag and native name
    options = [
        f"{SUPPORTED_LANGUAGES[code]['flag']} {SUPPORTED_LANGUAGES[code]['native_name']}"
        for code in lang_codes
    ]
    
    # Render selectbox
    selected_option = st.selectbox(
        get_text("language_selector", current_language),
        options,
        index=current_index,
        key="language_selector"
    )
    
    # Extract language code from selection
    selected_index = options.index(selected_option)
    selected_code = lang_codes[selected_index]
    
    return selected_code


def render_language_detection_indicator(
    detected_language: str,
    confidence: float,
    user_language: Optional[str] = None
) -> None:
    """
    Render language detection indicator showing detected language and confidence.
    
    Args:
        detected_language: Detected language code
        confidence: Detection confidence (0.0-1.0)
        user_language: User's preferred language for UI text
    """
    if user_language is None:
        user_language = "en"
    
    lang_info = SUPPORTED_LANGUAGES.get(detected_language, {
        "name": detected_language.upper(),
        "flag": "🌐",
        "native_name": detected_language
    })
    
    # Color based on confidence
    if confidence >= 0.9:
        color = "green"
        emoji = "✅"
    elif confidence >= 0.7:
        color = "blue"
        emoji = "ℹ️"
    else:
        color = "orange"
        emoji = "⚠️"
    
    # Render indicator
    st.markdown(
        f":{color}[{emoji} **{get_text('detected_language', user_language)}:** "
        f"{lang_info['flag']} {lang_info['native_name']} "
        f"({get_text('confidence', user_language)}: {confidence:.0%})]"
    )


def render_multilingual_examples(language: str = "en") -> None:
    """
    Render example queries in the selected language.
    
    Args:
        language: Language code for examples
    """
    st.markdown(f"### {get_text('example_queries', language)}")
    
    examples = EXAMPLE_QUERIES.get(language, EXAMPLE_QUERIES["en"])
    
    # API Examples
    with st.expander(f"💻 {get_text('api_queries', language)}", expanded=False):
        for i, query in enumerate(examples["api"], 1):
            if st.button(query, key=f"api_example_{language}_{i}", use_container_width=True):
                return query
    
    # RAG Examples
    with st.expander(f"📚 {get_text('rag_queries', language)}", expanded=False):
        for i, query in enumerate(examples["rag"], 1):
            if st.button(query, key=f"rag_example_{language}_{i}", use_container_width=True):
                return query
    
    # Hybrid Examples
    with st.expander(f"🔄 {get_text('hybrid_queries', language)}", expanded=False):
        for i, query in enumerate(examples["hybrid"], 1):
            if st.button(query, key=f"hybrid_example_{language}_{i}", use_container_width=True):
                return query
    
    return None


def get_language_name(language_code: str, display_language: str = "en") -> str:
    """
    Get the name of a language in another language.
    
    Args:
        language_code: Language code to get name for
        display_language: Language to display name in
        
    Returns:
        Language name with flag
    """
    lang_info = SUPPORTED_LANGUAGES.get(language_code, {
        "name": language_code.upper(),
        "flag": "🌐",
        "native_name": language_code
    })
    
    return f"{lang_info['flag']} {lang_info['native_name']}"


def render_language_info_box(
    detected_language: Optional[str] = None,
    confidence: Optional[float] = None,
    selected_language: Optional[str] = None
) -> None:
    """
    Render an info box showing language detection and selection status.
    
    Args:
        detected_language: Detected language from query
        confidence: Detection confidence
        selected_language: User's selected preference language
    """
    if detected_language and confidence:
        lang_name = get_language_name(detected_language, selected_language or "en")
        
        if detected_language == selected_language:
            st.info(f"✅ Query detected as {lang_name} (matches your preference)")
        else:
            user_lang = get_language_name(selected_language, selected_language) if selected_language else "English"
            st.info(
                f"🔄 Query detected as {lang_name}, responding in {user_lang}"
            )
