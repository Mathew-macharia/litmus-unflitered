"""
Gemini API Prompt Templates
THE CRITICAL COMPONENT - meticulously crafted prompts for product processing with search capabilities
"""

from typing import List, Dict
from parsers.category_extractor import CategoryExtractor
from config import Config


PROMPT_TEMPLATE = '''You are a Senior Technical Product Specialist for a B2B technology retailer.
Your audience: IT professionals, network engineers, procurement managers.
Write with technical precision, not marketing fluff.

{categories_text}

PRODUCT SKU: {product_sku}

DISTRIBUTOR SEARCH REQUIREMENTS
Search distributor sources for exact technical details before finalizing output.
Use these distributor domains first:
{distributor_sources}
If the distributor data conflicts, prioritize official manufacturer specifications.
Use only verifiable technical details in name, description, attributes, and price.

CRITICAL SEO REQUIREMENTS

name: Format using the "Universal Golden Formula":
Structure: [Brand] + [Model/Series] + [Primary Technical Specs]

UNIVERSAL RULE FOR ALL 100+ CATEGORIES:
You must identify the 2-3 most critical technical specifications that define this specfic item.
What would a technical buyer type to find EXACTLY this product?

EXAMPLES OF VARIETY:
Laptop: "... i5-1335U, 16GB RAM ..."
Server: "... Xeon Silver 4310, 64GB, 8x SFF ..."
Switch: "... 48-Port PoE+, Layer 3, 4x 10G SFP+ ..."
Cable: "... Cat6a Shielded, 5m, Blue ..."
Software: "... 1-Year License, 5 Users ..."
Hard Drive: "... 8TB, 7200RPM, SATA 6Gb/s ..."

CRITICAL: Do not just guess. Look at the product data. Pick the specs that matter for THAT specific item.
If it's a simple item (e.g., a screw), just describe it accurately. "M5 x 10mm Rack Screw" is better than fluff.

focus_keyphrase:
maximum of 4 words and the words must be from the product name. brand must be included.
the purpose is to match search terms most people use when looking for this product. it should be simple easily describing the product.
This keyphrase appears in the meta_description
In the description HTML, the EXACT keyphrase phrase appears ONLY ONCE (in the first paragraph)
EVERYWHERE ELSE in description, use SYNONYMS or DIFFERENT WORDING

stock_status: ALWAYS return "instock".
description: Generate technical HTML description. MINIMUM 350 WORDS.

KEYPHRASE RULES (EXTREMELY CRITICAL - READ CAREFULLY):
The EXACT focus_keyphrase phrase appears ONLY 1 TIME in the entire description HTML
That ONE time is in the first sentence of the intro paragraph inside <strong> tags
The H2 heading should use a SHORTENED product name (not the full keyphrase)
In Key Features, Why Choose, etc. - use SYNONYMS like "this device", "the monitor", "this system"
NEVER repeat the exact keyphrase phrase more than once - this causes RED SEO score

WORD COUNT:
MINIMUM 350 words in description (this is critical for green SEO)
Include detailed specifications and multiple features

BANNED WORDS:
stunning, perfect, elevate, unleash, immersive, sleek, vibrant, engaging, "perfect for", "ideal for"

WRITING STYLE:
Technical, factual, specification-focused
Active voice (>90%)
Sentences under 20 words
Use transition words: However, Additionally, Therefore, Consequently

HTML STRUCTURE:
code
Html
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

FEATURE FORMAT RULES:
FORMAT A: <strong>Title</strong><br />One sentence.
FORMAT B: <strong>Title</strong> then <ul> with bullets (NO text before list)
NEVER mix them.

TABLE RULES:
NO <h4>General</h4> before table
NO <strong> in <th> headers

short_description: MUST start with h3 heading matching product name, then table.
code
Html
<h3 data-start="..." data-end="...">[EXACT Product Name from 'name' field, without SKU]</h3>
<table>
<thead><tr><th></th><th></th></tr></thead>
<tbody>
<tr><td>[Spec]</td><td>[Value]</td></tr>
</tbody>
</table>

categories: Map to existing category list.
SELECT ONLY THE DEEPEST/MOST SPECIFIC PATH.
Do NOT select a parent category if you have selected its child.
Example: Choose "Accessories>Computing Accessories>Laptop Chargers", NOT "Accessories".
Select 1-2 categories max. NEVER invent new categories. Use EXACT strings from the list.

tags: 5-15 technical tags.
attributes: Object with relevant specs.
meta_description: STRICTLY 120-140 characters (NEVER exceed 145). Must include keyphrase once.
price: Extract from product data.

__OUTPUT__: Return ONLY valid JSON:
{{ "sku": "{product_sku}", "name": "[Name with keyphrase] - {product_sku}", "description": "...", "short_description": "<h3>Product Name</h3><table>...</table>", "categories": [], "tags": [], "attributes": {{}}, "focus_keyphrase": "...", "meta_description": "...", "price": 0, "stock_status": "instock" }}

{product_data}

Generate the JSON now.'''


class PromptBuilder:
    """Build prompts for Gemini API"""
    
    def __init__(self, categories_file: str = "data/product_categories.txt"):
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

    def format_distributor_sources(self) -> str:
        """Format configured distributor domains for prompt inclusion."""
        return "\n".join(f"- {domain}" for domain in self.competitors)
    
    def build_prompt(self, products: List[Dict]) -> str:
        """Build the complete prompt for Gemini for a single product with full JSON output"""
        
        if not products or len(products) != 1:
            raise ValueError("PromptBuilder.build_prompt expects exactly one product.")
        
        product = products[0]
        product_sku = product.get('_sku', 'UNKNOWN')
        
        prompt = PROMPT_TEMPLATE.format(
            categories_text=self.categories_text,
            product_sku=product_sku,
            distributor_sources=self.format_distributor_sources(),
            product_data=self.format_product_data(product),
        )

        return prompt
