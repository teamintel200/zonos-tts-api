# 구현 계획

- [x] 1. Voicevox 기능을 위한 데이터 모델 확장
  - schemas.py에 VoicevoxTTSRequest, VoicevoxSpeaker 모델 추가
  - 음성 매개변수 검증 포함 (speed_scale, pitch_scale 등)
  - 일본어 TTS를 위한 적절한 기본값과 선택적 필드 추가
  - _요구사항: 2.1, 5.1, 5.2_

- [x] 2. 별도 모듈에서 Voicevox 서비스 레이어 생성
  - [x] 2.1 VoicevoxService 클래스로 voicevox_service.py 생성
    - Voicevox 엔진 URL을 사용한 서비스 초기화 구현
    - 음성 설정 및 오류 처리를 포함한 text_to_speech 메서드 추가
    - API 실패 및 연결 오류에 대한 적절한 예외 처리 포함
    - _요구사항: 4.1, 4.2, 4.3_

  - [x] 2.2 VoicevoxService에 음성 관리 메서드 추가
    - 음성 목록을 검색하는 get_speakers 메서드 구현
    - 샘플 오디오 생성을 위한 get_speaker_preview 메서드 추가
    - 무료 음성 필터링 및 기본 음성 선택 포함
    - _요구사항: 2.2, 6.1, 6.2_

- [x] 3. 메인 tts_api.py에 Voicevox 엔드포인트 추가
  - [x] 3.1 VoicevoxService 가져오기 및 /tts_voicevox POST 엔드포인트 추가
    - tts_api.py에 voicevox_service 모듈 가져오기
    - 음성 설정과 함께 VoicevoxTTSRequest를 받는 엔드포인트 생성
    - VoicevoxService를 사용하여 각 세그먼트에 대한 오디오 파일 생성
    - 기존 get_next_output_filename 유틸리티 함수를 사용하여 파일 저장
    - 워크플로우 호환성을 위해 /tts_simple과 동일한 응답 형식 반환
    - _요구사항: 1.1, 1.2, 3.1, 3.2_

  - [x] 3.2 TTS 엔드포인트에 포괄적인 오류 처리 추가
    - Voicevox 엔진 연결 오류 처리
    - 잘못된 매개변수 및 지원되지 않는 텍스트 관리
    - 매개변수 검증 및 적절한 FastAPI HTTPException 응답 반환
    - 민감한 정보를 로그에 노출하지 않고 오류 기록
    - _요구사항: 4.1, 4.2, 4.3, 4.4_

- [x] 4. 메인 tts_api.py에 음성 관리 엔드포인트 추가
  - [x] 4.1 tts_api.py에 /voices/voicevox GET 엔드포인트 생성
    - 무료 Voicevox 음성 목록을 검색하고 반환하기 위해 VoicevoxService 사용
    - 연결 오류 처리 및 적절한 HTTP 응답 반환
    - _요구사항: 2.2, 2.3_

  - [x] 4.2 tts_api.py에 /voices/voicevox/{speaker_id}/sample GET 엔드포인트 생성
    - speaker_id를 경로 매개변수로 받기
    - VoicevoxService를 사용하여 음성 샘플 오디오 가져오기
    - 오디오 샘플을 스트리밍 응답으로 반환
    - 잘못된 speaker_id 및 연결 오류를 적절한 HTTP 상태 코드로 처리
    - _요구사항: 6.1, 6.2, 6.3, 6.4_

- [x] 5. 실제 API 호출로 Voicevox API 통합 테스트
  - [x] 5.1 Voicevox 연결을 위한 수동 테스트 스크립트 생성
    - Voicevox 엔진 연결 및 기본 기능을 확인하는 test_voicevox.py 스크립트 생성
    - 실제 Voicevox API로 음성 목록 검색 테스트
    - 일본어 텍스트로 간단한 텍스트 음성 변환 생성 테스트
    - 오디오 파일 생성 및 형식 호환성 확인
    - _요구사항: 4.1, 2.2, 6.2_

  - [x] 5.2 curl/Postman 예제로 모든 Voicevox 엔드포인트 테스트
    - 샘플 일본어 텍스트로 /tts_voicevox 엔드포인트 테스트
    - 사용 가능한 음성을 검색하기 위해 /voices/voicevox 엔드포인트 테스트
    - 음성 미리보기를 위해 /voices/voicevox/{speaker_id}/sample 엔드포인트 테스트
    - 잘못된 매개변수로 오류 처리 확인
    - 성공적인 테스트 케이스 및 예상 응답 문서화
    - _요구사항: 1.1, 1.2, 2.1, 6.1_

- [ ] 6. Voicevox 호환성을 위한 유틸리티 함수 업데이트
  - Voicevox 오디오 형식과 작동하도록 get_next_output_filename 수정
  - gTTS와 Voicevox 출력 간의 파일 명명 일관성 보장
  - combine_wav 기능이 Voicevox 생성 파일과 작동하는지 확인
  - _요구사항: 3.1, 3.2_

- [ ] 7. 입력 검증 및 보안 조치 추가
  - [ ] 7.1 매개변수 검증 구현
    - speed_scale, pitch_scale 등의 범위 검증
    - Voicevox API 제약 조건에 따른 텍스트 길이 제한 추가
    - 디렉토리 순회를 방지하기 위한 tempdir 경로 검증 구현
    - _요구사항: 5.3, 5.4_

  - [ ] 7.2 안전한 연결 처리 구현
    - 연결 실패 시 우아한 성능 저하 보장
    - 요청별 연결 관리만 사용
    - 민감한 데이터를 노출하지 않는 적절한 오류 메시지 구현
    - _요구사항: 4.1, 4.4_

- [ ] 8. 포괄적인 테스트 스위트 생성
  - [ ] 8.1 Voicevox 서비스 레이어를 위한 단위 테스트 작성
    - 연결 검증 및 오류 처리 테스트
    - 일관된 테스트를 위한 모의 Voicevox API 응답
    - 음성 설정 검증 및 기본값 테스트
    - _요구사항: 4.1, 5.3_

  - [ ] 8.2 새로운 엔드포인트를 위한 통합 테스트 작성
    - 모의 Voicevox API로 /tts_voicevox 엔드포인트 테스트
    - 다양한 시나리오로 음성 관리 엔드포인트 테스트
    - 오류 처리 및 응답 형식 확인
    - _요구사항: 1.1, 2.1, 6.1_

  - [ ] 8.3 엔드 투 엔드 워크플로우 호환성 테스트
    - /tts_voicevox → /combine_wav 워크플로우 테스트
    - 오디오 파일 형식 호환성 확인
    - 혼합 gTTS 및 Voicevox 파일 결합 테스트
    - _요구사항: 3.1, 3.2_

- [ ] 9. 문서 및 구성 업데이트
  - 새로운 Voicevox 엔드포인트 문서로 README.md 업데이트
  - 모든 새로운 엔드포인트에 대한 API 사용 예제 추가
  - Docker 구성 및 환경 변수 설정 문서화
  - _요구사항: 1.1, 4.1, 2.1, 6.1_

- [ ] 10. 한국어 지원 실험적 구현 (선택 사항)
  - 한국어 텍스트를 일본어 발음으로 변환하는 유틸리티 함수 생성
  - 한국어 → 로마자 → 가타카나 변환 파이프라인 구현
  - 제한된 한국어 지원에 대한 실험적 테스트 수행
  - _요구사항: 1.3, 1.4_