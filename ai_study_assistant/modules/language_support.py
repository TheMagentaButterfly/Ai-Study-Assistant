"""
Language support module for multi-language functionality.
"""
import logging
from googletrans import Translator
from langdetect import detect

from config import SUPPORTED_LANGUAGES

class LanguageManager:
    """
    Handles language detection and translation.
    """
    
    def __init__(self):
        """Initialize the language manager."""
        self.translator = Translator()
        self.supported_languages = SUPPORTED_LANGUAGES
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def detect_language(self, text):
        """
        Detect the language of the given text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Language code
        """
        try:
            language = detect(text)
            self.logger.info(f"Detected language: {language}")
            return language
        except Exception as e:
            self.logger.error(f"Language detection error: {e}")
            return "en"  # Default to English
    
    def translate_to_english(self, text, source_language=None):
        """
        Translate text to English.
        
        Args:
            text (str): Text to translate
            source_language (str, optional): Source language code
            
        Returns:
            str: Translated text
        """
        if not text.strip():
            return text
            
        try:
            # If source language is not provided, detect it
            if not source_language:
                source_language = self.detect_language(text)
                
            # If already English, return as is
            if source_language == "en":
                return text
                
            # Translate to English
            translated = self.translator.translate(text, src=source_language, dest='en')
            self.logger.info(f"Translated from {source_language} to English")
            return translated.text
        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            return text  # Return original text if translation fails
    
    def translate_from_english(self, text, target_language):
        """
        Translate text from English to another language.
        
        Args:
            text (str): English text to translate
            target_language (str): Target language code
            
        Returns:
            str: Translated text
        """
        if not text.strip() or target_language == "en":
            return text
            
        try:
            # Check if target language is supported
            if target_language not in self.supported_languages:
                self.logger.warning(f"Unsupported target language: {target_language}")
                return text
                
            # Translate from English
            translated = self.translator.translate(text, src='en', dest=target_language)
            self.logger.info(f"Translated from English to {target_language}")
            return translated.text
        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            return text  # Return original text if translation fails
    
    def get_supported_languages(self):
        """
        Get the list of supported languages.
        
        Returns:
            dict: Dictionary of language codes and names
        """
        return self.supported_languages