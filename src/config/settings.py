"""Application settings and configuration"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Centralized configuration for the Scientific Paper Writer"""
    
    # API Configuration
    GOOGLE_API_KEY: str = os.getenv('GOOGLE_API_KEY', '')
    GEMINI_MODEL: str = 'gemini-1.5-flash'  # Most stable production model (use 1.5-pro for better quality)
    TEMPERATURE: float = 0.7
    MAX_RETRIES: int = 5
    REQUEST_TIMEOUT: int = 180  # seconds
    REQUEST_DELAY: int = 5  # seconds between major operations (to stay under 15 req/min)
    
    # RAG Configuration
    PDF_LIBRARY_PATH: str = './pdf_library'
    RAG_DB_PATH: str = './rag_db'
    EMBEDDING_MODEL: str = 'all-MiniLM-L6-v2'
    CHUNK_SIZE: int = 500  # words
    CHUNK_OVERLAP: int = 50  # words
    TOP_K_RESULTS: int = 5  # number of RAG results to retrieve
    
    # Output Configuration
    OUTPUT_DIR: str = './outputs/papers'
    LOG_DIR: str = './outputs/logs'
    
    # Ensure directories exist
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        Path(cls.PDF_LIBRARY_PATH).mkdir(parents=True, exist_ok=True)
        Path(cls.RAG_DB_PATH).mkdir(parents=True, exist_ok=True)
        Path(cls.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        Path(cls.LOG_DIR).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Validate critical settings"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return True


# Initialize directories on import
Settings.ensure_directories()
