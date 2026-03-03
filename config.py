"""
Configuration file for WooCommerce CSV Generator
"""

import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)


class Config:
    """Configuration settings"""
    
    # Gemini API - load from .env file or environment variable
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # File paths
    CATEGORIES_FILE: str = "data/product_categories.txt"
    OUTPUT_DIR: str = "output"
    
    # Excel processing
    EXCLUDE_SHEETS: List[str] = ['Home page', 'Main Page', 'Rental', 'Services', 'BRANDS']
    
    # Location and competitors (for search context)
    LOCATION: str = "Nairobi CBD, Kenya"
    COMPETITORS: List[str] = [
        "supremenetworks.co.ke",
        "digitalstore.co.ke",
        "almiria.co.ke",
        "dataworld.co.ke",
        "dataworld",
    ]
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.GEMINI_API_KEY:
            print("Warning: GEMINI_API_KEY not set. Set it in config.py or as environment variable.")
            return False
        return True


# For backward compatibility and easy access
GEMINI_API_KEY = Config.GEMINI_API_KEY
CATEGORIES_FILE = Config.CATEGORIES_FILE
OUTPUT_DIR = Config.OUTPUT_DIR
LOCATION = Config.LOCATION
COMPETITORS = Config.COMPETITORS
