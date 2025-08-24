"""
TTS service factory for creating appropriate TTS service instances
"""

from typing import Union
from .base_tts_service import BaseTTSService
from .gtts_service import GTTSService
from .skt_ax_tts_service import SktAxTTSService

class TTSFactory:
    """Factory for creating TTS service instances"""
    
    @staticmethod
    def create_gtts_service(language: str = 'ko') -> GTTSService:
        """Create Google TTS service instance"""
        return GTTSService(language=language)
    
    @staticmethod
    def create_skt_ax_service() -> SktAxTTSService:
        """Create SKT A.X TTS service instance"""
        return SktAxTTSService()
    
    @staticmethod
    def get_service(service_type: str) -> BaseTTSService:
        """
        Get TTS service by type
        
        Args:
            service_type: Type of TTS service ('gtts' or 'skt_ax')
            
        Returns:
            BaseTTSService instance
            
        Raises:
            ValueError: If service_type is not supported
        """
        if service_type == 'gtts':
            return TTSFactory.create_gtts_service()
        elif service_type == 'skt_ax':
            return TTSFactory.create_skt_ax_service()
        else:
            raise ValueError(f"Unsupported TTS service type: {service_type}")