# AI-Powered WooCommerce CSV Generator for Yoast SEO Compliance

A Python tool that uses **Google Gemini AI** with Google Search integration to intelligently convert Excel product data into WooCommerce-compatible CSV files with full Yoast SEO compliance. Generates 300+ word descriptions, maps products to existing categories, and creates SEO-optimized content with real-time product information.

## Features

- ✅ **AI-Powered Generation**: Uses Gemini API with Google Search for intelligent, category-appropriate content generation
- ✅ **Real-Time Search**: Automatically searches online for product specifications, competitor pricing, and current information
- ✅ **Flexible Excel Parsing**: Handles completely variable Excel structures without assumptions
- ✅ **Category Mapping**: Maps products to your existing 200+ categories (no new categories created)
- ✅ **SEO-Optimized Descriptions**: Generates 300+ word descriptions with proper structure and headings
- ✅ **Intelligent Data Selection**: Uses only the most important/relevant Excel data for descriptions
- ✅ **Online Search Capability**: Claude can search online if Excel data is insufficient for accuracy
- ✅ **Batch Processing**: Processes 10-20 products per API call for optimal quality
- ✅ **Dynamic Attributes**: Extracts relevant attributes based on product type
- ✅ **Robust Error Handling**: Gracefully handles API errors, missing data, and retries

## Problem Solved

This tool addresses three main issues with WooCommerce product imports:

1. **Yoast SEO Failures**: AI generates 300+ word descriptions with proper structure, headings, and keyphrase integration
2. **Missing Related Products**: Maps products to your existing categories and generates relevant tags
3. **Incomplete Image Metadata**: Includes image metadata columns (requires WP All Import plugin for full support)

## Prerequisites

- Python 3.7+
- Gemini API key from Google (get it at https://makersuite.google.com/app/apikey)
- Excel file with product data (any structure)

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set your Gemini API key:**
   - Option 1: Set environment variable
     ```bash
     export GEMINI_API_KEY="your-api-key-here"
     ```
   - Option 2: Edit `config.py` and set `GEMINI_API_KEY`
   - Option 3: Pass via command line: `--api-key your-key`
   - Get your API key from: https://makersuite.google.com/app/apikey

3. **Verify installation:**
```bash
python --version  # Should be Python 3.7+
python -c "import google.generativeai as genai; print('Gemini API ready!')"
```

## Quick Start

1. **Prepare your Excel file:**
   - Can have any column structure
   - Multiple sheets supported
   - Category headers/subheadings are automatically filtered

2. **Run the script:**
```bash
python generate_woocommerce_csv_ai.py "your_excel_file.xlsx" --batch-size 15
```

3. **Review generated CSV:**
   - File saved in `output` directory
   - Contains all products with AI-generated content

4. **Add image URLs:**
   - Open CSV in Excel
   - Add image URLs to `Images` column (comma-separated)

5. **Import into WooCommerce:**
   - Use WooCommerce Product CSV Importer
   - Or WP All Import plugin for advanced features

## Usage

### Basic Usage

```bash
python generate_woocommerce_csv_ai.py "excel_file.xlsx"
```

### Advanced Usage

```bash
python generate_woocommerce_csv_ai.py "excel_file.xlsx" \
    --batch-size 15 \
    --output-dir my_output \
    --api-key your-claude-api-key \
    --exclude-sheets "Home page" "Rental" "Services"
```

### Parameters

- `excel_file`: Path to Excel file (required)
- `--batch-size`: Number of products per API call (default: 15, recommended: 10-20)
- `--output-dir`: Output directory for CSV file (default: `output`)
- `--api-key`: Claude API key (or set in config.py/environment)
- `--exclude-sheets`: Sheet names to exclude from processing

## File Structure

```
.
├── generate_woocommerce_csv_ai.py  # Main script
├── enhanced_excel_parser.py        # Excel file parser (handles any structure)
├── category_extractor.py           # Loads categories from product_categories.txt
├── gemini_api_client.py            # Gemini API integration with Google Search
├── prompt_templates.py             # AI prompt builder (CRITICAL)
├── ai_content_generator.py        # Orchestrates AI processing
├── json_to_csv_converter.py       # Converts AI JSON to WooCommerce CSV
├── config.py                       # Configuration settings
├── product_categories.txt          # Your existing category list
├── requirements.txt                # Python dependencies
├── woocommerce_csv_template.csv   # CSV template example
├── IMPORT_GUIDE.md                 # Import instructions
├── IMAGE_METADATA_SETUP.md         # Image metadata guide
└── README.md                       # This file
```

## How It Works

1. **Excel Parsing**: Reads Excel file and extracts all available data from any column structure
2. **Product Extraction**: Intelligently filters out category headers, empty rows, and non-product data
3. **Category Loading**: Loads your existing 200+ categories from `product_categories.txt`
4. **AI Processing**: Sends 10-20 products per batch to Gemini API with:
   - All available product data
   - Your category list for mapping
   - Detailed instructions for generating SEO-optimized content
   - Google Search capability for real-time product information
   - Location context (Nairobi CBD) and competitor websites
5. **Content Generation**: Gemini generates for EACH product:
   - 300+ word SEO description with headings
   - Category mapping (to your existing categories)
   - Relevant tags (5-15 per product)
   - Dynamic attributes (varies by product type)
   - Focus keyphrase and meta description
6. **CSV Conversion**: Converts AI JSON response to WooCommerce CSV format
7. **Output**: Generates single CSV file ready for WooCommerce import

## Excel File Format

The tool handles **completely variable Excel structures**. Examples:

### Format 1: Standard
| Part No / Model No | Product Description | Availability | Sale Price |
|-------------------|-------------------|--------------|------------|
| B67B3EA | HP 15-fd0474nia, Intel Core i3... | Ex-Stock | 75000 |

### Format 2: Different Columns
| SKU | Item Name | Stock | Price | Notes |
|-----|-----------|-------|-------|-------|
| ABC123 | Product details here... | In Stock | 50000 | Additional info |

### What's Supported
- ✅ Any column names (automatically detected)
- ✅ Missing descriptions (AI generates from available data)
- ✅ Different availability formats
- ✅ Multiple sheets (one per category)
- ✅ Category headers/subheadings (automatically filtered)
- ✅ Empty rows (automatically skipped)

## Category System

The tool uses your existing categories from `product_categories.txt`:
- **200+ categories** in hierarchical structure
- Products are **mapped** to existing categories (not created)
- Format: `"Computing > Laptops > HP Laptops"`

## Generated CSV Format

The generated CSV includes all WooCommerce standard columns plus:

- **SEO Fields:**
  - `Meta: _yoast_wpseo_focuskw`: AI-generated focus keyphrase
  - `Meta: _yoast_wpseo_metadesc`: AI-generated meta description (150-160 chars)

- **Image Metadata:**
  - `Image Alt Text`: Auto-generated from product name
  - `Image Caption`: Product image caption
  - `Image Description`: Image description

- **Product Attributes:**
  - Dynamically extracted based on product type
  - Examples: Processor, RAM, Storage, Display, etc.

## Documentation

- **[IMPORT_GUIDE.md](IMPORT_GUIDE.md)**: Step-by-step guide for importing CSV files into WooCommerce
- **[IMAGE_METADATA_SETUP.md](IMAGE_METADATA_SETUP.md)**: Guide for handling image metadata

## Troubleshooting

### Gemini API Key Not Set
```
Error: Gemini API key is required.
```
**Solution:** Set API key in `config.py`, environment variable, or `--api-key` argument. Get your key from https://makersuite.google.com/app/apikey

### API Rate Limits
```
Gemini API error: Rate limit exceeded
```
**Solution:** Reduce batch size or wait before retrying. The tool automatically retries failed batches.

### No Products Found
```
No products found. Please check your Excel file structure.
```
**Solution:** 
- Verify Excel file has product data
- Check that rows aren't being filtered as category headers
- Ensure products have some identifying data (SKU, name, etc.)

### JSON Parsing Errors
```
Could not extract JSON from Claude response
```
**Solution:** 
- Check API key is valid
- Verify internet connection
- Try smaller batch size (10 products)

## Configuration

Edit `config.py` to customize:

```python
GEMINI_API_KEY = "your-key-here"  # Or use environment variable
BATCH_SIZE = 15  # Products per API call (10-20 recommended)
OUTPUT_DIR = "output"  # Output directory
CATEGORIES_FILE = "product_categories.txt"  # Category list file
LOCATION = "Nairobi CBD, Kenya"  # Your location
COMPETITORS = ["supremenetworks.co.ke", "almiria.co.ke", "dataworld.co.ke"]  # Competitor sites
```

## API Costs

- Gemini API has free tier with generous limits
- Paid tier charges per token used
- Batch size of 15 products typically uses ~50,000-100,000 tokens per batch
- Google Search integration may add additional API calls
- Check Google AI Studio pricing for current rates

## Best Practices

1. **Test First**: Start with small batch (10 products) to verify output quality
2. **Review Descriptions**: Check AI-generated descriptions match your quality standards
3. **Category Mapping**: Verify products are mapped to correct categories
4. **Add Images**: Add image URLs before importing for best results
5. **Verify SEO Scores**: Check Yoast SEO scores after import
6. **Backup**: Always backup WordPress database before bulk imports
7. **Batch Size**: Use 10-20 products per batch for optimal quality vs cost

## Limitations

1. **Image Metadata**: Standard WooCommerce importer doesn't support image metadata columns. Use WP All Import plugin ($199) for full support.

2. **API Costs**: Claude API usage incurs costs. Monitor usage and adjust batch size as needed.

3. **Internet Required**: Requires internet connection for Claude API calls.

4. **Processing Time**: AI processing takes time (several seconds per batch). Large product catalogs may take hours.

## Support

For issues or questions:
1. Check documentation files
2. Review error messages
3. Verify API key is set correctly
4. Test with small batch first
5. Check Claude API status if errors persist

## License

This tool is provided as-is for use with WooCommerce product imports.
