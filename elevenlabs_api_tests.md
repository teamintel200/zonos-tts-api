# ElevenLabs API 새로운 파라미터 테스트 가이드

## 새로 추가된 파라미터들

### 1. `style` (감정/스타일 조절)
- **범위**: 0.0 - 1.0
- **기본값**: 0.0 (중성적)
- **설명**: 음성의 감정적 표현력을 조절
  - `0.0`: 중성적, 감정 없는 톤
  - `0.5`: 균형잡힌 표현력
  - `1.0`: 매우 표현적이고 감정적

### 2. `use_speaker_boost` (화자 부스트)
- **타입**: Boolean (true/false)
- **기본값**: true
- **설명**: 화자의 특성을 강화하여 더 명확하고 개성있는 목소리 생성

## 테스트 예제들

### 1. 중성적인 톤 (뉴스 읽기 스타일)
```bash
curl -X POST "http://localhost:8000/tts_elevenlabs" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "sk_c25429e2769e86f0e814a5bc533c163b6cba923acdbcc528",
    "voice_id": "hyuk",
    "segments": [
      {
        "id": 1,
        "text": "오늘 날씨는 맑고 기온은 25도입니다. 미세먼지 농도는 보통 수준을 유지하고 있습니다."
      }
    ],
    "tempdir": "neutral_news",
    "stability": 0.8,
    "similarity_boost": 0.9,
    "style": 0.0,
    "use_speaker_boost": true
  }'
```

### 2. 감정적인 톤 (스토리텔링 스타일)
```bash
curl -X POST "http://localhost:8000/tts_elevenlabs" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "sk_c25429e2769e86f0e814a5bc533c163b6cba923acdbcc528",
    "voice_id": "hyuk",
    "segments": [
      {
        "id": 1,
        "text": "옛날 옛적에 아름다운 공주가 살았습니다. 그녀는 매일 성 위에서 먼 바다를 바라보며 꿈을 꾸었어요."
      }
    ],
    "tempdir": "emotional_story",
    "stability": 0.5,
    "similarity_boost": 0.8,
    "style": 0.8,
    "use_speaker_boost": true
  }'
```

### 3. 여성 목소리로 활기찬 톤 (광고/마케팅 스타일)
```bash
curl -X POST "http://localhost:8000/tts_elevenlabs" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "sk_c25429e2769e86f0e814a5bc533c163b6cba923acdbcc528",
    "voice_id": "laura",
    "segments": [
      {
        "id": 1,
        "text": "지금 바로 주문하세요! 특별 할인가로 만나보실 수 있는 절호의 기회입니다!"
      }
    ],
    "tempdir": "energetic_ad",
    "stability": 0.4,
    "similarity_boost": 0.9,
    "style": 0.7,
    "use_speaker_boost": true
  }'
```

### 4. 차분한 여성 목소리 (교육/강의 스타일)
```bash
curl -X POST "http://localhost:8000/tts_elevenlabs" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "sk_c25429e2769e86f0e814a5bc533c163b6cba923acdbcc528",
    "voice_id": "aria",
    "segments": [
      {
        "id": 1,
        "text": "오늘 우리가 배울 내용은 인공지능의 기본 개념입니다. 차근차근 설명해드리겠습니다."
      }
    ],
    "tempdir": "calm_education",
    "stability": 0.7,
    "similarity_boost": 0.8,
    "style": 0.2,
    "use_speaker_boost": true
  }'
```

### 5. 화자 부스트 비교 테스트
```bash
# 화자 부스트 ON
curl -X POST "http://localhost:8000/tts_elevenlabs" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "sk_c25429e2769e86f0e814a5bc533c163b6cba923acdbcc528",
    "voice_id": "eric",
    "segments": [
      {
        "id": 1,
        "text": "안녕하세요. 화자 부스트가 켜진 상태의 목소리입니다."
      }
    ],
    "tempdir": "boost_on",
    "use_speaker_boost": true
  }'

# 화자 부스트 OFF
curl -X POST "http://localhost:8000/tts_elevenlabs" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "sk_c25429e2769e86f0e814a5bc533c163b6cba923acdbcc528",
    "voice_id": "eric",
    "segments": [
      {
        "id": 1,
        "text": "안녕하세요. 화자 부스트가 꺼진 상태의 목소리입니다."
      }
    ],
    "tempdir": "boost_off",
    "use_speaker_boost": false
  }'
```

## 파라미터 조합 가이드

### 📰 뉴스/정보 전달용
- **stability**: 0.8-0.9 (안정적)
- **similarity_boost**: 0.8-0.9 (일관성)
- **style**: 0.0-0.2 (중성적)
- **use_speaker_boost**: true

### 📚 교육/강의용
- **stability**: 0.6-0.8 (적당히 안정적)
- **similarity_boost**: 0.7-0.9 (일관성)
- **style**: 0.1-0.3 (약간의 표현력)
- **use_speaker_boost**: true

### 🎭 스토리텔링/내레이션용
- **stability**: 0.4-0.6 (표현력 허용)
- **similarity_boost**: 0.6-0.8 (다양성 허용)
- **style**: 0.5-0.8 (감정적)
- **use_speaker_boost**: true

### 📢 광고/마케팅용
- **stability**: 0.3-0.5 (역동적)
- **similarity_boost**: 0.8-1.0 (개성 강화)
- **style**: 0.6-0.9 (매우 표현적)
- **use_speaker_boost**: true

### 🤖 AI 어시스턴트용
- **stability**: 0.7-0.9 (안정적)
- **similarity_boost**: 0.7-0.8 (일관성)
- **style**: 0.0-0.3 (중성적)
- **use_speaker_boost**: true

## 음성별 추천 설정

### HYUK (한국어 전용 남성)
```json
{
  "voice_id": "hyuk",
  "stability": 0.6,
  "similarity_boost": 0.8,
  "style": 0.4,
  "use_speaker_boost": true
}
```

### Aria (차분한 여성)
```json
{
  "voice_id": "aria",
  "stability": 0.7,
  "similarity_boost": 0.8,
  "style": 0.2,
  "use_speaker_boost": true
}
```

### Laura (활기찬 젊은 여성)
```json
{
  "voice_id": "laura",
  "stability": 0.4,
  "similarity_boost": 0.9,
  "style": 0.7,
  "use_speaker_boost": true
}
```

### Eric (전문적인 남성)
```json
{
  "voice_id": "eric",
  "stability": 0.8,
  "similarity_boost": 0.8,
  "style": 0.3,
  "use_speaker_boost": true
}
```

## 일괄 테스트 스크립트

```bash
#!/bin/bash

# 다양한 스타일로 같은 텍스트 테스트
TEXT="안녕하세요. 이것은 다양한 감정 표현 테스트입니다."

# 중성적 (뉴스 스타일)
curl -X POST "http://localhost:8000/tts_elevenlabs" \
  -H "Content-Type: application/json" \
  -d "{
    \"api_key\": \"sk_c25429e2769e86f0e814a5bc533c163b6cba923acdbcc528\",
    \"voice_id\": \"hyuk\",
    \"segments\": [{\"id\": 1, \"text\": \"$TEXT\"}],
    \"tempdir\": \"neutral_test\",
    \"style\": 0.0
  }"

# 감정적 (스토리 스타일)  
curl -X POST "http://localhost:8000/tts_elevenlabs" \
  -H "Content-Type: application/json" \
  -d "{
    \"api_key\": \"sk_c25429e2769e86f0e814a5bc533c163b6cba923acdbcc528\",
    \"voice_id\": \"hyuk\",
    \"segments\": [{\"id\": 1, \"text\": \"$TEXT\"}],
    \"tempdir\": \"emotional_test\",
    \"style\": 0.8
  }"

echo "테스트 완료! 생성된 파일들을 비교해보세요:"
echo "- outputs/neutral_test/audio/tts/0001.mp3"
echo "- outputs/emotional_test/audio/tts/0001.mp3"
```

## 파일 재생 및 비교

```bash
# macOS에서 파일 재생
afplay outputs/neutral_test/audio/tts/0001.mp3
sleep 2
afplay outputs/emotional_test/audio/tts/0001.mp3

# 파일 정보 확인
ls -la outputs/*/audio/tts/*.mp3
```

---

이제 감정 표현과 화자 특성을 세밀하게 조절할 수 있습니다! 🎭🎤