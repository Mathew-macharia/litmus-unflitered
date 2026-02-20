"""
AI Content Generator
Orchestrates product processing through Gemini API
"""

import json
import os
import re
import time
from typing import Dict, Optional
from ai.gemini_client import GeminiAPIClient
from ai.prompt_templates import PromptBuilder

FAILED_DIR = os.path.join("output", "failed_responses")


class AIContentGenerator:
    """Generate product content using Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_client = GeminiAPIClient(api_key)
        self.prompt_builder = PromptBuilder()
        os.makedirs(FAILED_DIR, exist_ok=True)
    
    def repair_json(self, text: str) -> str:
        """Fix common LLM JSON mistakes: mismatched brackets, trailing commas"""
        chars = list(text)
        length = len(chars)
        i = 0
        in_string = False
        escape = False
        stack = []

        while i < length:
            c = chars[i]

            if escape:
                escape = False
                i += 1
                continue

            if c == '\\' and in_string:
                escape = True
                i += 1
                continue

            if c == '"' and not escape:
                in_string = not in_string
                i += 1
                continue

            if in_string:
                i += 1
                continue

            if c in ('{', '['):
                stack.append(c)
            elif c in ('}', ']'):
                if stack:
                    opener = stack[-1]
                    expected = '}' if opener == '{' else ']'
                    if c != expected:
                        chars[i] = expected
                    stack.pop()

            i += 1

        result = ''.join(chars)
        result = re.sub(r',\s*([}\]])', r'\1', result)
        return result
    
    def _try_parse(self, raw: str) -> Optional[Dict]:
        """Try json.loads, then retry with repair_json as fallback"""
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
        try:
            return json.loads(self.repair_json(raw))
        except json.JSONDecodeError:
            return None

    def extract_json_from_response(self, response: str) -> Dict:
        """Extract a single JSON object from Gemini's response"""

        # Method 1: Find ```json ... ``` code block explicitly (no regex)
        for marker in ('```json', '```'):
            start = response.find(marker)
            if start != -1:
                content_start = response.find('\n', start)
                if content_start != -1:
                    content_start += 1
                    end = response.find('```', content_start)
                    if end != -1:
                        result = self._try_parse(response[content_start:end].strip())
                        if result is not None:
                            return result

        # Method 2: Find outermost { to }
        first = response.find('{')
        last = response.rfind('}')
        if first != -1 and last != -1 and last > first:
            result = self._try_parse(response[first:last + 1])
            if result is not None:
                return result

        # Method 3: Try parsing entire response as JSON
        result = self._try_parse(response)
        if result is not None:
            return result

        raise Exception(f"JSON extraction failed ({len(response)} chars)")
    
    def _save_failed_response(self, sku: str, response: str, attempt: int):
        """Save a failed response to disk for debugging"""
        safe_sku = re.sub(r'[^\w\-]', '_', sku)
        path = os.path.join(FAILED_DIR, f"{safe_sku}_attempt{attempt}.txt")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(response)

    def process_single_product(self, product: Dict, index: int = 1, total: int = 1, max_retries: int = 2) -> Dict:
        """Process a single product through Gemini API with retry on bad JSON"""
        sku = product.get('_sku', 'unknown')
        print(f"  [{index}/{total}] {sku}...", end=" ", flush=True)
        prompt = self.prompt_builder.build_prompt([product])

        last_error = None
        for attempt in range(1, max_retries + 1):
            response = self.api_client.generate_with_retry(prompt)
            try:
                processed = self.extract_json_from_response(response)
                print("OK")
                return processed
            except Exception as e:
                last_error = e
                self._save_failed_response(sku, response, attempt)
                if attempt < max_retries:
                    print(f"bad response, retry {attempt}/{max_retries - 1}...", end=" ", flush=True)
                    time.sleep(2)

        raise Exception(f"{last_error} (after {max_retries} attempts). Saved to {FAILED_DIR}/")
    
    def validate_product(self, product: Dict) -> bool:
        """Validate a processed product has required fields"""
        required_fields = [
            'sku', 'brand', 'name', 'description', 'short_description', 'categories',
            'tags', 'attributes', 'focus_keyphrase', 'meta_description',
            'price', 'stock_status'
        ]
        
        for field in required_fields:
            if field not in product:
                print(f"    Validation Warning: missing field '{field}' in {product.get('sku', 'unknown')}")
                return False
        
        word_count = len(product.get('description', '').split())
        if word_count < 300:
            print(f"    Validation Warning: {product.get('sku')} description only {word_count} words (target: 300+)")
        
        return True
