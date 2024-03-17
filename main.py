import requests
from bs4 import BeautifulSoup
import csv
import logging

logging.basicConfig(level=logging.INFO)

# Function to fetch HTML content from the endpoint
def fetch_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        logging.error("Failed to fetch HTML content from the endpoint: %s", url)
        return None

# Function to parse the price string and return the symbol and parsed price
def parse_price(price_str):
    symbol = None
    price = None
    
    if len(price_str) >= 2:
        symbol = price_str[0]  # Extract the currency symbol
        try:
            # Attempt to parse the price part as a float
            price = float(price_str[1])
        except ValueError:
            logging.warning("Error parsing price: %s", price_str)
    
    # Check if symbol and price are both None, indicating a single-value case
    if symbol is None and price is None and len(price_str) == 1:
        price = price_str[0]
    
    return symbol, price

# Function to fetch product details and write them to CSV
def fetch_and_write_product_data(product_url, writer, tag):
    logging.info("Fetching data from %s", product_url)
    product_html = fetch_html(product_url)
    if product_html:
        soup = BeautifulSoup(product_html, 'html.parser')

        # Extracting product details

        # Product price
        price_span = soup.find('span', class_='price')
        price_parts = price_span.text.strip().split()
        symbol, price = parse_price(price_parts)

        # Product Brand
        brand_tag = soup.find('p', class_='brand_product').find('a')
        brand_name = brand_tag.text

        # Product Title
        title_tag = soup.find('h1', class_='single-post-title product_title entry-title', itemprop='name')
        product_title = title_tag.text

        # Product Color
        li_tag = soup.find('li', class_='woocommerce-product-attributes-item--attribute_pa_colore')
        span_tag = li_tag.find('span', class_='woocommerce-product-attributes-item__value')
        color = span_tag.text.strip()

        # Product Sizes
        table_tag = soup.find('table', class_='variations')
        select_tag = table_tag.find('select', id='taglia')
        sizes_set = {option.text.split(' - ')[0].split(' ')[-1].strip() for option in select_tag.find_all('option') if option.text.strip() and option['value']}
        sizes = list(sizes_set)[:5]   # Convert set back to a list if needed
        # Product Images
        slider_parent = soup.find('div', class_='woocommerce-product-gallery')
        image_urls = []
        if slider_parent:
            slider_images = slider_parent.find_all('img')
            for img in slider_images:
                image_url = img['src']
                image_urls.append(image_url)

        # Find the div with class 'site-breadcrumbs woocommerce-breadcrumbs clr'
        breadcrumbs_div = soup.find('div', class_='site-breadcrumbs woocommerce-breadcrumbs clr')

        # Find all <a> tags within the breadcrumbs_div
        links = breadcrumbs_div.find_all('a')

        # Extract text from <a> tags and store them in an array
        data_array = [link.text.strip() for link in links]

        product_category = data_array[2]
        product_type = data_array[3]
        product_sku = ''
        
        # Find the additional information panel and print its content
        body = soup.find("div", class_="wc-tabs-wrapper")


        # Extracting product description
        description_div = body.find('div', class_='woocommerce-Tabs-panel--description')

        # Initialize an empty string to store the description
        description_html = ''

        if description_div:
            # Find all spans with class 'sku_wrapper' and remove the last one
            sku_spans = description_div.find_all('span', class_='sku_wrapper')
            if sku_spans:
                last_sku_span = sku_spans[-1]
                last_sku_span.decompose()

            # Extract HTML content from all the paragraphs inside the description div
            paragraphs = description_div.find_all('p', style=lambda value: value is None or value.strip().lower() != 'display: none;')
            for paragraph in paragraphs:
                # Exclude the paragraph containing the span with display: none;
                if not paragraph.find('span', style=lambda value: value is not None and 'display: none;' in value):
                    description_html += str(paragraph) + '\n'

            # Find the next div
            next_div = description_div.find_next_sibling('div', class_='woocommerce-Tabs-panel')
            if next_div:
                # Extract HTML content from all the list items inside the next div
                list_items = next_div.find_all('li', style=lambda value: value is None or value.strip().lower() != 'display: none;')
                for li in list_items:
                    description_html += str(li) + '\n'

        print(description_html)
        images_length = len(image_urls)
        sizes_length = len(sizes)
        if body:
            # Find all paragraphs within the specific div
            paragraphs = body.find_all("p")

        # Check if there are paragraphs found
        if paragraphs and len(paragraphs) >= 2:
            # Get the content of the second paragraph
            second_paragraph_content = paragraphs[1].get_text(strip=True)

            # Split the content using ":"
            split_content = second_paragraph_content.split(":")

            # Check if the split content has at least two parts
            if len(split_content) >= 2:
                product_sku = split_content[1].strip()
            else:
                logging.warning("There was error getting sku of product")
        else:
            logging.warning("No paragraphs found within the description div or insufficient paragraphs")

        # Product Handle
        handle = product_title.lower().replace(' ', '-') + " | " + product_sku
        max_length = max(sizes_length, images_length)
        for index in range(max_length):
            if index == 0:
                csv_row = [handle, product_title, description_html, brand_name, None , product_type , tag , False, 'Size', sizes[index] if index < sizes_length else None, 'Color',color if index < sizes_length else None, product_sku+"-"+color, 0 , 'shopify', 1, 'deny','manual', price, None , True, False, None, image_urls[index] if index < images_length else None , (index+1) if index < images_length else None, product_title.lower().replace(" ", "-") if index < images_length else None, False , None,None,None,None,None,None,None,None,None,None,None,None,None,None,'kg',None,None,True, True, None, None, 'active']
            else:
                csv_row = [handle, None, None, None, None, None, None ,None, None, sizes[index] if index < sizes_length else None, None ,color if index < sizes_length else None, None, 0 if index < sizes_length else None, None, 1 if index < sizes_length else None, 'deny' if index < sizes_length else None,'manual' if index < sizes_length else None, price if index < sizes_length else None, None, True if index < sizes_length else None, False if index < sizes_length else None, None, image_urls[index] if index < images_length else None , (index+1) if index < images_length else None, product_title.lower().replace(" ", "-")  if index < images_length else None,None, None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None, None, None, None, None]
            # Writing data to CSV 
            writer.writerow(csv_row)
        logging.info("Writing data for %s", product_url)

# Main function to fetch HTML from the website and process product data
def main():
    base_url = "https://goccia.shop"
    female_endpoint = "/c/donna/"
    male_endpoint = "/c/uomo/"
    female_html = fetch_html(base_url + female_endpoint)
    male_html = fetch_html(base_url + male_endpoint)
    if female_html and male_html:
        logging.info("HTML content successfully fetched from the endpoints.")

        fieldnames = ['Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type', 'Tag', 'Published', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Inventory Policy', 'Variant Fulfillment Service', 'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping', 'Variant Taxable', 'Variant Barcode', 'Image Src', 'Image Position', 'Image Alt Text', 'Gift Card', 'SEO Title', 'SEO Description', 'Google Shopping / Google Product Category', 'Google Shopping / Gender', 'Google Shopping / Age Group', 'Google Shopping / MPN', 'Google Shopping / Condition', 'Google Shopping / Custom Product', 'Google Shopping / Custom Label 0', 'Google Shopping / Custom Label 1', 'Google Shopping / Custom Label 2', 'Google Shopping / Custom Label 3', 'Google Shopping / Custom Label 4', 'Variant Image', 'Variant Weight Unit', 'Variant Tax Code', 'Cost per item', 'Include / Japan', 'Include / International', 'Price / International', 'Compare At Price / International', 'Status']
        page_count = 0
        csv_count = 1

        csvfile = open(f'products_{csv_count}.csv', 'w', newline='', encoding='utf-8')
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)

        process_products(male_html, writer, 'male', page_count, csv_count)
        process_products(female_html, writer, 'female', page_count, csv_count)

        csvfile.close()  # Close the last CSV file after processing

        logging.info("Data written to 'products.csv' files successfully.")
    else:
        logging.error("Failed to fetch HTML content from the endpoints.")

# Function to process products from HTML and fetch their details
def process_products(html_content, writer, tag, page_count, csv_count):
    logging.info("Processing Html of %s......", tag)

    soup = BeautifulSoup(html_content, 'html.parser')

    ul_element = soup.find('ul', class_='page-numbers')
    li_elements = ul_element.find_all('li')
    li_content_list = [li.get_text(strip=True) for li in li_elements]
    last_page_number = int(li_content_list[-2])

    logging.info("Starting from Page %s", last_page_number)

    for i in range(last_page_number, 1, -1):
        logging.info("Page Number: %s", i)
        
        page_link = ""

        if tag == "male":
            page_link = f"https://goccia.shop/c/uomo/page/{i}"
        elif tag == "female":
            page_link = f"https://goccia.shop/c/donna/page/{i}"

        page_html = fetch_html(page_link)

        if page_html:
            logging.info("Fetching Html of %s", page_link)
            soup = BeautifulSoup(page_html, 'html.parser')
            
            products_div = soup.find('ul', class_='products')

            if products_div:
                logging.info("Getting Links from %s", page_link)
                product_links = products_div.find_all('a', class_='woocommerce-LoopProduct-link')
            else:
                logging.error("There was error getting products. Try Again")
                return

            unique_links = set()

            # Loop through each link and add it to the set
            for link in product_links:
                unique_links.add(link['href'])

            # Convert the set back to a list if needed
            unique_links_list = list(unique_links)
            # Extract href attribute from each <a> tag
            for link in unique_links:
                fetch_and_write_product_data(link, writer, tag)

            page_count += 1

            if page_count == 1:  # Create a new CSV file after how many pages
                csv_count += 1
                page_count = 0
                fieldnames = ['Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type', 'Tag', 'Published', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Inventory Policy', 'Variant Fulfillment Service', 'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping', 'Variant Taxable', 'Variant Barcode', 'Image Src', 'Image Position', 'Image Alt Text', 'Gift Card', 'SEO Title', 'SEO Description', 'Google Shopping / Google Product Category', 'Google Shopping / Gender', 'Google Shopping / Age Group', 'Google Shopping / MPN', 'Google Shopping / Condition', 'Google Shopping / Custom Product', 'Google Shopping / Custom Label 0', 'Google Shopping / Custom Label 1', 'Google Shopping / Custom Label 2', 'Google Shopping / Custom Label 3', 'Google Shopping / Custom Label 4', 'Variant Image', 'Variant Weight Unit', 'Variant Tax Code', 'Cost per item', 'Include / Japan', 'Include / International', 'Price / International', 'Compare At Price / International', 'Status']

                writer = csv.writer(open(f'products_{csv_count}.csv', 'w', newline='', encoding='utf-8'))
                writer.writerow(fieldnames)  # Write header for the new CSV file

        else:
            logging.error("Failed to fetch HTML content from the page: %s", page_link)

if __name__ == "__main__":
    main()
