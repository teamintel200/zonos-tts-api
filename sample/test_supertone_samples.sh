#!/bin/bash

# Supertone 음성 샘플 테스트 스크립트
echo "🎵 Supertone 음성 샘플 테스트 시작"

# API 키 확인
if [ -z "$SUPERTONE_APIKEY" ]; then
    echo "⚠️  SUPERTONE_APIKEY 환경변수가 설정되지 않았습니다."
    echo "   export SUPERTONE_APIKEY=your_api_key_here"
    echo "   또는 curl 명령에서 직접 api_key를 지정하세요."
fi

# 서버 주소
SERVER="http://localhost:8000"

echo ""
echo "📋 사용 가능한 Supertone 음성 목록 조회"
curl -X GET "$SERVER/voices/supertone" | python -m json.tool | head -20

echo ""
echo ""
echo "🎤 음성 샘플 테스트"

# 1. Adam 음성 샘플 (환경변수 사용)
echo "1️⃣ Adam 음성 샘플 다운로드 (환경변수 API 키 사용)"
curl -X POST "$SERVER/voices/supertone/91992bbd4758bdcf9c9b01/sample" \
  -H "Content-Type: application/json" \
  -d '{}' \
  --output "adam_sample.wav" \
  --silent --show-error

if [ $? -eq 0 ] && [ -f "adam_sample.wav" ]; then
    echo "✅ adam_sample.wav 다운로드 완료 ($(ls -lh adam_sample.wav | awk '{print $5}'))"
else
    echo "❌ Adam 샘플 다운로드 실패"
fi

echo ""

# 2. Agatha 음성 샘플 (직접 API 키 지정)
echo "2️⃣ Agatha 음성 샘플 다운로드 (직접 API 키 지정)"
read -p "API 키를 입력하세요 (Enter로 건너뛰기): " API_KEY

if [ ! -z "$API_KEY" ]; then
    curl -X POST "$SERVER/voices/supertone/e5f6fb1a53d0add87afb4f/sample" \
      -H "Content-Type: application/json" \
      -d "{\"api_key\": \"$API_KEY\"}" \
      --output "agatha_sample.wav" \
      --silent --show-error
    
    if [ $? -eq 0 ] && [ -f "agatha_sample.wav" ]; then
        echo "✅ agatha_sample.wav 다운로드 완료 ($(ls -lh agatha_sample.wav | awk '{print $5}'))"
    else
        echo "❌ Agatha 샘플 다운로드 실패"
    fi
else
    echo "⏭️  API 키 입력을 건너뛰었습니다."
fi

echo ""
echo "📁 생성된 파일들:"
ls -la *.wav 2>/dev/null || echo "생성된 WAV 파일이 없습니다."

echo ""
echo "🔍 Swagger UI에서 직접 테스트: $SERVER/docs"
echo "📖 자세한 사용법: sample/supertone_voice_sample_examples.json"