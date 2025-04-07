"""
Configuration settings for the AI Study Assistant.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ollama configuration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Voice settings
VOICE_LANGUAGE = "en-US"
SPEECH_RECOGNITION_TIMEOUT = 5

# Image processing
OCR_LANGUAGE = "eng"  # Default OCR language

# App settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
PORT = int(os.getenv("PORT", 5000))

# Study sessions
DEFAULT_POMODORO_WORK = 25  # minutes
DEFAULT_POMODORO_BREAK = 5  # minutes
DEFAULT_POMODORO_LONG_BREAK = 15  # minutes

# Supported languages for translation
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh-cn": "Chinese (Simplified)",
    "ru": "Russian",
    "ar": "Arabic",
    "hi": "Hindi"
}

# Path configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)