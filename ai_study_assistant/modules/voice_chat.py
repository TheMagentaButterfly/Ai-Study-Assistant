"""
Voice processing module for speech recognition and synthesis.
"""
import os
import uuid
import logging
import tempfile
import whisper
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import numpy as np
from scipy.io import wavfile

from config import VOICE_LANGUAGE, SPEECH_RECOGNITION_TIMEOUT, BASE_DIR

class VoiceProcessor:
    """
    Handles voice processing for the AI assistant.
    """
    
    def __init__(self):
        """Initialize the voice processor."""
        self.recognizer = sr.Recognizer()
        self.output_dir = os.path.join(BASE_DIR, "static", "audio")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize whisper model for offline speech recognition
        self.model = whisper.load_model("base")
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def transcribe(self, audio_path, language="en"):
        """
        Transcribe speech from an audio file to text.
        
        Args:
            audio_path (str): Path to the audio file
            language (str): Language code (e.g., 'en', 'es')
            
        Returns:
            str: Transcribed text
        """
        try:
            # First try whisper for better recognition
            result = self.model.transcribe(audio_path, language=language[:2])
            transcription = result["text"]
            self.logger.info(f"Whisper transcription successful: {transcription[:30]}...")
            return transcription
        except Exception as e:
            self.logger.warning(f"Whisper transcription failed: {e}, falling back to SpeechRecognition")
            
            # Fallback to SpeechRecognition
            try:
                with sr.AudioFile(audio_path) as source:
                    audio_data = self.recognizer.record(source)
                    language_map = {"en": "en-US", "es": "es-ES", "fr": "fr-FR", "de": "de-DE", 
                                   "it": "it-IT", "ja": "ja-JP", "ko": "ko-KR", "zh-cn": "zh-CN",
                                   "ru": "ru-RU", "ar": "ar-SA", "hi": "hi-IN"}
                    
                    sr_lang = language_map.get(language, language)
                    text = self.recognizer.recognize_google(audio_data, language=sr_lang)
                    return text
            except sr.UnknownValueError:
                return "I couldn't understand the audio."
            except sr.RequestError:
                return "Speech recognition service unavailable."
            except Exception as e:
                self.logger.error(f"Speech recognition error: {e}")
                return "An error occurred while processing your speech."
    
    def text_to_speech(self, text, language="en"):
        """
        Convert text to speech.
        
        Args:
            text (str): Text to convert to speech
            language (str): Language code
            
        Returns:
            str: Path to the generated audio file
        """
        try:
            # Map language codes to gTTS format if needed
            gtts_lang = language[:2] if language in ["zh-cn"] else language
            
            # Generate speech
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            
            # Save to a file
            filename = f"{uuid.uuid4()}.mp3"
            output_path = os.path.join(self.output_dir, filename)
            tts.save(output_path)
            
            self.logger.info(f"Text-to-speech generated: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Text-to-speech error: {e}")
            # Generate silent audio as fallback
            return self._generate_silent_audio()
    
    def _generate_silent_audio(self, duration=1):
        """Generate a silent audio file as fallback."""
        sample_rate = 24000
        samples = np.zeros(int(duration * sample_rate))
        
        filename = f"{uuid.uuid4()}.wav"
        output_path = os.path.join(self.output_dir, filename)
        
        wavfile.write(output_path, sample_rate, samples.astype(np.int16))
        return output_path
    
    def record_from_microphone(self, duration=5):
        """
        Record audio from microphone.
        
        Args:
            duration (int): Recording duration in seconds
            
        Returns:
            str: Path to the recorded audio file
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_path = temp_file.name
        temp_file.close()
        
        try:
            with sr.Microphone() as source:
                self.logger.info("Recording audio...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=duration)
                
                with open(temp_path, "wb") as f:
                    f.write(audio.get_wav_data())
                
                return temp_path
        except Exception as e:
            self.logger.error(f"Error recording audio: {e}")
            return None