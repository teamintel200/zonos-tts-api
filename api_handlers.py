"""
Common API handlers and utilities
"""

import logging
from typing import List, Dict, Any
from fastapi import HTTPException
from schemas import Segment, TTSRequest, SktAxTTSRequest
from services.base_tts_service import BaseTTSService
from utils import get_next_output_filename
from exceptions import handle_validation_error, handle_internal_error, handle_file_error

logger = logging.getLogger(__name__)

class TTSHandler:
    """Common handler for TTS operations"""
    
    @staticmethod
    def validate_tts_request(segments: List[Segment], tempdir: str) -> None:
        """Validate TTS request parameters"""
        if not segments:
            raise handle_validation_error("At least one segment is required")
        
        if not tempdir or '..' in tempdir or '/' in tempdir or '\\' in tempdir:
            raise handle_validation_error(f"Invalid tempdir format: {tempdir}")
    
    @staticmethod
    def process_tts_segments(
        tts_service: BaseTTSService, 
        segments: List[Segment], 
        tempdir: str,
        **service_kwargs
    ) -> List[Dict[str, Any]]:
        """
        Process multiple TTS segments using the provided service
        
        Args:
            tts_service: TTS service instance
            segments: List of text segments to process
            tempdir: Temporary directory name
            **service_kwargs: Additional parameters for TTS service
            
        Returns:
            List of TTS results
        """
        results = []
        extension = service_kwargs.get('extension', tts_service.get_file_extension())
        
        for segment in segments:
            output_path = get_next_output_filename(tempdir, extension=extension)
            logger.info(f"Processing segment {segment.id} -> {output_path}")
            
            try:
                result = tts_service.text_to_speech(segment, output_path, **service_kwargs)
                results.append(result)
                
            except Exception as e:
                if hasattr(e, 'status_code'):
                    # Convert TTSError to HTTPException
                    from exceptions import TTSError
                    if isinstance(e, TTSError):
                        raise HTTPException(status_code=e.status_code, detail=e.message)
                    raise e
                else:
                    raise handle_file_error(e, "TTS generation")
        
        logger.info(f"Successfully completed TTS processing for {len(results)} segments")
        return results

class ValidationHandler:
    """Common validation utilities"""
    
    @staticmethod
    def validate_api_key(api_key: str, service_name: str) -> None:
        """Validate API key parameter"""
        if not api_key or not api_key.strip():
            raise handle_validation_error(f"{service_name} API key is required")
    
    @staticmethod
    def validate_voice_name(voice_name: str) -> None:
        """Validate voice name parameter"""
        if not voice_name or not voice_name.strip():
            raise handle_validation_error("Voice name is required")