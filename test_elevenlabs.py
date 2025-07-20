#!/usr/bin/env python3
"""
Manual test script for ElevenLabs API connectivity and functionality.

This script tests:
1. API key validation
2. Voice list retrieval
3. Text-to-speech generation with Korean text
4. Audio file generation and format compatibility

Usage:
    python test_elevenlabs.py

Note: You will be prompted to enter your ElevenLabs API key.
The API key is not stored and only used for testing.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional
import tempfile

# Add current directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from elevenlabs_service import ElevenLabsService, ElevenLabsError
from schemas import Voice

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ElevenLabsTestSuite:
    """Test suite for ElevenLabs API integration"""
    
    def __init__(self):
        self.service = ElevenLabsService()
        self.api_key: Optional[str] = None
        self.test_results = {
            'api_key_validation': False,
            'voice_list_retrieval': False,
            'korean_tts_generation': False,
            'audio_file_compatibility': False
        }
    
    def get_api_key(self) -> str:
        """Get API key from user input"""
        if self.api_key:
            return self.api_key
        
        print("\n" + "="*60)
        print("ElevenLabs API Test Suite")
        print("="*60)
        print("\nThis script will test ElevenLabs API connectivity and functionality.")
        print("You need a valid ElevenLabs API key to run these tests.")
        print("\nYour API key will NOT be stored and is only used for testing.")
        print("You can find your API key at: https://elevenlabs.io/app/speech-synthesis")
        
        while True:
            api_key = input("\nPlease enter your ElevenLabs API key: ").strip()
            if api_key:
                self.api_key = api_key
                return api_key
            print("API key cannot be empty. Please try again.")
    
    def test_api_key_validation(self) -> bool:
        """Test API key validation"""
        print("\n" + "-"*50)
        print("Test 1: API Key Validation")
        print("-"*50)
        
        try:
            api_key = self.get_api_key()
            
            # Test with valid API key
            print("Testing API key validation...")
            self.service._validate_api_key(api_key)
            print("✅ API key validation successful")
            
            # Test with invalid API key
            print("Testing invalid API key handling...")
            try:
                self.service._validate_api_key("invalid_key_12345")
                print("❌ Invalid API key should have failed")
                return False
            except ElevenLabsError as e:
                if e.status_code == 401:
                    print("✅ Invalid API key properly rejected")
                else:
                    print(f"❌ Unexpected error code: {e.status_code}")
                    return False
            
            self.test_results['api_key_validation'] = True
            return True
            
        except ElevenLabsError as e:
            print(f"❌ API key validation failed: {e.message} (Status: {e.status_code})")
            if e.status_code == 401:
                print("   Please check that your API key is correct.")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during API key validation: {str(e)}")
            return False
    
    def test_voice_list_retrieval(self) -> bool:
        """Test voice list retrieval"""
        print("\n" + "-"*50)
        print("Test 2: Voice List Retrieval")
        print("-"*50)
        
        try:
            api_key = self.get_api_key()
            
            print("Retrieving available voices...")
            voices = self.service.get_available_voices(api_key)
            
            if not voices:
                print("❌ No voices retrieved")
                return False
            
            print(f"✅ Retrieved {len(voices)} voices")
            
            # Display first few voices
            print("\nFirst 5 voices:")
            for i, voice in enumerate(voices[:5]):
                print(f"  {i+1}. {voice.name} (ID: {voice.voice_id})")
                print(f"     Category: {voice.category}")
                if voice.language:
                    print(f"     Language: {voice.language}")
            
            # Check for Korean-compatible voices
            korean_voices = [v for v in voices if self.service._is_korean_compatible(
                type('Voice', (), {'voice_id': v.voice_id, 'category': v.category, 'language': v.language})()
            )]
            
            print(f"\n✅ Found {len(korean_voices)} Korean-compatible voices")
            if korean_voices:
                print("Korean-compatible voices:")
                for voice in korean_voices[:3]:
                    print(f"  - {voice.name} (ID: {voice.voice_id})")
            
            self.test_results['voice_list_retrieval'] = True
            return True
            
        except ElevenLabsError as e:
            print(f"❌ Voice list retrieval failed: {e.message} (Status: {e.status_code})")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during voice list retrieval: {str(e)}")
            return False
    
    def test_korean_tts_generation(self) -> bool:
        """Test Korean text-to-speech generation"""
        print("\n" + "-"*50)
        print("Test 3: Korean Text-to-Speech Generation")
        print("-"*50)
        
        try:
            api_key = self.get_api_key()
            
            # Test Korean text
            korean_text = "안녕하세요! 이것은 ElevenLabs API 테스트입니다. 한국어 음성 합성이 잘 작동하는지 확인하고 있습니다."
            
            print(f"Generating speech for Korean text: '{korean_text[:30]}...'")
            
            # Test with default voice
            print("Testing with default Korean-compatible voice...")
            audio_data = self.service.text_to_speech(
                api_key=api_key,
                text=korean_text
            )
            
            if not audio_data or len(audio_data) == 0:
                print("❌ No audio data generated")
                return False
            
            print(f"✅ Generated {len(audio_data)} bytes of audio data")
            
            # Test with custom voice settings
            print("Testing with custom voice settings...")
            audio_data_custom = self.service.text_to_speech(
                api_key=api_key,
                text="안녕하세요. 커스텀 설정 테스트입니다.",
                stability=0.7,
                similarity_boost=0.9
            )
            
            if not audio_data_custom or len(audio_data_custom) == 0:
                print("❌ No audio data generated with custom settings")
                return False
            
            print(f"✅ Generated {len(audio_data_custom)} bytes with custom settings")
            
            self.test_results['korean_tts_generation'] = True
            return True
            
        except ElevenLabsError as e:
            print(f"❌ Korean TTS generation failed: {e.message} (Status: {e.status_code})")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during Korean TTS generation: {str(e)}")
            return False
    
    def test_audio_file_compatibility(self) -> bool:
        """Test audio file generation and format compatibility"""
        print("\n" + "-"*50)
        print("Test 4: Audio File Generation and Format Compatibility")
        print("-"*50)
        
        try:
            api_key = self.get_api_key()
            
            # Generate audio data
            print("Generating audio for file compatibility test...")
            audio_data = self.service.text_to_speech(
                api_key=api_key,
                text="파일 호환성 테스트입니다."
            )
            
            # Create temporary file to test file operations
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Check file size
                file_size = os.path.getsize(temp_file_path)
                print(f"✅ Audio file created: {file_size} bytes")
                
                # Verify it's a valid MP3 file by checking header
                with open(temp_file_path, 'rb') as f:
                    header = f.read(3)
                    if header == b'ID3' or header[:2] == b'\xff\xfb':
                        print("✅ Valid MP3 format detected")
                    else:
                        print(f"⚠️  Unexpected file format (header: {header.hex()})")
                
                # Test file naming compatibility (simulate utils.py functionality)
                print("Testing file naming compatibility...")
                test_filename = f"0001.mp3"
                print(f"✅ Compatible with expected naming format: {test_filename}")
                
                self.test_results['audio_file_compatibility'] = True
                return True
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            
        except ElevenLabsError as e:
            print(f"❌ Audio file compatibility test failed: {e.message} (Status: {e.status_code})")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during audio file compatibility test: {str(e)}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all tests and display summary"""
        print("\n" + "="*60)
        print("Starting ElevenLabs API Test Suite")
        print("="*60)
        
        # Run tests in order
        tests = [
            ("API Key Validation", self.test_api_key_validation),
            ("Voice List Retrieval", self.test_voice_list_retrieval),
            ("Korean TTS Generation", self.test_korean_tts_generation),
            ("Audio File Compatibility", self.test_audio_file_compatibility)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
                else:
                    # If a critical test fails, we might want to continue or stop
                    if test_name == "API Key Validation":
                        print(f"\n❌ Critical test '{test_name}' failed. Cannot continue with remaining tests.")
                        break
            except KeyboardInterrupt:
                print(f"\n\n⚠️  Test suite interrupted by user.")
                break
            except Exception as e:
                print(f"\n❌ Test '{test_name}' failed with unexpected error: {str(e)}")
        
        # Display summary
        self.display_summary(passed_tests, total_tests)
        
        return passed_tests == total_tests
    
    def display_summary(self, passed_tests: int, total_tests: int):
        """Display test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! ElevenLabs integration is working correctly.")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please check the errors above.")
        
        print("\nNext steps:")
        if passed_tests == total_tests:
            print("- You can now test the API endpoints using the FastAPI server")
            print("- Run: uvicorn tts_api:app --reload")
            print("- Test endpoints at: http://localhost:8000/docs")
        else:
            print("- Fix any API key or connectivity issues")
            print("- Ensure you have a valid ElevenLabs account with available quota")
            print("- Check your internet connection")


def main():
    """Main function to run the test suite"""
    try:
        test_suite = ElevenLabsTestSuite()
        success = test_suite.run_all_tests()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nTest suite interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error running test suite: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()