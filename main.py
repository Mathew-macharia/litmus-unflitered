"""
AI-Powered WooCommerce CSV Generator
Main script that orchestrates the entire process
"""

import os
import sys
import json
import argparse
from datetime import datetime
from parsers.excel_parser import EnhancedExcelParser
from ai.content_generator import AIContentGenerator
from exporters.csv_converter import JSONToCSVConverter
from config import Config

PROGRESS_FILE = "progress.json"


def load_progress(output_dir: str) -> dict:
    """Load progress from JSON file"""
    path = os.path.join(output_dir, PROGRESS_FILE)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed_skus": [], "source_file": ""}


def save_progress(output_dir: str, progress: dict):
    """Save progress to JSON file (called after each product)"""
    path = os.path.join(output_dir, PROGRESS_FILE)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2)


def reset_progress(output_dir: str):
    """Delete the progress file"""
    path = os.path.join(output_dir, PROGRESS_FILE)
    if os.path.exists(path):
        os.remove(path)
        print(f"Progress reset. Deleted {path}")


class WooCommerceCSVGeneratorAI:
    """Generate WooCommerce CSV files using AI"""
    
    def __init__(self, excel_path: str, output_dir: str = None, api_key: str = None):
        self.excel_path = excel_path
        self.output_dir = output_dir or Config.OUTPUT_DIR
        self.api_key = api_key or Config.GEMINI_API_KEY
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        print("Initializing Excel parser...")
        self.parser = EnhancedExcelParser(excel_path)
        print("Initializing Gemini AI client...")
        self.ai_generator = AIContentGenerator(api_key=self.api_key)
        print("Ready.\n")
        self.csv_converter = JSONToCSVConverter()
    
    def process(self, exclude_sheets: list = None, limit: int = 10, reset: bool = False) -> str:
        """Process Excel file and generate WooCommerce CSV"""
        
        # Handle reset
        if reset:
            reset_progress(self.output_dir)
        
        # Load progress
        progress = load_progress(self.output_dir)
        processed_skus = set(progress.get("processed_skus", []))
        
        # Read Excel
        print(f"Reading Excel file: {self.excel_path}")
        self.parser.read_excel()
        
        # Extract products
        print("Extracting products from Excel sheets...\n")
        all_products = self.parser.parse_all_sheets(exclude_sheets=exclude_sheets)
        total_in_excel = len(all_products)
        
        if total_in_excel == 0:
            print("No products found. Please check your Excel file structure.")
            return None
        
        # Filter out already-processed products
        unprocessed = [p for p in all_products if p.get('_sku') not in processed_skus]
        already_done = total_in_excel - len(unprocessed)
        
        # Slice by limit
        products_to_process = unprocessed[:limit]
        
        # Print summary
        print("=== Excel Summary ===")
        print(f"  Total products in Excel: {total_in_excel}")
        print(f"  Already processed (previous runs): {already_done}")
        print(f"  Remaining unprocessed: {len(unprocessed)}")
        print(f"  Processing this run: {len(products_to_process)}")
        print("=====================\n")
        
        if len(products_to_process) == 0:
            print("All products have already been processed. Use --reset to start over.")
            return None
        
        # Process through AI (one product per API call)
        processed_products = []
        run_total = len(products_to_process)
        interrupted = False
        
        try:
            for i, product in enumerate(products_to_process):
                sku = product.get('_sku', 'unknown')
                
                try:
                    result = self.ai_generator.process_single_product(product, index=i + 1, total=run_total)
                    
                    if self.ai_generator.validate_product(result):
                        processed_products.append(result)
                        
                        # Save progress immediately after each successful product
                        progress["processed_skus"].append(sku)
                        progress["source_file"] = self.excel_path
                        save_progress(self.output_dir, progress)
                        processed_skus.add(sku)
                    else:
                        print(f"  [{i+1}/{run_total}] WARN - Skipped (validation failed): {sku}")
                        
                except KeyboardInterrupt:
                    print(f"\n\n  Interrupted at product {i+1}/{run_total}. Saving progress...")
                    interrupted = True
                    break
                except Exception as e:
                    err_msg = str(e)[:150]
                    print(f"\n  [{i+1}/{run_total}] ERROR - {sku}: {err_msg}")
                    continue
        except KeyboardInterrupt:
            print(f"\n\n  Interrupted. Saving progress...")
            interrupted = True
        
        if len(processed_products) == 0:
            print("\nNo products were successfully processed.")
            return None
        
        # Generate timestamped CSV
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        csv_filename = f"woocommerce_{timestamp}.csv"
        csv_path = os.path.join(self.output_dir, csv_filename)
        self.csv_converter.generate_csv(processed_products, csv_path)
        
        # Final summary
        total_processed_overall = len(progress.get("processed_skus", []))
        remaining = total_in_excel - total_processed_overall
        
        if interrupted:
            print("\n=== Run Interrupted (data saved) ===")
        else:
            print("\n=== Run Complete ===")
        print(f"  Processed this run: {len(processed_products)}/{run_total} successful")
        print(f"  Total processed overall: {total_processed_overall}/{total_in_excel}")
        print(f"  Remaining: {remaining}")
        print(f"  CSV saved: {csv_path}")
        print("====================")
        
        return csv_path


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Generate WooCommerce CSV files from Excel using Gemini AI'
    )
    parser.add_argument(
        'excel_file',
        help='Path to Excel file containing product data'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Number of unprocessed products to process this run (default: 10)'
    )
    parser.add_argument(
        '--output-dir',
        default=None,
        help=f'Output directory for CSV file (default: {Config.OUTPUT_DIR})'
    )
    parser.add_argument(
        '--api-key',
        default=None,
        help='Gemini API key (or set GEMINI_API_KEY environment variable)'
    )
    parser.add_argument(
        '--exclude-sheets',
        nargs='+',
        default=None,
        help='Sheet names to exclude from processing'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset progress tracking and start from scratch'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.excel_file):
        print(f"Error: Excel file not found: {args.excel_file}")
        sys.exit(1)
    
    api_key = args.api_key or Config.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: Gemini API key is required.")
        print("Set it using --api-key argument, GEMINI_API_KEY environment variable, or in config.py")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
        sys.exit(1)
    
    generator = WooCommerceCSVGeneratorAI(
        args.excel_file,
        output_dir=args.output_dir,
        api_key=api_key,
    )
    
    exclude_sheets = args.exclude_sheets or Config.EXCLUDE_SHEETS
    generator.process(exclude_sheets=exclude_sheets, limit=args.limit, reset=args.reset)


if __name__ == '__main__':
    main()
