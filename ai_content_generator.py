"""
AI Content Generator
Orchestrates product processing through Gemini API
"""

import json
import re
from typing import List, Dict, Optional
from gemini_api_client import GeminiAPIClient
from prompt_templates import PromptBuilder


class AIContentGenerator:
    """Generate product content using Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_client = GeminiAPIClient(api_key)
        self.prompt_builder = PromptBuilder()
    
    def extract_json_from_response(self, response: str) -> Dict:
        """Extract a single JSON object from Gemini's response"""
        # Look for JSON object pattern
        json_pattern = r'\{\s*".*?":.*?\}'
        match = re.search(json_pattern, response, re.DOTALL)
        
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Try to find code blocks
        code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(code_block_pattern, response, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Try parsing the entire response as JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        raise Exception(f"Could not extract JSON object from Gemini response. Response preview: {response[:500]}")
    
    def process_single_product(self, product: Dict) -> Dict:
        """Process a single product through Gemini API"""
        print(f"  Processing product: {product.get('name', product.get('sku', 'unknown'))} through Gemini API...")
        
        # Build prompt for a single product
        prompt = self.prompt_builder.build_prompt([product]) # Pass as list for prompt builder
        
        # Send to Gemini
        try:
            response = self.api_client.generate_with_retry(prompt)
            
            # Extract single JSON object
            processed_product = self.extract_json_from_response(response)
            
            # For debugging, print the extracted JSON
            print("\n--- EXTRACTED JSON START ---")
            print(json.dumps(processed_product, indent=2))
            print("--- EXTRACTED JSON END ---\n")
            
            return processed_product
            
        except Exception as e:
            print(f"    Error processing product {product.get('sku', 'unknown')}: {e}")
            raise # Re-raise the exception to indicate a problem
    
    def validate_product(self, product: Dict) -> bool:
        """Validate a processed product has required fields"""
        required_fields = [
            'sku', 'name', 'description', 'short_description', 'categories',
            'tags', 'attributes', 'focus_keyphrase', 'meta_description',
            'price', 'stock_status'
        ]
        
        for field in required_fields:
            if field not in product:
                print(f"    Validation Warning: Product {product.get('sku', 'unknown')} missing field: {field}")
                return False
        
        # Check description length
        if len(product.get('description', '').split()) < 300:
            print(f"    Validation Warning: Product {product.get('sku')} description is less than 300 words")
        
        return True
    
    def process_all(self, all_products: List[Dict]) -> List[Dict]:
        """Process all products one by one"""
        all_processed = []
        total_products = len(all_products)
        
        print(f"\nProcessing {total_products} products one by one through Gemini API...")
        
        for i, product in enumerate(all_products):
            print(f"\nProduct {i + 1}/{total_products}: {product.get('name', product.get('sku', 'unknown'))}")
            
            try:
                processed = self.process_single_product(product)
                
                # Validate product
                if self.validate_product(processed):
                    all_processed.append(processed)
                    print(f"    [OK] Processed product {product.get('sku', 'unknown')}")
                else:
                    print(f"    [WARN] Skipping invalid product {product.get('sku', 'unknown')} after processing.")
                
            except Exception as e:
                print(f"    [ERROR] Failed to process product {product.get('sku', 'unknown')}: {e}")
                # Continue with next product
                continue
        
        print(f"\n[SUCCESS] Processed {len(all_processed)}/{total_products} products successfully")
        return all_processed
