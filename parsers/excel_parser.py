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
    
    @staticmethod
    def _normalize(name: str) -> str:
        """Collapse a sheet name to a canonical form for fuzzy matching.
        Lowercases, then strips all spaces, hyphens, and underscores so that
        'Home page', 'Homepage', 'home-page', 'Home_Page' all become 'homepage'.
        """
        return re.sub(r'[\s\-_]+', '', name.strip().lower())
        
    def find_header_row(self, df_raw: "pd.DataFrame", max_scan: int = 20) -> int:
        """Scan the first max_scan rows to find the real column-header row.

        Returns the 0-based row index with the highest count of header-like
        keywords.  Returns 0 (pandas default) if nothing better is found.
        """
        HEADER_KEYWORDS = [
            'part', 'model', 'sku', 'item', 'product', 'description', 'desc',
            'name', 'details', 'price', 'cost', 'qty', 'quantity', 'stock',
            'availability', 'avail', 'code', 'reference', 'ref',
            'number', 'num', 'brand', 'category', 'sap', 'uom', 'unit',
        ]
        best_row = 0
        best_score = 0
        for row_idx in range(min(max_scan, len(df_raw))):
            row = df_raw.iloc[row_idx]
            score = sum(
                1 for val in row
                if pd.notna(val) and
                   any(kw in str(val).strip().lower() for kw in HEADER_KEYWORDS)
            )
            if score > best_score:
                best_score = score
                best_row = row_idx
        return best_row

    def read_excel(self, sheet_name: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """Read Excel file, auto-detecting the real header row per sheet."""
        try:
            # First pass: no header so we can scan every row freely
            raw_sheets = pd.read_excel(self.excel_path, sheet_name=sheet_name, header=None)
            if isinstance(raw_sheets, pd.DataFrame):
                raw_sheets = {'Sheet1': raw_sheets}

            self.sheets = {}
            for name, raw_df in raw_sheets.items():
                header_row = self.find_header_row(raw_df)
                df = pd.read_excel(self.excel_path, sheet_name=name, header=header_row)
                self.sheets[name] = df

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
            
            # Identify SKU/model column using prioritised matching.
            # Priority tiers handle the many naming conventions seen across
            # supplier sheets made by different people:
            #   Tier 1 – unambiguous SKU identifiers
            #   Tier 2 – model/part number variants
            #   Tier 3 – product/item number variants
            #   Tier 4 – broader fallbacks (code, ref, article, mpn…)
            SKU_PRIORITY = [
                # Tier 1: explicit SKU
                ['sku'],
                # Tier 2: part number variants
                ['part no', 'part number', 'part num', 'part#', 'part #',
                 'part_no', 'partno', 'partnumber'],
                # Tier 3: model number variants
                ['model no', 'model number', 'model num', 'model#', 'model #',
                 'model_no', 'modelno', 'modelnumber'],
                # Tier 4: product / item number variants
                ['product no', 'product number', 'product num', 'product#', 'product #',
                 'product code', 'product_no', 'productno',
                 'item no', 'item number', 'item num', 'item#', 'item #',
                 'item code', 'item_no', 'itemno'],
                # Tier 5: bare "model" or "part" column
                ['model', 'part'],
                # Tier 6: other common identifiers
                ['reference', 'ref no', 'ref number', 'ref#', 'ref',
                 'catalog no', 'cat no', 'catalogue no',
                 'article no', 'article number', 'article',
                 'mpn', 'sap code', 'sap', 'code'],
            ]

            sku = None
            for tier in SKU_PRIORITY:
                for key in product_data.keys():
                    key_norm = str(key).strip().lower().replace('_', ' ')
                    if any(key_norm == term or key_norm.startswith(term) for term in tier):
                        sku = product_data[key]
                        product_data['_sku'] = sku
                        break
                if sku:
                    break

            # If no SKU column matched, generate a positional fallback
            if not sku:
                sku = f"PROD-{sheet_name}-{idx}"
                product_data['_sku'] = sku
            
            products.append(product_data)
        
        return products
    
    def parse_all_sheets(self, exclude_sheets: List[str] = None) -> List[Dict]:
        """Parse all sheets and extract products"""
        if exclude_sheets is None:
            exclude_sheets = ['Home page', 'Main Page', 'Rental', 'Services']
            
        normalized_excludes = {self._normalize(s) for s in exclude_sheets}
        
        all_products = []
        
        for sheet_name, df in self.sheets.items():
            if self._normalize(sheet_name) in normalized_excludes:
                continue
            
            print(f"Processing sheet: {sheet_name}")
            products = self.extract_products(df, sheet_name)
            all_products.extend(products)
            print(f"  Found {len(products)} products")
        
        return all_products
