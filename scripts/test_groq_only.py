#!/usr/bin/env python3
"""
Quick test script to verify Groq provider is working with new API key
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.llm_providers.groq_provider import GroqProvider
from core.config import settings
from langchain_core.messages import HumanMessage

def test_groq_basic():
    """Test basic Groq provider functionality"""
    print("\n🧪 Testing Groq Provider with New API Key\n")
    
    try:
        # Initialize Groq provider
        print("1. Initializing Groq provider...")
        provider = GroqProvider(
            model=settings.fallback_model,
            api_key=settings.groq_api_key,
            priority=1
        )
        print(f"✓ Groq provider initialized with model: {settings.fallback_model}")
        
        # Test simple invocation
        print("\n2. Testing simple message...")
        messages = [HumanMessage(content="Say 'Hello from Groq!' in exactly those words.")]
        response = provider.invoke(messages)
        print(f"✓ Response: {response}")
        assert isinstance(response, str), "Response should be a string"
        
        # Test structured output
        print("\n3. Testing structured output...")
        from pydantic import BaseModel, Field
        
        class TestResponse(BaseModel):
            message: str = Field(description="A greeting message")
            success: bool = Field(description="Whether the test was successful")
        
        structured_response = provider.get_structured_output(
            messages=[HumanMessage(content="Create a greeting message with success=true")],
            response_format=TestResponse
        )
        print(f"✓ Structured response: {structured_response}")
        
        # Test with tools
        print("\n4. Testing tool calling...")
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather information for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA"
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
        
        tool_response = provider.invoke_with_tools(
            messages=[HumanMessage(content="What's the weather in London?")],
            tools=tools
        )
        print(f"✓ Tool response: {tool_response}")
        
        print("\n✅ All Groq tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_groq_basic()
    sys.exit(0 if success else 1)
