import requests as r
import pandas as pd
import os
import uuid
import hashlib
from bs4 import BeautifulSoup


class Product:
    def __init__(self, name, sku=None):
        self.name = name
        self.sku = sku if sku else self.generate_sku()

    def generate_sku(self):
        """Generate a SKU"""
        return f"p_{uuid.uuid4().hex[:8]}"


class Variant(Product):
    def __init__(self, name, parent_product, sku=None):
        super().__init__(name, sku)
        self.parent_product = parent_product


def get_primary_image_urls(product):
    """Get the primary image URLs of a product"""
    featured_image = product.get('featured_image', None)
    images = product.get('images', [])
    
    if featured_image and featured_image.get('src'):
        return [featured_image.get('src')]
    elif images:
        return [img.get('src', '') for img in images]
    else:
        return []

def get_primary_image_urls_for_variant(variant):
    """Get the primary image URLs of a variant"""
    featured_image = variant.get('featured_image', None)
    images = variant.get('images', [])
    
    if featured_image and featured_image.get('src'):
        return [featured_image.get('src')]
    elif images:
        return [img.get('src', '') for img in images]
    else:
        return []

def generate_sku():
    """Generate a SKU using UUID"""
    uuid_str = str(uuid.uuid4().hex)
    # 使用SHA256哈希函数
    hashed = hashlib.sha256(uuid_str.encode()).hexdigest()
    # 截取前6位作为SKU
    sku = hashed[:5]
    return sku

def clean_html(html_content):
    """Clean HTML content, keeping only image tags"""
    soup = BeautifulSoup(html_content, 'html.parser')
    # Remove all tags except for images
    for tag in soup.find_all():
        if tag.name not in ['img', 'p', 'span']:
            tag.decompose()
    return str(soup)

def generate_product_data(product_data, category_name):
    """Generate product data"""
    products_data = []
    tags = ', '.join(product_data.get('tags', []))
    variants = product_data.get('variants', [])
    options = product_data.get('options', [])
    variant_options = [option.get('values', []) for option in options]

    if len(variants) > 1:  # If the product has multiple variants
        parent_sku = generate_sku()  # Parent product SKU
        parent_product = Product(product_data['title'], parent_sku)
        parent_product_data = {
            "ID": "",
            "Type": "variable",
            "SKU": parent_product.sku,
            "Parent": "",
            "Name": product_data['title'],
            "Published": "1",
            "Is featured?": "0",
            "Visibility in catalog": "visible",
            "Short description": "",
            "Description": clean_html(product_data['body_html']), # Clean HTML tags
            "Tax status": "taxable",
            "Tax class": "",
            "In stock?": "1",
            "Backorders allowed": "0",
            "Sold_individually?": "0",
            "Weight (lbs)": "",
            "Length (in)": "",
            "Width (in)": "",
            "Height (in)": "",
            "Allow customer reviews?": "1",
            "Purchase note": "",
            "Sale price": "",
            "Regular price": '',
            "Categories": category_name,
            "Tags": tags,
            "Shipping class": "",
            "Images": ", ".join(get_primary_image_urls(product_data))
        }
        # Add variant options to parent data
        for i, option_values in enumerate(variant_options):
            parent_product_data[f"Attribute {i+1} name"] = options[i]['name']
            parent_product_data[f"Attribute {i+1} value(s)"] = '|'.join(option_values)
        
        products_data.append(parent_product_data)

        for variant_data in variants:
            variant_sku = generate_sku()  # Variant product SKU
            variant_product = Variant(variant_data['title'], parent_product, variant_sku)
            variant = {
                "ID": "",
                "Type": "variation",
                "SKU": variant_sku,
                "Parent": parent_sku,
                "Name": f"{product_data['title']} - {variant_data['title']}",
                "Published": "1",
                "Is featured?": "0",
                "Visibility in catalog": "visible",
                "Short description": "",
                "Description": clean_html(product_data['body_html']),   # Clean HTML tags
                "Tax status": "taxable",
                "Tax class": "",
                "In stock?": "1",
                "Backorders allowed": "0",
                "Sold_individually?": "0",
                "Weight (lbs)": "",
                "Length (in)": "",
                "Width (in)": "",
                "Height (in)": "",
                "Allow customer reviews?": "1",
                "Purchase note": "",
                "Sale price": "",
                "Regular price": variants[0].get('price', ''),
                "Categories": category_name,
                "Tags": tags,
                "Shipping class": "",
                
                "Attribute 1 name": options[0]['name'] if options else "",
                "Attribute 1 value(s)": variant_data.get('option1', ''),
                "Attribute 1 visible": "",
                "Attribute 1 global": "",
                "Attribute 2 name": options[1]['name'] if len(options) > 1 else "",
                "Attribute 2 value(s)": variant_data.get('option2', ''),
                "Attribute 2 visible": "",
                "Attribute 2 global": "",
                "Attribute 3 name": options[2]['name'] if len(options) > 2 else "",
                "Attribute 3 value(s)": variant_data.get('option3', ''),
                "Attribute 3 visible": "",
                "Attribute 3 global": "",
                "Images": ", ".join(get_primary_image_urls_for_variant(variant_data))
            }
            products_data.append(variant)
    else:  # If the product has only one variant
        product_sku = generate_sku()  # Product SKU
        product = Product(product_data['title'], product_sku)
        product_data = {
            "ID": "",
            "Type": "simple",
            "SKU": product.sku,
            "Parent": "",
            "Name": product_data['title'],
            "Published": "1",
            "Is featured?": "0",
            "Visibility in catalog": "visible",
            "Short description": "",
            "Description": clean_html(product_data['body_html']),   # Clean HTML tags
            "Tax status": "taxable",
            "Tax class": "",
            "In stock?": "1",
            "Backorders allowed": "0",
            "Sold_individually?": "0",
            "Weight (lbs)": "",
            "Length (in)": "",
            "Width (in)": "",
            "Height (in)": "",
            "Allow customer reviews?": "1",
            "Purchase note": "",
            "Sale price": "",
            "Regular price": variants[0].get('price', ''),
            "Categories": category_name,
            "Tags": tags,
            "Shipping class": "",
            "Images": ", ".join(get_primary_image_urls(product_data))
        }
        products_data.append(product_data)

    return products_data


categories_urls = {


'Robe Fleurie': 'https://robe-fleurie.fr/collections/robe-fleurie/products.json',
'Robe Fleurie Femme': 'https://robe-fleurie.fr/collections/robe-fleurie-femme/products.json',
}
# 调用 scrape_product_data 函数时传入页码信息
# for category, url in categories_urls.items():
#     page = 1
#     while True:
#         scraped_products = scrape_product_data(url, category, page)
#         if not scraped_products:
#             break
#         page += 1
def scrape_product_data(url, category_name, all_products_data):
    page = 1
    while True:
        try:
            req = r.get(url=url, params={'page': page, 'limit': 250}, timeout=5)
            req.raise_for_status()
            data = req.json()
        except r.RequestException as e:
            print(f"Error fetching data for category '{category_name}', page {page}: {e}")
            break

        # Stop if the product list is empty
        if not data.get('products', []):
            print(f"Reached the end of products for category '{category_name}'.")
            break

        for product_data in data.get('products', []):
            all_products_data.extend(generate_product_data(product_data, category_name))

        print(f"Scraped {len(all_products_data)} products for category '{category_name}' from page {page}.")
        
        page += 1

    return all_products_data

folder_path = "data"
for category, url in categories_urls.items():
    all_products_data = []
    
    scraped_products = scrape_product_data(url, category, all_products_data)
    
    if scraped_products:
        column_names = ["ID", "Type", "SKU", "Parent", "Name", "Published", "Is featured?", "Visibility in catalog", "Short description", "Description", "Tax status", "Tax class", "In stock?", "Backorders allowed", "Sold_individually?", "Weight (lbs)", "Length (in)", "Width (in)", "Height (in)", "Allow customer reviews?", "Purchase note", "Sale price", "Regular price", "Categories", "Tags", "Shipping class", "Attribute 1 name", "Attribute 1 value(s)", "Attribute 2 name", "Attribute 2 value(s)", "Attribute 1 visible", "Attribute 1 global", "Attribute 2 visible", "Attribute 2 global", "Attribute 3 name", "Attribute 3 value(s)", "Attribute 3 visible", "Attribute 3 global", "Images"]
        df = pd.DataFrame(scraped_products, columns=column_names)
        filename = f"{category.replace(' ', '_').replace('/', '_').lower()}_products.csv"  
        filepath = os.path.join(folder_path, filename)
         
        df.to_csv(filepath, index=False)
        print(f"All products for category: {category}, saved to {filepath}.")
