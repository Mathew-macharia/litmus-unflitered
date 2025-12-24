"""
Gemini API Prompt Templates
THE CRITICAL COMPONENT - meticulously crafted prompts for product processing with search capabilities
"""

from typing import List, Dict
from category_extractor import CategoryExtractor
from config import Config


class PromptBuilder:
    """Build prompts for Gemini API"""
    
    def __init__(self, categories_file: str = "product_categories.txt"):
        self.category_extractor = CategoryExtractor(categories_file)
        self.categories_text = self.category_extractor.format_for_prompt()
        self.location = Config.LOCATION
        self.competitors = Config.COMPETITORS
    
    def format_product_data(self, product: Dict) -> str:
        """Format single product data for inclusion in prompt"""
        formatted = "PRODUCT DATA:\n\n"
        
        formatted += f"Product Details:\n"
        
        # Include all available data including SKU
        for key, value in product.items():
            formatted += f"  {key}: {value}\n"
        
        formatted += "\n"
        
        return formatted
    
    def build_prompt(self, products: List[Dict]) -> str:
        """Build the complete prompt for Gemini for a single product with full JSON output"""
        
        if not products or len(products) != 1:
            raise ValueError("PromptBuilder.build_prompt expects exactly one product.")
        
        product = products[0]
        product_sku = product.get('_sku', 'UNKNOWN')
        
        prompt = f"""You are a Senior Technical Product Specialist for a B2B technology retailer.
Your audience: IT professionals, network engineers, procurement managers.
Write with technical precision, not marketing fluff.

{self.categories_text}

PRODUCT SKU: {product_sku}

__CRITICAL SEO REQUIREMENTS__

1. __focus_keyphrase__: Generate FIRST (2-4 words, e.g., "HP ProBook Laptop", "Cisco Catalyst Switch").
   - This keyphrase appears in the 'name' field and meta_description
   - In the description HTML, the EXACT keyphrase phrase appears ONLY ONCE (in the first paragraph)
   - EVERYWHERE ELSE in description, use SYNONYMS or DIFFERENT WORDING

2. __name__: Format as "[Product Name containing keyphrase] - {product_sku}"
   The name MUST contain all words from your focus_keyphrase.
   Example: If keyphrase is "HP ProBook Laptop", name could be "HP ProBook 450 G10 Laptop - 5G9Q2AA"

3. __stock_status__: ALWAYS return "instock".

4. __description__: Generate technical HTML description. MINIMUM 350 WORDS.

   __KEYPHRASE RULES (EXTREMELY CRITICAL - READ CAREFULLY)__:
   - The EXACT focus_keyphrase phrase appears ONLY 1 TIME in the entire description HTML
   - That ONE time is in the first sentence of the intro paragraph inside <strong> tags
   - The H2 heading should use a SHORTENED product name (not the full keyphrase)
   - In Key Features, Why Choose, etc. - use SYNONYMS like "this device", "the monitor", "this system"
   - NEVER repeat the exact keyphrase phrase more than once - this causes RED SEO score
   
   __WORD COUNT__:
   - MINIMUM 350 words in description (this is critical for green SEO)
   - Include detailed specifications and multiple features
   
   __BANNED WORDS__:
   stunning, perfect, elevate, unleash, immersive, sleek, vibrant, engaging, "perfect for", "ideal for"
   
   __WRITING STYLE__:
   - Technical, factual, specification-focused
   - Active voice (>90%)
   - Sentences under 20 words
   - Use transition words: However, Additionally, Therefore, Consequently
   
   __HTML STRUCTURE__:
   
   ```html
   <h2 data-start="..." data-end="...">[SHORT Product Name - NOT full keyphrase]</h2>
   <p data-start="..." data-end="...">The <strong>[FULL Product Name with KEYPHRASE - this is the ONLY place keyphrase appears]</strong> [technical summary]. [More details]. [Architecture info]. [Capability statement].</p>

   <h3 data-start="..." data-end="...">Key Features</h3>
   <ul data-start="..." data-end="...">
    <li data-start="..." data-end="...">
        <p data-start="..." data-end="..."><strong>[Feature Title]</strong><br />
        [ONE technical sentence].</p>
    </li>
    <li data-start="..." data-end="...">
        <p data-start="..." data-end="..."><strong>[Complex Feature Title]</strong></p>
        <ul data-start="..." data-end="...">
            <li>[Specific detail 1]</li>
            <li>[Specific detail 2]</li>
        </ul>
    </li>
   </ul>

   <h3 data-start="..." data-end="...">Specifications</h3>
   <div class="TyagGW_tableContainer">
   <div class="group TyagGW_tableWrapper flex w-fit flex-col-reverse">
   <table class="w-fit min-w-(--thread-content-width)" data-start="..." data-end="...">
   <thead>
   <tr>
   <th data-start="..." data-end="..." data-col-size="sm">Feature</th>
   <th data-start="..." data-end="..." data-col-size="md">Specification</th>
   </tr>
   </thead>
   <tbody>
   <tr>
   <td data-start="..." data-end="..." data-col-size="sm">[Spec Name]</td>
   <td data-start="..." data-end="..." data-col-size="md">[Value]</td>
   </tr>
   </tbody>
   </table>
   </div>
   </div>

   <h3 data-start="..." data-end="...">What's in the Box</h3>
   <ul>
    <li><p>[Item]</p></li>
   </ul>

   <h3 data-start="..." data-end="...">Why Choose [Product Name]</h3>
   <ul>
    <li><p>[Technical benefit - use synonyms, NOT the keyphrase]</p></li>
   </ul>
   ```

   __FEATURE FORMAT RULES__:
   - FORMAT A: `<strong>Title</strong><br />One sentence.`
   - FORMAT B: `<strong>Title</strong>` then `<ul>` with bullets (NO text before list)
   - NEVER mix them.
   
   __TABLE RULES__:
   - NO <h4>General</h4> before table
   - NO <strong> in <th> headers

5. __short_description__: MUST start with h3 heading matching product name, then table.
   ```html
   <h3 data-start="..." data-end="...">[EXACT Product Name from 'name' field, without SKU]</h3>
   <table>
   <thead><tr><th></th><th></th></tr></thead>
   <tbody>
   <tr><td>[Spec]</td><td>[Value]</td></tr>
   </tbody>
   </table>
   ```

6. __categories__: Map to existing category list.

7. __tags__: 5-15 technical tags.

8. __attributes__: Object with relevant specs.

9. __meta_description__: STRICTLY 120-140 characters (NEVER exceed 145). Must include keyphrase once.

10. __price__: Extract from product data.

__OUTPUT__: Return ONLY valid JSON:
{{ "sku": "{product_sku}", "name": "[Name with keyphrase] - {product_sku}", "description": "...", "short_description": "<h3>Product Name</h3><table>...</table>", "categories": [], "tags": [], "attributes": {{}}, "focus_keyphrase": "...", "meta_description": "...", "price": 0, "stock_status": "instock" }}

{self.format_product_data(product)}

Generate the JSON now."""

        return prompt
