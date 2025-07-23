# Supertone Voice Sample API - Swagger UI 사용 가이드

## 🎯 **API 엔드포인트**
`POST /voices/supertone/{voice_id}/sample`

## 📝 **Swagger UI에서 테스트하는 방법**

### 1. **Path Parameter 설정**
```
voice_id: 91992bbd4758bdcf9c9b01
```

### 2. **Request Body 예시들**

#### ✅ **기본 사용법 (한국어, neutral)**
```json
{
  "api_key": "your_supertone_api_key_here",
  "language": "ko",
  "style": "neutral"
}
```

#### 🎭 **감정 표현 (Agatha - happy)**  
```json
{
  "api_key": "your_supertone_api_key_here",
  "language": "ko",
  "style": "happy"
}
```
*voice_id: `e5f6fb1a53d0add87afb4f`*

#### 😠 **화난 감정 (Aiden - angry)**
```json
{
  "api_key": "your_supertone_api_key_here", 
  "language": "ko",
  "style": "angry"
}
```
*voice_id: `2d5a380030e78fcab0c82a`*

#### 🌍 **영어 샘플**
```json
{
  "api_key": "your_supertone_api_key_here",
  "language": "en", 
  "style": "neutral"
}
```

#### 🇯🇵 **일본어 샘플**
```json
{
  "api_key": "your_supertone_api_key_here",
  "language": "ja",
  "style": "neutral"
}
```

#### ✏️ **커스텀 텍스트**
```json
{
  "api_key": "your_supertone_api_key_here",
  "language": "ko",
  "style": "neutral",
  "sample_text": "이것은 내가 직접 입력한 테스트 문장입니다."
}
```

#### 🔐 **환경변수 API 키 사용**
```json
{
  "language": "ko",
  "style": "neutral"
}
```
*SUPERTONE_APIKEY 환경변수가 설정되어 있을 때*

## 🎤 **사용 가능한 음성 ID**

| Voice ID | 이름 | 성별 | 용도 | 지원 스타일 |
|----------|------|------|------|-------------|
| `91992bbd4758bdcf9c9b01` | Adam | 남성 | meme | neutral |
| `e5f6fb1a53d0add87afb4f` | Agatha | 여성 | narration | neutral, happy, serene |
| `2d5a380030e78fcab0c82a` | Aiden | 남성 | game | neutral, angry, curious, happy, sad, suspicious, triumphant |
| `ac449f240c2732b7f0b8bb` | Aiko | 여성 | meme | neutral |
| `b6c59d12355a00040d70a1` | Akari | 여성 | game | neutral |

## 🔧 **파라미터 상세**

### **Path Parameters**
- `voice_id` (required): Supertone 음성 ID

### **Request Body Parameters**
- `api_key` (optional): API 키 (환경변수 사용 가능)
- `language` (optional, default: "ko"): 언어 코드 (ko/en/ja)
- `style` (optional, default: "neutral"): 음성 스타일
- `sample_text` (optional): 커스텀 텍스트

## 📥 **응답 형식**
- Content-Type: `audio/wav`
- 파일명: `supertone_sample_{voice_id}.wav`

## ⚠️ **오류 코드**
- `400`: 잘못된 파라미터
- `401`: 잘못된 API 키  
- `404`: 존재하지 않는 음성 ID
- `429`: 요청 제한 초과
- `503`: 서비스 일시 중단

## 🚀 **테스트 순서**

1. **음성 목록 확인**: `GET /voices/supertone`
2. **기본 샘플 테스트**: Adam 음성으로 기본 설정
3. **감정 테스트**: Aiden 음성으로 angry 스타일  
4. **언어 테스트**: 영어/일본어 샘플
5. **커스텀 텍스트**: 원하는 문장으로 테스트