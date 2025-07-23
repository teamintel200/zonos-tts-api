import os
import glob
import re
from typing import List

OUTPUTS_DIR = "outputs"

def get_next_output_filename(tempdir: str, extension: str = "mp3") -> str:
    """Generate the next sequential output filename for TTS audio files."""
    if not tempdir or not isinstance(tempdir, str):
        raise ValueError("tempdir must be a non-empty string")
    
    clean_tempdir = re.sub(r'[/\\]', '_', tempdir.strip())
    if not clean_tempdir:
        raise ValueError("tempdir cannot be empty after sanitization")
    
    base_dir = os.path.join(OUTPUTS_DIR, clean_tempdir)
    output_path = os.path.join(base_dir, "audio", "tts")
    
    try:
        os.makedirs(output_path, exist_ok=True)
    except OSError as e:
        raise OSError(f"Failed to create output directory {output_path}: {e}")
    
    # Count existing files with any audio extension to maintain sequence
    existing_files = []
    for ext in ["mp3", "wav"]:
        existing_files.extend(glob.glob(os.path.join(output_path, f"*.{ext}")))
    
    existing_files = sorted(existing_files)
    next_num = len(existing_files) + 1
    
    return os.path.join(output_path, f"{next_num:04d}.{extension}")

def validate_audio_files_for_combine(tempdir: str) -> List[str]:
    """Validate and return sorted list of audio files ready for combining."""
    if not tempdir or not isinstance(tempdir, str):
        raise ValueError("tempdir must be a non-empty string")
    
    clean_tempdir = re.sub(r'[/\\]', '_', tempdir.strip())
    session_dir = os.path.join(OUTPUTS_DIR, clean_tempdir, "audio", "tts")
    
    if not os.path.isdir(session_dir):
        raise FileNotFoundError(f"Session directory not found: {session_dir}")
    
    # Support both MP3 and WAV files for compatibility with different TTS engines
    files = []
    for ext in ["mp3", "wav"]:
        search_path = os.path.join(session_dir, f"*.{ext}")
        files.extend(glob.glob(search_path))
    
    files = sorted(files)
    
    if not files:
        raise ValueError(f"No audio files found in session directory: {session_dir}")
    
    return files

def get_combined_output_path(tempdir: str) -> str:
    """Generate the output path for combined audio file."""
    if not tempdir or not isinstance(tempdir, str):
        raise ValueError("tempdir must be a non-empty string")
    
    clean_tempdir = re.sub(r'[/\\]', '_', tempdir.strip())
    combined_filename = f"combined_{clean_tempdir}.wav"
    return os.path.join(OUTPUTS_DIR, combined_filename)
