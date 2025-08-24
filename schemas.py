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

class SpeedAdjustRequest(BaseModel):
    input_file: str  # 입력 파일 경로
    speed_rate: float = Field(default=1.5, ge=0.25, le=4.0)  # 속도 배율
    method: str = Field(default="librosa", pattern="^(librosa|pydub)$")  # 속도 조절 방법
    preserve_pitch: bool = Field(default=True)  # 피치 유지 여부

class SktAxTTSRequest(BaseModel):
    segments: List[Segment]
    tempdir: str
    api_key: str = Field(description="SKT A.X TTS API key (required)")
    voice: str = Field(description="SKT A.X TTS voice name (model is auto-determined)")
    speed: Optional[str] = Field(default="1.0", description="Speech speed (e.g., '0.8', '1.0', '1.3')")
    sr: Optional[int] = Field(default=22050, description="Sample rate (default: 22050)")
    sformat: Optional[str] = Field(default="wav", description="Output format (wav, mp3)")

class SktAxVoice(BaseModel):
    voice_name: str = Field(description="Voice name identifier")
    voice_id: str = Field(description="Internal voice ID")
    model: str = Field(description="Model name (axtts-2-6, axtts-2-1, axtts-2-1-dialect)")
    gender: str = Field(description="Voice gender")
    age: str = Field(description="Voice age range")
    style: str = Field(description="Voice style and characteristics")
    nickname: str = Field(description="Voice nickname")
    language: str = Field(description="Language code (ko-KR)")

class SktAxVoicesRequest(BaseModel):
    api_key: str = Field(description="SKT A.X TTS API key (required)")

class CleanupRequest(BaseModel):
    max_age_hours: Optional[float] = Field(default=1.0, description="Maximum age of files to keep (in hours)")
    force_cleanup: Optional[bool] = Field(default=False, description="Force cleanup of all files regardless of age")