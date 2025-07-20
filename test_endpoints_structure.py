#!/usr/bin/env python3
"""
Test script to validate ElevenLabs API endpoint structure and functionality
without requiring a running server or real API key.

This script tests:
1. Endpoint route definitions
2. Request/response schema validation
3. Error handling logic
4. Input validation
"""

import sys
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the FastAPI app
from tts_api import app

# Create test client
client = TestClient(app)

def test_endpoint_structure():
    """Test that all expected endpoints are defined"""
    print("Testing endpoint structure...")
    
    # Get all routes
    routes = [route.path for route in app.routes if hasattr(route, 'path')]
    
    expected_endpoints = [
        "/tts_simple",
        "/tts_elevenlabs", 
        "/combine_wav",
        "/voices/elevenlabs",
        "/voices/elevenlabs/{voice_id}/sample"
    ]
    
    for endpoint in expected_endpoints:
        if endpoint in routes or any(endpoint.replace('{voice_id}', '') in route for route in routes):
            print(f"✅ Endpoint found: {endpoint}")
        else:
            print(f"❌ Endpoint missing: {endpoint}")
            return False
    
    return True

def test_tts_elevenlabs_validation():
    """Test input validation for /tts_elevenlabs endpoint"""
    print("\nTesting /tts_elevenlabs input validation...")
    
    # Test missing API key
    response = client.post("/tts_elevenlabs", json={
        "segments": [{"id": 1, "text": "test"}],
        "tempdir": "test"
    })
    
    if response.status_code == 400:
        print("✅ Missing API key properly rejected (400)")
    else:
        print(f"❌ Expected 400 for missing API key, got {response.status_code}")
        return False
    
    # Test empty segments
    response = client.post("/tts_elevenlabs", json={
        "segments": [],
        "tempdir": "test",
        "api_key": "test_key"
    })
    
    if response.status_code == 400:
        print("✅ Empty segments properly rejected (400)")
    else:
        print(f"❌ Expected 400 for empty segments, got {response.status_code}")
        return False
    
    # Test invalid stability
    response = client.post("/tts_elevenlabs", json={
        "segments": [{"id": 1, "text": "test"}],
        "tempdir": "test",
        "api_key": "test_key",
        "stability": 1.5
    })
    
    if response.status_code == 400:
        print("✅ Invalid stability properly rejected (400)")
    else:
        print(f"❌ Expected 400 for invalid stability, got {response.status_code}")
        return False
    
    # Test invalid tempdir
    response = client.post("/tts_elevenlabs", json={
        "segments": [{"id": 1, "text": "test"}],
        "tempdir": "../invalid",
        "api_key": "test_key"
    })
    
    if response.status_code == 400:
        print("✅ Invalid tempdir properly rejected (400)")
    else:
        print(f"❌ Expected 400 for invalid tempdir, got {response.status_code}")
        return False
    
    return True

def test_voices_elevenlabs_validation():
    """Test input validation for /voices/elevenlabs endpoint"""
    print("\nTesting /voices/elevenlabs input validation...")
    
    # Test missing API key
    response = client.post("/voices/elevenlabs", json={})
    
    if response.status_code == 400:
        print("✅ Missing API key properly rejected (400)")
    else:
        print(f"❌ Expected 400 for missing API key, got {response.status_code}")
        return False
    
    return True

def test_voice_sample_validation():
    """Test input validation for voice sample endpoint"""
    print("\nTesting /voices/elevenlabs/{voice_id}/sample input validation...")
    
    # Test missing API key
    response = client.post("/voices/elevenlabs/test_voice/sample", json={})
    
    if response.status_code == 400:
        print("✅ Missing API key properly rejected (400)")
    else:
        print(f"❌ Expected 400 for missing API key, got {response.status_code}")
        return False
    
    return True

def test_schema_validation():
    """Test Pydantic schema validation"""
    print("\nTesting Pydantic schema validation...")
    
    # Test ElevenLabsTTSRequest with invalid data types
    response = client.post("/tts_elevenlabs", json={
        "segments": "not_a_list",  # Should be list
        "tempdir": "test",
        "api_key": "test_key"
    })
    
    if response.status_code == 422:  # Pydantic validation error
        print("✅ Invalid segments type properly rejected (422)")
    else:
        print(f"❌ Expected 422 for invalid segments type, got {response.status_code}")
        return False
    
    # Test with invalid stability range (should be caught by Pydantic)
    response = client.post("/tts_elevenlabs", json={
        "segments": [{"id": 1, "text": "test"}],
        "tempdir": "test", 
        "api_key": "test_key",
        "stability": -0.5  # Below valid range
    })
    
    if response.status_code == 422:  # Pydantic validation error
        print("✅ Invalid stability range properly rejected by Pydantic (422)")
    else:
        print(f"❌ Expected 422 for invalid stability range, got {response.status_code}")
        return False
    
    return True

def test_error_response_format():
    """Test that error responses have correct format"""
    print("\nTesting error response format...")
    
    response = client.post("/tts_elevenlabs", json={
        "segments": [{"id": 1, "text": "test"}],
        "tempdir": "test"
        # Missing api_key
    })
    
    if response.status_code == 400:
        try:
            error_data = response.json()
            if "detail" in error_data:
                print("✅ Error response has correct format with 'detail' field")
                print(f"   Error message: {error_data['detail']}")
            else:
                print("❌ Error response missing 'detail' field")
                return False
        except:
            print("❌ Error response is not valid JSON")
            return False
    else:
        print(f"❌ Expected 400 status code, got {response.status_code}")
        return False
    
    return True

def run_all_tests():
    """Run all endpoint structure tests"""
    print("="*60)
    print("ElevenLabs API Endpoint Structure Tests")
    print("="*60)
    
    tests = [
        ("Endpoint Structure", test_endpoint_structure),
        ("TTS ElevenLabs Validation", test_tts_elevenlabs_validation),
        ("Voices ElevenLabs Validation", test_voices_elevenlabs_validation),
        ("Voice Sample Validation", test_voice_sample_validation),
        ("Schema Validation", test_schema_validation),
        ("Error Response Format", test_error_response_format)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
    
    print("\n" + "="*60)
    print(f"Test Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("🎉 All endpoint structure tests passed!")
        print("\nNext steps:")
        print("1. Start the server: uvicorn tts_api:app --reload")
        print("2. Test with real ElevenLabs API key using curl commands")
        print("3. Verify audio file generation and quality")
        return True
    else:
        print("⚠️  Some tests failed. Please fix the issues before proceeding.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)