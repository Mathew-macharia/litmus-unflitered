"""
Gemini API Client
Handles API communication with Google Gemini
"""

import json
import time
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from config import Config


class GeminiAPIClient:
    """Client for Gemini API with Google Search integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY in config.py or environment variable.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Use a more specific Gemini Flash model as suggested by the user
        # The model will automatically use Google Search when instructed in the prompt
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_content(self, prompt: str, max_output_tokens: int = 8192) -> str:
        """Send prompt to Gemini and get response with search capability"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_output_tokens,
                    temperature=0.7,
                )
            )
            
            if not response.candidates:
                print(f"    Warning: Gemini response has no candidates. Prompt feedback: {response.prompt_feedback}")
                return ""

            # Check for specific finish reasons if no text is returned
            if hasattr(response.candidates[0], 'finish_reason') and response.candidates[0].finish_reason == 2: # STOP due to safety or other reasons
                print(f"    Warning: Gemini candidate finished with reason 2 (stopped). Prompt feedback: {response.prompt_feedback}")
                return ""
            
            # Extract text from response
            if response.text:
                return response.text
            else:
                print(f"    Warning: Gemini response.text is empty. Full response: {response}")
                return ""
                
        except Exception as e:
            error_message = f"Gemini API client received an error: {e}"
            print(f"    {error_message}")
            if hasattr(response, 'candidates'):
                print(f"    Response candidates: {response.candidates}")
            if hasattr(response, 'prompt_feedback'):
                print(f"    Response prompt feedback: {response.prompt_feedback}")
            raise Exception(f"Gemini API error: {str(e)}")
    
    def generate_with_retry(self, prompt: str, max_retries: int = 3, delay: int = 2) -> str:
        """Generate content with retry logic"""
        for attempt in range(max_retries):
            try:
                return self.generate_content(prompt)
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"    Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise Exception(f"Failed after {max_retries} attempts: {str(e)}")
        
        return ""
