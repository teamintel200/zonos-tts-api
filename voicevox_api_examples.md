# Voicevox API Endpoints - Testing Examples and Documentation

This document provides comprehensive examples for testing all Voicevox-related endpoints using curl commands, along with expected responses and error handling scenarios.

## Prerequisites

- TTS API server running on `http://localhost:8000`
- Voicevox engine running on `http://localhost:50021`
- curl command available

## API Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/voices/voicevox` | GET | Get list of available free Voicevox speakers |
| `/voices/voicevox/{speaker_id}/sample` | GET | Get voice sample audio for preview |
| `/tts_voicevox` | POST | Convert text to speech using Voicevox |

## 1. Get Available Voicevox Voices

### Request
```bash
curl -X GET "http://localhost:8000/voices/voicevox"
```

### Expected Response (200 OK)
```json
[
  {
    "speaker_id": 2,
    "name": "四国めたん",
    "style_id": 0,
    "style_name": "あまあま",
    "type": "talk",
    "is_free": true
  },
  {
    "speaker_id": 2,
    "name": "四国めたん",
    "style_id": 2,
    "style_name": "ノーマル",
    "type": "talk",
    "is_free": true
  },
  {
    "speaker_id": 3,
    "name": "ずんだもん",
    "style_id": 1,
    "style_name": "あまあま",
    "type": "talk",
    "is_free": true
  }
]
```

### Error Response (503 Service Unavailable)
```json
{
  "detail": "Cannot connect to Voicevox engine. Please ensure the engine is running and accessible."
}
```

## 2. Get Voice Sample

### Request
```bash
curl -X GET "http://localhost:8000/voices/voicevox/2/sample" \
     -o "voice_sample.wav"
```

### Expected Response
- Status: 200 OK
- Content-Type: audio/wav
- Body: Binary WAV audio data

### Error Response - Invalid Speaker ID (400 Bad Request)
```json
{
  "detail": "Invalid speaker ID: 999. Please check the speaker ID and try again."
}
```

## 3. Basic Text-to-Speech

### Request
```bash
curl -X POST "http://localhost:8000/tts_voicevox" \
     -H "Content-Type: application/json" \
     -d '{
       "segments": [
         {
           "id": 1,
           "text": "こんにちは、世界！これは基本的なテストです。"
         }
       ],
       "tempdir": "voicevox_basic_test",
       "speaker_id": 2
     }'
```

### Expected Response (200 OK)
```json
[
  {
    "sequence": 1,
    "text": "こんにちは、世界！これは基本的なテストです。",
    "durationMillis": 3595,
    "path": "outputs/voicevox_basic_test/audio/tts/0001.wav"
  }
]
```

## 4. TTS with Custom Voice Parameters

### Request
```bash
curl -X POST "http://localhost:8000/tts_voicevox" \
     -H "Content-Type: application/json" \
     -d '{
       "segments": [
         {
           "id": 1,
           "text": "これはカスタムパラメータのテストです。速度と音程を調整しています。"
         }
       ],
       "tempdir": "voicevox_custom_test",
       "speaker_id": 2,
       "speed_scale": 1.2,
       "pitch_scale": 0.05,
       "intonation_scale": 1.1,
       "volume_scale": 0.9,
       "pre_phoneme_length": 0.15,
       "post_phoneme_length": 0.15,
       "enable_interrogative_upspeak": true
     }'
```

### Expected Response (200 OK)
```json
[
  {
    "sequence": 1,
    "text": "これはカスタムパラメータのテストです。速度と音程を調整しています。",
    "durationMillis": 4011,
    "path": "outputs/voicevox_custom_test/audio/tts/0001.wav"
  }
]
```

## 5. TTS with Multiple Segments

### Request
```bash
curl -X POST "http://localhost:8000/tts_voicevox" \
     -H "Content-Type: application/json" \
     -d '{
       "segments": [
         {
           "id": 1,
           "text": "これは最初のセグメントです。"
         },
         {
           "id": 2,
           "text": "これは二番目のセグメントです。"
         },
         {
           "id": 3,
           "text": "これは最後のセグメントです。"
         }
       ],
       "tempdir": "voicevox_multi_test",
       "speaker_id": 2
     }'
```

### Expected Response (200 OK)
```json
[
  {
    "sequence": 1,
    "text": "これは最初のセグメントです。",
    "durationMillis": 1963,
    "path": "outputs/voicevox_multi_test/audio/tts/0001.wav"
  },
  {
    "sequence": 2,
    "text": "これは二番目のセグメントです。",
    "durationMillis": 2037,
    "path": "outputs/voicevox_multi_test/audio/tts/0002.wav"
  },
  {
    "sequence": 3,
    "text": "これは最後のセグメントです。",
    "durationMillis": 1952,
    "path": "outputs/voicevox_multi_test/audio/tts/0003.wav"
  }
]
```

## 6. TTS with Different Speaker

### Request
```bash
curl -X POST "http://localhost:8000/tts_voicevox" \
     -H "Content-Type: application/json" \
     -d '{
       "segments": [
         {
           "id": 1,
           "text": "これは異なる音声での読み上げテストです。"
         }
       ],
       "tempdir": "voicevox_speaker_test",
       "speaker_id": 3
     }'
```

### Expected Response (200 OK)
```json
[
  {
    "sequence": 1,
    "text": "これは異なる音声での読み上げテストです。",
    "durationMillis": 3275,
    "path": "outputs/voicevox_speaker_test/audio/tts/0001.wav"
  }
]
```

## Error Handling Examples

### 7. Invalid Speaker ID

#### Request
```bash
curl -X POST "http://localhost:8000/tts_voicevox" \
     -H "Content-Type: application/json" \
     -d '{
       "segments": [
         {
           "id": 1,
           "text": "これは無効な音声IDのテストです。"
         }
       ],
       "tempdir": "voicevox_error_test",
       "speaker_id": 999
     }'
```

#### Expected Response (400 Bad Request)
```json
{
  "detail": "Speaker ID 999 is out of valid range (0-100)"
}
```

### 8. Empty Text

#### Request
```bash
curl -X POST "http://localhost:8000/tts_voicevox" \
     -H "Content-Type: application/json" \
     -d '{
       "segments": [
         {
           "id": 1,
           "text": ""
         }
       ],
       "tempdir": "voicevox_empty_test",
       "speaker_id": 2
     }'
```

#### Expected Response (400 Bad Request)
```json
{
  "detail": "Segment 1 has empty text"
}
```

### 9. Invalid Parameters

#### Request
```bash
curl -X POST "http://localhost:8000/tts_voicevox" \
     -H "Content-Type: application/json" \
     -d '{
       "segments": [
         {
           "id": 1,
           "text": "これは無効なパラメータのテストです。"
         }
       ],
       "tempdir": "voicevox_invalid_params_test",
       "speaker_id": 2,
       "speed_scale": 5.0,
       "pitch_scale": 1.0
     }'
```

#### Expected Response (422 Unprocessable Entity)
```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "speed_scale"],
      "msg": "Input should be less than or equal to 2.0",
      "input": 5.0
    },
    {
      "type": "less_than_equal",
      "loc": ["body", "pitch_scale"],
      "msg": "Input should be less than or equal to 0.15",
      "input": 1.0
    }
  ]
}
```

### 10. Invalid Voice Sample Request

#### Request
```bash
curl -X GET "http://localhost:8000/voices/voicevox/999/sample"
```

#### Expected Response (400 Bad Request)
```json
{
  "detail": "Invalid speaker ID: 999. Please check the speaker ID and try again."
}
```

## Parameter Reference

### VoicevoxTTSRequest Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `segments` | Array | Required | - | List of text segments to convert |
| `tempdir` | String | Required | - | Temporary directory name for output files |
| `speaker_id` | Integer | 0-100 | 2 | Voicevox speaker ID (2 = 四国めたん ノーマル) |
| `speed_scale` | Float | 0.5-2.0 | 1.0 | Speech speed multiplier |
| `pitch_scale` | Float | -0.15-0.15 | 0.0 | Pitch adjustment |
| `intonation_scale` | Float | 0.0-2.0 | 1.0 | Intonation strength |
| `volume_scale` | Float | 0.0-2.0 | 1.0 | Volume multiplier |
| `pre_phoneme_length` | Float | 0.0-1.5 | 0.1 | Pre-phoneme silence length (seconds) |
| `post_phoneme_length` | Float | 0.0-1.5 | 0.1 | Post-phoneme silence length (seconds) |
| `enable_interrogative_upspeak` | Boolean | - | true | Enable automatic interrogative upspeak |

### Available Free Speakers

| Speaker ID | Name | Style ID | Style Name | Type |
|------------|------|----------|------------|------|
| 2 | 四国めたん | 0 | あまあま | talk |
| 2 | 四国めたん | 2 | ノーマル | talk |
| 2 | 四国めたん | 4 | セクシー | talk |
| 2 | 四国めたん | 6 | ツンツン | talk |
| 3 | ずんだもん | 1 | あまあま | talk |
| 3 | ずんだもん | 3 | ノーマル | talk |
| 3 | ずんだもん | 5 | ツンツン | talk |
| 3 | ずんだもん | 22 | セクシー | talk |
| 8 | 春日部つむぎ | 8 | ノーマル | talk |
| 9 | 波音リツ | 9 | ノーマル | talk |
| 10 | 雨晴はう | 10 | ノーマル | talk |

## Integration with Other Endpoints

### Combining with WAV Combiner

After generating multiple segments with Voicevox, you can combine them using the `/combine_wav` endpoint:

```bash
# First, generate multiple segments
curl -X POST "http://localhost:8000/tts_voicevox" \
     -H "Content-Type: application/json" \
     -d '{
       "segments": [
         {"id": 1, "text": "最初の部分です。"},
         {"id": 2, "text": "二番目の部分です。"},
         {"id": 3, "text": "最後の部分です。"}
       ],
       "tempdir": "combine_test",
       "speaker_id": 2
     }'

# Then combine the generated files
curl -X POST "http://localhost:8000/combine_wav" \
     -H "Content-Type: application/json" \
     -d '{
       "tempdir": "combine_test"
     }'
```

## Testing Script Usage

Use the provided test script to run all tests automatically:

```bash
# Make script executable
chmod +x test_voicevox_endpoints.sh

# Run all tests
./test_voicevox_endpoints.sh
```

The script will:
1. Test all endpoints with valid inputs
2. Test error handling scenarios
3. Generate output files for verification
4. Create a summary report
5. Save detailed logs

## Postman Collection

For Postman users, create a collection with the following requests:

1. **Get Voicevox Voices**
   - Method: GET
   - URL: `{{base_url}}/voices/voicevox`

2. **Get Voice Sample**
   - Method: GET
   - URL: `{{base_url}}/voices/voicevox/2/sample`

3. **Basic TTS**
   - Method: POST
   - URL: `{{base_url}}/tts_voicevox`
   - Body: JSON with basic segment

4. **Custom Parameters TTS**
   - Method: POST
   - URL: `{{base_url}}/tts_voicevox`
   - Body: JSON with custom parameters

5. **Multiple Segments TTS**
   - Method: POST
   - URL: `{{base_url}}/tts_voicevox`
   - Body: JSON with multiple segments

Set environment variable:
- `base_url`: `http://localhost:8000`

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure TTS API server is running on port 8000
   - Ensure Voicevox engine is running on port 50021

2. **Invalid Speaker ID**
   - Check available speakers using `/voices/voicevox`
   - Use only free commercial-use speakers (IDs: 2, 3, 8, 9, 10)

3. **Parameter Validation Errors**
   - Check parameter ranges in the reference table
   - Ensure all required fields are provided

4. **Audio File Issues**
   - Generated files are in WAV format
   - Check file permissions in output directory
   - Verify Voicevox engine is properly configured

### Performance Notes

- TTS generation typically takes 1-3 seconds per segment
- Longer texts take proportionally more time
- Multiple segments are processed sequentially
- Voice samples are cached for better performance

## Requirements Verification

This testing suite verifies the following requirements:

- **Requirement 1.1**: Basic Voicevox TTS functionality ✅
- **Requirement 1.2**: Japanese text processing ✅
- **Requirement 2.1**: Multiple speaker support ✅
- **Requirement 2.2**: Speaker listing ✅
- **Requirement 6.1**: Voice preview functionality ✅
- **Requirement 6.2**: Sample audio generation ✅

All tests demonstrate successful implementation of the Voicevox integration according to the specified requirements.