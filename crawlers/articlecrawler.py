import requests
import re
import csv
import time
import random
from bs4 import BeautifulSoup
from collections import Counter
from queue import PriorityQueue
import threading
import logging
from PIL import Image
from io import BytesIO
import os
import csv
import os
from PIL import Image
from io import BytesIO
from urllib.parse import urlparse
import boto3
from dotenv import load_dotenv
from urllib.parse import urljoin

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Service": "sagemaker.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "s3.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}


# Values to filter out of CSV ranking file later
common_words = set([
    word for word in (set([
        "i", "and", "the", "my", "to", "a", "you", "me", "in", "so", "for", "etc", "by"
    ])) if not word.isdigit()  # Get rid of any digits (usually the price)
])

# Words to find articles if not in title
keywords = [
    "dress", "wear", "look", "moments", "style", "celebrity", "celebrity style", "photos", "show", "shows",
    "era", "trend", "wears", "jewelry", "season", "couture", "after-party", "girl", "women", "spring", "summer",
    "fall", "winter", "shoe", "swimwear", "bag", "report", "week", "fashion week", "edit", "she", "lookbook", 
    "Fall", "Summer", "Spring", "Winter", "wardrobe", "outfit", "styles", "outfits", "idea", "cute", "wore", 
    "weather", "best", "fits", "shop", "Shop", "Jewelry", "jewelry", "Style", "Women", "Women's", "Fashion Week","new", "How to", "cuter", "worth", "need", "needed", "these", "love", "happy", "guide","studio","brand","brands","clothing"
]

# Initialize a Counter object to count word frequencies
word_counter = Counter()


# Initialize URL queue object to prioritize types of pages
url_queue = PriorityQueue()


# Function to get HTML content from a URL
def get_html(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            logging.error(f"Failed to fetch HTML from {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error occurred while fetching HTML from {url}: {e}")
        return None

# Function to crawl a fashion page and discover articles 
def crawl_page(url):
    if url.startswith('/'):
        url = f"https:/{url}"
    html_content = get_html(url)
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        # Find all links on the page
        links = [link.get('href') for link in soup.find_all('a', href=True)]
        for link in links:
            if re.match(r'^https?://', link) and ('page=' in link):  
                url_queue.put((0, link))
            elif re.match(r'^/', link):  
                full_url = urljoin(url, link)
                url_queue.put((1, full_url))  
            elif re.match(r'^https?://', link) and any(keyword in link.lower() for keyword in keywords):
                url_queue.put((2, link)) 

def extract_article_content(url, output_dir, article_title):
    # Get HTML content of the article
    html_content = get_html(url)
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        # Extract text content from article
        text_content = ""
        for tag in soup.find_all(['p', 'span', 'alt', 'title']):
            text_content += tag.get_text() + "\n"

        # Save text content to a file
        file_name = article_title.replace('/', '_')  # Replace '/' in article title with '_'
        with open(f'{output_dir}/{file_name}_content.txt', 'w', encoding='utf-8') as file:
            file.write(text_content)
        logging.info(f"Article content extracted and saved to {output_dir}/{file_name}_content.txt")
        
    else:
        logging.error(f"Failed to fetch HTML from {url}")
        pass


# Function to scrape article content from a page and its subpages
def scrape_page(url):
    time.sleep(random.uniform(5, 10))
    html_content = get_html(url)
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        title_tags = soup.find_all(['h1', 'h2', 'h3','a'])
        if title_tags:
            title = title_tags[0].get_text().lower()
            
            # Extract text content from article
            text = " ".join(tag.get_text() for tag in soup.find_all(['p', 'span', 'alt', 'title', 'class', 'h1', 'h2', 'h3']))
            # Clean the text
            cleaned_text = re.sub(r'[^\w\s]', '', text.lower())  # Remove punctuation and convert to lowercase
            # Tokenize the text
            words = cleaned_text.split()
            words = [word for word in words if word not in common_words]
            word_counter.update(words)
            # Write article name and link to CSV to store URLS
            article_name = title_tags[0].get_text()
            with open('articles.csv', 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([url])

            # Extract and save full article text for AI model training
            output_dir = f'articletext'  
            os.makedirs(output_dir, exist_ok=True)  
            extract_article_content(url, output_dir, article_name)

            # Extract and save images
            images = soup.find_all('img')
            for idx, img in enumerate(images):
                img_url = img.get('src')
                download_and_resize_image(img_url, f'{article_name}_{idx}')

            logging.info(f"Scraped page: {url}")
        else:
            logging.warning(f"No title found for page: {url}")
            pass

        # Find all links on the page and scrape subpages
        links = [link.get('href') for link in soup.find_all(['div', 'a', 'h3', 'h6', 'span'], {'href': True})]
        for link in links:
            if re.match(r'^https?://', link):
                url_queue.put((1, link))  # Add subpage to the queue with higher priority

        logging.info(f"Scraped page: {url}")


    else:
        logging.error(f"Failed to scrape page: {url}")
        pass

# Function to download and resize images, accounting for different format types
def download_and_resize_image(img_url, filename):
    try:
        if not img_url:
            logging.error("Empty image URL provided.")
            return
        parsed_url = urlparse(img_url)
        if img_url.startswith('/'):
            img_url = f"{parsed_url.scheme}:{img_url}"
        if img_url.startswith('//'):
            img_url = f"{parsed_url.scheme}://{parsed_url.netloc}{img_url}"
        if img_url.startswith('://'):
            img_url = img_url[3:]
        if img_url.startswith('data:image'):
            img_url = f"{parsed_url.scheme}://{parsed_url.netloc}{img_url}"

        # Aritzia is so picky!
        if img_url.startswith('aritzia.scene7.com'):
            img_url = f"https://{img_url}" 

        # H&M is so picky!
        if img_url.startswith('lp2.hm.com'):
            img_url = f"https://{img_url}" 



        response = requests.get(img_url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            if img.mode == 'RGBA':
                img = img.convert('RGB')
                img.save(f'articleimages/{filename}.jpg', 'JPEG', quality=100)
            if img.mode == 'P':
                img.save(f'articleimages/{filename}.webp', 'WEBP', quality=100) 
            img = img.resize((256, 256))
            img.save(f'articleimages/{filename}.jpg', 'JPEG', quality=95)
        else:
            logging.error(f"Failed to download image from {img_url}. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error downloading or resizing image: {e}")
        pass



# Function to process URLs from the queue
def process_queue():
    while True:
        priority, url = url_queue.get()
        if priority == 0:  # High priority (article URLs)
            scrape_page(url)
        else:  # Low priority (pagination pages)
            crawl_page(url)
        url_queue.task_done()
        time.sleep(random.uniform(4, 14))  








# Run it!
def main():

    # Load environmental variables
    load_dotenv()
    ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    SECRET_KEY = os.getenv("AWS_SECRET_KEY")

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Start URLs for crawling
    start_urls = [
        "https://www.aritzia.com/en/clothing",
    ]

    # Add start URLs to the queue
    for url in start_urls:
        url_queue.put((0, url))

    # Create worker threads for efficiency
    num_threads = 10
    for _ in range(num_threads):
        thread = threading.Thread(target=process_queue)
        thread.daemon = True
        thread.start()
    
    # Wait for all URLs to be scraped
    url_queue.join()
    print("-" * 40)
    logging.info("All URLs have been scraped.")


    # Rank word frequencies and export them to a CSV file
    ranked_words = word_counter.most_common()
    with open('ranked_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Word', 'Frequency'])
        csv_writer.writerows(ranked_words)

    logging.info("All data has been successfully exported to their respective csv. files!")

    try:
        # Upload files to S3 bucket
        s3 = boto3.client(
            's3', 
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
        )
        #s3.upload_file('articles.csv', 'gaineddata', 'articles.csv')
        #s3.upload_file('ranked_data.csv', 'gaineddata', 'ranked_data.csv')
        
        for filename in os.listdir('articletext'):
            file_path = os.path.join('articletext', filename)  
            s3.upload_file(file_path, 'gaineddata', filename) 

        for filename in os.listdir('articleimages'):
            file_path = os.path.join('articleimages', filename)
            s3.upload_file(file_path, 'gaineddata/images/', filename)


        logging.info("Files have been uploaded to S3!")
    except Exception as e:
        logging.error(f"Error occurred while uploading files to S3: {e}")


if __name__ == "__main__":
    main()






# make sure to scrape on a jupyter server and not on a local machine

# eventually put a crawler into it from aws to analyze data