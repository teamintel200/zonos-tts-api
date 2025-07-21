from pydantic import BaseModel, Field
from typing import List, Optional

class Segment(BaseModel):
    id: int
    text: str

class TTSRequest(BaseModel):
    segments: List[Segment]
    tempdir: str

class CombineRequest(BaseModel):
    tempdir: str

class ElevenLabsTTSRequest(BaseModel):
    segments: List[Segment]
    tempdir: str
    api_key: Optional[str] = None  # Optional - will use environment variable if not provided
    voice_id: Optional[str] = None
    stability: Optional[float] = Field(default=0.5, ge=0.0, le=1.0)
    similarity_boost: Optional[float] = Field(default=0.8, ge=0.0, le=1.0)
    style: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)  # 감정/스타일 조절
    use_speaker_boost: Optional[bool] = Field(default=True)  # 화자 부스트
    speaking_rate: Optional[float] = Field(default=1.0, ge=0.25, le=4.0)  # 읽기 속도 (0.25x ~ 4.0x) - 기본값 1.0 권장
    seed: Optional[int] = Field(default=None, ge=0, le=2147483647)  # 재현 가능한 결과
    output_format: Optional[str] = Field(default="mp3_44100_128")  # 오디오 품질

class VoicesRequest(BaseModel):
    api_key: Optional[str] = None  # Optional - will use environment variable if not provided

class Voice(BaseModel):
    voice_id: str
    name: str
    category: str
    language: Optional[str] = None

class SpeedAdjustRequest(BaseModel):
    input_file: str  # 입력 파일 경로
    speed_rate: float = Field(default=1.5, ge=0.25, le=4.0)  # 속도 배율
    method: str = Field(default="librosa", pattern="^(librosa|pydub)$")  # 속도 조절 방법
    preserve_pitch: bool = Field(default=True)  # 피치 유지 여부
