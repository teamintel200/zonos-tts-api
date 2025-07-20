#!/usr/bin/env python3
"""
Test the combine_wav endpoint with utility functions
"""

import os
import shutil
import requests
from pydub import AudioSegment
from utils import get_next_output_filename

def create_test_session():
    """Create a test session with audio files"""
    test_tempdir = "endpoint_test_session"
    
    # Create test audio files using the utility function
    files = []
    for i in range(3):
        output_path = get_next_output_filename(test_tempdir)
        
        # Create a simple audio file
        audio = AudioSegment.silent(duration=1000)  # 1 second
        audio.export(output_path, format="mp3")
        files.append(output_path)
        print(f"Created test file: {os.path.basename(output_path)}")
    
    return test_tempdir, files

def test_combine_endpoint():
    """Test the combine_wav endpoint"""
    print("Testing combine_wav endpoint with utility functions...")
    
    # Create test session
    test_tempdir, files = create_test_session()
    
    try:
        # Test the combine endpoint
        response = requests.post(
            "http://localhost:8000/combine_wav",
            json={"tempdir": test_tempdir}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Combine endpoint successful")
            print(f"✓ Combined file: {result['combined_path']}")
            print(f"✓ Duration: {result['durationMillis']}ms")
            
            # Verify the combined file exists
            if os.path.exists(result['combined_path']):
                print("✓ Combined file exists on disk")
                
                # Verify it's a valid audio file
                combined_audio = AudioSegment.from_wav(result['combined_path'])
                print(f"✓ Combined audio duration: {len(combined_audio)}ms")
                
                # Clean up combined file
                os.remove(result['combined_path'])
                print("✓ Cleaned up combined file")
            else:
                print("❌ Combined file not found on disk")
                
        else:
            print(f"❌ Combine endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running - skipping endpoint test")
        print("To test the endpoint, start the server with: uvicorn tts_api:app --reload")
        
    finally:
        # Clean up test directory (if it still exists)
        test_dir = os.path.join("outputs", test_tempdir)
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print("✓ Cleaned up test directory")

if __name__ == "__main__":
    test_combine_endpoint()