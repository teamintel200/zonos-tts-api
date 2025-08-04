"""
SKT A.X TTS Service Layer

This module provides a service layer for interacting with the SKT A.X TTS API,
handling text-to-speech generation, voice management, and error handling.
"""

import logging
import json
import requests
from typing import List, Optional, Dict, Any
from schemas import SktAxVoice


class SktAxError(Exception):
    """Custom exception for SKT A.X TTS API errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class SktAxService:
    """Service class for SKT A.X TTS functionality"""
    
    BASE_URL = "https://apis.openapi.sk.com/axtts/tts"
    DEFAULT_SPEED = "1.0"
    DEFAULT_SR = 22050
    DEFAULT_FORMAT = "wav"
    
    # Voice to model mapping based on the markdown file
    VOICE_MODEL_MAPPING = {
        # axtts-2-6 voices
        "sophie": "axtts-2-6",
        "jemma": "axtts-2-6", 
        "aria": "axtts-2-6",
        "aria_dj": "axtts-2-6",
        "jiyoung": "axtts-2-6",
        "juwon": "axtts-2-6",
        "jihun": "axtts-2-6",
        "hamin": "axtts-2-6",
        "daeho": "axtts-2-6",
        "tiffany": "axtts-2-6",
        "bell": "axtts-2-6",
        "oliver": "axtts-2-6",
        "scarlett": "axtts-2-6",
        "natalie": "axtts-2-6",
        "lucy": "axtts-2-6",
        "andy": "axtts-2-6",
        "david": "axtts-2-6",
        "matthew": "axtts-2-6",
        "bitna": "axtts-2-6",
        "albert": "axtts-2-6",
        "polar": "axtts-2-6",
        "lily": "axtts-2-6",
        "daisy": "axtts-2-6",
        
        # axtts-2-1 voices (some overlap with 2-6, using 2-1 for specific variants)
        "aria_call": "axtts-2-1",
        "aria_chitchat": "axtts-2-1",
        "seohyun": "axtts-2-1",
        "hayun": "axtts-2-1",
        "jian": "axtts-2-1",
        "seojun": "axtts-2-1",
        "jiho": "axtts-2-1",
        "doyun": "axtts-2-1",
        "olivia": "axtts-2-1",
        "emma": "axtts-2-1",
        "andrew": "axtts-2-1",
        "jay": "axtts-2-1",
        "haru": "axtts-2-1",
        "kody": "axtts-2-1",
        
        # axtts-2-1-dialect voices
        "fjja": "axtts-2-1-dialect",  # jeonga
        "fljh": "axtts-2-1-dialect",  # juha
        "frjh": "axtts-2-1-dialect",  # jihye
        "mkdd": "axtts-2-1-dialect",  # dongjun
        "mksh": "axtts-2-1-dialect",  # seongho
        "mkws": "axtts-2-1-dialect",  # wonseok
        
        # axtts-2-6-ainews voices
        "msth0": "axtts-2-6-ainews",  # taehyun
        "fysy0": "axtts-2-6-ainews",  # seoyun
        "mswj0": "axtts-2-6-ainews",  # wonjun
        "fkhk0": "axtts-2-6-ainews",  # hyunkyung
        "mkjh0": "axtts-2-6-ainews",  # jaeho
        "fpje0": "axtts-2-6-ainews",  # juhee
    }
    
    # Voice information from the markdown file
    VOICE_INFO = {
        # axtts-2-6 voices
        "sophie": {"voice_id": "00003", "gender": "female", "age": "adult", "style": "general, kind"},
        "jemma": {"voice_id": "00411", "gender": "female", "age": "adult", "style": "general"},
        "aria": {"voice_id": "00422", "gender": "female", "age": "adult", "style": "general, kind, callcenter"},
        "aria_dj": {"voice_id": "00022", "gender": "female", "age": "adult", "style": "dj"},
        "jiyoung": {"voice_id": "00001", "gender": "female", "age": "adult", "style": "general"},
        "juwon": {"voice_id": "00019", "gender": "male", "age": "adult", "style": "general"},
        "jihun": {"voice_id": "00016", "gender": "male", "age": "adult", "style": "general"},
        "hamin": {"voice_id": "00012", "gender": "male", "age": "adult", "style": "general"},
        "daeho": {"voice_id": "00011", "gender": "male", "age": "adult", "style": "general"},
        "tiffany": {"voice_id": "00023", "gender": "female", "age": "adult", "style": "callcenter"},
        "bell": {"voice_id": "00021", "gender": "female", "age": "adult", "style": "news"},
        "oliver": {"voice_id": "00020", "gender": "male", "age": "adult", "style": "general, callcenter"},
        "scarlett": {"voice_id": "00008", "gender": "female", "age": "adult", "style": "general"},
        "natalie": {"voice_id": "00009", "gender": "female", "age": "adult", "style": "general"},
        "lucy": {"voice_id": "00413", "gender": "female", "age": "adult", "style": "general"},
        "andy": {"voice_id": "00014", "gender": "male", "age": "adult", "style": "general"},
        "david": {"voice_id": "00018", "gender": "male", "age": "adult", "style": "general"},
        "matthew": {"voice_id": "00017", "gender": "male", "age": "adult", "style": "general"},
        "bitna": {"voice_id": "00408", "gender": "female", "age": "adult", "style": "friendly"},
        "albert": {"voice_id": "00412", "gender": "male", "age": "child", "style": "character"},
        "polar": {"voice_id": "00414", "gender": "female", "age": "child", "style": "character"},
        "lily": {"voice_id": "00415", "gender": "female", "age": "child", "style": "character"},
        "daisy": {"voice_id": "00416", "gender": "female", "age": "child", "style": "character"},
        
        # axtts-2-1 specific voices
        "aria_call": {"voice_id": "00024", "gender": "female", "age": "adult", "style": "callcenter"},
        "aria_chitchat": {"voice_id": "00025", "gender": "female", "age": "adult", "style": "bright"},
        "seohyun": {"voice_id": "00018", "gender": "female", "age": "child", "style": "general"},
        "hayun": {"voice_id": "00004", "gender": "female", "age": "child", "style": "general"},
        "jian": {"voice_id": "00011", "gender": "female", "age": "child", "style": "general"},
        "seojun": {"voice_id": "00048", "gender": "male", "age": "child", "style": "general"},
        "jiho": {"voice_id": "00052", "gender": "male", "age": "child", "style": "general"},
        "doyun": {"voice_id": "00049", "gender": "male", "age": "child", "style": "general"},
        "olivia": {"voice_id": "00013", "gender": "female", "age": "adult", "style": "general"},
        "emma": {"voice_id": "00036", "gender": "female", "age": "adult", "style": "general"},
        "andrew": {"voice_id": "00051", "gender": "male", "age": "adult", "style": "general"},
        "jay": {"voice_id": "00035", "gender": "female", "age": "adult", "style": "friendly"},
        "haru": {"voice_id": "00050", "gender": "male", "age": "adult", "style": "friendly"},
        "kody": {"voice_id": "00033", "gender": "female", "age": "child", "style": "character"},
        
        # axtts-2-1-dialect voices
        "fjja": {"voice_id": "00000", "gender": "female", "age": "adult", "style": "jeollado", "nickname": "jeonga"},
        "fljh": {"voice_id": "00001", "gender": "female", "age": "adult", "style": "chungcheongdo", "nickname": "juha"},
        "frjh": {"voice_id": "00002", "gender": "female", "age": "adult", "style": "gyeongsangdo", "nickname": "jihye"},
        "mkdd": {"voice_id": "00003", "gender": "male", "age": "adult", "style": "gyeongsangdo", "nickname": "dongjun"},
        "mksh": {"voice_id": "00004", "gender": "male", "age": "adult", "style": "jeollado", "nickname": "seongho"},
        "mkws": {"voice_id": "00005", "gender": "male", "age": "adult", "style": "chungcheongdo", "nickname": "wonseok"},
        
        # axtts-2-6-ainews voices
        "msth0": {"voice_id": "00410", "gender": "male", "age": "adult", "style": "news reporter", "nickname": "taehyun"},
        "fysy0": {"voice_id": "00409", "gender": "female", "age": "adult", "style": "news reporter", "nickname": "seoyun"},
        "mswj0": {"voice_id": "00018", "gender": "male", "age": "adult", "style": "news reporter", "nickname": "wonjun"},
        "fkhk0": {"voice_id": "00413", "gender": "female", "age": "adult", "style": "news reporter", "nickname": "hyunkyung"},
        "mkjh0": {"voice_id": "00014", "gender": "male", "age": "adult", "style": "news reporter", "nickname": "jaeho"},
        "fpje0": {"voice_id": "00009", "gender": "female", "age": "adult", "style": "news reporter", "nickname": "juhee"},
    }
    
    def __init__(self):
        """Initialize the SKT A.X TTS service"""
        self.logger = logging.getLogger(__name__)
    
    def _validate_api_key(self, api_key: str) -> None:
        """
        Validate the provided API key
        
        Args:
            api_key: The SKT A.X TTS API key to validate
            
        Raises:
            SktAxError: If the API key is invalid
        """
        if not api_key or not api_key.strip():
            raise SktAxError("API key is required", 400)
        
        # Basic format validation
        if len(api_key.strip()) < 10:
            raise SktAxError("Invalid API key format", 401)
    
    def _get_model_for_voice(self, voice: str) -> str:
        """
        Get the appropriate model for the given voice
        
        Args:
            voice: Voice name
            
        Returns:
            str: Model name
            
        Raises:
            SktAxError: If voice is not found
        """
        if voice not in self.VOICE_MODEL_MAPPING:
            raise SktAxError(f"Voice '{voice}' not found", 404)
        
        return self.VOICE_MODEL_MAPPING[voice]
    
    def _validate_voice(self, voice: str) -> None:
        """
        Validate voice name
        
        Args:
            voice: Voice name to validate
            
        Raises:
            SktAxError: If voice is invalid
        """
        if voice not in self.VOICE_INFO:
            available_voices = list(self.VOICE_INFO.keys())
            raise SktAxError(
                f"Voice '{voice}' not available. Available voices: {', '.join(available_voices[:10])}...",
                400
            )

    def text_to_speech(
        self,
        api_key: str,
        text: str,
        voice: str,
        speed: Optional[str] = None,
        sr: Optional[int] = None,
        sformat: Optional[str] = None
    ) -> bytes:
        """
        Generate speech from text using SKT A.X TTS API
        
        Args:
            api_key: SKT A.X TTS API key
            text: Text to convert to speech
            voice: Voice name (automatically determines model)
            speed: Speech speed (default: "1.0")
            sr: Sample rate (default: 22050)
            sformat: Output format (default: "wav")
            
        Returns:
            bytes: Audio data
            
        Raises:
            SktAxError: If TTS generation fails
        """
        # Validate inputs
        self._validate_api_key(api_key)
        self._validate_voice(voice)
        
        if not text or not text.strip():
            raise SktAxError("Text cannot be empty", 400)
        
        if len(text) > 1000:  # Reasonable limit
            raise SktAxError("Text exceeds maximum length of 1000 characters", 400)
        
        # Use defaults
        speed = speed or self.DEFAULT_SPEED
        sr = sr or self.DEFAULT_SR
        sformat = sformat or self.DEFAULT_FORMAT
        
        # Get model for voice
        model = self._get_model_for_voice(voice)
        
        try:
            # Build API request
            payload = {
                "model": model,
                "voice": voice,
                "text": text,
                "speed": speed,
                "sr": sr,
                "sformat": sformat
            }
            
            headers = {
                "accept": f"audio/{sformat}",
                "content-type": "application/json",
                "appKey": api_key
            }
            
            self.logger.info(f"SKT A.X TTS request: model={model}, voice={voice}, speed={speed}")
            
            response = requests.post(self.BASE_URL, json=payload, headers=headers, timeout=30)
            
            # Handle API errors
            if response.status_code == 401:
                raise SktAxError("Invalid SKT A.X TTS API key", 401)
            elif response.status_code == 400:
                raise SktAxError(f"Bad request: {response.text}", 400)
            elif response.status_code == 404:
                raise SktAxError(f"Voice or model not found: {voice}", 404)
            elif response.status_code == 429:
                raise SktAxError("Rate limit exceeded", 429)
            elif response.status_code >= 500:
                raise SktAxError("SKT A.X TTS service temporarily unavailable", 503)
            elif not response.ok:
                raise SktAxError(f"API request failed: {response.text}", response.status_code)
            
            # Check if response is audio data
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('audio/'):
                # Try to parse error message from response
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Unknown error')
                    raise SktAxError(f"API error: {error_msg}", response.status_code)
                except:
                    raise SktAxError(f"Unexpected response format: {response.text[:200]}", 500)
            
            self.logger.info(f"Successfully generated SKT A.X TTS audio, size: {len(response.content)} bytes")
            return response.content
            
        except requests.RequestException as e:
            self.logger.error(f"SKT A.X TTS API request failed: {str(e)}")
            raise SktAxError("Failed to connect to SKT A.X TTS API", 503)
        except SktAxError:
            # Re-raise SktAxError as-is
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in SKT A.X TTS: {str(e)}")
            raise SktAxError(f"TTS generation failed: {str(e)}", 500)
    
    def get_available_voices(self) -> List[SktAxVoice]:
        """
        Retrieve list of available SKT A.X TTS voices
        
        Returns:
            List[SktAxVoice]: List of available voices
        """
        voices = []
        
        for voice_name, voice_info in self.VOICE_INFO.items():
            model = self.VOICE_MODEL_MAPPING[voice_name]
            
            voices.append(SktAxVoice(
                voice_name=voice_name,
                voice_id=voice_info["voice_id"],
                model=model,
                gender=voice_info["gender"],
                age=voice_info["age"],
                style=voice_info["style"],
                nickname=voice_info.get("nickname", voice_name),
                language="ko-KR"
            ))
        
        # Sort by model and then by voice name for better organization
        voices.sort(key=lambda x: (x.model, x.voice_name))
        
        self.logger.info(f"Retrieved {len(voices)} SKT A.X TTS voices")
        return voices
    
    def get_voice_preview(self, api_key: str, voice: str, speed: str = "1.0") -> bytes:
        """
        Get voice sample audio for preview
        
        Args:
            api_key: SKT A.X TTS API key
            voice: Voice name to preview
            speed: Speech speed for preview
            
        Returns:
            bytes: Audio sample data
            
        Raises:
            SktAxError: If voice preview fails
        """
        # Use a standard Korean sample text
        sample_text = "안녕하세요. SKT A.X TTS 음성 샘플입니다. 반갑습니다."
        
        try:
            return self.text_to_speech(
                api_key=api_key,
                text=sample_text,
                voice=voice,
                speed=speed
            )
        except Exception as e:
            self.logger.error(f"Voice preview failed for {voice}: {str(e)}")
            raise SktAxError(f"Failed to generate voice preview: {str(e)}", 500)
    
    def get_voices_by_model(self, model: str) -> List[str]:
        """
        Get list of voices available for a specific model
        
        Args:
            model: Model name
            
        Returns:
            List[str]: List of voice names for the model
        """
        return [voice for voice, voice_model in self.VOICE_MODEL_MAPPING.items() if voice_model == model]
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models
        
        Returns:
            List[str]: List of model names
        """
        return list(set(self.VOICE_MODEL_MAPPING.values()))