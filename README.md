# gTTS FastAPI 서버

이 프로젝트는 gTTS를 사용하여 텍스트를 음성으로 변환하는 간단한 FastAPI 서버입니다.

## Docker Compose로 실행 (권장)

이 방법은 애플리케이션을 실행하는 가장 권장되는 방법입니다. Docker Compose를 사용하여 이미지를 빌드하고 컨테이너를 실행하므로, FFmpeg를 포함한 모든 의존성이 올바르게 설치되고 구성됩니다.

### 서버 실행

```bash
docker-compose up --build
```

서버는 `http://localhost:8000`에서 사용할 수 있습니다.

## API 엔드포인트

이 서비스는 텍스트를 음성으로 변환하고(tts_simple), 생성된 음성 파일들을 하나로 합치는(combine_wav) 두 가지 엔드포인트를 제공합니다.

### 1. POST /tts_simple

지정된 임시 디렉토리(`tempdir`)에 텍스트 세그먼트별로 음성 파일을 생성합니다. `tempdir`는 각 작업 세션을 구분하는 고유한 이름으로 사용됩니다.

**요청 본문 (Request Body):**

```json
{
  "segments": [
    { "id": 1, "text": "안녕하세요." },
    { "id": 2, "text": "반갑습니다." }
  ],
  "tempdir": "내_고유한_세션_이름"  // 이 세션 이름을 기억해두세요!
}
```

**응답 (Response):**

```json
[
  {
    "sequence": 1,
    "text": "안녕하세요.",
    "durationMillis": 1500,
    "path": "outputs/내_고유한_세션_이름/audio/tts/0001.mp3"
  },
  {
    "sequence": 2,
    "text": "반갑습니다.",
    "durationMillis": 1200,
    "path": "outputs/내_고유한_세션_이름/audio/tts/0002.mp3"
  }
]
```

### 2. POST /combine_wav

`/tts_simple`에서 사용했던 `tempdir`에 생성된 모든 음성 파일들을 하나의 WAV 파일로 합칩니다. 합쳐진 후에는 해당 `tempdir` 디렉토리는 자동으로 삭제됩니다.

**요청 본문 (Request Body):**

```json
{
  "tempdir": "내_고유한_세션_이름"  // /tts_simple 에서 사용했던 세션 이름을 그대로 입력!
}
```

**응답 (Response):**

```json
{
  "combined_path": "outputs/combined_내_고유한_세션_이름.wav",
  "durationMillis": 2700
}
```

## 로컬 개발 (Docker 없이)

Docker 없이 로컬에서 애플리케이션을 실행하려면, 시스템에 FFmpeg가 설치되어 있어야 합니다.

### 필수 조건

-   **Python 3.9+**
-   **FFmpeg**: macOS에서는 Homebrew를 사용하여 설치할 수 있습니다:
    ```bash
    brew install ffmpeg
    ```
    다른 운영 체제의 경우, 공식 FFmpeg 문서를 참조하십시오.

### 설치

pip을 사용하여 필요한 Python 패키지를 설치합니다:

```bash
pip install -r requirements.txt
```

### 서버 실행

FastAPI 서버를 실행하려면 다음 명령어를 사용하십시오:

```bash
python -m uvicorn tts_api:app --reload
```
