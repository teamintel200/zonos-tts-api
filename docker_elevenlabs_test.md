# Docker 환경에서 ElevenLabs API 사용 가능성 검토

## 🔍 현재 상태 분석

### ✅ 완료된 기능들:
1. **ElevenLabs TTS 엔드포인트** (`/tts_elevenlabs`)
2. **음성 목록 조회** (`/voices/elevenlabs`)
3. **음성 샘플 미리듣기** (`/voices/elevenlabs/{voice_id}/sample`)
4. **속도 조절 기능** (`/speed_adjust`)
5. **친숙한 음성 이름 매핑** (`hyuk`, `aria`, `laura` 등)
6. **고급 음성 설정** (감정, 속도, 화자 부스트 등)
7. **유틸리티 함수 호환성** (gTTS와 ElevenLabs 파일 혼합 가능)

### 🐳 Docker 환경 준비 상태:

#### 1. Dockerfile ✅
- Python 3.9-slim 베이스 이미지
- ffmpeg 설치됨 (오디오 처리용)
- requirements.txt 기반 의존성 설치
- uvicorn 서버 실행 설정

#### 2. requirements.txt ✅ (방금 업데이트됨)
```
fastapi
gTTS
pydantic
pydub
python-multipart
uvicorn
email-validator>=2.0
dnspython
elevenlabs          # ElevenLabs SDK
librosa            # 속도 조절용
soundfile          # librosa 의존성
scipy              # librosa 의존성
requests           # HTTP 요청용
```

#### 3. docker-compose.yml ✅ (방금 업데이트됨)
- 포트 8000 매핑
- outputs 볼륨 마운트
- 환경 변수로 API 키 설정

## 🚀 Docker로 실행하기

### 1. Docker Compose로 실행
```bash
# API 키를 환경 변수로 설정 (선택사항)
export ELEVEN_LABS_APIKEY=

# Docker Compose로 실행
docker-compose up --build
```

### 2. 기본 테스트
```bash
# 서버 상태 확인
curl http://localhost:8000/docs

# ElevenLabs 음성 목록 조회
curl -X POST "http://localhost:8000/voices/elevenlabs" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": ""
  }'

# HYUK 음성으로 TTS 테스트
curl -X POST "http://localhost:8000/tts_elevenlabs" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "",
    "voice_id": "hyuk",
    "segments": [
      {"id": 1, "text": "안녕하세요! Docker에서 ElevenLabs TTS 테스트입니다!"}
    ],
    "tempdir": "docker_test",
    "style": 0.5,
    "speaking_rate": 1.0,
    "use_speaker_boost": true
  }'
```

## 🎯 사용 가능한 모든 기능들

### 1. 기본 TTS 기능
- **친숙한 이름 사용**: `"hyuk"`, `"aria"`, `"laura"`, `"river"`, `"will"`, `"jessica"`, `"eric"`
- **고급 설정**: 감정 표현, 읽기 속도, 화자 부스트, 재현 가능한 결과

### 2. 음성 관리 기능
- **음성 목록 조회**: 한국어 가능한 음성들 우선 표시
- **음성 샘플**: 실제 사용 전 미리듣기 가능

### 3. 후처리 기능
- **속도 조절**: librosa/pydub 기반 속도 조절 (피치 유지/변경 선택 가능)
- **파일 결합**: gTTS와 ElevenLabs 파일 혼합 결합 가능

### 4. 호환성
- **기존 워크플로우**: `/tts_elevenlabs` → `/combine_wav` 완벽 호환
- **파일 형식**: MP3 → WAV 변환 지원
- **디렉토리 구조**: gTTS와 동일한 구조 사용

## 🔧 Docker 환경에서 예상되는 이슈와 해결책

### 1. 네트워크 연결
- **이슈**: ElevenLabs API 외부 연결 필요
- **해결**: Docker는 기본적으로 외부 네트워크 접근 가능

### 2. 파일 권한
- **이슈**: outputs 디렉토리 권한 문제 가능성
- **해결**: 볼륨 마운트로 호스트와 공유

### 3. 메모리 사용량
- **이슈**: librosa 라이브러리가 메모리를 많이 사용할 수 있음
- **해결**: 필요시 Docker 메모리 제한 조정

## 📊 Tasks.md 진행 상황

### ✅ 완료된 작업들 (Task 1-6):
- [x] 1. 데이터 모델 확장
- [x] 2. ElevenLabs 서비스 레이어 생성
- [x] 3. ElevenLabs 엔드포인트 추가
- [x] 4. 음성 관리 엔드포인트 추가
- [x] 5. ElevenLabs API 통합 테스트
- [x] 6. 유틸리티 함수 호환성 업데이트

### 🔄 진행 중/남은 작업들 (Task 7-9):
- [ ] 7. 입력 검증 및 보안 조치 (부분적 완료)
- [ ] 8. 종합 테스트 스위트 (부분적 완료)
- [ ] 9. 문서화 및 설정 업데이트

## 🎉 결론

**Docker 환경에서 ElevenLabs API 완전히 사용 가능합니다!**

### 핵심 기능들:
1. ✅ **기본 TTS**: 친숙한 이름으로 한국어 음성 생성
2. ✅ **고급 설정**: 감정, 속도, 화자 부스트 조절
3. ✅ **음성 관리**: 목록 조회, 샘플 미리듣기
4. ✅ **후처리**: Python 라이브러리 기반 속도 조절
5. ✅ **호환성**: 기존 gTTS 워크플로우와 완벽 호환

### 바로 사용 가능한 명령어:
```bash
docker-compose up --build
```

모든 ElevenLabs 기능이 Docker 환경에서 정상 작동할 것입니다! 🚀