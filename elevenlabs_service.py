"""
ElevenLabs TTS Service Layer

This module provides a service layer for interacting with the ElevenLabs API,
handling text-to-speech generation, voice management, and error handling.
"""

import logging
from typing import List, Optional, Dict, Any
from elevenlabs import text_to_speech, voices, Voice as ElevenLabsVoice
from schemas import Voice
import requests


class ElevenLabsError(Exception):
    """Custom exception for ElevenLabs API errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ElevenLabsService:
    """Service class for ElevenLabs TTS functionality"""
    
    # Default Korean-compatible voice settings
    DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel - works well for Korean
    DEFAULT_STABILITY = 0.5
    DEFAULT_SIMILARITY_BOOST = 0.8
    DEFAULT_MODEL = "eleven_multilingual_v2"
    
    # Voice name to ID mapping for user-friendly names
    VOICE_NAME_MAPPING = {
        # 한국어 전용 음성
        "hyuk": "ZJCNdZEjYwkOElxugmW2",
        
        # 다국어 지원 음성 (한국어 가능)
        "aria": "9BWtsMINqrJLrRacOk9x",
        "laura": "FGY2WhTYpPnrIDTdsKH5", 
        "river": "SAz9YHcvj6GT2YYXdXww",
        "will": "bIHbv24MWmeRgasZH58o",
        "jessica": "cgSgspJ2msm6clMCkdW9",
        "eric": "cjVigY5qzO86Huf0OWal",
        
        # 기본 음성들 (추가)
        "rachel": "21m00Tcm4TlvDq8ikWAM",
        "sarah": "EXAVITQu4vr4xnSDxMaL",
        "charlie": "IKne3meq5aSn9XLyUdCD",
        "george": "JBFqnCBsd6RMkjVDRZzb",
        "callum": "N2lVS1w4EtoT3dr4eOWO",
        "liam": "TX3LPaxmHKxFdv7VOQHJ",
        "charlotte": "XB0fDUnXU5powFXDhCwa",
        "alice": "Xb7hH8MSUJpSbSDYk0k2",
        "matilda": "XrExE9yKIg1WjnnlVkGX",
        "chris": "iP95p4xoKVk53GoZ742B",
        "brian": "nPczCjzI2devNBz1zQrb",
        "daniel": "onwK4e9ZLuTAKqWW03F9",
        "lily": "pFZP5JQG7iQjIQuC4Bku",
        "bill": "pqHfZKP75CvOlQylNhV4"
    }
    
    def __init__(self):
        """Initialize the ElevenLabs service"""
        self.logger = logging.getLogger(__name__)
    
    def _validate_api_key(self, api_key: str) -> None:
        """
        Validate the provided API key by making a test request
        
        Args:
            api_key: The ElevenLabs API key to validate
            
        Raises:
            ElevenLabsError: If the API key is invalid or authentication fails
        """
        if not api_key or not api_key.strip():
            raise ElevenLabsError("API key is required", 400)
        
        try:
            # Test API key by making a simple voices request
            response = requests.get(
                "https://api.elevenlabs.io/v1/voices",
                headers={"xi-api-key": api_key}
            )
            
            if response.status_code == 401:
                raise ElevenLabsError("Invalid API key", 401)
            elif response.status_code == 429:
                raise ElevenLabsError("Rate limit exceeded", 429)
            elif response.status_code >= 500:
                raise ElevenLabsError("ElevenLabs service unavailable", 503)
            elif not response.ok:
                raise ElevenLabsError(f"API validation failed: {response.text}", response.status_code)
                
        except requests.RequestException as e:
            self.logger.error(f"API key validation failed: {str(e)}")
            raise ElevenLabsError("Failed to connect to ElevenLabs API", 503)
    
    def _resolve_voice_id(self, voice_input: Optional[str]) -> str:
        """
        Resolve voice input to actual ElevenLabs voice ID
        
        Args:
            voice_input: Voice name (e.g., "hyuk", "aria") or actual voice ID
            
        Returns:
            str: Actual ElevenLabs voice ID
        """
        if not voice_input:
            return self.DEFAULT_VOICE_ID
        
        # Check if it's a friendly name first
        voice_lower = voice_input.lower().strip()
        if voice_lower in self.VOICE_NAME_MAPPING:
            resolved_id = self.VOICE_NAME_MAPPING[voice_lower]
            self.logger.info(f"Resolved voice name '{voice_input}' to ID '{resolved_id}'")
            return resolved_id
        
        # If not found in mapping, assume it's already a voice ID
        self.logger.info(f"Using voice ID directly: '{voice_input}'")
        return voice_input

    def text_to_speech(
        self,
        api_key: str,
        text: str,
        voice_id: Optional[str] = None,
        stability: Optional[float] = None,
        similarity_boost: Optional[float] = None,
        style: Optional[float] = None,
        use_speaker_boost: Optional[bool] = None,
        speaking_rate: Optional[float] = None,
        seed: Optional[int] = None,
        output_format: Optional[str] = None
    ) -> bytes:
        """
        Generate speech from text using ElevenLabs API
        
        Args:
            api_key: ElevenLabs API key
            text: Text to convert to speech
            voice_id: Voice ID or friendly name (e.g., "hyuk", "aria", or actual ID)
            stability: Voice stability (0.0-1.0)
            similarity_boost: Voice similarity boost (0.0-1.0)
            
        Returns:
            bytes: Audio data in MP3 format
            
        Raises:
            ElevenLabsError: If TTS generation fails
        """
        # Validate API key first
        self._validate_api_key(api_key)
        
        # Resolve voice name to actual voice ID
        resolved_voice_id = self._resolve_voice_id(voice_id)
        
        # Use defaults for voice settings if not provided
        stability = stability if stability is not None else self.DEFAULT_STABILITY
        similarity_boost = similarity_boost if similarity_boost is not None else self.DEFAULT_SIMILARITY_BOOST
        style = style if style is not None else 0.0  # 기본값: 중성적
        use_speaker_boost = use_speaker_boost if use_speaker_boost is not None else True
        speaking_rate = speaking_rate if speaking_rate is not None else 1.0  # 기본값: 정상 속도
        output_format = output_format if output_format is not None else "mp3_44100_128"  # 기본값: 고품질 MP3
        
        try:
            # Generate audio using ElevenLabs API directly
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{resolved_voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }
            
            # Build voice settings with all parameters
            voice_settings = {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": use_speaker_boost,
                "speaking_rate": speaking_rate
            }
            
            data = {
                "text": text,
                "model_id": self.DEFAULT_MODEL,
                "voice_settings": voice_settings,
                "output_format": output_format
            }
            
            # Add seed if provided for reproducible results
            if seed is not None:
                data["seed"] = seed
            
            response = requests.post(url, json=data, headers=headers)
            
            if not response.ok:
                raise ElevenLabsError(f"TTS API request failed: {response.text}", response.status_code)
            
            return response.content
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Handle specific ElevenLabs errors
            if "unauthorized" in error_msg or "invalid api key" in error_msg:
                raise ElevenLabsError("Invalid API key", 401)
            elif "rate limit" in error_msg or "quota" in error_msg:
                raise ElevenLabsError("Rate limit exceeded", 429)
            elif "voice not found" in error_msg or "invalid voice" in error_msg:
                raise ElevenLabsError(f"Invalid voice ID: {voice_id}", 400)
            elif "service unavailable" in error_msg or "timeout" in error_msg:
                raise ElevenLabsError("ElevenLabs service temporarily unavailable", 503)
            else:
                self.logger.error(f"TTS generation failed: {str(e)}")
                raise ElevenLabsError(f"Text-to-speech generation failed: {str(e)}", 500)
    
    def get_available_voices(self, api_key: str) -> List[Voice]:
        """
        Retrieve list of Korean-compatible voices from ElevenLabs API
        
        Args:
            api_key: ElevenLabs API key
            
        Returns:
            List[Voice]: List of Korean-compatible voices only (for faster response)
            
        Raises:
            ElevenLabsError: If voice retrieval fails
        """
        # Validate API key first
        self._validate_api_key(api_key)
        
        # 한국어 가능한 음성들만 하드코딩으로 빠르게 제공
        korean_voices = [
            # 1. 한국어 전용 음성
            Voice(
                voice_id="ZJCNdZEjYwkOElxugmW2",
                name="HYUK",
                category="professional",
                language="ko"
            ),
            # 2. 다국어 지원 음성들 (한국어 가능)
            Voice(
                voice_id="9BWtsMINqrJLrRacOk9x",
                name="Aria",
                category="premade",
                language="multilingual"
            ),
            Voice(
                voice_id="FGY2WhTYpPnrIDTdsKH5",
                name="Laura",
                category="premade", 
                language="multilingual"
            ),
            Voice(
                voice_id="SAz9YHcvj6GT2YYXdXww",
                name="River",
                category="premade",
                language="multilingual"
            ),
            Voice(
                voice_id="bIHbv24MWmeRgasZH58o",
                name="Will",
                category="premade",
                language="multilingual"
            ),
            Voice(
                voice_id="cgSgspJ2msm6clMCkdW9",
                name="Jessica",
                category="premade",
                language="multilingual"
            ),
            Voice(
                voice_id="cjVigY5qzO86Huf0OWal",
                name="Eric",
                category="premade",
                language="multilingual"
            ),
            Voice(
                voice_id=self.DEFAULT_VOICE_ID,  # Rachel
                name="Rachel",
                category="premade",
                language="multilingual"
            )
        ]
        
        return korean_voices
    
    def get_voice_preview(self, api_key: str, voice_id: str) -> bytes:
        """
        Get voice sample audio for preview
        
        Args:
            api_key: ElevenLabs API key
            voice_id: ID of the voice to preview
            
        Returns:
            bytes: Audio sample data
            
        Raises:
            ElevenLabsError: If voice preview fails
        """
        # Validate API key first
        self._validate_api_key(api_key)
        
        try:
            # Generate a short sample text for preview
            sample_text = "안녕하세요. 이것은 음성 샘플입니다."  # Korean sample text
            
            # Use our own text_to_speech method instead of SDK
            return self.text_to_speech(
                api_key=api_key,
                text=sample_text,
                voice_id=voice_id,
                stability=self.DEFAULT_STABILITY,
                similarity_boost=self.DEFAULT_SIMILARITY_BOOST
            )
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if "unauthorized" in error_msg or "invalid api key" in error_msg:
                raise ElevenLabsError("Invalid API key", 401)
            elif "rate limit" in error_msg or "quota" in error_msg:
                raise ElevenLabsError("Rate limit exceeded", 429)
            elif "voice not found" in error_msg or "invalid voice" in error_msg:
                raise ElevenLabsError(f"Voice not found: {voice_id}", 404)
            elif "service unavailable" in error_msg or "timeout" in error_msg:
                raise ElevenLabsError("ElevenLabs service temporarily unavailable", 503)
            else:
                self.logger.error(f"Voice preview failed: {str(e)}")
                raise ElevenLabsError(f"Failed to generate voice preview: {str(e)}", 500)
    
    def _is_korean_compatible_dict(self, voice_info: Dict[str, Any]) -> bool:
        """
        Check if a voice is compatible with Korean text (for dict format)
        
        Args:
            voice_info: Voice information dictionary from API response
            
        Returns:
            bool: True if voice is Korean-compatible
        """
        voice_id = voice_info.get("voice_id", "")
        category = voice_info.get("category", "")
        labels = voice_info.get("labels", {})
        language = labels.get("language", "")
        
        # 1. 직접 한국어 지원 음성 (최우선)
        if language.lower() == "ko" or "korean" in language.lower():
            return True
        
        # 2. 한국어 전용 음성 ID (HYUK 등)
        korean_native_voices = [
            "ZJCNdZEjYwkOElxugmW2",  # HYUK - 한국어 전용
        ]
        if voice_id in korean_native_voices:
            return True
        
        # 3. 다국어 지원 음성 (multilingual_v2 모델 지원)
        fine_tuning = voice_info.get("fine_tuning", {})
        state = fine_tuning.get("state", {})
        if "eleven_multilingual_v2" in state and state["eleven_multilingual_v2"] == "fine_tuned":
            # 다국어 모델이 fine_tuned 상태인 음성들
            multilingual_voices = [
                "9BWtsMINqrJLrRacOk9x",  # Aria
                "FGY2WhTYpPnrIDTdsKH5",  # Laura  
                "SAz9YHcvj6GT2YYXdXww",  # River
                "bIHbv24MWmeRgasZH58o",  # Will
                "cgSgspJ2msm6clMCkdW9",  # Jessica
                "cjVigY5qzO86Huf0OWal",  # Eric
                self.DEFAULT_VOICE_ID,   # Rachel (기본값)
            ]
            if voice_id in multilingual_voices:
                return True
        
        return False
    
    def _is_korean_compatible(self, voice: ElevenLabsVoice) -> bool:
        """
        Check if a voice is compatible with Korean text
        
        Args:
            voice: ElevenLabs voice object
            
        Returns:
            bool: True if voice is Korean-compatible
        """
        # Check if voice supports multilingual model or is known to work well with Korean
        korean_compatible_voices = [
            self.DEFAULT_VOICE_ID,  # Rachel
            "EXAVITQu4vr4xnSDxMaL",  # Bella
            "VR6AewLTigWG4xSOukaG",  # Arnold
            "pNInz6obpgDQGcFmaJgB",  # Adam
        ]
        
        # Check by voice ID
        if voice.voice_id in korean_compatible_voices:
            return True
        
        # Check by category (premade voices generally work better with multilingual)
        if hasattr(voice, 'category') and voice.category == "premade":
            return True
        
        # Check by language if available
        if hasattr(voice, 'language'):
            language = getattr(voice, 'language', '').lower()
            if 'korean' in language or 'ko' in language or 'multilingual' in language:
                return True
        
        return False
    
    def get_default_voice_id(self) -> str:
        """
        Get the default Korean-compatible voice ID
        
        Returns:
            str: Default voice ID
        """
        return self.DEFAULT_VOICE_ID