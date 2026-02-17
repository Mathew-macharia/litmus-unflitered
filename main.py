"""
AI-Powered WooCommerce CSV Generator
Main script that orchestrates the entire process
"""

import os
import sys
import argparse
from parsers.excel_parser import EnhancedExcelParser
from ai.content_generator import AIContentGenerator
from exporters.csv_converter import JSONToCSVConverter
from config import Config


class WooCommerceCSVGeneratorAI:
    """Generate WooCommerce CSV files using AI"""
    
    def __init__(self, excel_path: str, output_dir: str = None, api_key: str = None, batch_size: int = None):
        self.excel_path = excel_path
        self.output_dir = output_dir or Config.OUTPUT_DIR
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.batch_size = batch_size or Config.BATCH_SIZE
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize components
        self.parser = EnhancedExcelParser(excel_path)
        self.ai_generator = AIContentGenerator(api_key=self.api_key)
        self.csv_converter = JSONToCSVConverter()
    
    def process(self, exclude_sheets: list = None) -> str:
        """Process Excel file and generate WooCommerce CSV"""
        print(f"Reading Excel file: {self.excel_path}")
        
        # Read Excel
        self.parser.read_excel()
        
        # Extract products
        print("\nExtracting products from Excel sheets...")
        all_products = self.parser.parse_all_sheets(exclude_sheets=exclude_sheets)
        
        print(f"\nTotal products found: {len(all_products)}")
        
        if len(all_products) == 0:
            print("No products found. Please check your Excel file structure.")
            return None
        
        # Take a smaller subset for initial sample generation (e.g., first 5 products)
        products_to_process = all_products[:10]
        print(f"Processing a sample of {len(products_to_process)} products for review...")

        # Process through AI (one product at a time)
        print(f"\nProcessing products through Gemini API (one product at a time)...")
        processed_products = self.ai_generator.process_all(products_to_process)
        
        if len(processed_products) == 0:
            print("No products were successfully processed.")
            return None
        
        # Generate CSV
        print(f"\nGenerating WooCommerce CSV file...")
        csv_path = os.path.join(self.output_dir, "woocommerce_products_ai_generated.csv")
        self.csv_converter.generate_csv(processed_products, csv_path)
        
        print(f"\n[SUCCESS] Generated CSV file: {os.path.abspath(csv_path)}")
        print(f"  Total products: {len(processed_products)}")
        
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
        '--output-dir',
        default=None,
        help=f'Output directory for CSV file (default: {Config.OUTPUT_DIR})'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=None,
        help=f'Number of products per API call (default: {Config.BATCH_SIZE})'
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
    
    args = parser.parse_args()
    
    # Check if Excel file exists
    if not os.path.exists(args.excel_file):
        print(f"Error: Excel file not found: {args.excel_file}")
        sys.exit(1)
    
    # Check API key
    api_key = args.api_key or Config.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Error: Gemini API key is required.")
        print("Set it using --api-key argument, GEMINI_API_KEY environment variable, or in config.py")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
        sys.exit(1)
    
    # Create generator and process
    generator = WooCommerceCSVGeneratorAI(
        args.excel_file,
        output_dir=args.output_dir,
        api_key=api_key,
        batch_size=args.batch_size
    )
    
    exclude_sheets = args.exclude_sheets or Config.EXCLUDE_SHEETS
    csv_path = generator.process(exclude_sheets=exclude_sheets)
    
    if csv_path:
        print("\nNext steps:")
        print("1. Review the generated CSV file")
        print("2. Add image URLs to the 'Images' column (comma-separated)")
        print("3. Update image metadata if needed")
        print("4. Import CSV file into WooCommerce using the Product CSV Importer")
        print("5. Verify Yoast SEO scores after import")


if __name__ == '__main__':
    main()
