import os
import glob
import re
from typing import List

OUTPUTS_DIR = "outputs"

def get_next_output_filename(tempdir: str) -> str:
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
    
    existing_files = sorted(glob.glob(os.path.join(output_path, "*.mp3")))
    next_num = len(existing_files) + 1
    
    return os.path.join(output_path, f"{next_num:04d}.mp3")

def validate_audio_files_for_combine(tempdir: str) -> List[str]:
    """Validate and return sorted list of audio files ready for combining."""
    if not tempdir or not isinstance(tempdir, str):
        raise ValueError("tempdir must be a non-empty string")
    
    clean_tempdir = re.sub(r'[/\\]', '_', tempdir.strip())
    session_dir = os.path.join(OUTPUTS_DIR, clean_tempdir, "audio", "tts")
    
    if not os.path.isdir(session_dir):
        raise FileNotFoundError(f"Session directory not found: {session_dir}")
    
    search_path = os.path.join(session_dir, "*.mp3")
    files = sorted(glob.glob(search_path))
    
    if not files:
        raise ValueError(f"No MP3 files found in session directory: {session_dir}")
    
    return files

def get_combined_output_path(tempdir: str) -> str:
    """Generate the output path for combined audio file."""
    if not tempdir or not isinstance(tempdir, str):
        raise ValueError("tempdir must be a non-empty string")
    
    clean_tempdir = re.sub(r'[/\\]', '_', tempdir.strip())
    combined_filename = f"combined_{clean_tempdir}.wav"
    return os.path.join(OUTPUTS_DIR, combined_filename)
