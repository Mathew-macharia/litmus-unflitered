# Image Metadata Setup Guide

This guide explains how to handle image metadata (Alt Text, Caption, Description) when importing products into WooCommerce.

## The Problem

Standard WooCommerce CSV importer does **not** support importing image metadata (Alt Text, Caption, Description) directly. These fields are included in the generated CSV files but need special handling.

## Solution Options

### Option 1: WP All Import Plugin (Recommended)

**WP All Import** is a premium plugin ($199) that supports importing image metadata.

#### Setup Steps:

1. **Purchase and install WP All Import:**
   - Visit: https://www.wpallimport.com/
   - Purchase license
   - Install plugin in WordPress

2. **Create new import:**
   - Go to: All Import → New Import
   - Upload your CSV file
   - Select "Products" as import type

3. **Map image metadata fields:**
   - In the mapping section, find "Images" section
   - Map `Image Alt Text` column to "Alt Text"
   - Map `Image Caption` column to "Caption"
   - Map `Image Description` column to "Description"

4. **Run import:**
   - Preview import to verify mapping
   - Run import

**Pros:**
- Full support for image metadata
- Can import images from URLs
- Handles multiple images per product
- Professional import tool

**Cons:**
- Paid plugin ($199)
- Requires additional setup

### Option 2: Post-Import Script (Free Alternative)

If you don't want to use WP All Import, you can add image metadata after import using a custom script.

#### Using WordPress REST API:

Create a script to update image metadata after products are imported:

```python
import requests
import csv
import json

# WordPress site credentials
WP_URL = "https://yourwebsite.com"
WP_USERNAME = "your_username"
WP_APP_PASSWORD = "your_app_password"  # Generate in WordPress Users → Profile

def update_image_metadata():
    # Read CSV file
    with open('your_csv_file.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            sku = row['SKU']
            image_urls = row['Images'].split(',') if row['Images'] else []
            alt_texts = row['Image Alt Text'].split(',') if row['Image Alt Text'] else []
            
            # Find product by SKU
            product = find_product_by_sku(sku)
            if not product:
                continue
            
            # Update image metadata
            for i, image_url in enumerate(image_urls):
                image_id = get_image_id_by_url(image_url)
                if image_id:
                    update_image_metadata_api(image_id, alt_texts[i] if i < len(alt_texts) else '')

def find_product_by_sku(sku):
    # Use WooCommerce REST API to find product
    response = requests.get(
        f"{WP_URL}/wp-json/wc/v3/products",
        params={'sku': sku},
        auth=(WP_USERNAME, WP_APP_PASSWORD)
    )
    products = response.json()
    return products[0] if products else None

def update_image_metadata_api(image_id, alt_text):
    # Update image metadata via REST API
    data = {
        'alt_text': alt_text
    }
    response = requests.post(
        f"{WP_URL}/wp-json/wp/v2/media/{image_id}",
        json=data,
        auth=(WP_USERNAME, WP_APP_PASSWORD)
    )
    return response.json()
```

**Note:** This requires WordPress REST API access and app password setup.

### Option 3: Manual Update via WordPress Admin

For small batches, you can manually update image metadata:

1. **Import products** (images will be imported)
2. **Go to:** Media → Library
3. **Click on each image**
4. **Edit Alt Text, Caption, and Description** in the attachment details
5. **Save**

**Pros:**
- Free
- Full control

**Cons:**
- Time-consuming for large batches
- Not scalable for 3000+ products

### Option 4: Bulk Edit Plugin

Use a bulk edit plugin to update image metadata:

1. **Install:** "Media Library Assistant" or similar plugin
2. **Bulk select images**
3. **Edit metadata** in bulk
4. **Save**

## Recommended Workflow

For importing 3000+ products:

1. **Use WP All Import** if budget allows (best solution)
2. **Or use standard importer** and add image metadata later:
   - Import products with images (images will be downloaded)
   - Use bulk edit plugin or script to add metadata
   - Or manually update critical product images

## Image URL Format in CSV

In your CSV file, use this format for images:

```
Images: https://example.com/image1.jpg,https://example.com/image2.jpg
Image Alt Text: Product Name | Front View,Product Name | Side View
Image Caption: Product Name - Front View,Product Name - Side View
Image Description: High-quality image showing front view,High-quality image showing side view
```

**Important:**
- URLs must be publicly accessible
- Use comma to separate multiple images
- Ensure same number of items in each column (or leave empty)

## Best Practices

1. **Use descriptive alt text:**
   - Include product name
   - Describe what's in the image
   - Example: "HP 15-fd0474nia Laptop - Front View"

2. **Write helpful captions:**
   - Brief description of image
   - Can include product features visible in image

3. **Add detailed descriptions:**
   - More detailed than alt text
   - Can include technical details
   - Helps with SEO

4. **Optimize images before upload:**
   - Compress images for web
   - Use appropriate file sizes
   - Use descriptive filenames

## Troubleshooting

### Images Not Importing

**Issue:** Images show as broken links
- **Fix:** Ensure image URLs are publicly accessible
- **Fix:** Check URL format (must be direct links to images)

### Metadata Not Saving

**Issue:** Alt text not showing after import
- **Fix:** Use WP All Import plugin
- **Fix:** Or manually update via WordPress admin

### Multiple Images Not Working

**Issue:** Only first image imports
- **Fix:** Ensure comma-separated format is correct
- **Fix:** Check WooCommerce settings for multiple images support

## Additional Resources

- WooCommerce CSV Import Documentation: https://woocommerce.com/document/product-csv-importer-exporter/
- WP All Import Documentation: https://www.wpallimport.com/documentation/
- WordPress REST API: https://developer.wordpress.org/rest-api/


