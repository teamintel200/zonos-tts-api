#!/usr/bin/env python3
"""
Test script for voice management endpoints
"""

import requests
import json

# 서버 URL
BASE_URL = "http://localhost:8000"

# 여기에 실제 ElevenLabs API 키를 입력하세요
API_KEY = "your_elevenlabs_api_key_here"

def test_get_voices():
    """음성 목록 가져오기 테스트"""
    print("=== 음성 목록 가져오기 테스트 ===")
    
    url = f"{BASE_URL}/voices/elevenlabs"
    payload = {"api_key": API_KEY}
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            voices = response.json()
            print(f"총 {len(voices)}개의 음성을 찾았습니다:")
            for voice in voices[:5]:  # 처음 5개만 출력
                print(f"  - {voice['name']} ({voice['voice_id']}) - {voice['category']}")
            return voices
        else:
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def test_voice_sample(voice_id):
    """음성 샘플 다운로드 테스트"""
    print(f"\n=== 음성 샘플 테스트 (Voice ID: {voice_id}) ===")
    
    url = f"{BASE_URL}/voices/elevenlabs/{voice_id}/sample"
    payload = {"api_key": API_KEY}
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            filename = f"voice_sample_{voice_id}.mp3"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"음성 샘플이 {filename}에 저장되었습니다.")
            print(f"파일 크기: {len(response.content)} bytes")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

def test_tts_elevenlabs():
    """ElevenLabs TTS 테스트"""
    print("\n=== ElevenLabs TTS 테스트 ===")
    
    url = f"{BASE_URL}/tts_elevenlabs"
    payload = {
        "segments": [
            {"id": 1, "text": "안녕하세요, 이것은 테스트 메시지입니다."},
            {"id": 2, "text": "ElevenLabs 음성 합성이 잘 작동하는지 확인해보겠습니다."}
        ],
        "tempdir": "test_session_123",
        "api_key": API_KEY,
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel (기본 한국어 호환 음성)
        "stability": 0.5,
        "similarity_boost": 0.8
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            results = response.json()
            print(f"TTS 생성 완료! {len(results)}개 세그먼트 처리됨:")
            for result in results:
                print(f"  - 세그먼트 {result['sequence']}: {result['durationMillis']}ms")
                print(f"    파일: {result['path']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    print("Voice Management Endpoints 테스트 시작")
    print("=" * 50)
    
    # API 키 확인
    if API_KEY == "your_elevenlabs_api_key_here":
        print("⚠️  API_KEY를 실제 ElevenLabs API 키로 변경해주세요!")
        exit(1)
    
    # 1. 음성 목록 가져오기
    voices = test_get_voices()
    
    if voices:
        # 2. 첫 번째 음성으로 샘플 테스트
        first_voice_id = voices[0]['voice_id']
        test_voice_sample(first_voice_id)
        
        # 3. TTS 테스트
        test_tts_elevenlabs()
    
    print("\n테스트 완료!")