#!/usr/bin/env python3
"""
음성 속도 조절 테스트 스크립트
다양한 방법으로 음성 속도를 조절해보겠습니다.
"""

import os
import librosa
import soundfile as sf
from pydub import AudioSegment
from pydub.effects import speedup
import numpy as np

def test_speed_methods(input_file):
    """다양한 속도 조절 방법 테스트"""
    
    if not os.path.exists(input_file):
        print(f"❌ 파일을 찾을 수 없습니다: {input_file}")
        return
    
    print(f"🎵 원본 파일: {input_file}")
    
    # 방법 1: pydub speedup (피치 변경됨)
    print("\n1️⃣ pydub speedup 방법 (피치 변경됨)")
    try:
        audio = AudioSegment.from_mp3(input_file)
        
        # 1.5배속
        fast_audio = speedup(audio, playback_speed=1.5)
        output1 = "speed_test_pydub_1.5x.mp3"
        fast_audio.export(output1, format="mp3")
        print(f"✅ 1.5배속: {output1}")
        
        # 2배속
        very_fast_audio = speedup(audio, playback_speed=2.0)
        output2 = "speed_test_pydub_2x.mp3"
        very_fast_audio.export(output2, format="mp3")
        print(f"✅ 2배속: {output2}")
        
    except Exception as e:
        print(f"❌ pydub 방법 실패: {e}")
    
    # 방법 2: librosa time stretching (피치 유지)
    print("\n2️⃣ librosa time stretching 방법 (피치 유지)")
    try:
        # 오디오 로드
        y, sr = librosa.load(input_file, sr=None)
        
        # 1.5배속 (피치 유지)
        y_fast = librosa.effects.time_stretch(y, rate=1.5)
        output3 = "speed_test_librosa_1.5x.wav"
        sf.write(output3, y_fast, sr)
        print(f"✅ 1.5배속 (피치 유지): {output3}")
        
        # 2배속 (피치 유지)
        y_very_fast = librosa.effects.time_stretch(y, rate=2.0)
        output4 = "speed_test_librosa_2x.wav"
        sf.write(output4, y_very_fast, sr)
        print(f"✅ 2배속 (피치 유지): {output4}")
        
        # 0.7배속 (느리게, 피치 유지)
        y_slow = librosa.effects.time_stretch(y, rate=0.7)
        output5 = "speed_test_librosa_0.7x.wav"
        sf.write(output5, y_slow, sr)
        print(f"✅ 0.7배속 (느리게, 피치 유지): {output5}")
        
    except Exception as e:
        print(f"❌ librosa 방법 실패: {e}")
    
    # 방법 3: pydub frame rate 조절 (간단한 방법)
    print("\n3️⃣ pydub frame rate 조절 방법")
    try:
        audio = AudioSegment.from_mp3(input_file)
        
        # 1.5배속 (frame rate 조절)
        fast_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * 1.5)})
        fast_audio = fast_audio.set_frame_rate(audio.frame_rate)
        output6 = "speed_test_framerate_1.5x.mp3"
        fast_audio.export(output6, format="mp3")
        print(f"✅ 1.5배속 (frame rate): {output6}")
        
    except Exception as e:
        print(f"❌ frame rate 방법 실패: {e}")
    
    print("\n🎉 속도 조절 테스트 완료!")
    print("\n재생해서 비교해보세요:")
    print(f"afplay {input_file}  # 원본")
    print("afplay speed_test_pydub_1.5x.mp3  # pydub 1.5배속")
    print("afplay speed_test_pydub_2x.mp3    # pydub 2배속")
    print("afplay speed_test_librosa_1.5x.wav  # librosa 1.5배속 (피치 유지)")
    print("afplay speed_test_librosa_2x.wav    # librosa 2배속 (피치 유지)")
    print("afplay speed_test_librosa_0.7x.wav  # librosa 0.7배속 (느리게)")

if __name__ == "__main__":
    # HYUK의 감정적인 음성 파일로 테스트
    test_file = "outputs/hyuk_normal_speed_emotional/audio/tts/0001.mp3"
    
    if os.path.exists(test_file):
        test_speed_methods(test_file)
    else:
        print("❌ 테스트 파일이 없습니다. 먼저 HYUK 음성을 생성해주세요.")
        print("사용 가능한 파일들:")
        import glob
        mp3_files = glob.glob("outputs/*/audio/tts/*.mp3")
        for f in mp3_files[-5:]:  # 최근 5개만 표시
            print(f"  - {f}")