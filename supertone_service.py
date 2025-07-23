"""
Supertone TTS Service Layer

This module provides a service layer for interacting with the Supertone API,
handling text-to-speech generation, voice management, and error handling.
"""

import logging
import json
import os
from typing import List, Optional, Dict, Any
import requests
from schemas import SupertoneVoice


class SupertoneError(Exception):
    """Custom exception for Supertone API errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class SupertoneService:
    """Service class for Supertone TTS functionality"""
    
    BASE_URL = "https://supertoneapi.com"
    DEFAULT_MODEL = "sona_speech_1"
    DEFAULT_LANGUAGE = "ko"
    DEFAULT_STYLE = "neutral"
    
    # Sample voice mapping (would normally be retrieved from API)
    SAMPLE_VOICES = {
        "sona_korean_female": {
            "voice_id": "sona_korean_female",
            "name": "소나 (한국어 여성)",
            "gender": "female",
            "age": "adult",
            "use_case": "general",
            "supported_languages": ["ko"],
            "available_styles": ["neutral", "happy", "sad", "excited"]
        },
        "aria_multilingual": {
            "voice_id": "aria_multilingual",
            "name": "아리아 (다국어)",
            "gender": "female", 
            "age": "adult",
            "use_case": "professional",
            "supported_languages": ["ko", "en", "ja"],
            "available_styles": ["neutral", "professional", "friendly"]
        },
        "jun_korean_male": {
            "voice_id": "jun_korean_male",
            "name": "준 (한국어 남성)",
            "gender": "male",
            "age": "adult",
            "use_case": "narrative",
            "supported_languages": ["ko"],
            "available_styles": ["neutral", "serious", "warm"]
        }
    }
    
    def __init__(self):
        """Initialize the Supertone service"""
        self.logger = logging.getLogger(__name__)
        self.voice_data = {}
        self._load_voice_data()
    
    def _load_voice_data(self):
        """Load voice data from supertone_type.json file"""
        try:
            # Get the current directory and look for the sample file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(current_dir, "sample", "supertone_type.json")
            
            if not os.path.exists(json_path):
                self.logger.warning(f"Voice data file not found at {json_path}, using sample data")
                return
                
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Process and filter voice data for Korean-compatible voices
            self.voice_data = {}
            for item in data.get("items", []):
                voice_id = item.get("voice_id")
                languages = item.get("language", [])
                
                # Only include voices that support Korean
                if "ko" in languages and voice_id:
                    # Extract available styles
                    styles = item.get("styles", ["neutral"])
                    
                    self.voice_data[voice_id] = {
                        "voice_id": voice_id,
                        "name": item.get("name", "Unknown"),
                        "gender": item.get("gender", "unknown"),
                        "age": item.get("age", "unknown"),
                        "use_case": item.get("use_case", "general"),
                        "supported_languages": languages,
                        "available_styles": styles,
                        "description": item.get("description", ""),
                        "models": item.get("models", [self.DEFAULT_MODEL]),
                        "samples": item.get("samples", [])
                    }
            
            self.logger.info(f"Loaded {len(self.voice_data)} Korean-compatible voices from supertone_type.json")
            
        except Exception as e:
            self.logger.error(f"Failed to load voice data: {str(e)}")
            # Fall back to sample voices if file loading fails
            self.voice_data = self.SAMPLE_VOICES.copy()
    
    def _validate_api_key(self, api_key: str) -> None:
        """
        Validate the provided API key by making a test request
        
        Args:
            api_key: The Supertone API key to validate
            
        Raises:
            SupertoneError: If the API key is invalid or authentication fails
        """
        if not api_key or not api_key.strip():
            raise SupertoneError("API key is required", 400)
        
        try:
            # Test API key with a simple voices request (if available)
            # For now, just check if key format is valid
            if len(api_key.strip()) < 10:  # Basic validation
                raise SupertoneError("Invalid API key format", 401)
                
        except Exception as e:
            self.logger.error(f"API key validation failed: {str(e)}")
            raise SupertoneError("Failed to validate Supertone API key", 401)
    
    def _validate_voice_and_language(self, voice_id: str, language: str) -> None:
        """
        Validate voice ID and language compatibility
        
        Args:
            voice_id: Voice ID to validate
            language: Language code to validate
            
        Raises:
            SupertoneError: If voice or language is invalid
        """
        if voice_id not in self.voice_data:
            raise SupertoneError(f"Voice not found: {voice_id}", 404)
        
        voice_info = self.voice_data[voice_id]
        if language not in voice_info["supported_languages"]:
            raise SupertoneError(
                f"Language {language} not supported by voice {voice_id}. "
                f"Supported languages: {', '.join(voice_info['supported_languages'])}", 
                400
            )
    
    def _validate_style(self, voice_id: str, style: str) -> None:
        """
        Validate style for the given voice
        
        Args:
            voice_id: Voice ID
            style: Style to validate
            
        Raises:
            SupertoneError: If style is not available for this voice
        """
        if voice_id in self.voice_data:
            voice_info = self.voice_data[voice_id]
            if style not in voice_info["available_styles"]:
                raise SupertoneError(
                    f"Style '{style}' not available for voice {voice_id}. "
                    f"Available styles: {', '.join(voice_info['available_styles'])}",
                    400
                )

    def text_to_speech(
        self,
        api_key: str,
        text: str,
        voice_id: str,
        language: str = "ko",
        style: Optional[str] = None,
        model: Optional[str] = None,
        pitch_shift: Optional[float] = None,
        pitch_variance: Optional[float] = None,
        speed: Optional[float] = None,
        output_format: Optional[str] = None
    ) -> bytes:
        """
        Generate speech from text using Supertone API
        
        Args:
            api_key: Supertone API key
            text: Text to convert to speech (max 300 characters)
            voice_id: Voice identifier
            language: Language code (ko, en, ja)
            style: Emotional style
            model: Model name
            pitch_shift: Pitch adjustment (-12 to +12)
            pitch_variance: Intonation variation (0.1 to 2.0)  
            speed: Speech rate (0.5 to 2.0)
            output_format: Output format (wav, mp3)
            
        Returns:
            bytes: Audio data
            
        Raises:
            SupertoneError: If TTS generation fails
        """
        # Validate API key
        self._validate_api_key(api_key)
        
        # Validate text length
        if len(text) > 300:
            raise SupertoneError("Text exceeds maximum length of 300 characters", 400)
        
        if not text.strip():
            raise SupertoneError("Text cannot be empty", 400)
        
        # Validate voice and language compatibility
        self._validate_voice_and_language(voice_id, language)
        
        # Use defaults
        style = style or self.DEFAULT_STYLE
        model = model or self.DEFAULT_MODEL
        pitch_shift = pitch_shift if pitch_shift is not None else 0.0
        pitch_variance = pitch_variance if pitch_variance is not None else 1.0
        speed = speed if speed is not None else 1.0
        output_format = output_format or "wav"
        
        # Validate style
        self._validate_style(voice_id, style)
        
        try:
            # Build API request
            url = f"{self.BASE_URL}/v1/text-to-speech/{voice_id}"
            
            headers = {
                "x-sup-api-key": api_key,
                "Content-Type": "application/json"
            }
            
            # Add output format to query parameters if not wav
            if output_format != "wav":
                url += f"?output_format={output_format}"
            
            data = {
                "text": text,
                "language": language,
                "style": style,
                "model": model,
                "voice_settings": {
                    "pitch_shift": pitch_shift,
                    "pitch_variance": pitch_variance,
                    "speed": speed
                }
            }
            
            self.logger.info(f"Supertone TTS request: voice={voice_id}, language={language}, style={style}")
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            # Handle API errors
            if response.status_code == 401:
                raise SupertoneError("Invalid Supertone API key", 401)
            elif response.status_code == 400:
                raise SupertoneError(f"Bad request: {response.text}", 400)
            elif response.status_code == 404:
                raise SupertoneError(f"Voice not found: {voice_id}", 404)
            elif response.status_code == 429:
                raise SupertoneError("Rate limit exceeded", 429)
            elif response.status_code >= 500:
                raise SupertoneError("Supertone service temporarily unavailable", 503)
            elif not response.ok:
                raise SupertoneError(f"API request failed: {response.text}", response.status_code)
            
            # Return audio data
            audio_length = response.headers.get("X-Audio-Length", "unknown")
            self.logger.info(f"Successfully generated Supertone audio, length: {audio_length}s")
            
            return response.content
            
        except requests.RequestException as e:
            self.logger.error(f"Supertone API request failed: {str(e)}")
            raise SupertoneError("Failed to connect to Supertone API", 503)
        except Exception as e:
            self.logger.error(f"Unexpected error in Supertone TTS: {str(e)}")
            raise SupertoneError(f"TTS generation failed: {str(e)}", 500)
    
    def get_available_voices(self, api_key: Optional[str] = None) -> List[SupertoneVoice]:
        """
        Retrieve list of available Supertone voices
        
        Args:
            api_key: Supertone API key (optional for demo)
            
        Returns:
            List[SupertoneVoice]: List of available voices
            
        Raises:
            SupertoneError: If voice retrieval fails
        """
        # Return voices loaded from supertone_type.json
        voices = []
        
        for voice_id, voice_info in self.voice_data.items():
            voices.append(SupertoneVoice(
                voice_id=voice_info["voice_id"],
                name=voice_info["name"],
                gender=voice_info["gender"],
                age=voice_info.get("age", "unknown"),
                use_case=voice_info.get("use_case", "general"),
                supported_languages=voice_info["supported_languages"],
                available_styles=voice_info["available_styles"]
            ))
        
        self.logger.info(f"Retrieved {len(voices)} Supertone voices")
        return voices
    
    def get_voice_preview(self, api_key: str, voice_id: str, language: str = "ko", style: str = "neutral", custom_text: Optional[str] = None) -> bytes:
        """
        Get voice sample audio for preview
        
        Args:
            api_key: Supertone API key
            voice_id: ID of the voice to preview
            language: Language for sample text
            style: Style for preview
            custom_text: Custom sample text (optional)
            
        Returns:
            bytes: Audio sample data
            
        Raises:
            SupertoneError: If voice preview fails
        """
        # Validate API key
        self._validate_api_key(api_key)
        
        # Validate voice and language
        self._validate_voice_and_language(voice_id, language)
        
        # Use custom text or default sample texts
        if custom_text and custom_text.strip():
            sample_text = custom_text.strip()
        else:
            # Default sample texts for different languages
            sample_texts = {
                "ko": "안녕하세요. 수퍼톤 음성 샘플입니다.",
                "en": "Hello. This is a Supertone voice sample.",
                "ja": "こんにちは。スーパートーン音声サンプルです。"
            }
            sample_text = sample_texts.get(language, sample_texts["ko"])
        
        try:
            # Generate sample using our TTS method
            return self.text_to_speech(
                api_key=api_key,
                text=sample_text,
                voice_id=voice_id,
                language=language,
                style=style
            )
            
        except Exception as e:
            self.logger.error(f"Voice preview failed for {voice_id}: {str(e)}")
            raise SupertoneError(f"Failed to generate voice preview: {str(e)}", 500)