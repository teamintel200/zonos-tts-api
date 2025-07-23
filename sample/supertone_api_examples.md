# Supertone TTS API 사용 예시

## 1. 직접 Supertone API 호출

### 기본 요청 구조
```bash
POST https://api.supertone.ai/v1/text-to-speech/{voice_id}?output_format=wav
x-sup-api-key: YOUR_SUPERTONE_API_KEY
Content-Type: application/json

{
  "text": "안녕하세요, 수퍼톤 API입니다.",
  "language": "ko",
  "style": "neutral",
  "model": "sona_speech_1",
  "voice_settings": {
    "pitch_shift": 0,
    "pitch_variance": 1,
    "speed": 1
  }
}
```

### curl 예시
```bash
curl -X POST "https://api.supertone.ai/v1/text-to-speech/91992bbd4758bdcf9c9b01?output_format=wav" \
  -H "x-sup-api-key: YOUR_SUPERTONE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "안녕하세요, 수퍼톤 API 샘플입니다.",
    "language": "ko",
    "style": "neutral",
    "model": "sona_speech_1",
    "voice_settings": {
      "pitch_shift": 0,
      "pitch_variance": 1,
      "speed": 1
    }
  }' \
  --output supertone_sample.wav
```

## 2. 우리 TTS API 서버를 통한 호출

### 환경 설정
```bash
export SUPERTONE_APIKEY=YOUR_SUPERTONE_API_KEY
```

### API 호출
```bash
curl -X POST http://localhost:8000/tts_supertone \
  -H "Content-Type: application/json" \
  -d '{
    "segments": [
      {"id": 1, "text": "안녕하세요, 수퍼톤 API 샘플입니다."}
    ],
    "tempdir": "supertone_sample_test",
    "voice_id": "91992bbd4758bdcf9c9b01",
    "language": "ko",
    "style": "neutral",
    "model": "sona_speech_1",
    "pitch_shift": 0,
    "pitch_variance": 1,
    "speed": 1,
    "output_format": "wav"
  }'
```

### 예상 응답
```json
[
  {
    "sequence": 1,
    "text": "안녕하세요, 수퍼톤 API 샘플입니다.",
    "durationMillis": 2500,
    "path": "outputs/supertone_sample_test/audio/tts/0001.wav"
  }
]
```

## 3. 사용 가능한 음성 목록 조회

```bash
curl -X GET http://localhost:8000/voices/supertone
```

### 응답 예시 (일부)
```json
[
  {
    "voice_id": "91992bbd4758bdcf9c9b01",
    "name": "Adam",
    "gender": "male",
    "age": "young-adult",
    "use_case": "meme",
    "supported_languages": ["ko", "en", "ja"],
    "available_styles": ["neutral"]
  },
  {
    "voice_id": "e5f6fb1a53d0add87afb4f",
    "name": "Agatha",
    "gender": "female",
    "age": "young-adult",
    "use_case": "narration",
    "supported_languages": ["ko", "en", "ja"],
    "available_styles": ["neutral", "happy", "serene"]
  }
]
```

## 4. 음성 샘플 미리보기

```bash
curl -X POST http://localhost:8000/voices/supertone/91992bbd4758bdcf9c9b01/sample \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_API_KEY"}' \
  --output adam_sample.wav
```

## 5. 다양한 감정 표현 예시

### 화난 음성 (Aiden - 7가지 감정 지원)
```bash
curl -X POST http://localhost:8000/tts_supertone \
  -H "Content-Type: application/json" \
  -d '{
    "segments": [{"id": 1, "text": "정말 화가 났습니다!"}],
    "tempdir": "angry_test",
    "voice_id": "2d5a380030e78fcab0c82a",
    "language": "ko",
    "style": "angry",
    "speed": 1.2,
    "pitch_shift": 2
  }'
```

### 행복한 음성 (Agatha - 3가지 감정 지원)
```bash
curl -X POST http://localhost:8000/tts_supertone \
  -H "Content-Type: application/json" \
  -d '{
    "segments": [{"id": 1, "text": "정말 기쁘고 행복합니다!"}],
    "tempdir": "happy_test",
    "voice_id": "e5f6fb1a53d0add87afb4f",
    "language": "ko",
    "style": "happy",
    "speed": 0.9,
    "pitch_variance": 1.5
  }'
```

## 6. 파라미터 설명

### voice_settings
- **pitch_shift**: 피치 조정 (-12 ~ +12, 기본값: 0)
- **pitch_variance**: 억양 변화 (0.1 ~ 2.0, 기본값: 1.0)
- **speed**: 말하기 속도 (0.5 ~ 2.0, 기본값: 1.0)

### 기타 파라미터
- **language**: 언어 (ko/en/ja)
- **style**: 감정 스타일 (음성마다 다름)
- **model**: 모델명 (기본: sona_speech_1)
- **output_format**: 출력 형식 (wav/mp3)

## 7. 오류 코드

- **400**: 잘못된 파라미터 (텍스트 길이, 언어, 스타일 등)
- **401**: 잘못된 API 키
- **404**: 음성 ID 또는 스타일을 찾을 수 없음
- **429**: 요청 제한 초과
- **503**: 서비스 일시 중단