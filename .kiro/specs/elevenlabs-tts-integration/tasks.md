# Implementation Plan

- [x] 1. Extend data models for ElevenLabs functionality
  - Add ElevenLabsTTSRequest, VoicesRequest, and Voice models to schemas.py
  - Include validation for stability and similarity_boost parameters (0.0-1.0 range)
  - Add optional fields with appropriate defaults for Korean TTS
  - _Requirements: 2.1, 6.3, 6.4_

- [x] 2. Create ElevenLabs service layer in separate module
  - [x] 2.1 Create elevenlabs_service.py with ElevenLabsService class
    - Implement service initialization with dynamic API key handling
    - Add text_to_speech method with voice settings and error handling
    - Include proper exception handling for API failures and invalid keys
    - _Requirements: 2.4, 4.1, 4.2_

  - [x] 2.2 Add voice management methods to ElevenLabsService
    - Implement get_available_voices method to retrieve voice list
    - Add get_voice_preview method for sample audio streaming
    - Include Korean-compatible voice filtering and default voice selection
    - _Requirements: 5.2, 7.2, 2.3_

- [x] 3. Add ElevenLabs endpoints to main tts_api.py
  - [x] 3.1 Import ElevenLabsService and add /tts_elevenlabs POST endpoint
    - Import elevenlabs_service module into tts_api.py
    - Create endpoint that accepts ElevenLabsTTSRequest with API key and voice settings
    - Use ElevenLabsService to generate audio files for each segment
    - Save files using existing get_next_output_filename utility function
    - Return same response format as /tts_simple for workflow compatibility
    - _Requirements: 1.1, 1.3, 3.1, 3.3_

  - [x] 3.2 Add comprehensive error handling to TTS endpoint
    - Handle ElevenLabs API authentication errors (401)
    - Manage rate limiting and service unavailable errors
    - Validate voice settings and return appropriate FastAPI HTTPException responses
    - Log errors without exposing API keys in logs
    - _Requirements: 2.4, 4.1, 4.2, 4.3, 4.4_

- [x] 4. Add voice management endpoints to main tts_api.py
  - [x] 4.1 Create /voices/elevenlabs POST endpoint in tts_api.py
    - Accept VoicesRequest with API key parameter
    - Use ElevenLabsService to retrieve and return list of available voices
    - Handle authentication errors and return appropriate HTTP responses
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 4.2 Create /voices/elevenlabs/{voice_id}/sample POST endpoint in tts_api.py
    - Accept voice_id as path parameter and API key in request body
    - Use ElevenLabsService to get voice sample audio
    - Return audio sample as streaming response
    - Handle invalid voice_id and authentication errors with proper HTTP status codes
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 5. Test ElevenLabs API integration with real API calls
  - [x] 5.1 Create manual test script for ElevenLabs connectivity
    - Create test_elevenlabs.py script to verify API key and basic functionality
    - Test voice list retrieval with real ElevenLabs API
    - Test simple text-to-speech generation with Korean text
    - Verify audio file generation and format compatibility
    - _Requirements: 2.4, 5.2, 7.2_

  - [x] 5.2 Test all ElevenLabs endpoints with curl/Postman examples
    - Test /tts_elevenlabs endpoint with sample Korean text and real API key
    - Test /voices/elevenlabs endpoint to retrieve available voices
    - Test /voices/elevenlabs/{voice_id}/sample endpoint for voice preview
    - Verify error handling with invalid API keys and parameters
    - Document successful test cases and expected responses
    - _Requirements: 1.1, 1.3, 5.1, 7.1_

- [x] 6. Update utility functions for ElevenLabs compatibility
  - Modify get_next_output_filename to work with ElevenLabs audio format
  - Ensure file naming consistency between gTTS and ElevenLabs outputs
  - Verify combine_wav functionality works with ElevenLabs generated files
  - _Requirements: 3.1, 3.2_

- [ ] 7. Add input validation and security measures
  - [ ] 7.1 Implement parameter validation
    - Validate stability and similarity_boost ranges (0.0-1.0)
    - Add text length limits based on ElevenLabs API constraints
    - Implement tempdir path validation to prevent directory traversal
    - _Requirements: 6.4_

  - [ ] 7.2 Implement secure API key handling
    - Ensure API keys are not logged or stored
    - Add request-scoped API key usage only
    - Implement proper error messages without exposing sensitive data
    - _Requirements: 2.1, 2.4_

- [ ] 8. Create comprehensive test suite
  - [ ] 8.1 Write unit tests for ElevenLabs service layer
    - Test API key validation and error handling
    - Mock ElevenLabs API responses for consistent testing
    - Test voice settings validation and defaults
    - _Requirements: 2.4, 6.4_

  - [ ] 8.2 Write integration tests for new endpoints
    - Test /tts_elevenlabs endpoint with mock ElevenLabs API
    - Test voice management endpoints with various scenarios
    - Verify error handling and response formats
    - _Requirements: 1.1, 5.1, 7.1_

  - [ ] 8.3 Test end-to-end workflow compatibility
    - Test /tts_elevenlabs → /combine_wav workflow
    - Verify audio file format compatibility
    - Test mixed gTTS and ElevenLabs file combining
    - _Requirements: 3.1, 3.2_

- [ ] 9. Update documentation and configuration
  - Update README.md with new ElevenLabs endpoints documentation
  - Add API usage examples for all new endpoints
  - Document required API key format and error responses
  - _Requirements: 1.1, 2.1, 5.1, 7.1_