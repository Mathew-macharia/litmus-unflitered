# WooCommerce CSV Import Guide

This guide will help you use the generated CSV files to import products into WooCommerce with Yoast SEO compliance.

## Prerequisites

- WordPress site with WooCommerce installed
- Yoast SEO plugin installed and activated
- Product CSV Importer (built into WooCommerce) or WP All Import plugin (for advanced features)

## Step 1: Generate CSV File

Run the AI-powered script to generate WooCommerce CSV file from your Excel file:

```bash
python generate_woocommerce_csv_ai.py "your_excel_file.xlsx" --batch-size 15 --output-dir output
```

**Parameters:**
- `your_excel_file.xlsx`: Path to your Excel file
- `--batch-size`: Number of products per Claude API call (default: 15, recommended: 10-20)
- `--output-dir`: Directory where CSV file will be saved (default: `output`)
- `--api-key`: Your Claude API key (or set in config.py/environment variable)

**Example:**
```bash
python generate_woocommerce_csv_ai.py "DN Solutions Ltd - Price list for the month of October 2025 Ver 2.2.xlsx" --batch-size 15
```

**Note:** You need a Claude API key from Anthropic. Set it in `config.py`, as environment variable `CLAUDE_API_KEY`, or via `--api-key` argument.

This will create a single CSV file in the `output` directory with all products processed through Claude AI.

## Step 2: Review Generated CSV File

Before importing, review the generated CSV file:

1. **Open the CSV file** in Excel or a text editor
2. **Check the following:**
   - Product names are correct and clear
   - Descriptions are 300+ words (check word count) with proper headings
   - Categories are mapped to your existing categories (not new ones)
   - Tags are relevant and appropriate (5-15 per product)
   - Attributes are extracted correctly (varies by product type)
   - Focus keyphrases are appropriate
   - Meta descriptions are 150-160 characters
   - Prices are correct
   - Stock status is set correctly

## Step 3: Add Image URLs

The generated CSV file has empty `Images` columns. You need to add image URLs:

1. **Find product images online** (download or use direct URLs)
2. **Add image URLs** to the `Images` column (comma-separated for multiple images)
   - Example: `https://example.com/image1.jpg,https://example.com/image2.jpg`
3. **Update image metadata:**
   - `Image Alt Text`: Comma-separated alt text for each image
   - `Image Caption`: Comma-separated captions
   - `Image Description`: Comma-separated descriptions

**Note:** Image metadata columns are included for WP All Import plugin. Standard WooCommerce importer may not support these columns directly.

## Step 4: Import into WooCommerce

### Using Standard WooCommerce CSV Importer

1. **Go to:** WooCommerce → Products → Import
2. **Click:** "Choose File" and select your CSV file
3. **Click:** "Continue"
4. **Map columns** (usually auto-detected correctly)
5. **Click:** "Run the importer"
6. **Wait for import to complete**

**Note:** The AI generates a single CSV file with all products, so you only need to import once.

### Using WP All Import Plugin (Recommended for Image Metadata)

1. **Install WP All Import** plugin (paid plugin, $199)
2. **Go to:** All Import → New Import
3. **Upload your CSV file**
4. **Map fields** including image metadata columns
5. **Run import**

## Step 5: Verify Yoast SEO Scores

After importing, check each product's Yoast SEO score:

1. **Go to:** Products → All Products
2. **Click on a product** to edit
3. **Scroll down** to Yoast SEO section
4. **Check the SEO score** (should be green/orange, not grey)

### Common Issues and Fixes

**Grey SEO Score (Poor):**
- **Issue:** Description too short (< 300 words)
- **Fix:** Edit product description to add more content

**Low Keyphrase Density:**
- **Issue:** Focus keyphrase not used enough
- **Fix:** Add focus keyphrase naturally throughout description

**Missing Subheadings:**
- **Issue:** No H2/H3 headings in description
- **Fix:** The generated descriptions include headings, but you may need to adjust formatting

**No Related Products:**
- **Issue:** Missing categories or tags
- **Fix:** Ensure categories and tags are properly set in CSV

## Step 6: Large Catalog Processing

For importing 3000+ products:

1. **AI Processing:** The script processes products in batches of 10-20 through Claude API
   - This ensures quality but takes time
   - Monitor API usage and costs
   - Failed batches are automatically retried

2. **Single CSV Output:** All products are combined into one CSV file
   - Import once into WooCommerce
   - Or split manually if needed for testing

3. **Add images gradually:**
   - You can import products first
   - Add images later via WordPress media library
   - Or use WP All Import to import with images

## Troubleshooting

### Import Errors

**"Invalid SKU" errors:**
- Ensure SKUs are unique
- Check for special characters in SKUs

**"Category not found" errors:**
- Categories will be created automatically if they don't exist
- Ensure category format is correct: `Parent > Child`

**"Image not found" errors:**
- Ensure image URLs are accessible
- Images must be publicly accessible (not behind authentication)

### SEO Issues

**Descriptions not showing:**
- Check if HTML formatting is preserved
- Some themes may strip HTML - check theme settings

**Focus keyphrase not detected:**
- Ensure keyphrase matches exactly (case-sensitive in some cases)
- Keyphrase should appear in first paragraph

## Best Practices

1. **Test with small batch first:** Process 10-20 products first to verify AI output quality
2. **Review AI output:** Check that descriptions are accurate and categories are mapped correctly
3. **Backup before importing:** Always backup your WordPress database before bulk imports
4. **Monitor SEO scores:** Check Yoast SEO scores after import
5. **Customize if needed:** AI-generated descriptions are high quality but can be refined
6. **Add internal links:** Manually add internal links to related products/pages for better SEO
7. **Monitor API costs:** Track Claude API usage for large catalogs

## Support

If you encounter issues:
1. Check the error messages in WooCommerce import logs
2. Verify CSV file format matches WooCommerce requirements
3. Ensure all required columns are present
4. Check WordPress/WooCommerce error logs

