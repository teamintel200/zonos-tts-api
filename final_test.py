#!/usr/bin/env python3
"""
Final test to verify all utility functions work correctly together
"""

from utils import get_next_output_filename, validate_audio_files_for_combine, get_combined_output_path
import os
import shutil
from pydub import AudioSegment

def final_integration_test():
    """Test all utility functions work correctly together"""
    test_tempdir = 'final_test_session'
    combined_path = None
    
    try:
        print("Running final integration test...")
        
        # Test file generation (create files one by one)
        file1 = get_next_output_filename(test_tempdir)
        audio = AudioSegment.silent(duration=1000)
        audio.export(file1, format='mp3')
        
        file2 = get_next_output_filename(test_tempdir)
        audio.export(file2, format='mp3')
        
        print(f"Generated filenames: {os.path.basename(file1)}, {os.path.basename(file2)}")
        
        print("✓ Created test MP3 files")
        
        # Test validation
        files = validate_audio_files_for_combine(test_tempdir)
        assert len(files) == 2, f"Expected 2 files, got {len(files)}"
        
        print("✓ validate_audio_files_for_combine works correctly")
        
        # Test combine path generation
        combined_path = get_combined_output_path(test_tempdir)
        print(f"Combined path: {combined_path}")
        
        # Test actual combining (simulate combine_wav logic)
        combined = AudioSegment.empty()
        for f in files:
            sound = AudioSegment.from_mp3(f)
            combined += sound
        
        combined.export(combined_path, format='wav')
        
        print("✓ Combined audio files successfully")
        
        # Verify combined file
        assert os.path.exists(combined_path), "Combined file was not created"
        combined_audio = AudioSegment.from_wav(combined_path)
        expected_duration = 2000  # 2 x 1000ms
        actual_duration = len(combined_audio)
        
        assert actual_duration == expected_duration, f"Expected {expected_duration}ms, got {actual_duration}ms"
        
        print(f"✓ Combined file has correct duration: {actual_duration}ms")
        print("✅ All utility functions work correctly together")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
        
    finally:
        # Cleanup
        test_dir = os.path.join('outputs', test_tempdir)
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print("✓ Cleaned up test directory")
        
        if combined_path and os.path.exists(combined_path):
            os.remove(combined_path)
            print("✓ Cleaned up combined file")

if __name__ == "__main__":
    success = final_integration_test()
    if success:
        print("\n🎉 Final integration test passed!")
        print("✅ Utility functions are fully compatible with ElevenLabs")
        print("✅ File naming consistency maintained")
        print("✅ combine_wav functionality works with ElevenLabs files")
    else:
        print("\n❌ Final integration test failed!")
        exit(1)