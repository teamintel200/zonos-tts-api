"""
Base TTS service interface
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from schemas import Segment

class BaseTTSService(ABC):
    """Base class for TTS services"""
    
    @abstractmethod
    def text_to_speech(self, segment: Segment, output_path: str, **kwargs) -> Dict[str, Any]:
        """
        Convert text to speech and save to output path
        
        Args:
            segment: Text segment to convert
            output_path: Path to save audio file
            **kwargs: Additional parameters specific to TTS service
            
        Returns:
            Dict containing sequence, text, durationMillis, path
        """
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get the default file extension for this TTS service"""
        pass
    
    def validate_segment(self, segment: Segment) -> None:
        """Validate segment data - can be overridden by subclasses"""
        if not segment.text or not segment.text.strip():
            raise ValueError(f"Segment {segment.id} has empty text")