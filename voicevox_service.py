"""
Voicevox TTS Service Layer

This module provides a service layer for interacting with the Voicevox TTS engine,
handling text-to-speech generation, voice management, and error handling.
"""

import logging
import requests
import json
from typing import List, Dict, Any, Optional
from schemas import VoicevoxSpeaker


class VoicevoxError(Exception):
    """Custom exception for Voicevox API errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class VoicevoxService:
    """Service class for Voicevox TTS functionality"""
    
    # Default settings
    DEFAULT_SPEAKER_ID = 2  # 四国めたん (노멀)
    DEFAULT_SPEED_SCALE = 1.0
    DEFAULT_PITCH_SCALE = 0.0
    DEFAULT_INTONATION_SCALE = 1.0
    DEFAULT_VOLUME_SCALE = 1.0
    DEFAULT_PRE_PHONEME_LENGTH = 0.1
    DEFAULT_POST_PHONEME_LENGTH = 0.1
    DEFAULT_TIMEOUT = 30  # seconds
    
    # Sample text for voice previews
    SAMPLE_TEXT = "こんにちは、世界！これは音声サンプルです。"
    
    def __init__(self, base_url: str = "http://localhost:50021"):
        """
        Initialize the Voicevox service
        
        Args:
            base_url: Base URL of the Voicevox engine (default: http://localhost:50021)
        """
        self.base_url = base_url.rstrip('/')
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.timeout = self.DEFAULT_TIMEOUT
        
        self.logger.info(f"Initialized VoicevoxService with base_url: {self.base_url}")
    
    def _validate_connection(self) -> None:
        """
        Validate connection to Voicevox engine
        
        Raises:
            VoicevoxError: If connection fails
        """
        try:
            response = self.session.get(f"{self.base_url}/version")
            if not response.ok:
                raise VoicevoxError(
                    f"Voicevox engine connection failed: HTTP {response.status_code}",
                    503
                )
            self.logger.debug(f"Voicevox engine version: {response.text}")
            
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Failed to connect to Voicevox engine at {self.base_url}")
            raise VoicevoxError(
                "Cannot connect to Voicevox engine. Please ensure the engine is running.",
                503
            )
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout connecting to Voicevox engine at {self.base_url}")
            raise VoicevoxError(
                "Timeout connecting to Voicevox engine. Please check the engine status.",
                503
            )
        except Exception as e:
            self.logger.error(f"Unexpected error connecting to Voicevox engine: {str(e)}")
            raise VoicevoxError(
                "Failed to connect to Voicevox engine due to unexpected error.",
                503
            )
    
    def text_to_speech(
        self,
        text: str,
        speaker_id: int = None,
        speed_scale: float = None,
        pitch_scale: float = None,
        intonation_scale: float = None,
        volume_scale: float = None,
        pre_phoneme_length: float = None,
        post_phoneme_length: float = None,
        enable_interrogative_upspeak: bool = None
    ) -> bytes:
        """
        Convert text to speech using Voicevox engine
        
        Args:
            text: Text to convert to speech (Japanese)
            speaker_id: Speaker ID (default: 2 - 四국めたん 노멀)
            speed_scale: Speech speed scale (0.5-2.0, default: 1.0)
            pitch_scale: Pitch adjustment scale (-0.15-0.15, default: 0.0)
            intonation_scale: Intonation strength scale (0.0-2.0, default: 1.0)
            volume_scale: Volume scale (0.0-2.0, default: 1.0)
            pre_phoneme_length: Pre-phoneme length in seconds (0.0-1.5, default: 0.1)
            post_phoneme_length: Post-phoneme length in seconds (0.0-1.5, default: 0.1)
            enable_interrogative_upspeak: Enable automatic interrogative upspeak (default: True)
            
        Returns:
            bytes: Audio data in WAV format
            
        Raises:
            VoicevoxError: If TTS generation fails
        """
        # Validate connection first
        self._validate_connection()
        
        # Use defaults if not provided
        speaker_id = speaker_id if speaker_id is not None else self.DEFAULT_SPEAKER_ID
        speed_scale = speed_scale if speed_scale is not None else self.DEFAULT_SPEED_SCALE
        pitch_scale = pitch_scale if pitch_scale is not None else self.DEFAULT_PITCH_SCALE
        intonation_scale = intonation_scale if intonation_scale is not None else self.DEFAULT_INTONATION_SCALE
        volume_scale = volume_scale if volume_scale is not None else self.DEFAULT_VOLUME_SCALE
        pre_phoneme_length = pre_phoneme_length if pre_phoneme_length is not None else self.DEFAULT_PRE_PHONEME_LENGTH
        post_phoneme_length = post_phoneme_length if post_phoneme_length is not None else self.DEFAULT_POST_PHONEME_LENGTH
        enable_interrogative_upspeak = enable_interrogative_upspeak if enable_interrogative_upspeak is not None else True
        
        # Validate input parameters
        if not text or not text.strip():
            raise VoicevoxError("Text cannot be empty", 400)
        
        if len(text) > 1000:  # Reasonable limit for Voicevox
            raise VoicevoxError("Text is too long (maximum 1000 characters)", 400)
        
        self.logger.info(f"Generating speech for text: '{text[:50]}...' with speaker_id: {speaker_id}")
        
        try:
            # Step 1: Generate audio query
            audio_query_url = f"{self.base_url}/audio_query"
            audio_query_params = {
                "text": text,
                "speaker": speaker_id
            }
            
            self.logger.debug(f"Requesting audio query: {audio_query_url}")
            audio_query_response = self.session.post(
                audio_query_url,
                params=audio_query_params
            )
            
            if not audio_query_response.ok:
                error_msg = f"Audio query failed: HTTP {audio_query_response.status_code}"
                if audio_query_response.status_code == 422:
                    error_msg += " - Invalid speaker ID or text format"
                elif audio_query_response.status_code == 400:
                    error_msg += " - Bad request parameters"
                
                self.logger.error(f"{error_msg}: {audio_query_response.text}")
                raise VoicevoxError(error_msg, audio_query_response.status_code)
            
            # Parse audio query response
            try:
                audio_query = audio_query_response.json()
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse audio query response: {str(e)}")
                raise VoicevoxError("Invalid response from Voicevox engine", 500)
            
            # Step 2: Modify audio query with custom parameters
            audio_query.update({
                "speedScale": speed_scale,
                "pitchScale": pitch_scale,
                "intonationScale": intonation_scale,
                "volumeScale": volume_scale,
                "prePhonemeLength": pre_phoneme_length,
                "postPhonemeLength": post_phoneme_length,
                "outputSamplingRate": 24000,  # Standard output sampling rate
                "outputStereo": False  # Mono output
            })
            
            # Handle interrogative upspeak
            if enable_interrogative_upspeak and "accent_phrases" in audio_query:
                for phrase in audio_query["accent_phrases"]:
                    if phrase.get("is_interrogative", False):
                        # Adjust the last mora for interrogative upspeak
                        if phrase.get("moras") and len(phrase["moras"]) > 0:
                            last_mora = phrase["moras"][-1]
                            if "pitch" in last_mora:
                                last_mora["pitch"] = min(last_mora["pitch"] * 1.2, 6.5)
            
            # Step 3: Generate synthesis
            synthesis_url = f"{self.base_url}/synthesis"
            synthesis_params = {
                "speaker": speaker_id
            }
            
            self.logger.debug(f"Requesting synthesis: {synthesis_url}")
            synthesis_response = self.session.post(
                synthesis_url,
                params=synthesis_params,
                json=audio_query,
                headers={"Content-Type": "application/json"}
            )
            
            if not synthesis_response.ok:
                error_msg = f"Synthesis failed: HTTP {synthesis_response.status_code}"
                if synthesis_response.status_code == 422:
                    error_msg += " - Invalid audio query or speaker ID"
                elif synthesis_response.status_code == 400:
                    error_msg += " - Bad synthesis parameters"
                
                self.logger.error(f"{error_msg}: {synthesis_response.text}")
                raise VoicevoxError(error_msg, synthesis_response.status_code)
            
            # Return audio data
            audio_data = synthesis_response.content
            self.logger.info(f"Successfully generated {len(audio_data)} bytes of audio data")
            
            return audio_data
            
        except requests.exceptions.ConnectionError:
            self.logger.error("Connection error during TTS generation")
            raise VoicevoxError("Connection to Voicevox engine lost during processing", 503)
            
        except requests.exceptions.Timeout:
            self.logger.error("Timeout during TTS generation")
            raise VoicevoxError("Voicevox engine request timed out", 503)
            
        except VoicevoxError:
            # Re-raise VoicevoxError as-is
            raise
            
        except Exception as e:
            self.logger.error(f"Unexpected error during TTS generation: {str(e)}")
            raise VoicevoxError(f"TTS generation failed: {str(e)}", 500)
    
    def get_speakers(self) -> List[VoicevoxSpeaker]:
        """
        Get list of available Voicevox speakers (free voices only)
        
        Returns:
            List[VoicevoxSpeaker]: List of available free speakers
            
        Raises:
            VoicevoxError: If speaker retrieval fails
        """
        # Validate connection first
        self._validate_connection()
        
        try:
            speakers_url = f"{self.base_url}/speakers"
            self.logger.debug(f"Requesting speakers list: {speakers_url}")
            
            response = self.session.get(speakers_url)
            
            if not response.ok:
                error_msg = f"Failed to retrieve speakers: HTTP {response.status_code}"
                self.logger.error(f"{error_msg}: {response.text}")
                raise VoicevoxError(error_msg, response.status_code)
            
            try:
                speakers_data = response.json()
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse speakers response: {str(e)}")
                raise VoicevoxError("Invalid response from Voicevox engine", 500)
            
            # Filter and format speakers (focus on free commercial-use voices)
            free_speakers = []
            
            # Define known free commercial-use speakers with English names
            free_speaker_mapping = {
                # ずんだもん (Zundamon) - 완전 무료 상업적 사용 가능
                3: {
                    "name": "ずんだもん", 
                    "english_name": "Zundamon",
                    "styles": {0: "ノーマル", 1: "あまあま", 2: "ツンツン", 3: "セクシー"},
                    "english_styles": {0: "Normal", 1: "Sweet", 2: "Tsundere", 3: "Sexy"}
                },
                
                # 四国めたん (Shikoku Metan) - 완전 무료 상업적 사용 가능  
                2: {
                    "name": "四国めたん", 
                    "english_name": "Shikoku_Metan",
                    "styles": {0: "ノーマル", 1: "あまあま", 2: "ツンツン", 3: "セクシー"},
                    "english_styles": {0: "Normal", 1: "Sweet", 2: "Tsundere", 3: "Sexy"}
                },
                
                # 春日部つむぎ (Kasukabe Tsumugi) - 완전 무료 상업적 사용 가능
                8: {
                    "name": "春日部つむぎ", 
                    "english_name": "Kasukabe_Tsumugi",
                    "styles": {0: "ノーマル"},
                    "english_styles": {0: "Normal"}
                },
                
                # 雨晴はう (Amehare Hau) - 완전 무료 상업적 사용 가능
                10: {
                    "name": "雨晴はう", 
                    "english_name": "Amehare_Hau",
                    "styles": {0: "ノーマル"},
                    "english_styles": {0: "Normal"}
                },
                
                # 波音リツ (Namine Ritsu) - 완전 무료 상업적 사용 가능
                9: {
                    "name": "波音リツ", 
                    "english_name": "Namine_Ritsu",
                    "styles": {0: "ノーマル"},
                    "english_styles": {0: "Normal"}
                },
            }
            
            for speaker_data in speakers_data:
                speaker_uuid = speaker_data.get("speaker_uuid", "")
                speaker_name = speaker_data.get("name", "")
                styles = speaker_data.get("styles", [])
                
                # Check if this is a known free speaker
                for style in styles:
                    style_id = style.get("id")
                    style_name = style.get("name", "")
                    style_type = style.get("type", "talk")
                    
                    # Map style_id to speaker_id for known free speakers
                    for known_speaker_id, speaker_info in free_speaker_mapping.items():
                        if speaker_name == speaker_info["name"]:
                            # Check if this style is in our known free styles
                            known_styles = speaker_info["styles"]
                            for known_style_idx, known_style_name in known_styles.items():
                                if style_name == known_style_name:
                                    english_style_name = speaker_info["english_styles"].get(known_style_idx, style_name)
                                    free_speakers.append(VoicevoxSpeaker(
                                        speaker_id=known_speaker_id,
                                        name=speaker_name,
                                        english_name=speaker_info["english_name"],
                                        style_id=style_id,
                                        style_name=style_name,
                                        english_style_name=english_style_name,
                                        type=style_type,
                                        is_free=True
                                    ))
                                    break
                            break
            
            # Sort by speaker_id for consistent ordering
            free_speakers.sort(key=lambda x: (x.speaker_id, x.style_id))
            
            self.logger.info(f"Retrieved {len(free_speakers)} free speakers")
            return free_speakers
            
        except requests.exceptions.ConnectionError:
            self.logger.error("Connection error during speakers retrieval")
            raise VoicevoxError("Connection to Voicevox engine lost", 503)
            
        except requests.exceptions.Timeout:
            self.logger.error("Timeout during speakers retrieval")
            raise VoicevoxError("Voicevox engine request timed out", 503)
            
        except VoicevoxError:
            # Re-raise VoicevoxError as-is
            raise
            
        except Exception as e:
            self.logger.error(f"Unexpected error during speakers retrieval: {str(e)}")
            raise VoicevoxError(f"Failed to retrieve speakers: {str(e)}", 500)
    
    def get_speaker_preview(self, speaker_id: int) -> bytes:
        """
        Generate voice sample audio for preview
        
        Args:
            speaker_id: ID of the speaker to preview
            
        Returns:
            bytes: Audio sample data in WAV format
            
        Raises:
            VoicevoxError: If preview generation fails
        """
        self.logger.info(f"Generating voice preview for speaker_id: {speaker_id}")
        
        try:
            # Use our text_to_speech method to generate a sample
            return self.text_to_speech(
                text=self.SAMPLE_TEXT,
                speaker_id=speaker_id,
                speed_scale=self.DEFAULT_SPEED_SCALE,
                pitch_scale=self.DEFAULT_PITCH_SCALE,
                intonation_scale=self.DEFAULT_INTONATION_SCALE,
                volume_scale=self.DEFAULT_VOLUME_SCALE
            )
            
        except VoicevoxError as e:
            # Handle specific errors for preview
            if e.status_code == 422:
                # Invalid speaker ID
                self.logger.warning(f"Invalid speaker_id for preview: {speaker_id}")
                raise VoicevoxError(f"Invalid speaker ID: {speaker_id}", 404)
            else:
                # Re-raise other VoicevoxErrors
                raise
                
        except Exception as e:
            self.logger.error(f"Unexpected error generating preview for speaker {speaker_id}: {str(e)}")
            raise VoicevoxError(f"Failed to generate voice preview: {str(e)}", 500)
    
    def get_default_speaker_id(self) -> int:
        """
        Get the default speaker ID
        
        Returns:
            int: Default speaker ID (四국めたん 노멀)
        """
        return self.DEFAULT_SPEAKER_ID
    
    def is_speaker_free(self, speaker_id: int) -> bool:
        """
        Check if a speaker is free for commercial use
        
        Args:
            speaker_id: Speaker ID to check
            
        Returns:
            bool: True if speaker is free for commercial use
        """
        # Known free commercial-use speaker IDs
        free_speaker_ids = {2, 3, 8, 9, 10}  # 四국めたん, ずんだもん, 春日部つむぎ, 波音リツ, 雨晴はう
        return speaker_id in free_speaker_ids
    
    def __del__(self):
        """Cleanup session on destruction"""
        if hasattr(self, 'session'):
            self.session.close()