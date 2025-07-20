# ElevenLabs TTS API 테스트 가이드

## 1. 서버 시작하기

### 1-1. 터미널에서 API 서버 실행
```bash
uvicorn tts_api:app --reload --host 0.0.0.0 --port 8000
```

서버가 성공적으로 시작되면 다음과 같은 메시지가 표시됩니다:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
```

### 1-2. 서버 상태 확인
브라우저에서 `http://localhost:8000/docs`로 접속하여 FastAPI 문서 페이지가 열리는지 확인하세요.

## 2. ElevenLabs TTS 테스트

### 2-1. 기본 TTS 테스트 (curl 사용)

새 터미널을 열고 다음 명령어를 실행하세요:

```bash
curl -X POST "http://localhost:8000/tts_elevenlabs" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "sk_c25429e2769e86f0e814a5bc533c163b6cba923acdbcc528",
    "segments": [
      {
        "id": 1,
        "text": "안녕하세요. ElevenLabs TTS 테스트입니다."
      },
      {
        "id": 2,
        "text": "이것은 한국어 음성 합성 테스트입니다."
      }
    ],
    "tempdir": "my_test_session"
  }'
```

### 2-2. 음성 설정을 포함한 테스트

```bash
curl -X POST "http://localhost:8000/tts_elevenlabs" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "sk_c25429e2769e86f0e814a5bc533c163b6cba923acdbcc528",
    "segments": [
      {
        "id": 1,
        "text": "안녕하세요. 음성 설정을 조정한 테스트입니다."
      }
    ],
    "tempdir": "voice_settings_test",
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "stability": 0.7,
    "similarity_boost": 0.9
  }'
```

### 2-3. 성공적인 응답 예시

테스트가 성공하면 다음과 같은 JSON 응답을 받게 됩니다:

```json
[
  {
    "sequence": 1,
    "text": "안녕하세요. ElevenLabs TTS 테스트입니다.",
    "durationMillis": 3500,
    "path": "outputs/my_test_session/audio/tts/0001.mp3"
  },
  {
    "sequence": 2,
    "text": "이것은 한국어 음성 합성 테스트입니다.",
    "durationMillis": 4200,
    "path": "outputs/my_test_session/audio/tts/0002.mp3"
  }
]
```

## 3. 생성된 음성 파일 확인

### 3-1. 파일 위치 확인
```bash
ls -la outputs/my_test_session/audio/tts/
```

다음과 같은 파일들이 생성되어야 합니다:
- `0001.mp3`
- `0002.mp3`

### 3-2. 음성 파일 재생 (macOS)
```bash
# 첫 번째 파일 재생
afplay outputs/my_test_session/audio/tts/0001.mp3

# 두 번째 파일 재생
afplay outputs/my_test_session/audio/tts/0002.mp3
```

## 4. 음성 파일 합치기 테스트

### 4-1. combine_wav 엔드포인트 테스트
```bash
curl -X POST "http://localhost:8000/combine_wav" \
  -H "Content-Type: application/json" \
  -d '{
    "tempdir": "my_test_session"
  }'
```

### 4-2. 합쳐진 파일 확인 및 재생
```bash
# 합쳐진 파일 확인
ls -la outputs/combined_my_test_session.wav

# 합쳐진 파일 재생
afplay outputs/combined_my_test_session.wav
```

## 5. 사용 가능한 음성 목록 확인

### 5-1. ElevenLabs 음성 목록 가져오기
```bash
curl -X POST "http://localhost:8000/voices/elevenlabs" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "sk_c25429e2769e86f0e814a5bc533c163b6cba923acdbcc528"
  }'
```

### 5-2. 특정 음성 샘플 듣기
```bash
# Rachel 음성 샘플 다운로드
curl -X POST "http://localhost:8000/voices/elevenlabs/21m00Tcm4TlvDq8ikWAM/sample" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "sk_c25429e2769e86f0e814a5bc533c163b6cba923acdbcc528"
  }' \
  --output rachel_sample.mp3

# 샘플 재생
afplay rachel_sample.mp3
```

## 6. 자동화된 테스트 실행

### 6-1. 기존 테스트 스크립트 실행
```bash
# 유틸리티 함수 호환성 테스트
python test_utils_compatibility.py

# ElevenLabs 호환성 테스트
python test_elevenlabs_compatibility.py

# 최종 통합 테스트
python final_test.py
```

### 6-2. 엔드포인트 구조 테스트
```bash
python test_endpoints_structure.py
```

## 7. 문제 해결

### 7-1. 일반적인 오류들

**401 Unauthorized 오류**
- API 키가 올바른지 확인하세요
- API 키에 충분한 크레딧이 있는지 확인하세요

**429 Rate Limit 오류**
- 요청을 너무 빠르게 보내고 있습니다. 잠시 기다린 후 다시 시도하세요

**500 Internal Server Error**
- 서버 로그를 확인하여 구체적인 오류 메시지를 확인하세요
- 텍스트가 너무 길지 않은지 확인하세요 (5000자 제한)

### 7-2. 로그 확인
서버를 실행한 터미널에서 실시간 로그를 확인할 수 있습니다. 오류가 발생하면 자세한 정보가 표시됩니다.

### 7-3. 파일 정리
테스트 후 생성된 파일들을 정리하려면:
```bash
# 특정 세션 디렉토리 삭제
rm -rf outputs/my_test_session/

# 합쳐진 파일 삭제
rm outputs/combined_my_test_session.wav

# 모든 출력 파일 삭제 (주의!)
rm -rf outputs/
```

## 8. 고급 테스트

### 8-1. 혼합 엔진 테스트 (gTTS + ElevenLabs)

먼저 gTTS로 파일 생성:
```bash
curl -X POST "http://localhost:8000/tts_simple" \
  -H "Content-Type: application/json" \
  -d '{
    "segments": [
      {
        "id": 1,
        "text": "이것은 gTTS로 생성된 음성입니다."
      }
    ],
    "tempdir": "mixed_test_session"
  }'
```

그 다음 ElevenLabs로 추가 파일 생성:
```bash
curl -X POST "http://localhost:8000/tts_elevenlabs" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "sk_c25429e2769e86f0e814a5bc533c163b6cba923acdbcc528",
    "segments": [
      {
        "id": 2,
        "text": "이것은 ElevenLabs로 생성된 음성입니다."
      }
    ],
    "tempdir": "mixed_test_session"
  }'
```

마지막으로 두 엔진의 파일을 합치기:
```bash
curl -X POST "http://localhost:8000/combine_wav" \
  -H "Content-Type: application/json" \
  -d '{
    "tempdir": "mixed_test_session"
  }'
```

## 9. 성능 모니터링

### 9-1. 응답 시간 측정
```bash
time curl -X POST "http://localhost:8000/tts_elevenlabs" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "sk_c25429e2769e86f0e814a5bc533c163b6cba923acdbcc528",
    "segments": [{"id": 1, "text": "성능 테스트"}],
    "tempdir": "performance_test"
  }'
```

### 9-2. 동시 요청 테스트
여러 터미널에서 동시에 요청을 보내어 서버의 동시 처리 능력을 테스트할 수 있습니다.

---

이 가이드를 따라하면 ElevenLabs TTS API의 모든 기능을 체계적으로 테스트할 수 있습니다. 문제가 발생하면 서버 로그를 확인하고 API 키와 네트워크 연결을 점검해보세요.