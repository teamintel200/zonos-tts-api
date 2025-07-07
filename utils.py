import os
import glob

OUTPUTS_DIR = "outputs"

def get_next_output_filename(tempdir: str) -> str:
    base_dir = os.path.join(OUTPUTS_DIR, tempdir)
    output_path = os.path.join(base_dir, "audio", "tts")
    os.makedirs(output_path, exist_ok=True)
    existing_files = sorted(glob.glob(os.path.join(output_path, "*.mp3")))
    next_num = len(existing_files) + 1
    return os.path.join(output_path, f"{next_num:04d}.mp3")
