"""
Enhanced Excel Parser
Handles variable Excel structures, filters non-product rows intelligently
Extracts all available data without assumptions
"""

import pandas as pd
import re
from typing import Dict, List, Optional


class EnhancedExcelParser:
    """Parse Excel files with completely variable structures"""
    
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.sheets = {}
        
    def read_excel(self, sheet_name: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """Read Excel file and return dictionary of sheets"""
        try:
            self.sheets = pd.read_excel(self.excel_path, sheet_name=sheet_name)
            if isinstance(self.sheets, pd.DataFrame):
                # Single sheet, convert to dict
                self.sheets = {'Sheet1': self.sheets}
            return self.sheets
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")
    
    def is_likely_category_header(self, row: pd.Series, df: pd.DataFrame) -> bool:
        """Determine if a row is likely a category header/subheading"""
        # Check if row has mostly empty values except one or two columns
        non_null_count = row.notna().sum()
        total_cols = len(row)
        
        # Category headers typically have 1-2 non-empty columns
        if non_null_count <= 2 and total_cols > 3:
            # Check if the non-empty value looks like a category name
            for val in row:
                if pd.notna(val):
                    val_str = str(val).strip()
                    # Category indicators
                    if any(indicator in val_str.lower() for indicator in [
                        'laptops', 'desktops', 'monitors', 'printers', 'accessories',
                        'ram', 'ssd', 'hdd', 'ups', 'bags', 'graphics', 'cards',
                        'software', 'scanners', 'keyboard', 'mouse', 'printer'
                    ]):
                        # Check if it's all caps or has specific formatting
                        if val_str.isupper() or len(val_str.split()) <= 3:
                            return True
        
        return False
    
    def is_empty_row(self, row: pd.Series) -> bool:
        """Check if row is essentially empty"""
        # Count non-null, non-empty values
        non_empty = 0
        for val in row:
            if pd.notna(val):
                val_str = str(val).strip()
                if val_str and val_str.lower() not in ['nan', 'none', '']:
                    non_empty += 1
        
        return non_empty == 0
    
    def extract_all_data(self, row: pd.Series, df: pd.DataFrame) -> Dict[str, any]:
        """Extract all available data from a row as dictionary"""
        data = {}
        for col_name in df.columns:
            val = row.get(col_name)
            if pd.notna(val):
                # Convert to string and clean
                val_str = str(val).strip()
                if val_str and val_str.lower() not in ['nan', 'none']:
                    data[str(col_name)] = val_str
        return data
    
    def extract_products(self, df: pd.DataFrame, sheet_name: str = "") -> List[Dict]:
        """Extract product data from DataFrame"""
        products = []
        
        for idx, row in df.iterrows():
            # Skip empty rows
            if self.is_empty_row(row):
                continue
            
            # Skip category headers
            if self.is_likely_category_header(row, df):
                continue
            
            # Extract all available data
            product_data = self.extract_all_data(row, df)
            
            # Must have at least some data
            if len(product_data) < 2:
                continue
            
            # Add metadata
            product_data['_sheet_name'] = sheet_name
            product_data['_row_index'] = idx
            
            # Try to identify SKU/Part No (common column names)
            sku = None
            for key in product_data.keys():
                key_lower = str(key).lower()
                if any(term in key_lower for term in ['part', 'model', 'sku', 'code', 'item']):
                    sku = product_data[key]
                    product_data['_sku'] = sku
                    break
            
            # If no SKU found, generate one
            if not sku:
                sku = f"PROD-{sheet_name}-{idx}"
                product_data['_sku'] = sku
            
            products.append(product_data)
        
        return products
    
    def parse_all_sheets(self, exclude_sheets: List[str] = None) -> List[Dict]:
        """Parse all sheets and extract products"""
        if exclude_sheets is None:
            exclude_sheets = ['Home page', 'Main Page', 'Rental', 'Services']
            
        # Normalize to lowercase and strip whitespace for robust matching
        normalized_excludes = [s.strip().lower() for s in exclude_sheets]
        
        all_products = []
        
        for sheet_name, df in self.sheets.items():
            if sheet_name.strip().lower() in normalized_excludes:
                continue
            
            print(f"Processing sheet: {sheet_name}")
            products = self.extract_products(df, sheet_name)
            all_products.extend(products)
            print(f"  Found {len(products)} products")
        
        return all_products
