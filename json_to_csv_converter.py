"""
Convert Claude JSON response to WooCommerce CSV format
"""

import csv
import os
from typing import List, Dict, Any


class JSONToCSVConverter:
    """Convert processed product JSON to WooCommerce CSV"""
    
    def __init__(self):
        # WooCommerce CSV columns
        self.columns = [
            'Type', 'SKU', 'Name', 'Published', 'Is featured', 'Visibility in catalog',
            'Short description', 'Description', 'Date sale price starts', 'Date sale price ends',
            'Tax status', 'Tax class', 'In stock?', 'Stock', 'Backorders allowed?',
            'Sold individually?', 'Weight (kg)', 'Length (cm)', 'Width (cm)', 'Height (cm)',
            'Allow customer reviews?', 'Purchase note', 'Sale price', 'Regular price',
            'Categories', 'Tags', 'Shipping class', 'Images', 'Download limit',
            'Download expiry days', 'Parent', 'Grouped products', 'Upsells', 'Cross-sells',
            'External URL', 'Button text', 'Position',
            'Attribute 1 name', 'Attribute 1 value(s)', 'Attribute 1 visible', 'Attribute 1 global',
            'Attribute 2 name', 'Attribute 2 value(s)', 'Attribute 2 visible', 'Attribute 2 global',
            'Attribute 3 name', 'Attribute 3 value(s)', 'Attribute 3 visible', 'Attribute 3 global',
            'Meta: _yoast_wpseo_focuskw', 'Meta: _yoast_wpseo_metadesc',
            'Image Alt Text', 'Image Caption', 'Image Description'
        ]
    
    def format_categories(self, categories: List[str]) -> str:
        """Format categories for WooCommerce (pipe-separated)"""
        if not categories:
            return ""
        return " | ".join(categories)
    
    def format_tags(self, tags: List[str]) -> str:
        """Format tags for WooCommerce (pipe-separated)"""
        if not tags:
            return ""
        return " | ".join(tags)
    
    def format_attributes(self, attributes: Dict[str, Any]) -> Dict[str, str]:
        """Format attributes for WooCommerce CSV"""
        formatted = {
            'Attribute 1 name': '',
            'Attribute 1 value(s)': '',
            'Attribute 1 visible': '',
            'Attribute 1 global': '',
            'Attribute 2 name': '',
            'Attribute 2 value(s)': '',
            'Attribute 2 visible': '',
            'Attribute 2 global': '',
            'Attribute 3 name': '',
            'Attribute 3 value(s)': '',
            'Attribute 3 visible': '',
            'Attribute 3 global': '',
        }
        
        if not attributes:
            return formatted
        
        # Take first 3 attributes
        attr_items = list(attributes.items())[:3]
        
        for i, (attr_name, attr_value) in enumerate(attr_items, 1):
            formatted[f'Attribute {i} name'] = str(attr_name)
            
            # Handle value (could be string, list, or other)
            if isinstance(attr_value, list):
                formatted[f'Attribute {i} value(s)'] = " | ".join(str(v) for v in attr_value)
            else:
                formatted[f'Attribute {i} value(s)'] = str(attr_value)
            
            formatted[f'Attribute {i} visible'] = '1'
            formatted[f'Attribute {i} global'] = '0'
        
        return formatted
    
    def convert_product(self, product: Dict) -> Dict[str, str]:
        """Convert a single product JSON to CSV row"""
        row = {
            'Type': 'simple',
            'SKU': str(product.get('sku', '')),
            'Name': str(product.get('name', '')),
            'Published': '1',
            'Is featured': '0',
            'Visibility in catalog': 'visible',
            'Short description': str(product.get('short_description', '')),
            'Description': str(product.get('description', '')),
            'Date sale price starts': '',
            'Date sale price ends': '',
            'Tax status': 'taxable',
            'Tax class': '',
            'In stock?': '1' if product.get('stock_status', 'instock') == 'instock' else '0',
            'Stock': '',
            'Backorders allowed?': '0',
            'Sold individually?': '0',
            'Weight (kg)': '',
            'Length (cm)': '',
            'Width (cm)': '',
            'Height (cm)': '',
            'Allow customer reviews?': '1',
            'Purchase note': '',
            'Sale price': '',
            'Regular price': str(int(product.get('price', 0))) if product.get('price') else '',
            'Categories': self.format_categories(product.get('categories', [])),
            'Tags': self.format_tags(product.get('tags', [])),
            'Shipping class': '',
            'Images': '',  # User will add manually
            'Download limit': '',
            'Download expiry days': '',
            'Parent': '',
            'Grouped products': '',
            'Upsells': '',
            'Cross-sells': '',
            'External URL': '',
            'Button text': '',
            'Position': '0',
            'Meta: _yoast_wpseo_focuskw': str(product.get('focus_keyphrase', '')),
            'Meta: _yoast_wpseo_metadesc': str(product.get('meta_description', '')),
            'Image Alt Text': str(product.get('name', '')),
            'Image Caption': f"{product.get('name', '')} - Product Image",
            'Image Description': f"High-quality image of {product.get('name', '')} showing design and features",
        }
        
        # Add attributes
        attributes = self.format_attributes(product.get('attributes', {}))
        row.update(attributes)
        
        return row
    
    def generate_csv(self, products: List[Dict], output_path: str):
        """Generate WooCommerce CSV file from processed products"""
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.columns, extrasaction='ignore')
            writer.writeheader()
            
            for product in products:
                try:
                    row = self.convert_product(product)
                    writer.writerow(row)
                except Exception as e:
                    print(f"    Warning: Error converting product {product.get('sku', 'unknown')}: {e}")
                    continue
        
        print(f"    [OK] Generated CSV: {output_path} ({len(products)} products)")
