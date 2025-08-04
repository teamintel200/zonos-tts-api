from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import StreamingResponse
import os
import logging
import io
from gtts import gTTS
from pydub import AudioSegment
import shutil
import glob
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from schemas import Segment, TTSRequest, CombineRequest, ElevenLabsTTSRequest, VoicesRequest, SpeedAdjustRequest, VoicevoxTTSRequest, SupertoneTTSRequest, SupertoneVoiceSampleRequest, SktAxTTSRequest, SktAxVoicesRequest
from utils import get_next_output_filename, validate_audio_files_for_combine, get_combined_output_path, OUTPUTS_DIR
from elevenlabs_service import ElevenLabsService, ElevenLabsError
from voicevox_service import VoicevoxService, VoicevoxError
from supertone_service import SupertoneService, SupertoneError
from skt_ax_service import SktAxService, SktAxError
import librosa
import soundfile as sf
import tempfile

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ElevenLabs service
elevenlabs_service = ElevenLabsService()

# Initialize Voicevox service
VOICEVOX_URL = os.getenv("VOICEVOX_URL", "http://localhost:50021")
voicevox_service = VoicevoxService(base_url=VOICEVOX_URL)

# Initialize Supertone service
supertone_service = SupertoneService()

# Initialize SKT A.X service
skt_ax_service = SktAxService()

# API keys are now required parameters in requests

@app.post("/tts_simple")
async def tts_simple(req: TTSRequest = Body(...)):
    results = []
    for segment in req.segments:
        output_path = get_next_output_filename(req.tempdir)
        print(f"Tempdir: {req.tempdir}, ID: {segment.id}, Text: {segment.text}, Path: {output_path}")
        try:
            tts = gTTS(text=segment.text, lang='ko')
            tts.save(output_path)
            audio = AudioSegment.from_mp3(output_path)
            duration_ms = len(audio)
            results.append({
                "sequence": segment.id,
                "text": segment.text,
                "durationMillis": duration_ms,
                "path": output_path
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return results

@app.post("/tts_elevenlabs")
async def tts_elevenlabs(req: ElevenLabsTTSRequest = Body(...)):
    # API key is now required in request
    api_key = req.api_key
    
    # Input validation
    if not api_key or not api_key.strip():
        logger.warning("ElevenLabs TTS request failed: Missing API key")
        raise HTTPException(status_code=400, detail="API key is required")
    
    if not req.segments:
        logger.warning("ElevenLabs TTS request failed: No segments provided")
        raise HTTPException(status_code=400, detail="At least one segment is required")
    
    # Validate voice settings ranges (additional validation beyond Pydantic)
    if req.stability is not None and (req.stability < 0.0 or req.stability > 1.0):
        logger.warning(f"ElevenLabs TTS request failed: Invalid stability value {req.stability}")
        raise HTTPException(status_code=400, detail="Stability must be between 0.0 and 1.0")
    
    if req.similarity_boost is not None and (req.similarity_boost < 0.0 or req.similarity_boost > 1.0):
        logger.warning(f"ElevenLabs TTS request failed: Invalid similarity_boost value {req.similarity_boost}")
        raise HTTPException(status_code=400, detail="Similarity boost must be between 0.0 and 1.0")
    
    # Validate text length for each segment
    for segment in req.segments:
        if not segment.text or not segment.text.strip():
            logger.warning(f"ElevenLabs TTS request failed: Empty text in segment {segment.id}")
            raise HTTPException(status_code=400, detail=f"Segment {segment.id} has empty text")
        
        if len(segment.text) > 5000:  # ElevenLabs typical limit
            logger.warning(f"ElevenLabs TTS request failed: Text too long in segment {segment.id}")
            raise HTTPException(status_code=400, detail=f"Segment {segment.id} text exceeds 5000 characters")
    
    # Validate tempdir to prevent directory traversal
    if not req.tempdir or '..' in req.tempdir or '/' in req.tempdir or '\\' in req.tempdir:
        logger.warning(f"ElevenLabs TTS request failed: Invalid tempdir: {req.tempdir}")
        raise HTTPException(status_code=400, detail="Invalid tempdir format")
    
    logger.info(f"Processing ElevenLabs TTS request for {len(req.segments)} segments in tempdir: {req.tempdir}")
    
    results = []
    for segment in req.segments:
        output_path = get_next_output_filename(req.tempdir)
        logger.info(f"Processing segment {segment.id} with {len(segment.text)} characters")
        
        try:
            # Generate audio using ElevenLabs service
            audio_data = elevenlabs_service.text_to_speech(
                api_key=api_key,
                text=segment.text,
                voice_id=req.voice_id,
                stability=req.stability,
                similarity_boost=req.similarity_boost,
                style=req.style,
                use_speaker_boost=req.use_speaker_boost,
                speaking_rate=req.speaking_rate,
                seed=req.seed,
                output_format=req.output_format
            )
            
            # Save audio data to file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            # Get duration using pydub (same as /tts_simple)
            audio = AudioSegment.from_mp3(output_path)
            duration_ms = len(audio)
            
            results.append({
                "sequence": segment.id,
                "text": segment.text,
                "durationMillis": duration_ms,
                "path": output_path
            })
            
            logger.info(f"Successfully processed segment {segment.id}, duration: {duration_ms}ms")
            
        except ElevenLabsError as e:
            # Log error without exposing API key
            logger.error(f"ElevenLabs API error for segment {segment.id}: {e.message} (status: {e.status_code})")
            
            # Handle specific ElevenLabs errors with appropriate HTTP status codes
            if e.status_code == 401:
                raise HTTPException(
                    status_code=401, 
                    detail="Invalid ElevenLabs API key. Please check your API key and try again."
                )
            elif e.status_code == 429:
                raise HTTPException(
                    status_code=429, 
                    detail="ElevenLabs API rate limit exceeded. Please wait and try again later."
                )
            elif e.status_code == 400:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid request parameters: {e.message}"
                )
            elif e.status_code == 404:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Voice not found: {e.message}"
                )
            elif e.status_code == 503:
                raise HTTPException(
                    status_code=503, 
                    detail="ElevenLabs service is temporarily unavailable. Please try again later."
                )
            else:
                raise HTTPException(
                    status_code=500, 
                    detail="ElevenLabs TTS generation failed. Please try again."
                )
                
        except FileNotFoundError as e:
            logger.error(f"File system error for segment {segment.id}: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to save audio file. Please check server configuration."
            )
            
        except PermissionError as e:
            logger.error(f"Permission error for segment {segment.id}: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="Permission denied when saving audio file. Please check server permissions."
            )
            
        except Exception as e:
            # Log unexpected errors without exposing sensitive information
            logger.error(f"Unexpected error processing segment {segment.id}: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="An unexpected error occurred during TTS generation. Please try again."
            )
    
    logger.info(f"Successfully completed ElevenLabs TTS request for {len(results)} segments")
    return results

@app.post("/tts_voicevox")
async def tts_voicevox(req: VoicevoxTTSRequest = Body(...)):
    """
    Convert text to speech using Voicevox engine
    
    Args:
        req: VoicevoxTTSRequest containing segments, tempdir, and voice settings
        
    Returns:
        List of generated audio file information with same format as /tts_simple
        
    Raises:
        HTTPException: For validation errors, connection issues, or processing failures
    """
    # Input validation
    if not req.segments:
        logger.warning("Voicevox TTS request failed: No segments provided")
        raise HTTPException(status_code=400, detail="At least one segment is required")
    
    # Validate tempdir to prevent directory traversal
    if not req.tempdir or '..' in req.tempdir or '/' in req.tempdir or '\\' in req.tempdir:
        logger.warning(f"Voicevox TTS request failed: Invalid tempdir: {req.tempdir}")
        raise HTTPException(status_code=400, detail="Invalid tempdir format")
    
    # Validate speaker_id is within reasonable range
    if req.speaker_id < 0 or req.speaker_id > 100:  # Reasonable range for Voicevox speakers
        logger.warning(f"Voicevox TTS request failed: Invalid speaker_id: {req.speaker_id}")
        raise HTTPException(status_code=400, detail=f"Speaker ID {req.speaker_id} is out of valid range (0-100)")
    
    # Additional parameter validation beyond Pydantic constraints
    if req.speed_scale < 0.5 or req.speed_scale > 2.0:
        logger.warning(f"Voicevox TTS request failed: Invalid speed_scale: {req.speed_scale}")
        raise HTTPException(status_code=400, detail="Speed scale must be between 0.5 and 2.0")
    
    if req.pitch_scale < -0.15 or req.pitch_scale > 0.15:
        logger.warning(f"Voicevox TTS request failed: Invalid pitch_scale: {req.pitch_scale}")
        raise HTTPException(status_code=400, detail="Pitch scale must be between -0.15 and 0.15")
    
    if req.intonation_scale < 0.0 or req.intonation_scale > 2.0:
        logger.warning(f"Voicevox TTS request failed: Invalid intonation_scale: {req.intonation_scale}")
        raise HTTPException(status_code=400, detail="Intonation scale must be between 0.0 and 2.0")
    
    if req.volume_scale < 0.0 or req.volume_scale > 2.0:
        logger.warning(f"Voicevox TTS request failed: Invalid volume_scale: {req.volume_scale}")
        raise HTTPException(status_code=400, detail="Volume scale must be between 0.0 and 2.0")
    
    if req.pre_phoneme_length < 0.0 or req.pre_phoneme_length > 1.5:
        logger.warning(f"Voicevox TTS request failed: Invalid pre_phoneme_length: {req.pre_phoneme_length}")
        raise HTTPException(status_code=400, detail="Pre-phoneme length must be between 0.0 and 1.5")
    
    if req.post_phoneme_length < 0.0 or req.post_phoneme_length > 1.5:
        logger.warning(f"Voicevox TTS request failed: Invalid post_phoneme_length: {req.post_phoneme_length}")
        raise HTTPException(status_code=400, detail="Post-phoneme length must be between 0.0 and 1.5")
    
    # Validate text content and length for each segment
    for segment in req.segments:
        if not segment.text or not segment.text.strip():
            logger.warning(f"Voicevox TTS request failed: Empty text in segment {segment.id}")
            raise HTTPException(status_code=400, detail=f"Segment {segment.id} has empty text")
        
        if len(segment.text) > 1000:  # Voicevox typical limit
            logger.warning(f"Voicevox TTS request failed: Text too long in segment {segment.id}")
            raise HTTPException(status_code=400, detail=f"Segment {segment.id} text exceeds 1000 characters")
        
        # Check for potentially problematic characters
        if any(ord(char) > 65535 for char in segment.text):  # Check for characters outside BMP
            logger.warning(f"Voicevox TTS request failed: Unsupported characters in segment {segment.id}")
            raise HTTPException(status_code=400, detail=f"Segment {segment.id} contains unsupported characters")
    
    # Check if Voicevox service is available before processing
    try:
        # Quick connection test
        voicevox_service._validate_connection()
    except VoicevoxError as e:
        logger.error(f"Voicevox engine connection check failed: {e.message}")
        if e.status_code == 503:
            raise HTTPException(
                status_code=503, 
                detail="Voicevox engine is not available. Please ensure the engine is running and accessible."
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to connect to Voicevox engine. Please try again later."
            )
    
    logger.info(f"Processing Voicevox TTS request for {len(req.segments)} segments in tempdir: {req.tempdir}")
    
    results = []
    for segment in req.segments:
        # Generate WAV output path for Voicevox
        output_path = get_next_output_filename(req.tempdir, extension="wav")
        logger.info(f"Processing segment {segment.id} with {len(segment.text)} characters")
        
        try:
            # Generate audio using Voicevox service
            audio_data = voicevox_service.text_to_speech(
                text=segment.text,
                speaker_id=req.speaker_id,
                speed_scale=req.speed_scale,
                pitch_scale=req.pitch_scale,
                intonation_scale=req.intonation_scale,
                volume_scale=req.volume_scale,
                pre_phoneme_length=req.pre_phoneme_length,
                post_phoneme_length=req.post_phoneme_length,
                enable_interrogative_upspeak=req.enable_interrogative_upspeak
            )
            
            # Save audio data to file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            # Get duration using pydub (same format as other TTS endpoints)
            audio = AudioSegment.from_wav(output_path)
            duration_ms = len(audio)
            
            results.append({
                "sequence": segment.id,
                "text": segment.text,
                "durationMillis": duration_ms,
                "path": output_path
            })
            
            logger.info(f"Successfully processed segment {segment.id}, duration: {duration_ms}ms")
            
        except VoicevoxError as e:
            # Log error without exposing sensitive information
            logger.error(f"Voicevox API error for segment {segment.id}: {e.message} (status: {e.status_code})")
            
            # Handle specific Voicevox errors with appropriate HTTP status codes
            if e.status_code == 503:
                raise HTTPException(
                    status_code=503, 
                    detail="Cannot connect to Voicevox engine. Please ensure the engine is running."
                )
            elif e.status_code == 400:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid request parameters: {e.message}"
                )
            elif e.status_code == 404:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Invalid speaker ID: {req.speaker_id}. Please check the speaker ID and try again."
                )
            elif e.status_code == 422:
                raise HTTPException(
                    status_code=422, 
                    detail=f"Invalid text or speaker parameters: {e.message}"
                )
            else:
                raise HTTPException(
                    status_code=500, 
                    detail="Voicevox TTS generation failed. Please try again."
                )
                
        except FileNotFoundError as e:
            logger.error(f"File system error for segment {segment.id}: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to save audio file. Please check server configuration."
            )
            
        except PermissionError as e:
            logger.error(f"Permission error for segment {segment.id}: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="Permission denied when saving audio file. Please check server permissions."
            )
            
        except Exception as e:
            # Log unexpected errors without exposing sensitive information
            logger.error(f"Unexpected error processing segment {segment.id}: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="An unexpected error occurred during TTS generation. Please try again."
            )
    
    logger.info(f"Successfully completed Voicevox TTS request for {len(results)} segments")
    return results

@app.post("/combine_wav")
async def combine_wav(req: CombineRequest = Body(...)):
    """
    Combine audio files from both gTTS and ElevenLabs engines into a single WAV file.
    
    This endpoint works with audio files generated by either gTTS or ElevenLabs,
    maintaining compatibility across both TTS engines.
    
    Args:
        req: CombineRequest containing tempdir
        
    Returns:
        dict: Combined file path and total duration
        
    Raises:
        HTTPException: For missing files, invalid tempdir, or processing errors
    """
    logger.info(f"Processing combine_wav request for tempdir: {req.tempdir}")
    
    try:
        # Use utility function to validate and get audio files
        # This works with both gTTS and ElevenLabs generated files
        files = validate_audio_files_for_combine(req.tempdir)
        logger.info(f"Found {len(files)} audio files to combine")
        
        # Combine all audio files (works with mixed gTTS/ElevenLabs/Voicevox files)
        combined = AudioSegment.empty()
        for i, file_path in enumerate(files, 1):
            try:
                # Auto-detect file format based on extension
                if file_path.lower().endswith('.wav'):
                    sound = AudioSegment.from_wav(file_path)
                else:
                    sound = AudioSegment.from_mp3(file_path)
                combined += sound
                logger.debug(f"Added file {i}/{len(files)}: {os.path.basename(file_path)}")
            except Exception as e:
                logger.error(f"Failed to process audio file {file_path}: {str(e)}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to process audio file: {os.path.basename(file_path)}"
                )
        
        # Generate output path using utility function
        combined_path = get_combined_output_path(req.tempdir)
        
        # Export combined audio as WAV
        try:
            combined.export(combined_path, format="wav")
            logger.info(f"Successfully exported combined audio to: {combined_path}")
        except Exception as e:
            logger.error(f"Failed to export combined audio: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to export combined audio file"
            )
        
        # Clean up temporary directory
        dir_to_delete = os.path.join(OUTPUTS_DIR, req.tempdir)
        try:
            shutil.rmtree(dir_to_delete)
            logger.info(f"Cleaned up temporary directory: {dir_to_delete}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary directory {dir_to_delete}: {str(e)}")
            # Don't fail the request if cleanup fails
        
        total_duration_ms = len(combined)
        
        logger.info(f"Successfully combined {len(files)} files, total duration: {total_duration_ms}ms")
        
        return {
            "combined_path": combined_path,
            "durationMillis": total_duration_ms
        }
        
    except FileNotFoundError as e:
        logger.warning(f"Combine request failed - directory not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
        
    except ValueError as e:
        logger.warning(f"Combine request failed - validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"Unexpected error in combine_wav: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while combining audio files"
        )

@app.post("/voices/elevenlabs")
async def get_elevenlabs_voices(req: VoicesRequest = Body(...)):
    """
    Retrieve list of available ElevenLabs voices
    
    Args:
        req: VoicesRequest containing API key
        
    Returns:
        List of available voices with Korean-compatible voices prioritized
        
    Raises:
        HTTPException: For authentication errors or API failures
    """
    # API key is now required in request
    api_key = req.api_key
    
    # Input validation
    if not api_key or not api_key.strip():
        logger.warning("ElevenLabs voices request failed: Missing API key")
        raise HTTPException(status_code=400, detail="API key is required")
    
    logger.info("Processing ElevenLabs voices request")
    
    try:
        # Get available voices using ElevenLabs service
        voices_list = elevenlabs_service.get_available_voices(api_key)
        
        # Convert to dict format for JSON response
        voices_response = [
            {
                "voice_id": voice.voice_id,
                "name": voice.name,
                "category": voice.category,
                "language": voice.language
            }
            for voice in voices_list
        ]
        
        logger.info(f"Successfully retrieved {len(voices_response)} voices")
        return voices_response
        
    except ElevenLabsError as e:
        # Log error without exposing API key
        logger.error(f"ElevenLabs API error retrieving voices: {e.message} (status: {e.status_code})")
        
        # Handle specific ElevenLabs errors with appropriate HTTP status codes
        if e.status_code == 401:
            raise HTTPException(
                status_code=401, 
                detail="Invalid ElevenLabs API key. Please check your API key and try again."
            )
        elif e.status_code == 429:
            raise HTTPException(
                status_code=429, 
                detail="ElevenLabs API rate limit exceeded. Please wait and try again later."
            )
        elif e.status_code == 503:
            raise HTTPException(
                status_code=503, 
                detail="ElevenLabs service is temporarily unavailable. Please try again later."
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to retrieve voices. Please try again."
            )
            
    except Exception as e:
        # Log unexpected errors without exposing sensitive information
        logger.error(f"Unexpected error retrieving voices: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while retrieving voices. Please try again."
        )

@app.post("/voices/elevenlabs/{voice_id}/sample")
async def get_elevenlabs_voice_sample(voice_id: str, req: VoicesRequest = Body(...)):
    """
    Get voice sample audio for preview
    
    Args:
        voice_id: ID of the voice to preview
        req: VoicesRequest containing API key
        
    Returns:
        StreamingResponse: Audio sample as streaming response
        
    Raises:
        HTTPException: For authentication errors, invalid voice_id, or API failures
    """
    # API key is now required in request
    api_key = req.api_key
    
    # Input validation
    if not api_key or not api_key.strip():
        logger.warning(f"ElevenLabs voice sample request failed: Missing API key for voice {voice_id}")
        raise HTTPException(status_code=400, detail="API key is required")
    
    if not voice_id or not voice_id.strip():
        logger.warning("ElevenLabs voice sample request failed: Missing voice_id")
        raise HTTPException(status_code=400, detail="Voice ID is required")
    
    logger.info(f"Processing ElevenLabs voice sample request for voice: {voice_id}")
    
    try:
        # Get voice sample using ElevenLabs service
        audio_data = elevenlabs_service.get_voice_preview(api_key, voice_id)
        
        # Create streaming response with audio data
        audio_stream = io.BytesIO(audio_data)
        
        logger.info(f"Successfully generated voice sample for voice: {voice_id}")
        
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=voice_sample_{voice_id}.mp3"
            }
        )
        
    except ElevenLabsError as e:
        # Log error without exposing API key
        logger.error(f"ElevenLabs API error getting voice sample for {voice_id}: {e.message} (status: {e.status_code})")
        
        # Handle specific ElevenLabs errors with appropriate HTTP status codes
        if e.status_code == 401:
            raise HTTPException(
                status_code=401, 
                detail="Invalid ElevenLabs API key. Please check your API key and try again."
            )
        elif e.status_code == 404:
            raise HTTPException(
                status_code=404, 
                detail=f"Voice not found: {voice_id}. Please check the voice ID and try again."
            )
        elif e.status_code == 429:
            raise HTTPException(
                status_code=429, 
                detail="ElevenLabs API rate limit exceeded. Please wait and try again later."
            )
        elif e.status_code == 503:
            raise HTTPException(
                status_code=503, 
                detail="ElevenLabs service is temporarily unavailable. Please try again later."
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate voice sample. Please try again."
            )
            
    except Exception as e:
        # Log unexpected errors without exposing sensitive information
        logger.error(f"Unexpected error getting voice sample for {voice_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while generating voice sample. Please try again."
        )

@app.get("/voices/voicevox")
async def get_voicevox_voices():
    """
    Retrieve list of available free Voicevox voices for commercial use
    
    Returns:
        List of available free Voicevox speakers with their details
        
    Raises:
        HTTPException: For connection errors or API failures
    """
    logger.info("Processing Voicevox voices request")
    
    try:
        # Get available free voices using Voicevox service
        speakers_list = voicevox_service.get_speakers()
        
        # Convert to dict format for JSON response
        speakers_response = [
            {
                "speaker_id": speaker.speaker_id,
                "name": speaker.name,
                "english_name": speaker.english_name,
                "style_id": speaker.style_id,
                "style_name": speaker.style_name,
                "english_style_name": speaker.english_style_name,
                "type": speaker.type,
                "is_free": speaker.is_free
            }
            for speaker in speakers_list
        ]
        
        logger.info(f"Successfully retrieved {len(speakers_response)} free Voicevox speakers")
        return speakers_response
        
    except VoicevoxError as e:
        # Log error and handle specific Voicevox errors
        logger.error(f"Voicevox API error retrieving speakers: {e.message} (status: {e.status_code})")
        
        # Handle specific Voicevox errors with appropriate HTTP status codes
        if e.status_code == 503:
            raise HTTPException(
                status_code=503, 
                detail="Cannot connect to Voicevox engine. Please ensure the engine is running and accessible."
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to retrieve Voicevox voices. Please try again."
            )
            
    except Exception as e:
        # Log unexpected errors without exposing sensitive information
        logger.error(f"Unexpected error retrieving Voicevox voices: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while retrieving Voicevox voices. Please try again."
        )

@app.get("/voices/voicevox/{speaker_id}/sample")
async def get_voicevox_voice_sample(speaker_id: int):
    """
    Get voice sample audio for preview using Voicevox
    
    Args:
        speaker_id: ID of the Voicevox speaker to preview
        
    Returns:
        StreamingResponse: Audio sample as streaming response in WAV format
        
    Raises:
        HTTPException: For invalid speaker_id, connection errors, or API failures
    """
    # Input validation
    if speaker_id < 0 or speaker_id > 100:  # Reasonable range for Voicevox speakers
        logger.warning(f"Voicevox voice sample request failed: Invalid speaker_id: {speaker_id}")
        raise HTTPException(status_code=400, detail=f"Speaker ID {speaker_id} is out of valid range (0-100)")
    
    logger.info(f"Processing Voicevox voice sample request for speaker: {speaker_id}")
    
    try:
        # Get voice sample using Voicevox service
        audio_data = voicevox_service.get_speaker_preview(speaker_id)
        
        # Save sample to outputs directory for reference
        sample_filename = f"voicevox_sample_speaker_{speaker_id}.wav"
        sample_path = os.path.join(OUTPUTS_DIR, sample_filename)
        
        # Ensure outputs directory exists
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        
        # Save the sample file
        with open(sample_path, 'wb') as f:
            f.write(audio_data)
        
        logger.info(f"Successfully generated voice sample for speaker: {speaker_id}, saved to: {sample_path}")
        
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=voicevox_sample_{speaker_id}.wav"
            }
        )
        
    except VoicevoxError as e:
        # Log error and handle specific Voicevox errors
        logger.error(f"Voicevox API error getting voice sample for {speaker_id}: {e.message} (status: {e.status_code})")
        
        # Handle specific Voicevox errors with appropriate HTTP status codes
        if e.status_code == 503:
            raise HTTPException(
                status_code=503, 
                detail="Cannot connect to Voicevox engine. Please ensure the engine is running and accessible."
            )
        elif e.status_code == 404 or e.status_code == 422:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid speaker ID: {speaker_id}. Please check the speaker ID and try again."
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate voice sample. Please try again."
            )
            
    except Exception as e:
        # Log unexpected errors without exposing sensitive information
        logger.error(f"Unexpected error getting voice sample for {speaker_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while generating voice sample. Please try again."
        )
        if e.status_code == 404:
            raise HTTPException(
                status_code=404, 
                detail=f"Speaker not found: {speaker_id}. Please check the speaker ID and try again."
            )
        elif e.status_code == 503:
            raise HTTPException(
                status_code=503, 
                detail="Cannot connect to Voicevox engine. Please ensure the engine is running and accessible."
            )
        elif e.status_code == 400 or e.status_code == 422:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid speaker ID: {speaker_id}. Please use a valid speaker ID."
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate voice sample. Please try again."
            )
            
    except Exception as e:
        # Log unexpected errors without exposing sensitive information
        logger.error(f"Unexpected error getting voice sample for speaker {speaker_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while generating voice sample. Please try again."
        )

@app.post("/speed_adjust")
async def speed_adjust(req: SpeedAdjustRequest = Body(...)):
    """
    Adjust the speed of an audio file using various methods
    
    Args:
        req: SpeedAdjustRequest containing input file path, speed rate, method, and options
        
    Returns:
        dict: Output file path and processing details
        
    Raises:
        HTTPException: For file not found, processing errors, or invalid parameters
    """
    logger.info(f"Processing speed adjustment request: {req.input_file} -> {req.speed_rate}x speed")
    
    # Validate input file exists
    if not os.path.exists(req.input_file):
        logger.warning(f"Speed adjust request failed: File not found: {req.input_file}")
        raise HTTPException(status_code=404, detail=f"Input file not found: {req.input_file}")
    
    try:
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(req.input_file))[0]
        method_suffix = "pitch_preserved" if req.preserve_pitch else "pitch_changed"
        output_filename = f"{base_name}_speed_{req.speed_rate}x_{req.method}_{method_suffix}"
        
        if req.method == "librosa":
            # Use librosa for pitch-preserving speed adjustment
            logger.info(f"Using librosa method with preserve_pitch={req.preserve_pitch}")
            
            # Load audio file
            y, sr = librosa.load(req.input_file, sr=None)
            
            if req.preserve_pitch:
                # Time stretching (preserves pitch)
                y_adjusted = librosa.effects.time_stretch(y, rate=req.speed_rate)
            else:
                # Simple resampling (changes pitch)
                y_adjusted = librosa.resample(y, orig_sr=sr, target_sr=int(sr * req.speed_rate))
            
            # Save as WAV
            output_path = f"{output_filename}.wav"
            sf.write(output_path, y_adjusted, sr)
            
        elif req.method == "pydub":
            # Use pydub for speed adjustment
            logger.info(f"Using pydub method with preserve_pitch={req.preserve_pitch}")
            
            audio = AudioSegment.from_file(req.input_file)
            
            if req.preserve_pitch:
                # Use pydub's speedup function (changes pitch)
                from pydub.effects import speedup
                audio_adjusted = speedup(audio, playback_speed=req.speed_rate)
            else:
                # Frame rate adjustment (changes pitch)
                audio_adjusted = audio._spawn(
                    audio.raw_data, 
                    overrides={"frame_rate": int(audio.frame_rate * req.speed_rate)}
                ).set_frame_rate(audio.frame_rate)
            
            # Save as MP3
            output_path = f"{output_filename}.mp3"
            audio_adjusted.export(output_path, format="mp3")
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported method: {req.method}")
        
        # Get output file info
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            
            # Calculate duration
            if req.method == "librosa":
                duration_seconds = len(y_adjusted) / sr
            else:
                duration_seconds = len(audio_adjusted) / 1000.0
            
            logger.info(f"Successfully created speed-adjusted audio: {output_path}")
            
            return {
                "input_file": req.input_file,
                "output_file": output_path,
                "speed_rate": req.speed_rate,
                "method": req.method,
                "preserve_pitch": req.preserve_pitch,
                "duration_seconds": round(duration_seconds, 2),
                "file_size_bytes": file_size
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create output file")
            
    except Exception as e:
        logger.error(f"Speed adjustment failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Speed adjustment failed: {str(e)}"
        )

@app.post("/tts_supertone")
async def tts_supertone(req: SupertoneTTSRequest = Body(...)):
    """
    Convert text to speech using Supertone API
    
    Args:
        req: SupertoneTTSRequest containing segments, tempdir, and voice settings
        
    Returns:
        List of generated audio file information with same format as other TTS endpoints
        
    Raises:
        HTTPException: For validation errors, authentication issues, or processing failures
    """
    # API key is now required in request
    api_key = req.api_key
    
    # Input validation
    if not api_key or not api_key.strip():
        logger.warning("Supertone TTS request failed: Missing API key")
        raise HTTPException(status_code=400, detail="API key is required")
    
    if not req.segments:
        logger.warning("Supertone TTS request failed: No segments provided")
        raise HTTPException(status_code=400, detail="At least one segment is required")
    
    # Validate language code
    if req.language not in ["ko", "en", "ja"]:
        logger.warning(f"Supertone TTS request failed: Invalid language: {req.language}")
        raise HTTPException(status_code=400, detail="Language must be one of: ko, en, ja")
    
    # Validate tempdir to prevent directory traversal
    if not req.tempdir or '..' in req.tempdir or '/' in req.tempdir or '\\' in req.tempdir:
        logger.warning(f"Supertone TTS request failed: Invalid tempdir: {req.tempdir}")
        raise HTTPException(status_code=400, detail="Invalid tempdir format")
    
    # Validate text length for each segment
    for segment in req.segments:
        if not segment.text or not segment.text.strip():
            logger.warning(f"Supertone TTS request failed: Empty text in segment {segment.id}")
            raise HTTPException(status_code=400, detail=f"Segment {segment.id} has empty text")
        
        if len(segment.text) > 300:  # Supertone limit
            logger.warning(f"Supertone TTS request failed: Text too long in segment {segment.id}")
            raise HTTPException(status_code=400, detail=f"Segment {segment.id} text exceeds 300 characters")
    
    logger.info(f"Processing Supertone TTS request for {len(req.segments)} segments in tempdir: {req.tempdir}")
    
    results = []
    for segment in req.segments:
        # Generate output path based on output format
        extension = "wav" if req.output_format == "wav" else "mp3"
        output_path = get_next_output_filename(req.tempdir, extension=extension)
        logger.info(f"Processing segment {segment.id} with {len(segment.text)} characters")
        
        try:
            # Generate audio using Supertone service
            audio_data = supertone_service.text_to_speech(
                api_key=api_key,
                text=segment.text,
                voice_id=req.voice_id,
                language=req.language,
                style=req.style,
                model=req.model,
                pitch_shift=req.pitch_shift,
                pitch_variance=req.pitch_variance,
                speed=req.speed,
                output_format=req.output_format
            )
            
            # Save audio data to file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            # Get duration using pydub (same format as other TTS endpoints)
            if extension == "wav":
                audio = AudioSegment.from_wav(output_path)
            else:
                audio = AudioSegment.from_mp3(output_path)
            duration_ms = len(audio)
            
            results.append({
                "sequence": segment.id,
                "text": segment.text,
                "durationMillis": duration_ms,
                "path": output_path
            })
            
            logger.info(f"Successfully processed segment {segment.id}, duration: {duration_ms}ms")
            
        except SupertoneError as e:
            # Log error without exposing API key
            logger.error(f"Supertone API error for segment {segment.id}: {e.message} (status: {e.status_code})")
            
            # Handle specific Supertone errors with appropriate HTTP status codes
            if e.status_code == 401:
                raise HTTPException(
                    status_code=401, 
                    detail="Invalid Supertone API key. Please check your API key and try again."
                )
            elif e.status_code == 429:
                raise HTTPException(
                    status_code=429, 
                    detail="Supertone API rate limit exceeded. Please wait and try again later."
                )
            elif e.status_code == 400:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid request parameters: {e.message}"
                )
            elif e.status_code == 404:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Voice or style not found: {e.message}"
                )
            elif e.status_code == 503:
                raise HTTPException(
                    status_code=503, 
                    detail="Supertone service is temporarily unavailable. Please try again later."
                )
            else:
                raise HTTPException(
                    status_code=500, 
                    detail="Supertone TTS generation failed. Please try again."
                )
                
        except FileNotFoundError as e:
            logger.error(f"File system error for segment {segment.id}: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to save audio file. Please check server configuration."
            )
            
        except PermissionError as e:
            logger.error(f"Permission error for segment {segment.id}: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="Permission denied when saving audio file. Please check server permissions."
            )
            
        except Exception as e:
            # Log unexpected errors without exposing sensitive information
            logger.error(f"Unexpected error processing segment {segment.id}: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="An unexpected error occurred during TTS generation. Please try again."
            )
    
    logger.info(f"Successfully completed Supertone TTS request for {len(results)} segments")
    return results

@app.get("/voices/supertone")
async def get_supertone_voices():
    """
    Retrieve list of available Supertone voices
    
    Returns:
        List of available Supertone voices with their characteristics
        
    Raises:
        HTTPException: For API failures
    """
    logger.info("Processing Supertone voices request")
    
    try:
        # Get available voices using Supertone service
        voices_list = supertone_service.get_available_voices()
        
        # Convert to dict format for JSON response
        voices_response = [
            {
                "voice_id": voice.voice_id,
                "name": voice.name,
                "gender": voice.gender,
                "age": voice.age,
                "use_case": voice.use_case,
                "supported_languages": voice.supported_languages,
                "available_styles": voice.available_styles
            }
            for voice in voices_list
        ]
        
        logger.info(f"Successfully retrieved {len(voices_response)} Supertone voices")
        return voices_response
        
    except Exception as e:
        # Log unexpected errors without exposing sensitive information
        logger.error(f"Unexpected error retrieving Supertone voices: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while retrieving Supertone voices. Please try again."
        )

@app.post("/voices/supertone/{voice_id}/sample")
async def get_supertone_voice_sample(voice_id: str, req: SupertoneVoiceSampleRequest = Body(...)):
    """
    Get voice sample audio for preview using Supertone
    
    Args:
        voice_id: ID of the Supertone voice to preview
        req: SupertoneVoiceSampleRequest containing API key, language, style, and optional custom text
        
    Returns:
        StreamingResponse: Audio sample as streaming response
        
    Raises:
        HTTPException: For authentication errors, invalid voice_id, or API failures
    """
    # API key is now required in request
    api_key = req.api_key
    
    # Input validation
    if not api_key or not api_key.strip():
        logger.warning(f"Supertone voice sample request failed: Missing API key for voice {voice_id}")
        raise HTTPException(status_code=400, detail="API key is required")
    
    if not voice_id or not voice_id.strip():
        logger.warning("Supertone voice sample request failed: Missing voice_id")
        raise HTTPException(status_code=400, detail="Voice ID is required")
    
    # Validate language
    if req.language not in ["ko", "en", "ja"]:
        logger.warning(f"Supertone voice sample request failed: Invalid language: {req.language}")
        raise HTTPException(status_code=400, detail="Language must be one of: ko, en, ja")
    
    logger.info(f"Processing Supertone voice sample request for voice: {voice_id}, language: {req.language}, style: {req.style}")
    
    try:
        # Get voice sample using Supertone service with custom parameters
        audio_data = supertone_service.get_voice_preview(
            api_key=api_key, 
            voice_id=voice_id, 
            language=req.language, 
            style=req.style,
            custom_text=req.sample_text
        )
        
        logger.info(f"Successfully generated voice sample for voice: {voice_id}")
        
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=supertone_sample_{voice_id}.wav"
            }
        )
        
    except SupertoneError as e:
        # Log error without exposing API key
        logger.error(f"Supertone API error getting voice sample for {voice_id}: {e.message} (status: {e.status_code})")
        
        # Handle specific Supertone errors with appropriate HTTP status codes
        if e.status_code == 401:
            raise HTTPException(
                status_code=401, 
                detail="Invalid Supertone API key. Please check your API key and try again."
            )
        elif e.status_code == 404:
            raise HTTPException(
                status_code=404, 
                detail=f"Voice not found: {voice_id}. Please check the voice ID and try again."
            )
        elif e.status_code == 429:
            raise HTTPException(
                status_code=429, 
                detail="Supertone API rate limit exceeded. Please wait and try again later."
            )
        elif e.status_code == 503:
            raise HTTPException(
                status_code=503, 
                detail="Supertone service is temporarily unavailable. Please try again later."
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate voice sample. Please try again."
            )
            
    except Exception as e:
        # Log unexpected errors without exposing sensitive information
        logger.error(f"Unexpected error getting voice sample for {voice_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while generating voice sample. Please try again."
        )

@app.post("/tts_skt_ax")
async def tts_skt_ax(req: SktAxTTSRequest = Body(...)):
    """
    Convert text to speech using SKT A.X TTS API
    
    Args:
        req: SktAxTTSRequest containing segments, tempdir, voice, and other settings
        
    Returns:
        List of generated audio file information with same format as other TTS endpoints
        
    Raises:
        HTTPException: For validation errors, API failures, or processing errors
    """
    # API key is now required in request
    api_key = req.api_key
    
    # Input validation
    if not api_key or not api_key.strip():
        logger.warning("SKT A.X TTS request failed: Missing API key")
        raise HTTPException(status_code=400, detail="API key is required")
    
    if not req.segments:
        logger.warning("SKT A.X TTS request failed: No segments provided")
        raise HTTPException(status_code=400, detail="At least one segment is required")
    
    if not req.voice or not req.voice.strip():
        logger.warning("SKT A.X TTS request failed: Missing voice")
        raise HTTPException(status_code=400, detail="Voice is required")
    
    # Validate tempdir to prevent directory traversal
    if not req.tempdir or '..' in req.tempdir or '/' in req.tempdir or '\\' in req.tempdir:
        logger.warning(f"SKT A.X TTS request failed: Invalid tempdir: {req.tempdir}")
        raise HTTPException(status_code=400, detail="Invalid tempdir format")
    
    # Validate speed format
    try:
        speed_float = float(req.speed)
        if speed_float < 0.5 or speed_float > 2.0:
            logger.warning(f"SKT A.X TTS request failed: Invalid speed: {req.speed}")
            raise HTTPException(status_code=400, detail="Speed must be between 0.5 and 2.0")
    except ValueError:
        logger.warning(f"SKT A.X TTS request failed: Invalid speed format: {req.speed}")
        raise HTTPException(status_code=400, detail="Speed must be a valid number")
    
    # Validate sample rate
    if req.sr not in [16000, 22050, 44100, 48000]:
        logger.warning(f"SKT A.X TTS request failed: Invalid sample rate: {req.sr}")
        raise HTTPException(status_code=400, detail="Sample rate must be one of: 16000, 22050, 44100, 48000")
    
    # Validate output format
    if req.sformat not in ["wav", "mp3"]:
        logger.warning(f"SKT A.X TTS request failed: Invalid format: {req.sformat}")
        raise HTTPException(status_code=400, detail="Format must be 'wav' or 'mp3'")
    
    # Validate text content and length for each segment
    for segment in req.segments:
        if not segment.text or not segment.text.strip():
            logger.warning(f"SKT A.X TTS request failed: Empty text in segment {segment.id}")
            raise HTTPException(status_code=400, detail=f"Segment {segment.id} has empty text")
        
        if len(segment.text) > 1000:
            logger.warning(f"SKT A.X TTS request failed: Text too long in segment {segment.id}")
            raise HTTPException(status_code=400, detail=f"Segment {segment.id} text exceeds 1000 characters")
    
    logger.info(f"Processing SKT A.X TTS request for {len(req.segments)} segments in tempdir: {req.tempdir}")
    
    results = []
    for segment in req.segments:
        # Generate output path with appropriate extension
        output_path = get_next_output_filename(req.tempdir, extension=req.sformat)
        logger.info(f"Processing segment {segment.id} with {len(segment.text)} characters")
        
        try:
            # Generate audio using SKT A.X service
            audio_data = skt_ax_service.text_to_speech(
                api_key=api_key,
                text=segment.text,
                voice=req.voice,
                speed=req.speed,
                sr=req.sr,
                sformat=req.sformat
            )
            
            # Save audio data to file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            # Get duration using pydub (same format as other TTS endpoints)
            if req.sformat == "wav":
                audio = AudioSegment.from_wav(output_path)
            else:
                audio = AudioSegment.from_mp3(output_path)
            duration_ms = len(audio)
            
            results.append({
                "sequence": segment.id,
                "text": segment.text,
                "durationMillis": duration_ms,
                "path": output_path
            })
            
            logger.info(f"Successfully processed segment {segment.id}, duration: {duration_ms}ms")
            
        except SktAxError as e:
            # Log error without exposing API key
            logger.error(f"SKT A.X API error for segment {segment.id}: {e.message} (status: {e.status_code})")
            
            # Handle specific SKT A.X errors with appropriate HTTP status codes
            if e.status_code == 401:
                raise HTTPException(
                    status_code=401, 
                    detail="Invalid SKT A.X TTS API key. Please check your API key and try again."
                )
            elif e.status_code == 429:
                raise HTTPException(
                    status_code=429, 
                    detail="SKT A.X TTS API rate limit exceeded. Please wait and try again later."
                )
            elif e.status_code == 400:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid request parameters: {e.message}"
                )
            elif e.status_code == 404:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Voice not found: {e.message}"
                )
            elif e.status_code == 503:
                raise HTTPException(
                    status_code=503, 
                    detail="SKT A.X TTS service is temporarily unavailable. Please try again later."
                )
            else:
                raise HTTPException(
                    status_code=500, 
                    detail="SKT A.X TTS generation failed. Please try again."
                )
                
        except FileNotFoundError as e:
            logger.error(f"File system error for segment {segment.id}: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to save audio file. Please check server configuration."
            )
            
        except PermissionError as e:
            logger.error(f"Permission error for segment {segment.id}: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="Permission denied when saving audio file. Please check server permissions."
            )
            
        except Exception as e:
            # Log unexpected errors without exposing sensitive information
            logger.error(f"Unexpected error processing segment {segment.id}: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="An unexpected error occurred during TTS generation. Please try again."
            )
    
    logger.info(f"Successfully completed SKT A.X TTS request for {len(results)} segments")
    return results

@app.post("/voices/skt_ax")
async def get_skt_ax_voices(req: SktAxVoicesRequest = Body(...)):
    """
    Retrieve list of available SKT A.X TTS voices
    
    Args:
        req: SktAxVoicesRequest containing optional API key
        
    Returns:
        List of available voices organized by model
        
    Raises:
        HTTPException: For authentication errors or API failures
    """
    # API key is now required in request
    api_key = req.api_key
    
    # Input validation
    if not api_key or not api_key.strip():
        logger.warning("SKT A.X voices request failed: Missing API key")
        raise HTTPException(status_code=400, detail="API key is required")
    
    # Validate API key
    try:
        skt_ax_service._validate_api_key(api_key)
    except SktAxError as e:
        if e.status_code == 401:
            logger.warning("SKT A.X voices request: Invalid API key provided")
            raise HTTPException(
                status_code=401, 
                detail="Invalid SKT A.X TTS API key. Please check your API key."
            )
    
    logger.info("Processing SKT A.X TTS voices request")
    
    try:
        # Get available voices using SKT A.X service
        voices_list = skt_ax_service.get_available_voices()
        
        # Convert to dict format for JSON response
        voices_response = [
            {
                "voice_name": voice.voice_name,
                "voice_id": voice.voice_id,
                "model": voice.model,
                "gender": voice.gender,
                "age": voice.age,
                "style": voice.style,
                "nickname": voice.nickname,
                "language": voice.language
            }
            for voice in voices_list
        ]
        
        logger.info(f"Successfully retrieved {len(voices_response)} SKT A.X TTS voices")
        return voices_response
        
    except Exception as e:
        # Log unexpected errors without exposing sensitive information
        logger.error(f"Unexpected error retrieving SKT A.X voices: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while retrieving voices. Please try again."
        )

@app.post("/voices/skt_ax/{voice_name}/sample")
async def get_skt_ax_voice_sample(voice_name: str, req: SktAxVoicesRequest = Body(...)):
    """
    Get voice sample audio for preview
    
    Args:
        voice_name: Name of the voice to preview
        req: SktAxVoicesRequest containing API key
        
    Returns:
        StreamingResponse: Audio sample as streaming response
        
    Raises:
        HTTPException: For authentication errors, invalid voice_name, or API failures
    """
    # API key is now required in request
    api_key = req.api_key
    
    # Input validation
    if not api_key or not api_key.strip():
        logger.warning(f"SKT A.X voice sample request failed: Missing API key for voice {voice_name}")
        raise HTTPException(status_code=400, detail="API key is required")
    
    if not voice_name or not voice_name.strip():
        logger.warning("SKT A.X voice sample request failed: Missing voice_name")
        raise HTTPException(status_code=400, detail="Voice name is required")
    
    logger.info(f"Processing SKT A.X voice sample request for voice: {voice_name}")
    
    try:
        # Get voice sample using SKT A.X service
        audio_data = skt_ax_service.get_voice_preview(api_key, voice_name)
        
        logger.info(f"Successfully generated voice sample for voice: {voice_name}")
        
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=skt_ax_sample_{voice_name}.wav"
            }
        )
        
    except SktAxError as e:
        # Log error without exposing API key
        logger.error(f"SKT A.X API error getting voice sample for {voice_name}: {e.message} (status: {e.status_code})")
        
        # Handle specific SKT A.X errors with appropriate HTTP status codes
        if e.status_code == 401:
            raise HTTPException(
                status_code=401, 
                detail="Invalid SKT A.X TTS API key. Please check your API key and try again."
            )
        elif e.status_code == 404:
            raise HTTPException(
                status_code=404, 
                detail=f"Voice not found: {voice_name}. Please check the voice name and try again."
            )
        elif e.status_code == 429:
            raise HTTPException(
                status_code=429, 
                detail="SKT A.X TTS API rate limit exceeded. Please wait and try again later."
            )
        elif e.status_code == 503:
            raise HTTPException(
                status_code=503, 
                detail="SKT A.X TTS service is temporarily unavailable. Please try again later."
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate voice sample. Please try again."
            )
            
    except Exception as e:
        # Log unexpected errors without exposing sensitive information
        logger.error(f"Unexpected error getting voice sample for {voice_name}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while generating voice sample. Please try again."
        )

@app.get("/voices/skt_ax/models")
async def get_skt_ax_models():
    """
    Get list of available SKT A.X TTS models
    
    Returns:
        List of available model names with voice counts
    """
    logger.info("Processing SKT A.X models request")
    
    try:
        models = skt_ax_service.get_available_models()
        
        # Get voice count for each model
        models_info = []
        for model in models:
            voices = skt_ax_service.get_voices_by_model(model)
            models_info.append({
                "model": model,
                "voice_count": len(voices),
                "sample_voices": voices[:5]  # Show first 5 voices as examples
            })
        
        logger.info(f"Successfully retrieved {len(models_info)} SKT A.X models")
        return models_info
        
    except Exception as e:
        logger.error(f"Unexpected error retrieving SKT A.X models: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while retrieving models. Please try again."
        )