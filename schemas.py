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
    api_key: str = Field(description="ElevenLabs API key (required)")
    voice_id: Optional[str] = None
    stability: Optional[float] = Field(default=0.5, ge=0.0, le=1.0)
    similarity_boost: Optional[float] = Field(default=0.8, ge=0.0, le=1.0)
    style: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)  # 감정/스타일 조절
    use_speaker_boost: Optional[bool] = Field(default=True)  # 화자 부스트
    speaking_rate: Optional[float] = Field(default=1.0, ge=0.25, le=4.0)  # 읽기 속도 (0.25x ~ 4.0x) - 기본값 1.0 권장
    seed: Optional[int] = Field(default=None, ge=0, le=2147483647)  # 재현 가능한 결과
    output_format: Optional[str] = Field(default="mp3_44100_128")  # 오디오 품질

class VoicesRequest(BaseModel):
    api_key: str = Field(description="API key (required)")

class SupertoneVoiceSampleRequest(BaseModel):
    api_key: str = Field(description="Supertone API key (required)")
    language: Optional[str] = Field(default="ko", description="Language code (ko, en, ja)")
    style: Optional[str] = Field(default="neutral", description="Voice style for preview")
    sample_text: Optional[str] = Field(default=None, description="Custom sample text (optional)")

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

class VoicevoxTTSRequest(BaseModel):
    segments: List[Segment]
    tempdir: str
    speaker_id: int = Field(default=2, description="Voicevox speaker ID (default: 四국めたん 노멀)")
    speed_scale: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed scale")
    pitch_scale: float = Field(default=0.0, ge=-0.15, le=0.15, description="Pitch adjustment scale")
    intonation_scale: float = Field(default=1.0, ge=0.0, le=2.0, description="Intonation strength scale")
    volume_scale: float = Field(default=1.0, ge=0.0, le=2.0, description="Volume scale")
    pre_phoneme_length: float = Field(default=0.1, ge=0.0, le=1.5, description="Pre-phoneme length in seconds")
    post_phoneme_length: float = Field(default=0.1, ge=0.0, le=1.5, description="Post-phoneme length in seconds")
    enable_interrogative_upspeak: bool = Field(default=True, description="Enable automatic interrogative upspeak")

class VoicevoxSpeaker(BaseModel):
    speaker_id: int = Field(description="Unique speaker identifier")
    name: str = Field(description="Speaker name (Japanese)")
    english_name: str = Field(description="Speaker name (English)")
    style_id: int = Field(description="Style identifier for the speaker")
    style_name: str = Field(description="Style name (Japanese, e.g., ノーマル, あまあま)")
    english_style_name: str = Field(description="Style name (English, e.g., Normal, Sweet)")
    type: str = Field(description="Speaker type (e.g., talk, sing)")
    is_free: bool = Field(default=True, description="Whether the speaker is free for commercial use")

class SupertoneTTSRequest(BaseModel):
    segments: List[Segment]
    tempdir: str
    api_key: str = Field(description="Supertone API key (required)")
    voice_id: str = Field(description="Supertone voice identifier")
    language: str = Field(default="ko", description="Language code (ko, en, ja)")
    style: Optional[str] = Field(default="neutral", description="Emotional style (neutral, happy, sad, angry, etc.)")
    model: Optional[str] = Field(default="sona_speech_1", description="Supertone model name")
    pitch_shift: Optional[float] = Field(default=0.0, ge=-12.0, le=12.0, description="Pitch adjustment (-12 to +12)")
    pitch_variance: Optional[float] = Field(default=1.0, ge=0.1, le=2.0, description="Intonation variation (0.1 to 2.0)")
    speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0, description="Speech rate (0.5 to 2.0)")
    output_format: Optional[str] = Field(default="wav", description="Output format (wav, mp3)")

class SupertoneVoice(BaseModel):
    voice_id: str = Field(description="Unique voice identifier")
    name: str = Field(description="Voice display name")
    gender: str = Field(description="Voice gender")
    age: Optional[str] = Field(description="Voice age range")
    use_case: Optional[str] = Field(description="Recommended use case")
    supported_languages: List[str] = Field(description="Supported language codes")
    available_styles: List[str] = Field(description="Available emotional styles")

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
