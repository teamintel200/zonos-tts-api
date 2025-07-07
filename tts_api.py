from fastapi import FastAPI, Body, HTTPException
import os
from gtts import gTTS
from pydub import AudioSegment
import shutil
import glob

from schemas import Segment, TTSRequest, CombineRequest
from utils import get_next_output_filename, OUTPUTS_DIR

app = FastAPI()

@app.post("/tts_simple")
async def tts_simple(req: TTSRequest = Body(...)):
    results = []
    for segment in req.segments:
        output_path = get_next_output_filename(req.tempdir)
        print(f"Tempdir: {req.tempdir}, ID: {segment.id}, Text: {segment.text}, Path: {output_path}")
        try:
            tts = gTTS(text=segment.text, lang='ko')
            tts.save(output_path)
            audio = AudioSegment.from_mp3(output_path)
            duration_ms = len(audio)
            results.append({
                "sequence": segment.id,
                "text": segment.text,
                "durationMillis": duration_ms,
                "path": output_path
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return results

@app.post("/combine_wav")
async def combine_wav(req: CombineRequest = Body(...)):
    session_dir = os.path.join(OUTPUTS_DIR, req.tempdir, "audio", "tts")
    if not os.path.isdir(session_dir):
        raise HTTPException(status_code=404, detail=f"Directory not found: {session_dir}")

    search_path = os.path.join(session_dir, "*.mp3")
    files = sorted(glob.glob(search_path))

    if not files:
        raise HTTPException(status_code=404, detail=f"No MP3 files found in: {session_dir}")

    combined = AudioSegment.empty()
    for file_path in files:
        sound = AudioSegment.from_mp3(file_path)
        combined += sound

    dir_to_delete = os.path.join(OUTPUTS_DIR, req.tempdir)

    combined_filename = f"combined_{req.tempdir}.wav"
    combined_path = os.path.join(OUTPUTS_DIR, combined_filename)
    combined.export(combined_path, format="wav")

    shutil.rmtree(dir_to_delete)

    total_duration_ms = len(combined)

    return {
        "combined_path": combined_path,
        "durationMillis": total_duration_ms
    }