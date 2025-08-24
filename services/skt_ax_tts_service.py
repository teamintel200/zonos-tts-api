"""
SKT A.X TTS service implementation
"""

import logging
from typing import Dict, Any
from pydub import AudioSegment
from .base_tts_service import BaseTTSService
from schemas import Segment
from skt_ax_service import SktAxService, SktAxError
from exceptions import TTSError, handle_auth_error, handle_not_found_error, handle_rate_limit_error, handle_service_error

logger = logging.getLogger(__name__)

class SktAxTTSService(BaseTTSService):
    """SKT A.X TTS service implementation"""
    
    def __init__(self):
        self.skt_ax_service = SktAxService()
    
    def validate_segment(self, segment: Segment) -> None:
        """Validate segment for SKT A.X TTS requirements"""
        super().validate_segment(segment)
        
        if len(segment.text) > 1000:
            raise ValueError(f"Segment {segment.id} text exceeds 1000 characters")
    
    def text_to_speech(self, segment: Segment, output_path: str, **kwargs) -> Dict[str, Any]:
        """
        Convert text to speech using SKT A.X TTS
        
        Args:
            segment: Text segment to convert
            output_path: Path to save audio file
            **kwargs: api_key, voice, speed, sr, sformat
            
        Returns:
            Dict containing sequence, text, durationMillis, path
        """
        self.validate_segment(segment)
        
        # Extract required parameters
        api_key = kwargs.get('api_key')
        voice = kwargs.get('voice', 'default')
        speed = kwargs.get('speed', 1.0)
        sr = kwargs.get('sr', 22050)
        sformat = kwargs.get('sformat', 'wav')
        
        if not api_key:
            raise TTSError("API key is required for SKT A.X TTS", 400)
        
        try:
            logger.info(f"Processing SKT A.X segment {segment.id}: {len(segment.text)} characters")
            
            # Generate audio using SKT A.X service
            audio_data = self.skt_ax_service.text_to_speech(
                api_key=api_key,
                text=segment.text,
                voice=voice,
                speed=speed,
                sr=sr,
                sformat=sformat
            )
            
            # Save audio data to file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            # Get duration using pydub
            extension = self.get_file_extension(sformat)
            if extension == "wav":
                audio = AudioSegment.from_wav(output_path)
            else:
                audio = AudioSegment.from_mp3(output_path)
            duration_ms = len(audio)
            
            logger.info(f"Successfully processed SKT A.X segment {segment.id}, duration: {duration_ms}ms")
            
            return {
                "sequence": segment.id,
                "text": segment.text,
                "durationMillis": duration_ms,
                "path": output_path
            }
            
        except SktAxError as e:
            logger.error(f"SKT A.X API error for segment {segment.id}: {e.message} (status: {e.status_code})")
            
            # Map SKT A.X errors to appropriate HTTP responses
            if e.status_code == 401:
                raise TTSError("Invalid SKT A.X TTS API key. Please check your API key and try again.", 401)
            elif e.status_code == 400:
                raise TTSError(f"Invalid request parameters: {e.message}", 400)
            elif e.status_code == 404:
                raise TTSError(f"Voice not found: {voice}. Please check the voice name and try again.", 404)
            elif e.status_code == 429:
                raise TTSError("SKT A.X TTS API rate limit exceeded. Please wait and try again later.", 429)
            elif e.status_code == 503:
                raise TTSError("SKT A.X TTS service is temporarily unavailable. Please try again later.", 503)
            else:
                raise TTSError("SKT A.X TTS generation failed. Please try again.")
                
        except Exception as e:
            logger.error(f"Unexpected error processing SKT A.X segment {segment.id}: {str(e)}")
            raise TTSError(f"An unexpected error occurred during TTS generation: {str(e)}")
    
    def get_file_extension(self, sformat: str = "wav") -> str:
        """Get the file extension based on format"""
        return "wav" if sformat == "wav" else "mp3"