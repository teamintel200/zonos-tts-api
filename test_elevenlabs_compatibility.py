#!/usr/bin/env python3
"""
Test script to verify ElevenLabs compatibility with utility functions
This test simulates the actual ElevenLabs workflow to ensure compatibility
"""

import os
import tempfile
import shutil
import sys
from pydub import AudioSegment
from utils import get_next_output_filename, validate_audio_files_for_combine, get_combined_output_path

def create_test_mp3(file_path: str, duration_ms: int = 1000):
    """Create a test MP3 file with specified duration"""
    # Create a simple audio segment with the specified duration
    audio = AudioSegment.silent(duration=duration_ms)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Export as MP3
    audio.export(file_path, format="mp3")
    return file_path

def test_elevenlabs_file_generation():
    """Test that get_next_output_filename works for ElevenLabs workflow"""
    print("Testing ElevenLabs file generation workflow...")
    
    test_tempdir = "elevenlabs_test_session"
    
    try:
        # Simulate ElevenLabs TTS generation workflow
        segments = [
            {"id": 1, "text": "안녕하세요"},
            {"id": 2, "text": "이것은 테스트입니다"},
            {"id": 3, "text": "ElevenLabs 호환성 테스트"}
        ]
        
        generated_files = []
        
        # Simulate the ElevenLabs TTS endpoint behavior
        for segment in segments:
            # Get next output filename (same as in tts_elevenlabs endpoint)
            output_path = get_next_output_filename(test_tempdir)
            
            # Create a test MP3 file (simulating ElevenLabs audio generation)
            create_test_mp3(output_path, duration_ms=2000)
            generated_files.append(output_path)
            
            print(f"✓ Generated file for segment {segment['id']}: {os.path.basename(output_path)}")
        
        # Verify file naming consistency
        expected_names = ["0001.mp3", "0002.mp3", "0003.mp3"]
        for i, file_path in enumerate(generated_files):
            filename = os.path.basename(file_path)
            assert filename == expected_names[i], f"Expected {expected_names[i]}, got {filename}"
        
        print("✓ File naming is consistent with expected pattern")
        
        # Test that validate_audio_files_for_combine works with these files
        audio_files = validate_audio_files_for_combine(test_tempdir)
        assert len(audio_files) == 3, f"Expected 3 files, got {len(audio_files)}"
        
        print("✓ validate_audio_files_for_combine works with ElevenLabs files")
        
        # Test combine functionality (simulate combine_wav logic)
        combined = AudioSegment.empty()
        total_duration = 0
        
        for file_path in audio_files:
            sound = AudioSegment.from_mp3(file_path)
            combined += sound
            total_duration += len(sound)
            print(f"✓ Successfully loaded and combined: {os.path.basename(file_path)}")
        
        # Test combined output path generation
        combined_path = get_combined_output_path(test_tempdir)
        combined.export(combined_path, format="wav")
        
        # Verify the combined file exists and has expected duration
        assert os.path.exists(combined_path), "Combined file was not created"
        
        # Load the combined file to verify it's valid
        combined_audio = AudioSegment.from_wav(combined_path)
        assert len(combined_audio) == total_duration, "Combined audio duration mismatch"
        
        print(f"✓ Combined audio file created: {os.path.basename(combined_path)}")
        print(f"✓ Total duration: {total_duration}ms")
        
        print("✅ ElevenLabs file generation workflow test passed")
        
    finally:
        # Clean up test files
        test_dir = os.path.join("outputs", test_tempdir)
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        combined_file = os.path.join("outputs", f"combined_{test_tempdir}.wav")
        if os.path.exists(combined_file):
            os.remove(combined_file)

def test_mixed_gtts_elevenlabs_compatibility():
    """Test that gTTS and ElevenLabs files can be combined together"""
    print("\nTesting mixed gTTS and ElevenLabs file compatibility...")
    
    test_tempdir = "mixed_engines_test"
    
    try:
        # Simulate mixed workflow: gTTS -> ElevenLabs -> gTTS
        files_info = [
            {"engine": "gTTS", "text": "첫 번째 세그먼트"},
            {"engine": "ElevenLabs", "text": "두 번째 세그먼트"},
            {"engine": "gTTS", "text": "세 번째 세그먼트"},
            {"engine": "ElevenLabs", "text": "네 번째 세그먼트"}
        ]
        
        generated_files = []
        
        for i, file_info in enumerate(files_info, 1):
            # Both engines use the same utility function
            output_path = get_next_output_filename(test_tempdir)
            
            # Create test audio (duration varies to simulate different engines)
            duration = 1500 if file_info["engine"] == "gTTS" else 2000
            create_test_mp3(output_path, duration_ms=duration)
            generated_files.append(output_path)
            
            print(f"✓ Generated {file_info['engine']} file {i}: {os.path.basename(output_path)}")
        
        # Verify sequential naming regardless of engine
        for i, file_path in enumerate(generated_files, 1):
            expected_name = f"{i:04d}.mp3"
            actual_name = os.path.basename(file_path)
            assert actual_name == expected_name, f"Expected {expected_name}, got {actual_name}"
        
        print("✓ Sequential naming maintained across different engines")
        
        # Test that combine functionality works with mixed files
        audio_files = validate_audio_files_for_combine(test_tempdir)
        assert len(audio_files) == 4, f"Expected 4 files, got {len(audio_files)}"
        
        # Simulate combine_wav logic
        combined = AudioSegment.empty()
        for file_path in audio_files:
            sound = AudioSegment.from_mp3(file_path)
            combined += sound
        
        # Export combined file
        combined_path = get_combined_output_path(test_tempdir)
        combined.export(combined_path, format="wav")
        
        # Verify combined file
        assert os.path.exists(combined_path), "Combined file was not created"
        combined_audio = AudioSegment.from_wav(combined_path)
        
        # Should have 4 segments: 1500ms + 2000ms + 1500ms + 2000ms = 7000ms
        expected_duration = 1500 + 2000 + 1500 + 2000
        actual_duration = len(combined_audio)
        
        # Allow small tolerance for audio processing
        assert abs(actual_duration - expected_duration) < 100, f"Duration mismatch: expected ~{expected_duration}ms, got {actual_duration}ms"
        
        print(f"✓ Combined mixed-engine audio: {actual_duration}ms duration")
        print("✅ Mixed gTTS and ElevenLabs compatibility test passed")
        
    finally:
        # Clean up test files
        test_dir = os.path.join("outputs", test_tempdir)
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        combined_file = os.path.join("outputs", f"combined_{test_tempdir}.wav")
        if os.path.exists(combined_file):
            os.remove(combined_file)

def test_audio_format_compatibility():
    """Test that ElevenLabs MP3 format is compatible with combine functionality"""
    print("\nTesting audio format compatibility...")
    
    test_tempdir = "format_compatibility_test"
    
    try:
        # Create files with different audio characteristics to test robustness
        test_cases = [
            {"name": "short", "duration": 500, "frequency": 440},
            {"name": "medium", "duration": 2000, "frequency": 880},
            {"name": "long", "duration": 5000, "frequency": 220},
        ]
        
        generated_files = []
        
        for test_case in test_cases:
            output_path = get_next_output_filename(test_tempdir)
            
            # Create audio with specific duration (simplified approach)
            create_test_mp3(output_path, duration_ms=test_case["duration"])
            generated_files.append(output_path)
            
            print(f"✓ Created {test_case['name']} audio file: {test_case['duration']}ms")
        
        # Test that all files can be loaded and combined
        audio_files = validate_audio_files_for_combine(test_tempdir)
        combined = AudioSegment.empty()
        total_expected_duration = 0
        
        for i, file_path in enumerate(audio_files):
            sound = AudioSegment.from_mp3(file_path)
            combined += sound
            total_expected_duration += test_cases[i]["duration"]
            print(f"✓ Successfully processed {test_cases[i]['name']} file")
        
        # Export and verify combined file
        combined_path = get_combined_output_path(test_tempdir)
        combined.export(combined_path, format="wav")
        
        combined_audio = AudioSegment.from_wav(combined_path)
        actual_duration = len(combined_audio)
        
        # Verify duration (allow small tolerance)
        assert abs(actual_duration - total_expected_duration) < 100, f"Duration mismatch: expected {total_expected_duration}ms, got {actual_duration}ms"
        
        print(f"✓ Combined audio duration: {actual_duration}ms (expected: {total_expected_duration}ms)")
        print("✅ Audio format compatibility test passed")
        
    finally:
        # Clean up test files
        test_dir = os.path.join("outputs", test_tempdir)
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        combined_file = os.path.join("outputs", f"combined_{test_tempdir}.wav")
        if os.path.exists(combined_file):
            os.remove(combined_file)

def test_error_handling_compatibility():
    """Test error handling in utility functions with ElevenLabs workflow"""
    print("\nTesting error handling compatibility...")
    
    # Test 1: Invalid tempdir handling (function sanitizes paths)
    result = get_next_output_filename("../invalid/path")
    # Should sanitize the path and return a safe filename
    assert "outputs" in result and ".._invalid_path" in result
    print("✓ Invalid tempdir properly sanitized")
    
    # Test 2: Missing directory for validation
    try:
        validate_audio_files_for_combine("nonexistent_session")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        print("✓ Missing directory properly handled")
    
    # Test 3: Empty directory
    test_tempdir = "empty_test_session"
    try:
        # Create empty directory
        session_dir = os.path.join("outputs", test_tempdir, "audio", "tts")
        os.makedirs(session_dir, exist_ok=True)
        
        validate_audio_files_for_combine(test_tempdir)
        assert False, "Should have raised ValueError for empty directory"
    except ValueError:
        print("✓ Empty directory properly handled")
    finally:
        test_dir = os.path.join("outputs", test_tempdir)
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
    
    print("✅ Error handling compatibility test passed")

if __name__ == "__main__":
    print("Running ElevenLabs compatibility tests...\n")
    
    try:
        test_elevenlabs_file_generation()
        test_mixed_gtts_elevenlabs_compatibility()
        test_audio_format_compatibility()
        test_error_handling_compatibility()
        
        print("\n🎉 All ElevenLabs compatibility tests passed!")
        print("✅ ElevenLabs file generation workflow works correctly")
        print("✅ Mixed gTTS and ElevenLabs files can be combined")
        print("✅ Audio format compatibility verified")
        print("✅ Error handling works correctly")
        print("✅ Utility functions are fully compatible with ElevenLabs")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        sys.exit(1)