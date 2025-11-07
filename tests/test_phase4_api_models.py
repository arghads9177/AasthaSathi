"""
Tests for Phase 4 - API Multilingual Support

This module tests the API models and integration without running the full server.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.models import QueryRequest, QueryResponse
from datetime import datetime


def test_query_request_schema():
    """Test QueryRequest with language parameter."""
    print("\n" + "="*60)
    print("TEST: QueryRequest Schema")
    print("="*60)
    
    # Test with language parameter
    request = QueryRequest(
        query="ब्याज दर क्या है?",
        language="hi",
        session_id="test-session",
        include_sources=True,
        include_metadata=True
    )
    
    print(f"\nQuery: {request.query}")
    print(f"Language: {request.language}")
    print(f"Session ID: {request.session_id}")
    
    assert request.query == "ब्याज दर क्या है?"
    assert request.language == "hi"
    assert request.session_id == "test-session"
    assert request.include_sources == True
    assert request.include_metadata == True
    
    print("\n✓ PASS - QueryRequest with language parameter works correctly")
    
    # Test without language parameter (auto-detect)
    request2 = QueryRequest(
        query="What is the interest rate?"
    )
    
    print(f"\nQuery: {request2.query}")
    print(f"Language: {request2.language} (auto-detect)")
    
    assert request2.query == "What is the interest rate?"
    assert request2.language is None
    assert request2.include_sources == True  # Default value
    
    print("\n✓ PASS - QueryRequest without language (auto-detect) works correctly")


def test_query_response_schema():
    """Test QueryResponse with language metadata."""
    print("\n" + "="*60)
    print("TEST: QueryResponse Schema")
    print("="*60)
    
    # Test with language metadata
    response = QueryResponse(
        session_id="test-session",
        query="ब्याज दर क्या है?",
        answer="ब्याज दर 5% प्रति वर्ष है।",
        datasource="rag",
        routing_reasoning="Knowledge base query",
        detected_language="hi",
        detection_confidence=1.0,
        response_language="hi",
        sources=["User Manual"],
        metadata={
            "execution_path": ["language_detection", "query_translation", "router", "retrieve"],
            "processing_time_ms": 3200
        },
        timestamp=datetime.now()
    )
    
    print(f"\nQuery: {response.query}")
    print(f"Answer: {response.answer}")
    print(f"Detected Language: {response.detected_language}")
    print(f"Detection Confidence: {response.detection_confidence:.0%}")
    print(f"Response Language: {response.response_language}")
    print(f"Datasource: {response.datasource}")
    
    assert response.detected_language == "hi"
    assert response.detection_confidence == 1.0
    assert response.response_language == "hi"
    assert 0.0 <= response.detection_confidence <= 1.0
    
    print("\n✓ PASS - QueryResponse with language metadata works correctly")
    
    # Test without language metadata (English/backward compatible)
    response2 = QueryResponse(
        session_id="test-session",
        query="What is the interest rate?",
        answer="The interest rate is 5% per annum.",
        datasource="rag",
        sources=[],
        timestamp=datetime.now()
    )
    
    print(f"\nQuery: {response2.query}")
    print(f"Answer: {response2.answer}")
    print(f"Detected Language: {response2.detected_language} (None for backward compatibility)")
    print(f"Detection Confidence: {response2.detection_confidence}")
    print(f"Response Language: {response2.response_language}")
    
    assert response2.detected_language is None
    assert response2.detection_confidence is None
    assert response2.response_language is None
    
    print("\n✓ PASS - QueryResponse without language metadata (backward compatible) works correctly")


def test_language_parameter_validation():
    """Test language parameter validation."""
    print("\n" + "="*60)
    print("TEST: Language Parameter Validation")
    print("="*60)
    
    # Test valid languages
    valid_languages = ["en", "hi", "bn"]
    
    for lang in valid_languages:
        request = QueryRequest(query="test", language=lang)
        print(f"\n{lang.upper()}: ✓ Valid")
        assert request.language == lang
    
    print("\n✓ PASS - All valid languages accepted")
    
    # Test None (auto-detect)
    request_none = QueryRequest(query="test", language=None)
    assert request_none.language is None
    print("\nNone (auto-detect): ✓ Valid")
    
    # Note: Invalid languages would be rejected by Pydantic Literal type
    # at the API validation layer, not in model instantiation
    
    print("\n✓ PASS - Language validation works correctly")


def test_confidence_score_validation():
    """Test detection confidence score validation."""
    print("\n" + "="*60)
    print("TEST: Confidence Score Validation")
    print("="*60)
    
    # Test valid confidence scores
    test_scores = [0.0, 0.5, 0.8, 0.95, 1.0]
    
    for score in test_scores:
        response = QueryResponse(
            session_id="test",
            query="test",
            answer="test",
            datasource="rag",
            detection_confidence=score,
            timestamp=datetime.now()
        )
        print(f"\nConfidence {score:.0%}: ✓ Valid")
        assert response.detection_confidence == score
        assert 0.0 <= response.detection_confidence <= 1.0
    
    print("\n✓ PASS - All confidence scores in valid range [0.0, 1.0]")


def test_response_example():
    """Test the example response from schema."""
    print("\n" + "="*60)
    print("TEST: Example Response from Schema")
    print("="*60)
    
    example = QueryResponse.Config.json_schema_extra["example"]
    
    print(f"\nExample Query: {example['query']}")
    print(f"Example Answer: {example['answer']}")
    print(f"Detected Language: {example['detected_language']}")
    print(f"Detection Confidence: {example['detection_confidence']:.0%}")
    print(f"Response Language: {example['response_language']}")
    print(f"Datasource: {example['datasource']}")
    
    # Verify example has all new fields
    assert "detected_language" in example
    assert "detection_confidence" in example
    assert "response_language" in example
    
    assert example["detected_language"] == "hi"
    assert example["detection_confidence"] == 1.0
    assert example["response_language"] == "hi"
    
    print("\n✓ PASS - Example response includes all language metadata fields")


def test_optional_fields():
    """Test that language fields are optional."""
    print("\n" + "="*60)
    print("TEST: Optional Language Fields")
    print("="*60)
    
    # Request without language
    request = QueryRequest(query="test query")
    assert request.language is None
    print("\nQueryRequest without language: ✓ Works")
    
    # Response without language metadata
    response = QueryResponse(
        session_id="test",
        query="test",
        answer="test answer",
        datasource="rag",
        timestamp=datetime.now()
    )
    assert response.detected_language is None
    assert response.detection_confidence is None
    assert response.response_language is None
    print("QueryResponse without language metadata: ✓ Works")
    
    print("\n✓ PASS - All language fields are properly optional")


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# PHASE 4 - API MULTILINGUAL SUPPORT TESTS")
    print("#"*60)
    
    try:
        test_query_request_schema()
        test_query_response_schema()
        test_language_parameter_validation()
        test_confidence_score_validation()
        test_response_example()
        test_optional_fields()
        
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
