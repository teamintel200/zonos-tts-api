"""
Google TTS service implementation
"""

import logging
from typing import Dict, Any
from gtts import gTTS
from pydub import AudioSegment
from .base_tts_service import BaseTTSService
from schemas import Segment
from exceptions import TTSError

logger = logging.getLogger(__name__)

class GTTSService(BaseTTSService):
    """Google TTS service implementation"""
    
    def __init__(self, language: str = 'ko'):
        self.language = language
    
    def text_to_speech(self, segment: Segment, output_path: str, **kwargs) -> Dict[str, Any]:
        """
        Convert text to speech using Google TTS
        
        Args:
            segment: Text segment to convert
            output_path: Path to save MP3 file
            **kwargs: Additional parameters (language override)
            
        Returns:
            Dict containing sequence, text, durationMillis, path
        """
        self.validate_segment(segment)
        
        language = kwargs.get('language', self.language)
        
        try:
            logger.info(f"Processing gTTS segment {segment.id}: {len(segment.text)} characters")
            
            tts = gTTS(text=segment.text, lang=language)
            tts.save(output_path)
            
            # Get duration using pydub
            audio = AudioSegment.from_mp3(output_path)
            duration_ms = len(audio)
            
            logger.info(f"Successfully processed gTTS segment {segment.id}, duration: {duration_ms}ms")
            
            return {
                "sequence": segment.id,
                "text": segment.text,
                "durationMillis": duration_ms,
                "path": output_path
            }
            
        except Exception as e:
            logger.error(f"gTTS processing failed for segment {segment.id}: {str(e)}")
            raise TTSError(f"gTTS generation failed: {str(e)}")
    
    def get_file_extension(self) -> str:
        """Get the default file extension for gTTS"""
        return "mp3"