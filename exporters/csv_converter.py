"""
Convert AI JSON response to WooCommerce CSV format
"""

import csv
import os
from typing import List, Dict, Any

MAX_ATTRIBUTES = 10


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
        ]
        for i in range(1, MAX_ATTRIBUTES + 1):
            self.columns += [
                f'Attribute {i} name', f'Attribute {i} value(s)',
                f'Attribute {i} visible', f'Attribute {i} global',
            ]
        self.columns += [
            'Meta: _yoast_wpseo_focuskw', 'Meta: _yoast_wpseo_metadesc',
            'Image Alt Text', 'Image Caption', 'Image Description',
        ]
    
    def expand_category_hierarchy(self, category_path: str) -> List[str]:
        """Expand a category path into all ancestor paths.
        'A > B > C' becomes ['A', 'A > B', 'A > B > C']
        so the product is assigned to every level in WooCommerce.
        """
        parts = [p.strip() for p in category_path.split('>')]
        return [' > '.join(parts[:i + 1]) for i in range(len(parts))]
    
    def format_categories(self, categories) -> str:
        """Format categories for WooCommerce CSV (comma-separated, full hierarchy).
        Each deepest path is expanded so the product belongs to every ancestor category.
        Handles AI returning a string instead of a list.
        """
        if not categories:
            return ""
        # AI sometimes returns a string instead of a list -- wrap it
        if isinstance(categories, str):
            categories = [categories]
        all_paths = []
        for cat in categories:
            for path in self.expand_category_hierarchy(cat):
                if path not in all_paths:
                    all_paths.append(path)
        return ', '.join(all_paths)
    
    def format_tags(self, tags) -> str:
        """Format tags for WooCommerce (comma-separated)"""
        if not tags:
            return ""
        if isinstance(tags, str):
            tags = [tags]
        return ', '.join(str(t) for t in tags)
    
    def format_attributes(self, brand: str, attributes: Dict[str, Any]) -> Dict[str, str]:
        """Format brand + attributes for WooCommerce CSV.
        Attribute 1 is always Brand (global=1 so WooCommerce creates the term).
        Attributes 2+ are product specs from the AI.
        """
        formatted = {}
        for i in range(1, MAX_ATTRIBUTES + 1):
            formatted[f'Attribute {i} name'] = ''
            formatted[f'Attribute {i} value(s)'] = ''
            formatted[f'Attribute {i} visible'] = ''
            formatted[f'Attribute {i} global'] = ''

        # Attribute 1: Brand (global so WoodMart recognizes it)
        if brand:
            formatted['Attribute 1 name'] = 'Product brand'
            formatted['Attribute 1 value(s)'] = str(brand)
            formatted['Attribute 1 visible'] = '1'
            formatted['Attribute 1 global'] = '1'

        if not attributes:
            return formatted

        # Attributes 2+: product specs
        attr_items = list(attributes.items())[:MAX_ATTRIBUTES - 1]

        for i, (attr_name, attr_value) in enumerate(attr_items, 2):
            formatted[f'Attribute {i} name'] = str(attr_name)

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
            'Images': '',
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
        
        # Add brand as Attribute 1 (global) + AI attributes as Attribute 2+
        attributes = self.format_attributes(
            brand=product.get('brand', ''),
            attributes=product.get('attributes', {}),
        )
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
