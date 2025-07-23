# Voicevox 음성 파라미터 가이드라인

이 가이드는 Voicevox TTS API에서 다양한 음성 효과를 얻기 위한 파라미터 설정 방법을 설명합니다.

## 사용 가능한 영어 음성 이름

### 기본 화자 (Free Commercial Use)

| Speaker ID | English Name | Japanese Name | Available Styles |
|------------|--------------|---------------|------------------|
| 2 | Shikoku_Metan | 四国めたん | Normal, Sweet, Tsundere, Sexy |
| 3 | Zundamon | ずんだもん | Normal, Sweet, Tsundere, Sexy |
| 8 | Kasukabe_Tsumugi | 春日部つむぎ | Normal |
| 9 | Namine_Ritsu | 波音リツ | Normal |
| 10 | Amehare_Hau | 雨晴はう | Normal |

### 스타일별 특성

- **Normal**: 자연스러운 일반적인 음성
- **Sweet**: 부드럽고 달콤한 음성
- **Tsundere**: 약간 까칠하고 도도한 음성
- **Sexy**: 성숙하고 매력적인 음성

## 음성 파라미터 설정 가이드

### 1. 속도 조절 (speed_scale)

**범위**: 0.5 ~ 2.0 (기본값: 1.0)

```json
{
  "speed_scale": 0.7,  // 느린 속도 (70%)
  "speed_scale": 1.0,  // 보통 속도 (100%)
  "speed_scale": 1.5   // 빠른 속도 (150%)
}
```

**효과별 권장 설정**:
- **매우 느림**: 0.5-0.7 (명상, 학습용)
- **느림**: 0.7-0.9 (뉴스, 설명)
- **보통**: 0.9-1.1 (일반 대화)
- **빠름**: 1.1-1.5 (활기찬 대화)
- **매우 빠름**: 1.5-2.0 (긴급, 흥미진진)

### 2. 음높이 조절 (pitch_scale)

**범위**: -0.15 ~ 0.15 (기본값: 0.0)

```json
{
  "pitch_scale": -0.1,  // 낮은 음성 (저음)
  "pitch_scale": 0.0,   // 기본 음성
  "pitch_scale": 0.1    // 높은 음성 (고음)
}
```

**효과별 권장 설정**:
- **매우 낮음**: -0.15 ~ -0.1 (남성적, 진중함)
- **약간 낮음**: -0.1 ~ -0.05 (차분함)
- **기본**: -0.05 ~ 0.05 (자연스러움)
- **약간 높음**: 0.05 ~ 0.1 (밝음, 활기)
- **매우 높음**: 0.1 ~ 0.15 (귀여움, 어린이)

### 3. 억양 강도 (intonation_scale)

**범위**: 0.0 ~ 2.0 (기본값: 1.0)

```json
{
  "intonation_scale": 0.5,  // 평평한 억양
  "intonation_scale": 1.0,  // 기본 억양
  "intonation_scale": 1.5   // 강한 억양
}
```

**효과별 권장 설정**:
- **평평함**: 0.0-0.5 (로봇적, 단조로움)
- **약한 억양**: 0.5-0.8 (차분함, 뉴스)
- **기본 억양**: 0.8-1.2 (자연스러운 대화)
- **강한 억양**: 1.2-1.6 (감정적, 드라마틱)
- **매우 강함**: 1.6-2.0 (과장된, 연극적)

### 4. 음량 조절 (volume_scale)

**범위**: 0.0 ~ 2.0 (기본값: 1.0)

```json
{
  "volume_scale": 0.5,  // 작은 음량
  "volume_scale": 1.0,  // 기본 음량
  "volume_scale": 1.5   // 큰 음량
}
```

**효과별 권장 설정**:
- **속삭임**: 0.3-0.6
- **조용함**: 0.6-0.8
- **보통**: 0.8-1.2
- **큰 소리**: 1.2-1.6
- **외침**: 1.6-2.0

### 5. 음성 전후 무음 길이

**pre_phoneme_length** (음성 시작 전 무음): 0.0 ~ 1.5초 (기본값: 0.1)
**post_phoneme_length** (음성 종료 후 무음): 0.0 ~ 1.5초 (기본값: 0.1)

```json
{
  "pre_phoneme_length": 0.2,   // 시작 전 0.2초 무음
  "post_phoneme_length": 0.3   // 종료 후 0.3초 무음
}
```

## 상황별 파라미터 조합 예시

### 1. 뉴스 아나운서 스타일
```json
{
  "speaker_id": 2,
  "speed_scale": 0.9,
  "pitch_scale": -0.05,
  "intonation_scale": 0.8,
  "volume_scale": 1.0,
  "pre_phoneme_length": 0.1,
  "post_phoneme_length": 0.2
}
```

### 2. 활기찬 대화 스타일
```json
{
  "speaker_id": 3,
  "speed_scale": 1.3,
  "pitch_scale": 0.08,
  "intonation_scale": 1.4,
  "volume_scale": 1.1,
  "pre_phoneme_length": 0.05,
  "post_phoneme_length": 0.1
}
```

### 3. 차분한 설명 스타일
```json
{
  "speaker_id": 8,
  "speed_scale": 0.8,
  "pitch_scale": -0.03,
  "intonation_scale": 0.9,
  "volume_scale": 0.9,
  "pre_phoneme_length": 0.15,
  "post_phoneme_length": 0.2
}
```

### 4. 귀여운 캐릭터 스타일
```json
{
  "speaker_id": 3,
  "speed_scale": 1.1,
  "pitch_scale": 0.12,
  "intonation_scale": 1.3,
  "volume_scale": 1.0,
  "pre_phoneme_length": 0.1,
  "post_phoneme_length": 0.15
}
```

### 5. 진중한 내레이션 스타일
```json
{
  "speaker_id": 9,
  "speed_scale": 0.7,
  "pitch_scale": -0.1,
  "intonation_scale": 0.7,
  "volume_scale": 1.2,
  "pre_phoneme_length": 0.2,
  "post_phoneme_length": 0.3
}
```

## API 호출 예시

### 기본 호출 (영어 이름 사용)
```bash
curl -X POST "http://localhost:8000/tts_voicevox" \
     -H "Content-Type: application/json" \
     -d '{
       "segments": [
         {
           "id": 1,
           "text": "こんにちは！今日はいい天気ですね。"
         }
       ],
       "tempdir": "my_voice_test",
       "speaker_id": 2
     }'
```

### 빠른 속도 + 높은 음성
```bash
curl -X POST "http://localhost:8000/tts_voicevox" \
     -H "Content-Type: application/json" \
     -d '{
       "segments": [
         {
           "id": 1,
           "text": "急いで話しています！"
         }
       ],
       "tempdir": "fast_high_voice",
       "speaker_id": 3,
       "speed_scale": 1.5,
       "pitch_scale": 0.1,
       "intonation_scale": 1.3
     }'
```

### 느린 속도 + 낮은 음성
```bash
curl -X POST "http://localhost:8000/tts_voicevox" \
     -H "Content-Type: application/json" \
     -d '{
       "segments": [
         {
           "id": 1,
           "text": "ゆっくりと話しています。"
         }
       ],
       "tempdir": "slow_low_voice",
       "speaker_id": 2,
       "speed_scale": 0.7,
       "pitch_scale": -0.08,
       "intonation_scale": 0.8
     }'
```

## 파일 저장 위치

생성된 음성 파일은 다음 경로에 저장됩니다:

```
outputs/
├── {tempdir}/
│   └── audio/
│       └── tts/
│           ├── 0001.wav
│           ├── 0002.wav
│           └── ...
└── combined_{tempdir}.wav  (combine_wav 사용 시)
```

예시:
- `outputs/my_voice_test/audio/tts/0001.wav`
- `outputs/fast_high_voice/audio/tts/0001.wav`
- `outputs/combined_my_voice_test.wav`

## 음성 미리듣기

각 화자의 음성을 미리 들어보려면:

```bash
# Shikoku_Metan (ID: 2) 미리듣기
curl -X GET "http://localhost:8000/voices/voicevox/2/sample" \
     -o "preview_shikoku_metan.wav"

# Zundamon (ID: 3) 미리듣기
curl -X GET "http://localhost:8000/voices/voicevox/3/sample" \
     -o "preview_zundamon.wav"
```

## 팁과 권장사항

### 1. 자연스러운 음성을 위한 팁
- 극단적인 파라미터 값은 피하세요
- 여러 파라미터를 동시에 크게 변경하지 마세요
- 텍스트 길이에 따라 파라미터를 조정하세요

### 2. 성능 최적화
- 긴 텍스트는 여러 세그먼트로 나누세요
- 동일한 설정을 반복 사용할 때는 tempdir을 재사용하세요
- 불필요한 무음 길이는 줄이세요

### 3. 감정 표현
- 기쁨: speed_scale ↑, pitch_scale ↑, intonation_scale ↑
- 슬픔: speed_scale ↓, pitch_scale ↓, intonation_scale ↓
- 화남: speed_scale ↑, intonation_scale ↑, volume_scale ↑
- 차분함: speed_scale ↓, intonation_scale ↓

### 4. 용도별 추천 화자
- **뉴스/공지**: Shikoku_Metan (ID: 2) - Normal
- **친근한 대화**: Zundamon (ID: 3) - Sweet
- **전문적 설명**: Kasukabe_Tsumugi (ID: 8) - Normal
- **내레이션**: Namine_Ritsu (ID: 9) - Normal
- **밝은 안내**: Amehare_Hau (ID: 10) - Normal

이 가이드를 참고하여 원하는 음성 효과를 얻으시기 바랍니다!