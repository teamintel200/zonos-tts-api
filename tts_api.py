from fastapi import FastAPI, Form, Body
import os
import torchaudio
import torch
from gradio_interface import generate_audio
import glob
import torchaudio
from pydantic import BaseModel
from typing import List

app = FastAPI()

# 고정 파라미터
FIXED_PARAMS = {
    "model_choice": "Zyphra/Zonos-v0.1-transformer",
    "language": "ko",
    "e1": 1.0, "e2": 0.05, "e3": 0.05, "e4": 0.05, "e5": 0.05,
    "e6": 0.05, "e7": 0.1, "e8": 0.2, "vq_single": 0.78,
    "fmax": 24000, "pitch_std": 45, "speaking_rate": 15,
    "dnsmos_ovrl": 4.0, "speaker_noised": False, "cfg_scale": 2.0,
    "top_p": 0, "top_k": 0, "min_p": 0, "linear": 0.5, "confidence": 0.4,
    "quadratic": 0, "seed": 420, "randomize_seed": True,
    "unconditional_keys": ["emotion"]
}

class Segment(BaseModel):
    id: int
    text: str

class TTSRequest(BaseModel):
    segments: List[Segment]
    tempdir: str
    speaker_name: str

class Segment(BaseModel):
    id: int
    text: str

class TTSRequest(BaseModel):
    segments: Segment  # 👈 단일 객체
    tempdir: str
    speaker_name: str

# 호출 순서대로 파일명 결정
def get_next_output_filename(tempdir):
    output_path = os.path.join(tempdir, "audio", "tts")
    os.makedirs(output_path, exist_ok=True)
    existing_files = sorted(glob.glob(os.path.join(output_path, "*.wav")))
    next_num = len(existing_files) + 1
    return os.path.join(output_path, f"{next_num:04d}.wav")

@app.post("/tts_simple")
async def tts_simple(req: TTSRequest = Body(...)):
    segment = req.segments
    tempdir = req.tempdir
    speaker_name = req.speaker_name
    id = segment.id
    text = segment.text

    print(f"ID: {segment.id}, Text: {segment.text}")
    print("Tempdir:", req.tempdir)
    print("Speaker:", req.speaker_name)

    # speaker wav 경로 구성
    speaker_audio_path = f"./voice/{speaker_name}.wav"
    if not os.path.isfile(speaker_audio_path):
        return {"error": f"Speaker audio file not found: {speaker_audio_path}"}

    # generate_audio 호출
    (sr_out, wav_out), used_seed = generate_audio(
        model_choice=FIXED_PARAMS["model_choice"],
        text=text,
        language=FIXED_PARAMS["language"],
        speaker_audio=speaker_audio_path,
        prefix_audio=None,
        e1=FIXED_PARAMS["e1"],
        e2=FIXED_PARAMS["e2"],
        e3=FIXED_PARAMS["e3"],
        e4=FIXED_PARAMS["e4"],
        e5=FIXED_PARAMS["e5"],
        e6=FIXED_PARAMS["e6"],
        e7=FIXED_PARAMS["e7"],
        e8=FIXED_PARAMS["e8"],
        vq_single=FIXED_PARAMS["vq_single"],
        fmax=FIXED_PARAMS["fmax"],
        pitch_std=FIXED_PARAMS["pitch_std"],
        speaking_rate=FIXED_PARAMS["speaking_rate"],
        dnsmos_ovrl=FIXED_PARAMS["dnsmos_ovrl"],
        speaker_noised=FIXED_PARAMS["speaker_noised"],
        cfg_scale=FIXED_PARAMS["cfg_scale"],
        top_p=FIXED_PARAMS["top_p"],
        top_k=FIXED_PARAMS["top_k"],
        min_p=FIXED_PARAMS["min_p"],
        linear=FIXED_PARAMS["linear"],
        confidence=FIXED_PARAMS["confidence"],
        quadratic=FIXED_PARAMS["quadratic"],
        seed=FIXED_PARAMS["seed"],
        randomize_seed=FIXED_PARAMS["randomize_seed"],
        unconditional_keys=FIXED_PARAMS["unconditional_keys"]
    )

    # 결과 파일 저장
    output_path = get_next_output_filename(tempdir)
    torchaudio.save(output_path, torch.tensor(wav_out).unsqueeze(0), sample_rate=sr_out)

    info = torchaudio.info(output_path)
    duration_ms = int(info.num_frames / info.sample_rate * 1000)

    return {
        "sequence": id,
        "text": text,
        "durationMillis": duration_ms
    }


@app.post("/combine_wav")
async def combine_wav(tempdir: str = Form(...)):
    tts_dir = os.path.join(tempdir, "audio", "tts")
    pattern = os.path.join(tts_dir, "*.wav")
    files = glob.glob(pattern)

    if not files:
        return {"error": f"No wav files found in: {tts_dir}"}

    def extract_num(file_path):
        filename = os.path.splitext(os.path.basename(file_path))[0]
        return int(filename)

    files_sorted = sorted(files, key=extract_num)

    # 첫 파일 로드
    combined_waveform, sr = torchaudio.load(files_sorted[0])

    # 이후 파일 결합
    for file in files_sorted[1:]:
        waveform, _ = torchaudio.load(file)
        combined_waveform = torch.cat((combined_waveform, waveform), dim=1)

    # 저장 경로
    combined_path = os.path.join(tempdir, "audio", "tts", "combined.wav")
    torchaudio.save(combined_path, combined_waveform, sample_rate=sr)

    # 개별 파일 삭제
    for f in files_sorted:
        os.remove(f)

    # 총 길이 계산 (밀리초)
    total_duration_ms = int(combined_waveform.shape[1] / sr * 1000)

    return {
        "combined_path": combined_path,
        "durationMillis": total_duration_ms
    }
