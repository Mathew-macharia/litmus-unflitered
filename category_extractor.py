"""
Extract product categories from text file
Simple and straightforward category loader
"""

from typing import List


class CategoryExtractor:
    """Extract and format categories from text file"""
    
    def __init__(self, categories_file: str = "product_categories.txt"):
        self.categories_file = categories_file
        self.categories = []
        
    def load_categories(self) -> List[str]:
        """Load categories from text file"""
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse hierarchical structure
            categories = []
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Skip tree structure markers
                if line.startswith('├──') or line.startswith('└──') or line.startswith('│'):
                    # Extract category name
                    category = line.replace('├──', '').replace('└──', '').replace('│', '').strip()
                    if category:
                        # Build full path
                        categories.append(category)
                elif line and not line.startswith('None'):
                    # Top-level category
                    categories.append(line)
            
            # Also extract full hierarchical paths
            full_categories = self._build_hierarchical_paths(content)
            
            self.categories = full_categories if full_categories else categories
            return self.categories
            
        except Exception as e:
            raise Exception(f"Error loading categories: {str(e)}")
    
    def _build_hierarchical_paths(self, content: str) -> List[str]:
        """Build full hierarchical category paths"""
        categories = []
        lines = content.split('\n')
        stack = []  # Track current path
        
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped == 'None':
                continue
            
            # Determine depth
            if not line.startswith('├──') and not line.startswith('└──') and not line.startswith('│'):
                # Top level
                stack = [stripped]
                categories.append(stripped)
            else:
                # Count depth
                depth = 0
                for char in line:
                    if char in ['│', '├', '└']:
                        depth += 1
                    elif char == '─':
                        break
                    else:
                        break
                
                # Extract category name
                category = stripped.replace('├──', '').replace('└──', '').replace('│', '').strip()
                if category:
                    # Adjust stack to current depth
                    stack = stack[:depth]
                    stack.append(category)
                    
                    # Build full path
                    full_path = ' > '.join(stack)
                    categories.append(full_path)
        
        return categories
    
    def format_for_prompt(self) -> str:
        """Format categories for inclusion in Claude prompt"""
        if not self.categories:
            self.load_categories()
        
        formatted = "EXISTING PRODUCT CATEGORIES (map products to these, do NOT create new categories):\n\n"
        
        for category in self.categories:
            formatted += f"- {category}\n"
        
        return formatted
    
    def get_categories_list(self) -> List[str]:
        """Get list of all categories"""
        if not self.categories:
            self.load_categories()
        return self.categories


if __name__ == '__main__':
    # Test
    extractor = CategoryExtractor()
    categories = extractor.load_categories()
    print(f"Loaded {len(categories)} categories")
    print("\nFirst 10 categories:")
    for cat in categories[:10]:
        print(f"  - {cat}")
