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
        
        # Include all available data (but note we want only most important used)
        for key, value in product.items():
            # Skip internal metadata
            if key.startswith('_'):
                continue
            formatted += f"  {key}: {value}\n"
        
        formatted += "\n"
        
        return formatted
    
    def build_prompt(self, products: List[Dict]) -> str:
        """Build the complete prompt for Gemini for a single product with full JSON output"""
        
        # We now assume 'products' list contains only one product for this prompt
        if not products or len(products) != 1:
            raise ValueError("PromptBuilder.build_prompt expects exactly one product when generating single-product prompts.")
        
        product = products[0] # Get the single product
        
        prompt = f"""You are an expert e-commerce product content writer specializing in SEO-optimized product descriptions for a technology retailer.

{self.categories_text}

You will receive data for ONE product.

__CRITICAL INSTRUCTIONS - For THIS single product, you must generate the following:__

1. __Product Name__: Extract or generate an appropriate, clear product name from the available data.

   - If unclear, consider general search for verification (do not use specific search tool calls).
   - Use manufacturer's official product name when possible.

2. __Description__: Generate ONE 300+ word SEO-optimized, detailed, HTML-formatted description for THIS SPECIFIC PRODUCT. Follow the structure below. Ensure high readability by:

   - Keeping sentences under 20 words (ideally).

   - Keeping paragraphs under 150 words.

   - Using subheadings (H2, H3) to break up content every ~300 words.

   - Incorporating transition words where appropriate.

   - Limiting passive voice to under 10%.

   - Avoiding 3+ consecutive sentences starting with the same word.

   - __HTML Structure for Description__:

     ```html
     <h2 data-start="..." data-end="...">Product Name</h2>
     <p data-start="..." data-end="...">Introductory paragraph with key product highlights. This paragraph should be engaging and concise, setting the stage for the features. It should clearly introduce the product and its primary benefits.</p>

     <h3 data-start="..." data-end="...">Key Features</h3>
     <ul>
     	<li><p data-start="..." data-end=""><strong>Feature Name 1</strong><br />Detailed explanation of feature 1, ensuring the text is clear, concise, and easy to read. Break down long sentences and paragraphs.</p></li>
     	<li><p data-start="..." data-end=""><strong>Feature Name 2</strong><br />Detailed explanation of feature 2, focusing on readability. Use strong tags for emphasis where appropriate and ensure sentence variety.</p></li>
     	<li><p data-start="..." data-end=""><strong>Feature Name 3</strong><br />Detailed explanation of feature 3. Remember to use transition words and keep the language active and direct.</p></li>
     </ul>

     <h3 data-start="..." data-end="...">Specifications</h3>
     <h4><strong data-start="..." data-end="...">General</strong></h4>
     <div class="TyagGW_tableContainer">
     <div class="group TyagGW_tableWrapper flex w-fit flex-col-reverse">
     <table class="w-fit min-w-(--thread-content-width)" data-start="..." data-end="...">
     <thead>
     <tr>
     <th data-start="..." data-end="..." data-col-size="sm"><strong data-start="..." data-end="...">Feature</strong></th>
     <th data-start="..." data-end="..." data-col-size="sm"><strong data-start="..." data-end="...">Specification</strong></th>
     </tr>
     </thead>
     <tbody>
     <tr>
     <td data-start="..." data-end="..." data-col-size="sm">Specification Item 1</td>
     <td data-start="..." data-end="..." data-col-size="sm">Value 1</td>
     </tr>
     <tr>
     <td data-start="..." data-end="..." data-col-size="sm">Specification Item 2</td>
     <td data-start="..." data-end="..." data-col-size="sm">Value 2</td>
     </tr>
     </tbody>
     </table>
     </div>
     </div>

     <h3 data-start="..." data-end="...">[Relevant Section Heading e.g., Layer 2 & Layer 3 Features]</h3>
     <ul>
     	<li><p data-start="..." data-end="">Point 1 about this section, formatted for readability.</p></li>
     	<li><p data-start="..." data-end="">Point 2 about this section, formatted for readability.</p></li>
     </ul>

     <h3 data-start="..." data-end="...">What’s in the Box</h3>
     <ul>
     	<li><p data-start="..." data-end="">Item 1</p></li>
     	<li><p data-start="..." data-end="">Item 2</p></li>
     </ul>

     <h3 data-start="..." data-end="...">Why Choose [Product Name]</h3>
     <ul>
     	<li><p data-start="..." data-end="">Benefit 1</p></li>
     	<li><p data-start="..." data-end="">Benefit 2</p></li>
     </ul>
     ```

   - __IMPORTANT__: Ensure data-start and data-end attributes are included as in the example, but you can use placeholder values like "..." for now.

3. __Short Description__: Generate a concise HTML-formatted summary using a table structure, highlighting key specifications and value propositions. Ensure readability and conciseness. Adhere to the following HTML structure:

   - __HTML Structure for Short Description__:

     ```html
     <h3 data-start="..." data-end="...">Product Name</h3>
     <table>
     <thead>
     <tr>
     <th></th>
     <th></th>
     </tr>
     </thead>
     <tbody>
     <tr>
     <td>Feature 1</td>
     <td>Value 1</td>
     </tr>
     <tr>
     <td>Feature 2</td>
     <td>Value 2</td>
     </tr>
     </tbody>
     </table>
     ```

   - __IMPORTANT__: Ensure data-start and data-end attributes are included as in the example, but you can use placeholder values like "..." for now.

4. __Categories__: MAP this product to the most appropriate category from the existing category list above.

   - Use hierarchical format if category has subcategories (e.g., "Computing > Laptops > HP Laptops").
   - Do NOT create new categories - only use categories from the provided list.
   - Match based on product name, description, specifications, and product type.
   - If product could fit multiple categories, choose the most specific/appropriate one.
   - Return as array of category strings (usually 1 category, but can be multiple if product fits multiple).

5. __Tags__: Generate 5-15 relevant tags based on product features, brand, specifications.

   - Include brand name if identifiable.
   - Include key specifications (e.g., "8GB RAM", "512GB SSD", "Intel Core i5").
   - Include product type and features.
   - Return as array of tag strings.

6. __Attributes__: Extract whatever attributes are relevant for this product type.

   - Attributes vary by product (laptops have processor/RAM/storage, monitors have size/resolution, etc.).
   - Only include attributes that are verified (either from product data or general knowledge).
   - Return as object with attribute names as keys and values as strings or arrays.
   - Example: {{"Processor": "Intel Core i5 1335U", "RAM": "8GB DDR4", "Storage": "512GB SSD"}}.

7. __Focus Keyphrase__: Generate an appropriate SEO keyphrase for this product.

   - Should be 2-4 words.
   - Include brand and product type when possible.
   - Example: "HP 15 Laptop" or "Dell Monitor".

8. __Meta Description__: Generate meta description (150-160 characters). STRICTLY adhere to this character limit.

   - Compelling summary for search results.
   - Include key features and benefits.
   - Include price if available.

9. __Price__: Extract price from product data if available (numeric value).

   - Use the price provided in product data (this is our selling price).
   - Do not change or adjust the price.

10. __Stock Status__: Determine stock status from availability data.

    - "instock" if available/Ex-Stock.
    - "outofstock" if Check Availability or similar.
    - Default to "instock" if unclear.

__OUTPUT FORMAT__: Return ONLY a valid JSON object. ABSOLUTELY NO other text, conversation, or markdown (e.g., "```json") outside of the JSON object. The JSON object must have this exact structure:

{{ "sku": "product SKU or identifier", "name": "Product Name", "description": "Full 300+ word HTML description", "short_description": "Brief HTML table summary", "categories": ["Category > Subcategory"], "tags": ["tag1", "tag2", "tag3"], "attributes": {{"Attribute Name": "Value"}}, "focus_keyphrase": "SEO keyphrase", "meta_description": "Meta description text (150-160 characters)", "price": 75000, "stock_status": "instock" }}

__CRITICAL REQUIREMENTS__:

- The output MUST be ONLY a valid JSON object, parsable directly by `json.loads()`. Do NOT include any introductory or concluding text, or markdown code block fences (like ```json).
- Generate content for this ONE product only.
- Descriptions must be AT LEAST 300 words and in plain text, following the specified HTML structure.
- Short description must follow the specified HTML table structure.
- Meta description must be 150-160 characters.
- Be specific and accurate - use actual product data.
- Map to existing categories only.

{self.format_product_data(product)}

Now, generate the JSON object for this product based on the provided data. """

        
        return prompt
