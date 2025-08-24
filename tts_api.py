from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
import os
import logging
import io
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()

from schemas import TTSRequest, CombineRequest, SktAxTTSRequest, SktAxVoicesRequest
from utils import validate_audio_files_for_combine, get_combined_output_path, OUTPUTS_DIR
from skt_ax_service import SktAxService, SktAxError
from docker_cleanup_utils import cleanup_tts_session, cleanup_old_combined_files, get_docker_storage_info
from services import GTTSService
from services.skt_ax_tts_service import SktAxTTSService
from api_handlers import TTSHandler, ValidationHandler
from exceptions import handle_validation_error, handle_internal_error

app = FastAPI(title="TTS API", version="1.0.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
gtts_service = GTTSService()
skt_ax_tts_service = SktAxTTSService()
skt_ax_service = SktAxService()

@app.post("/tts_simple")
async def tts_simple(req: TTSRequest = Body(...)):
    """Convert text to speech using Google TTS"""
    try:
        TTSHandler.validate_tts_request(req.segments, req.tempdir)
        logger.info(f"Processing gTTS request for {len(req.segments)} segments")
        
        results = TTSHandler.process_tts_segments(
            gtts_service, req.segments, req.tempdir, language='ko'
        )
        return results
    except Exception as e:
        if hasattr(e, 'status_code'):
            raise e
        raise handle_internal_error(f"gTTS processing failed: {str(e)}")

@app.post("/tts_skt_ax")
async def tts_skt_ax(req: SktAxTTSRequest = Body(...)):
    """Convert text to speech using SKT A.X TTS API"""
    try:
        TTSHandler.validate_tts_request(req.segments, req.tempdir)
        ValidationHandler.validate_api_key(req.api_key, "SKT A.X TTS")
        
        logger.info(f"Processing SKT A.X TTS request for {len(req.segments)} segments")
        
        extension = "wav" if req.sformat == "wav" else "mp3"
        results = TTSHandler.process_tts_segments(
            skt_ax_tts_service, req.segments, req.tempdir,
            api_key=req.api_key, voice=req.voice, speed=req.speed,
            sr=req.sr, sformat=req.sformat, extension=extension
        )
        return results
    except Exception as e:
        if hasattr(e, 'status_code'):
            raise e
        raise handle_internal_error(f"SKT A.X TTS processing failed: {str(e)}")

@app.post("/combine_wav")
async def combine_wav(req: CombineRequest = Body(...)):
    """Combine audio files into a single WAV file and cleanup temp files"""
    logger.info(f"Processing combine_wav request for tempdir: {req.tempdir}")
    
    try:
        files = validate_audio_files_for_combine(req.tempdir)
        logger.info(f"Found {len(files)} audio files to combine")
        
        # Combine all audio files
        combined = AudioSegment.empty()
        for file_path in files:
            if file_path.lower().endswith('.wav'):
                sound = AudioSegment.from_wav(file_path)
            else:
                sound = AudioSegment.from_mp3(file_path)
            combined += sound
        
        # Export combined audio
        combined_path = get_combined_output_path(req.tempdir)
        combined.export(combined_path, format="wav")
        
        # Clean up temporary files
        cleanup_result = cleanup_tts_session(req.tempdir, OUTPUTS_DIR)
        if cleanup_result["success"]:
            logger.info(f"Cleaned up {cleanup_result['deleted_files']} files")
        
        # Auto-cleanup old files
        cleanup_old_combined_files(OUTPUTS_DIR, max_age_minutes=30)
        
        return {
            "combined_path": combined_path,
            "durationMillis": len(combined)
        }
    except Exception as e:
        if hasattr(e, 'status_code'):
            raise e
        raise handle_internal_error(f"Combine operation failed: {str(e)}")

@app.post("/voices/skt_ax")
async def get_skt_ax_voices(req: SktAxVoicesRequest = Body(...)):
    """Get available SKT A.X TTS voices"""
    try:
        ValidationHandler.validate_api_key(req.api_key, "SKT A.X TTS")
        voices_list = skt_ax_service.get_available_voices()
        
        return [
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
    except Exception as e:
        if hasattr(e, 'status_code'):
            raise e
        raise handle_internal_error("Failed to retrieve voices")

@app.post("/voices/skt_ax/{voice_name}/sample")
async def get_skt_ax_voice_sample(voice_name: str, req: SktAxVoicesRequest = Body(...)):
    """Get voice sample audio for preview"""
    try:
        ValidationHandler.validate_api_key(req.api_key, "SKT A.X TTS")
        ValidationHandler.validate_voice_name(voice_name)
        
        audio_data = skt_ax_service.get_voice_preview(req.api_key, voice_name)
        
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename=sample_{voice_name}.wav"}
        )
    except Exception as e:
        if hasattr(e, 'status_code'):
            raise e
        raise handle_internal_error("Failed to generate voice sample")

@app.get("/storage_info")
async def get_storage_info():
    """Get current storage usage information"""
    try:
        return get_docker_storage_info(OUTPUTS_DIR)
    except Exception as e:
        raise handle_internal_error(f"Failed to get storage info: {str(e)}")

@app.post("/cleanup")
async def cleanup_storage():
    """Clean up old files and temporary directories"""
    logger.info("Starting storage cleanup")
    
    try:
        # Clean old combined files
        old_files_result = cleanup_old_combined_files(OUTPUTS_DIR, max_age_minutes=60)
        
        # Clean temp directories
        temp_cleaned = 0
        if os.path.exists(OUTPUTS_DIR):
            for item in os.listdir(OUTPUTS_DIR):
                item_path = os.path.join(OUTPUTS_DIR, item)
                if os.path.isdir(item_path):
                    cleanup_result = cleanup_tts_session(item, OUTPUTS_DIR)
                    if cleanup_result["success"]:
                        temp_cleaned += cleanup_result["deleted_files"]
        
        total_cleaned = old_files_result["deleted_files"] + temp_cleaned
        
        return {
            "success": True,
            "total_files_cleaned": total_cleaned,
            "old_combined_files": old_files_result["deleted_files"],
            "temp_files_cleaned": temp_cleaned
        }
    except Exception as e:
        raise handle_internal_error(f"Cleanup failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)