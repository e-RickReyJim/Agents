"""LLM Service for managing language model initialization"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from ..config.settings import Settings


class LLMService:
    """Service for initializing and managing LLM instances"""
    
    def __init__(self):
        """Initialize LLM service with settings"""
        self.settings = Settings
        self._llm = None
    
    def get_llm(self):
        """
        Initialize and return the Gemini LLM with rate limiting.
        
        Returns:
            ChatGoogleGenerativeAI instance
        
        Raises:
            ValueError: If GOOGLE_API_KEY not found
        """
        if self._llm is None:
            # Validate API key exists
            if not self.settings.GOOGLE_API_KEY:
                raise ValueError(
                    "GOOGLE_API_KEY not found in environment variables.\n"
                    "Please create a .env file with your Google API key."
                )
            
            # Initialize Gemini LLM with retry logic for 503 errors
            self._llm = ChatGoogleGenerativeAI(
                model=self.settings.GEMINI_MODEL,
                temperature=self.settings.TEMPERATURE,
                google_api_key=self.settings.GOOGLE_API_KEY,
                max_retries=self.settings.MAX_RETRIES,
                request_timeout=self.settings.REQUEST_TIMEOUT
            )
        
        return self._llm
    
    @property
    def model_name(self) -> str:
        """Get the current model name"""
        return self.settings.GEMINI_MODEL
    
    @property
    def temperature(self) -> float:
        """Get the current temperature setting"""
        return self.settings.TEMPERATURE
