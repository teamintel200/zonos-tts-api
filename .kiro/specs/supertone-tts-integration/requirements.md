# 요구사항 문서

## 개요

이 기능은 기존 TTS 서비스에 Supertone TTS API를 통합하여 고품질의 한국어, 영어, 일본어 텍스트 음성 변환 기능을 다양한 음성 스타일과 감정 표현과 함께 제공합니다. Supertone은 다양한 감정 스타일과 음성 특성을 포함한 광범위한 커스터마이징 옵션을 통해 프리미엄 음성 품질을 제공합니다.

## 요구사항

### 요구사항 1

**사용자 스토리:** 개발자로서, 기존 TTS 서비스에 Supertone TTS API를 통합하여 감정 표현이 가능한 고품질 다국어 텍스트 음성 변환을 제공하고 싶습니다.

#### 수락 기준

1. WHEN 시스템이 Supertone TTS 요청을 받으면 THEN 텍스트 음성 변환 생성을 위해 Supertone API 엔드포인트를 사용해야 합니다
2. WHEN 시스템이 Supertone 요청을 처리하면 THEN 한국어, 영어, 일본어를 지원해야 합니다
3. WHEN 시스템이 Supertone API 호출을 하면 THEN API 키를 사용한 인증을 처리해야 합니다
4. WHEN Supertone API가 오디오 데이터를 반환하면 THEN 시스템은 적절한 오디오 형식으로 반환해야 합니다

### 요구사항 2

**사용자 스토리:** 개발자로서, Supertone API 키를 제공하고 음성 옵션을 지정하여 내 계정을 사용하고 음성 특성을 커스터마이징하고 싶습니다.

#### 수락 기준

1. WHEN Supertone TTS 요청이 만들어지면 THEN 시스템은 유효한 API 키를 요구해야 합니다
2. WHEN 잘못된 API 키가 제공되면 THEN 시스템은 401 인증 오류를 반환해야 합니다
3. WHEN API 키가 누락되면 THEN 시스템은 400 잘못된 요청 오류를 반환해야 합니다
4. WHEN API 키 검증이 실패하면 THEN 시스템은 명확한 오류 메시지를 제공해야 합니다

### 요구사항 3

**사용자 스토리:** 개발자로서, 사용 사례에 가장 적합한 음성을 선택할 수 있도록 특성과 함께 사용 가능한 Supertone 음성을 선택하고 싶습니다.

#### 수락 기준

1. WHEN 사용 가능한 음성을 요청하면 THEN 시스템은 voice_id, name, age, gender, use_case 정보와 함께 음성을 반환해야 합니다
2. WHEN 사용 가능한 음성을 요청하면 THEN 시스템은 각 음성에 대해 지원되는 언어(ko, en, ja)를 포함해야 합니다
3. WHEN 사용 가능한 음성을 요청하면 THEN 시스템은 각 음성에 대해 사용 가능한 스타일을 포함해야 합니다
4. WHEN 음성이 여러 스타일을 지원하면 THEN 시스템은 모든 사용 가능한 감정 스타일(neutral, happy, sad, angry 등)을 나열해야 합니다

### 요구사항 4

**사용자 스토리:** 개발자로서, 적절한 톤과 감정으로 음성을 생성할 수 있도록 음성 스타일과 감정 표현을 지정하고 싶습니다.

#### 수락 기준

1. WHEN TTS 요청을 하면 THEN 시스템은 감정 표현을 위한 style 파라미터를 받아야 합니다
2. WHEN 스타일이 지정되면 THEN 시스템은 선택된 음성의 사용 가능한 스타일에 대해 검증해야 합니다
3. WHEN 잘못된 스타일이 제공되면 THEN 시스템은 사용 가능한 스타일과 함께 400 오류를 반환해야 합니다
4. WHEN 스타일이 지정되지 않으면 THEN 시스템은 "neutral" 스타일을 기본값으로 사용해야 합니다

### 요구사항 5

**사용자 스토리:** 개발자로서, 음성 품질과 특성을 제어할 수 있도록 Supertone 음성 파라미터를 커스터마이징하고 싶습니다.

#### 수락 기준

1. WHEN TTS 요청을 하면 THEN 시스템은 음성 속도 제어를 위한 speed 파라미터를 지원해야 합니다
2. WHEN TTS 요청을 하면 THEN 시스템은 음성 피치 조정을 위한 pitch 파라미터를 지원해야 합니다
3. WHEN TTS 요청을 하면 THEN 시스템은 오디오 볼륨 제어를 위한 volume 파라미터를 지원해야 합니다
4. WHEN 잘못된 파라미터가 제공되면 THEN 시스템은 허용 가능한 범위와 함께 검증 오류를 반환해야 합니다

### 요구사항 6

**사용자 스토리:** 개발자로서, 사용자에게 의미 있는 피드백을 제공할 수 있도록 Supertone API 오류를 우아하게 처리하고 싶습니다.

#### 수락 기준

1. WHEN Supertone API가 오류를 반환하면 THEN 시스템은 적절한 HTTP 상태 코드로 매핑해야 합니다
2. WHEN 속도 제한이 초과되면 THEN 시스템은 재시도 정보와 함께 429 오류를 반환해야 합니다
3. WHEN 서비스를 사용할 수 없으면 THEN 시스템은 503 오류를 반환해야 합니다
4. WHEN 음성이나 스타일을 찾을 수 없으면 THEN 시스템은 사용 가능한 옵션과 함께 404 오류를 반환해야 합니다

### 요구사항 7

**사용자 스토리:** 개발자로서, 전체 콘텐츠를 생성하기 전에 다양한 음성과 스타일을 테스트할 수 있도록 음성 샘플을 미리 들어보고 싶습니다.

#### 수락 기준

1. WHEN 음성 미리보기를 요청하면 THEN 시스템은 지정된 음성과 스타일을 사용하여 짧은 샘플을 생성해야 합니다
2. WHEN 음성 미리보기를 요청하면 THEN 시스템은 언어에 적합한 샘플 텍스트를 사용해야 합니다
3. WHEN 음성 미리보기를 요청하면 THEN 시스템은 일반 TTS와 동일한 형식으로 오디오 데이터를 반환해야 합니다
4. WHEN 미리보기 생성이 실패하면 THEN 시스템은 적절한 오류 메시지를 반환해야 합니다

### 요구사항 8

**사용자 스토리:** 개발자로서, 기존 시스템 내에서 일관되게 사용할 수 있도록 Supertone 통합이 다른 TTS 제공업체와 동일한 인터페이스를 따르기를 원합니다.

#### 수락 기준

1. WHEN Supertone을 통합하면 THEN 다른 TTS 제공업체와 동일한 서비스 인터페이스를 구현해야 합니다
2. WHEN TTS 요청을 하면 THEN 시스템은 모든 제공업체에서 동일한 응답 형식을 지원해야 합니다
3. WHEN 오류를 처리하면 THEN 시스템은 일관된 오류 처리 패턴을 사용해야 합니다
4. WHEN 오디오 데이터를 반환하면 THEN 시스템은 일관된 오디오 형식 표준을 유지해야 합니다

## 구현 상태

### ✅ 완료된 구현

#### 1. API 엔드포인트
- **POST `/tts_supertone`**: Supertone TTS 텍스트 음성 변환
- **GET `/voices/supertone`**: 사용 가능한 Supertone 음성 목록 조회
- **POST `/voices/supertone/{voice_id}/sample`**: 음성 샘플 미리보기

#### 2. 데이터 스키마
- **SupertoneTTSRequest**: TTS 요청 스키마 (최대 300자 제한)
- **SupertoneVoice**: 음성 정보 스키마 (특성, 언어, 스타일 포함)

#### 3. 지원 기능
- **언어**: 한국어(ko), 영어(en), 일본어(ja)
- **감정 스타일**: neutral, happy, sad, angry 등
- **음성 파라미터**: 
  - pitch_shift (-12 ~ +12)
  - pitch_variance (0.1 ~ 2.0)  
  - speed (0.5 ~ 2.0)
- **출력 형식**: WAV, MP3

#### 4. 인증 및 오류 처리
- API 키 검증 (요청 또는 환경변수 SUPERTONE_APIKEY)
- 적절한 HTTP 상태 코드 (401, 404, 429, 503 등)
- 상세한 오류 메시지와 로깅

#### 5. 기존 시스템과의 통합
- 다른 TTS 제공업체와 동일한 응답 형식
- 동일한 combine_wav 엔드포인트 호환성
- 일관된 파일 저장 및 관리 패턴

### 🔧 기술적 세부사항

#### 구현 파일
- `supertone_service.py`: Supertone API 서비스 계층
- `schemas.py`: Pydantic 데이터 모델 (SupertoneTTSRequest, SupertoneVoice)  
- `tts_api.py`: FastAPI 엔드포인트 추가

#### 환경 변수
```bash
SUPERTONE_APIKEY=your_supertone_api_key_here
```

#### 사용 예시
```json
POST /tts_supertone
{
  "segments": [{"id": 1, "text": "안녕하세요, 수퍼톤입니다."}],
  "tempdir": "temp_001",
  "voice_id": "sona_korean_female",
  "language": "ko",
  "style": "happy",
  "speed": 1.2,
  "pitch_shift": 2.0
}
```

### 📋 요구사항 충족 확인

- [x] **요구사항 1**: Supertone API 엔드포인트 사용, 다국어 지원, API 키 인증, 적절한 오디오 형식 반환
- [x] **요구사항 2**: API 키 검증, 401/400 오류 처리, 명확한 오류 메시지
- [x] **요구사항 3**: 음성 특성 정보 제공 (voice_id, name, age, gender, use_case, 지원 언어, 스타일)
- [x] **요구사항 4**: 스타일 파라미터 지원, 검증, 기본값 neutral, 400 오류 처리
- [x] **요구사항 5**: speed, pitch_shift, pitch_variance 파라미터 지원, 범위 검증
- [x] **요구사항 6**: HTTP 상태 코드 매핑, 429/503/404 오류 처리
- [x] **요구사항 7**: 음성 미리보기 기능, 언어별 샘플 텍스트, 동일한 오디오 형식
- [x] **요구사항 8**: 기존 TTS 제공업체와 동일한 인터페이스, 응답 형식, 오류 처리 패턴