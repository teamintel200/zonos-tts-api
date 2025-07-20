# Design Document

## Overview

기존 gTTS 기반 TTS API 서버에 ElevenLabs AI TTS 기능을 추가하는 설계입니다. 기존 API는 그대로 유지하면서 ElevenLabs 전용 엔드포인트들을 새로 추가하여, 사용자가 자신의 API 키로 고품질 AI 음성 합성을 사용할 수 있도록 합니다.

## Architecture

### Project Structure
```
Project Root
├── tts_api.py              # Main FastAPI application (all endpoints)
├── schemas.py              # Pydantic data models
├── utils.py                # Utility functions (file management)
├── elevenlabs_service.py   # ElevenLabs service layer (NEW)
├── requirements.txt        # Dependencies
├── Dockerfile             # Container configuration
└── outputs/               # Audio file storage
```

### API Endpoints Structure
```
FastAPI App (tts_api.py)
├── [Existing] POST /tts_simple (gTTS)
├── [Existing] POST /combine_wav
├── [NEW] POST /tts_elevenlabs
├── [NEW] POST /voices/elevenlabs
└── [NEW] POST /voices/elevenlabs/{voice_id}/sample
```

### Module Dependencies
```
tts_api.py
├── imports schemas.py (data models)
├── imports utils.py (file utilities)
├── imports elevenlabs_service.py (NEW - ElevenLabs logic)
└── uses existing gTTS functionality
```

## Components and Interfaces

### 1. New API Endpoints

#### `/tts_elevenlabs` (POST)
- **Purpose**: ElevenLabs TTS 생성 (기존 `/tts_simple`과 동일한 워크플로우)
- **Input**: 
  ```json
  {
    "segments": [{"id": 1, "text": "안녕하세요"}],
    "tempdir": "session_name",
    "api_key": "user_elevenlabs_api_key",
    "voice_id": "optional_voice_id",
    "stability": 0.5,
    "similarity_boost": 0.8
  }
  ```
- **Output**: 기존 `/tts_simple`과 동일한 형식

#### `/voices/elevenlabs` (POST)
- **Purpose**: 사용 가능한 ElevenLabs 음성 목록 조회
- **Input**: 
  ```json
  {
    "api_key": "user_elevenlabs_api_key"
  }
  ```
- **Output**: 
  ```json
  [
    {
      "voice_id": "voice_id_string",
      "name": "Voice Name",
      "category": "premade/cloned",
      "language": "ko/en/etc"
    }
  ]
  ```

#### `/voices/elevenlabs/{voice_id}/sample` (POST)
- **Purpose**: 특정 음성의 샘플 오디오 제공
- **Input**: 
  ```json
  {
    "api_key": "user_elevenlabs_api_key"
  }
  ```
- **Output**: Audio file stream

### 2. Service Layer Components

#### ElevenLabsService
```python
class ElevenLabsService:
    def generate_speech(api_key, text, voice_id, settings) -> bytes
    def get_voices(api_key) -> List[Voice]
    def get_voice_sample(api_key, voice_id) -> bytes
    def validate_api_key(api_key) -> bool
```

#### ElevenLabsClient
```python
class ElevenLabsClient:
    def __init__(api_key)
    def text_to_speech(text, voice_id, stability, similarity_boost)
    def get_available_voices()
    def get_voice_preview(voice_id)
```

### 3. Data Models (Extended)

#### ElevenLabsTTSRequest
```python
class ElevenLabsTTSRequest(BaseModel):
    segments: List[Segment]
    tempdir: str
    api_key: str
    voice_id: Optional[str] = None
    stability: Optional[float] = 0.5
    similarity_boost: Optional[float] = 0.8
```

#### VoicesRequest
```python
class VoicesRequest(BaseModel):
    api_key: str
```

#### Voice
```python
class Voice(BaseModel):
    voice_id: str
    name: str
    category: str
    language: Optional[str] = None
```

## Data Models

### File Structure (Unchanged)
```
outputs/
├── {tempdir}/
│   └── audio/
│       └── tts/
│           ├── 0001.mp3  # gTTS or ElevenLabs generated
│           ├── 0002.mp3
│           └── ...
└── combined_{tempdir}.wav
```

### Audio Format Compatibility
- **ElevenLabs Output**: MP3 format (same as gTTS)
- **File Naming**: Sequential numbering (0001.mp3, 0002.mp3, ...)
- **Combine Compatibility**: ElevenLabs 생성 파일도 기존 `/combine_wav` 엔드포인트에서 처리 가능

## Error Handling

### ElevenLabs API Errors
```python
class ElevenLabsError(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code

# Error Types:
# - 401: Invalid API Key
# - 429: Rate limit exceeded
# - 400: Invalid voice_id or parameters
# - 500: ElevenLabs service unavailable
```

### Error Response Format
```json
{
    "error": "error_type",
    "message": "Human readable error message",
    "details": "Additional technical details if available"
}
```

### Fallback Strategy
- **No Fallback**: ElevenLabs 실패 시 gTTS로 자동 전환하지 않음
- **Clear Error Messages**: 사용자가 문제를 이해하고 해결할 수 있도록 명확한 에러 메시지 제공

## Testing Strategy

### Unit Tests
1. **ElevenLabsService Tests**
   - API key validation
   - Text-to-speech generation
   - Voice list retrieval
   - Error handling

2. **API Endpoint Tests**
   - Request validation
   - Response format verification
   - Error response testing

### Integration Tests
1. **End-to-End Workflow**
   - `/tts_elevenlabs` → `/combine_wav` 전체 플로우
   - File system integration
   - Audio format compatibility

2. **ElevenLabs API Integration**
   - Real API calls with test account
   - Rate limiting behavior
   - Error scenarios

### Mock Testing
```python
# Mock ElevenLabs API responses for consistent testing
@pytest.fixture
def mock_elevenlabs_api():
    with patch('elevenlabs.generate') as mock_generate:
        mock_generate.return_value = b'fake_audio_data'
        yield mock_generate
```

## Security Considerations

### API Key Handling
- **No Storage**: 사용자 API 키를 서버에 저장하지 않음
- **Request Scope**: API 키는 요청 처리 중에만 메모리에 보관
- **Logging**: API 키를 로그에 기록하지 않음

### Input Validation
- **Text Length**: 텍스트 길이 제한 (ElevenLabs API 제한 고려)
- **Parameter Validation**: stability, similarity_boost 범위 검증 (0.0-1.0)
- **Tempdir Validation**: 경로 트래버설 공격 방지

### Rate Limiting
- **Client-Side**: 사용자가 자신의 API 키로 직접 ElevenLabs와 통신하므로 서버 측 rate limiting 불필요
- **Error Handling**: ElevenLabs rate limit 에러를 적절히 전달

## Performance Considerations

### Audio Processing
- **Streaming**: 큰 오디오 파일의 경우 스트리밍 처리 고려
- **Concurrent Processing**: 여러 세그먼트 동시 처리 가능성
- **Memory Management**: 오디오 데이터의 메모리 사용량 최적화

### File Management
- **Cleanup**: 임시 파일 정리 정책 유지
- **Storage**: 기존 파일 저장 구조 그대로 활용
- **Concurrent Access**: 동시 요청 시 파일 충돌 방지

## Default Configuration

### Korean TTS Optimized Settings
```python
DEFAULT_ELEVENLABS_SETTINGS = {
    "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel (English, but works well for Korean)
    "stability": 0.5,
    "similarity_boost": 0.8,
    "model_id": "eleven_multilingual_v2"  # Supports Korean
}
```

### Voice Selection Priority
1. User-specified voice_id
2. Korean-compatible default voice
3. Fallback to ElevenLabs default voice