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

from schemas import Segment, TTSRequest, CombineRequest, ElevenLabsTTSRequest, VoicesRequest, SpeedAdjustRequest
from utils import get_next_output_filename, validate_audio_files_for_combine, get_combined_output_path, OUTPUTS_DIR
from elevenlabs_service import ElevenLabsService, ElevenLabsError
import librosa
import soundfile as sf
import tempfile

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ElevenLabs service
elevenlabs_service = ElevenLabsService()

# Get default API key from environment
DEFAULT_ELEVENLABS_API_KEY = os.getenv("ELEVEN_LABS_APIKEY")

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
    # Use environment API key if not provided in request
    api_key = req.api_key or DEFAULT_ELEVENLABS_API_KEY
    
    # Input validation
    if not api_key or not api_key.strip():
        logger.warning("ElevenLabs TTS request failed: Missing API key")
        raise HTTPException(status_code=400, detail="API key is required (provide in request or set ELEVEN_LABS_APIKEY environment variable)")
    
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
        
        # Combine all audio files (works with mixed gTTS/ElevenLabs files)
        combined = AudioSegment.empty()
        for i, file_path in enumerate(files, 1):
            try:
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
    # Use environment API key if not provided in request
    api_key = req.api_key or DEFAULT_ELEVENLABS_API_KEY
    
    # Input validation
    if not api_key or not api_key.strip():
        logger.warning("ElevenLabs voices request failed: Missing API key")
        raise HTTPException(status_code=400, detail="API key is required (provide in request or set ELEVEN_LABS_APIKEY environment variable)")
    
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
    # Use environment API key if not provided in request
    api_key = req.api_key or DEFAULT_ELEVENLABS_API_KEY
    
    # Input validation
    if not api_key or not api_key.strip():
        logger.warning(f"ElevenLabs voice sample request failed: Missing API key for voice {voice_id}")
        raise HTTPException(status_code=400, detail="API key is required (provide in request or set ELEVEN_LABS_APIKEY environment variable)")
    
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

