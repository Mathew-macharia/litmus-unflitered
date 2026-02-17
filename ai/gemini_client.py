"""
Gemini API Client
Handles API communication with Google Gemini using the google-genai SDK
"""

import re
import time
from typing import Optional
from google import genai
from google.genai import types
from config import Config


class GeminiAPIClient:
    """Client for Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY in config.py or environment variable.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-3-flash-preview"
    
    def generate_content(self, prompt: str, max_output_tokens: int = 8192) -> str:
        """Send prompt to Gemini and get response"""
        try:
            config = types.GenerateContentConfig(
                max_output_tokens=max_output_tokens,
                temperature=0.7,
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
            
            if not response.candidates:
                return ""

            if response.text:
                return response.text
            return ""
                
        except Exception as e:
            raise Exception(str(e))
    
    def _extract_retry_delay(self, error_msg: str) -> int:
        """Extract the retry delay from a 429 error message"""
        match = re.search(r'retryDelay.*?(\d+)', error_msg)
        if match:
            return int(match.group(1))
        return 10
    
    def generate_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Generate content with retry logic that respects API rate limits"""
        for attempt in range(max_retries):
            try:
                return self.generate_content(prompt)
            except Exception as e:
                error_msg = str(e)
                is_rate_limit = '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg
                
                if attempt < max_retries - 1:
                    if is_rate_limit:
                        wait = self._extract_retry_delay(error_msg) + 2
                        print(f"rate limited, waiting {wait}s...", end=" ", flush=True)
                    else:
                        wait = 5
                        print(f"error, retrying in {wait}s...", end=" ", flush=True)
                    time.sleep(wait)
                else:
                    if is_rate_limit:
                        raise Exception("Rate limit exceeded. Wait a minute and try again, or upgrade your API plan.")
                    raise Exception(f"Failed after {max_retries} attempts: {error_msg[:200]}")
        
        return ""
