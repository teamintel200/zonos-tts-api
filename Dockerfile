FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-devel
RUN pip install uv

RUN apt update && \
    apt install -y espeak-ng && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . ./

RUN pip install --upgrade pip setuptools wheel && \
    pip install -e .

# FastAPI 서버 실행
CMD ["uvicorn", "tts_api:app", "--host", "0.0.0.0", "--port", "8000"]