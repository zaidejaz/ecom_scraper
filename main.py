import requests
from bs4 import BeautifulSoup
import csv
import time

# Function to fetch HTML content from the endpoint
def fetch_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print("Failed to fetch HTML content from the endpoint:", url)
        return None

# Function to fetch product details and write them to CSV
def fetch_and_write_product_data(product_url, writer, tag):
    print(f"Fetching data from {product_url}")
    product_html = fetch_html(product_url)
    if product_html:
        soup = BeautifulSoup(product_html, 'html.parser')

        # Extracting product details

        # Product price
        price_span = soup.find('span', class_='price')
        symbol = price_span.find('span', class_='woocommerce-Price-currencySymbol').text.strip()
        price = symbol + price_span.text.replace(symbol, '').strip()

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
        sizes = list(sizes_set)  # Convert set back to a list if needed
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
        images_length = len(image_urls)
        sizes_length = len(sizes)
        if images_length > 6:
            images_length = 6
        
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
                print("SKU:", product_sku)
            else:
                print("No second data found after splitting by ':'")
        else:
            print("No paragraphs found within the description div or insufficient paragraphs")

        # Product Handle
        handle = product_title.lower().replace(' ', '-') + " | " + product_sku
        max_length = max(sizes_length, images_length)

        for index in range(max_length):
            if index == 0:
                csv_row = [handle, product_title, body, brand_name, '', product_type , tag ,'False', 'Size', sizes[index] if index < sizes_length else '', '', '', product_sku, 0 , 'shopify', '1', 'deny','manual', price, '', 'True', 'False', '', image_urls[index] if index < images_length else '' , (index+1) if index < images_length else '', product_title.lower().replace(" ", "-") if index < images_length else '','False', '','','','','','','','','','','','','','','kg','','','True', 'True', '', '', 'active']
            else:
                csv_row = [handle, '', '', '', '', '', '' ,'', '', sizes[index] if index < sizes_length else '', '','', '', 0 if index < sizes_length else '', '', '', 'deny','manual', '', '', '', '', '', image_urls[index] if index < images_length else '' , (index+1) if index < images_length else '', product_title.lower().replace(" ", "-")  if index < images_length else '','', '','','','','','','','','','','','','','','','','','', '', '', '', '']
            # Writing data to CSV 
            writer.writerow(csv_row)

        print(f"Writing data for {product_url}")
       

# Main function to fetch HTML from the website and process product data
def main():
    base_url = "https://goccia.shop"
    female_endpoint = "/c/donna/"
    male_endpoint = "/c/uomo/"
    female_html = fetch_html(base_url + female_endpoint)
    male_html = fetch_html(base_url + male_endpoint)
    if female_html and male_html:
        print("HTML content successfully fetched from the endpoints.")

        fieldnames = ['Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type', 'Tag', 'Published', 'Option1 Name', 'Option1 Value', 'Option 2 Name', 'Option2 Value', 'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Inventory Policy', 'Variant Fulfillment Service', 'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping', 'Variant Taxable', 'Variant Barcode', 'Image Src', 'Image Position', 'Image Alt Text', 'Gift Card', 'SEO Title', 'SEO Description', 'Google Shopping / Google Product Category', 'Google Shopping / Gender', 'Google Shopping / Age Group', 'Google Shopping / MPN', 'Google Shopping / Condition', 'Google Shopping / Custom Product', 'Google Shopping / Custom Label 0', 'Google Shopping / Custom Label 1', 'Google Shopping / Custom Label 2', 'Google Shopping / Custom Label 3', 'Google Shopping / Custom Label 4', 'Variant Image', 'Variant Weight Unit', 'Variant Tax Code', 'Cost per item', 'Include / Japan', 'Include / International', 'Price / International', 'Compare At Price / International', 'Status']
        page_count = 0
        csv_count = 1

        csvfile = open(f'products_{csv_count}.csv', 'w', newline='', encoding='utf-8')
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)

        process_products(male_html, writer, 'male', page_count, csv_count)
        process_products(female_html, writer, 'female', page_count, csv_count)

        csvfile.close()  # Close the last CSV file after processing

        print("Data written to 'products.csv' files successfully.")
    else:
        print("Failed to fetch HTML content from the endpoints.")

# Function to process products from HTML and fetch their details
def process_products(html_content, writer, tag, page_count, csv_count):
    print(f"Processing Html of {tag}......")

    soup = BeautifulSoup(html_content, 'html.parser')

    ul_element = soup.find('ul', class_='page-numbers')
    li_elements = ul_element.find_all('li')
    li_content_list = [li.get_text(strip=True) for li in li_elements]
    last_page_number = int(li_content_list[-2])

    print(f"Starting from Page {last_page_number}")

    for i in range(last_page_number, 1, -1):
        print("Page Number: ", i)
        
        page_link = ""

        if tag == "male":
            page_link = f"https://goccia.shop/c/uomo/page/{i}"
        elif tag == "female":
            page_link = f"https://goccia.shop/c/donna/page/{i}"

        page_html = fetch_html(page_link)

        if page_html:
            print(f"Fetching Html of {page_link}")
            soup = BeautifulSoup(page_html, 'html.parser')
            
            products_div = soup.find('ul', class_='products')

            if products_div:
                print(f"Getting Links from {page_link}")
                product_links = products_div.find_all('a', class_='woocommerce-LoopProduct-link')
            else:
                print("There was error getting products. Try Again")
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

            if page_count == 2:  # Create a new CSV file after how many pages
                csv_count += 1
                page_count = 0
                fieldnames = ['Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type', 'Tag', 'Published', 'Option1 Name', 'Option1 Value', 'Option 2 Name', 'Option2 Value', 'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Inventory Policy', 'Variant Fulfillment Service', 'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping', 'Variant Taxable', 'Variant Barcode', 'Image Src', 'Image Position', 'Image Alt Text', 'Gift Card', 'SEO Title', 'SEO Description', 'Google Shopping / Google Product Category', 'Google Shopping / Gender', 'Google Shopping / Age Group', 'Google Shopping / MPN', 'Google Shopping / Condition', 'Google Shopping / Custom Product', 'Google Shopping / Custom Label 0', 'Google Shopping / Custom Label 1', 'Google Shopping / Custom Label 2', 'Google Shopping / Custom Label 3', 'Google Shopping / Custom Label 4', 'Variant Image', 'Variant Weight Unit', 'Variant Tax Code', 'Cost per item', 'Include / Japan', 'Include / International', 'Price / International', 'Compare At Price / International', 'Status']

                writer = csv.writer(open(f'products_{csv_count}.csv', 'w', newline='', encoding='utf-8'))
                writer.writerow(fieldnames)  # Write header for the new CSV file

        else:
            print(f"Failed to fetch HTML content from the page: {page_link}")

if __name__ == "__main__":
    main()
