"""
Load product categories from text file.
Each line is a full category path like 'Networking > Routers > TP-Link Routers'.
"""

from typing import List


class CategoryExtractor:
    """Load and format categories from text file"""
    
    def __init__(self, categories_file: str = "product_categories.txt"):
        self.categories_file = categories_file
        self.categories: List[str] = []
        
    def load_categories(self) -> List[str]:
        """Load categories from text file (one path per line)"""
        with open(self.categories_file, 'r', encoding='utf-8') as f:
            self.categories = [line.strip() for line in f if line.strip()]
        return self.categories
    
    def format_for_prompt(self) -> str:
        """Format categories for inclusion in the AI prompt"""
        if not self.categories:
            self.load_categories()
        
        lines = ["EXISTING PRODUCT CATEGORIES (map products to these, do NOT create new categories):\n"]
        for category in self.categories:
            lines.append(f"- {category}")
        
        return "\n".join(lines) + "\n"
    
    def get_categories_list(self) -> List[str]:
        """Get list of all categories"""
        if not self.categories:
            self.load_categories()
        return self.categories
