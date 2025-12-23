"""
Configuration file for WooCommerce CSV Generator
"""

import os
from typing import Optional, List


class Config:
    """Configuration settings"""
    
    # Gemini API
    GEMINI_API_KEY: Optional[str] = "AIzaSyAKALv9-BSgWUbkbk4uSMksr9thbU9Ls6E"
    
    # Batch settings
    BATCH_SIZE: int = 15  # Products per API call (10-20 recommended)
    
    # File paths
    CATEGORIES_FILE: str = "product_categories.txt"
    OUTPUT_DIR: str = "output"
    
    # Excel processing
    EXCLUDE_SHEETS: List[str] = ['Home page', 'Rental', 'Services']
    
    # Location and competitors (for search context)
    LOCATION: str = "Nairobi CBD, Kenya"
    COMPETITORS: List[str] = [
        "supremenetworks.co.ke",
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
BATCH_SIZE = Config.BATCH_SIZE
CATEGORIES_FILE = Config.CATEGORIES_FILE
OUTPUT_DIR = Config.OUTPUT_DIR
LOCATION = Config.LOCATION
COMPETITORS = Config.COMPETITORS
