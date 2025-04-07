"""
AI Core module for interacting with Ollama API.
"""
import requests
import json
import logging
from config import OLLAMA_API_URL, OLLAMA_MODEL

class OllamaAI:
    """
    Handles interactions with the Ollama API for AI responses.
    """
    
    def __init__(self):
        """Initialize the Ollama AI handler."""
        self.api_url = f"{OLLAMA_API_URL}/generate"
        self.model = OLLAMA_MODEL
        self.conversation_history = []
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test connection to Ollama API."""
        try:
            response = requests.get(f"{OLLAMA_API_URL}/version")
            if response.status_code == 200:
                self.logger.info(f"Connected to Ollama API: {response.json()}")
            else:
                self.logger.warning(f"Failed to connect to Ollama API: {response.status_code}")
        except requests.RequestException as e:
            self.logger.error(f"Error connecting to Ollama API: {e}")
            self.logger.info("Make sure Ollama is running with 'ollama serve' command")
    
    def get_response(self, user_message, system_prompt=None):
        """
        Get a response from the AI.
        
        Args:
            user_message (str): The user's message
            system_prompt (str, optional): System prompt to guide the AI
            
        Returns:
            str: The AI's response
        """
        if not system_prompt:
            system_prompt = """You are an educational AI study assistant focused on helping students achieve 
            academic excellence. Be concise, informative, and encouraging. Provide accurate 
            information and study tips. When helping with complex topics, break them down 
            into manageable parts. Always try to guide students toward understanding rather 
            than just providing answers."""
        
        # Update conversation history (keep last 6 exchanges for context)
        self.conversation_history.append({"role": "user", "content": user_message})
        if len(self.conversation_history) > 12:  # 6 exchanges (user + assistant)
            self.conversation_history = self.conversation_history[-12:]
        
        try:
            payload = {
                "model": self.model,
                "system": system_prompt,
                "messages": self.conversation_history,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(self.api_url, json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                ai_message = response_data.get("response", "")
                # Update conversation history with AI's response
                self.conversation_history.append({"role": "assistant", "content": ai_message})
                return ai_message
            else:
                self.logger.error(f"Error from Ollama API: {response.status_code} - {response.text}")
                return "I'm having trouble connecting to my AI core. Please check your Ollama setup."
                
        except requests.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return "I'm experiencing network issues. Please try again later."
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return "I received an invalid response format. Please check your Ollama setup."
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return "An unexpected error occurred. Please try again."
    
    def get_specialized_response(self, user_message, subject_area):
        """
        Get a response specialized for a particular subject area.
        
        Args:
            user_message (str): The user's message
            subject_area (str): The academic subject (math, science, etc.)
            
        Returns:
            str: The AI's response
        """
        subject_prompts = {
            "math": "You are a mathematics tutor. Explain concepts clearly and provide step-by-step solutions.",
            "science": "You are a science tutor. Explain scientific concepts and provide examples from the real world.",
            "history": "You are a history tutor. Provide accurate historical information and help with contextualizing events.",
            "literature": "You are a literature tutor. Help with literary analysis, writing, and understanding texts.",
            "language": "You are a language tutor. Help with grammar, vocabulary, and language learning strategies."
        }
        
        system_prompt = subject_prompts.get(
            subject_area.lower(), 
            f"You are an expert tutor in {subject_area}. Provide clear explanations and helpful insights."
        )
        
        return self.get_response(user_message, system_prompt)