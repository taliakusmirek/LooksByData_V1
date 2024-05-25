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


# Initialize a priority queue to store URLs to scrape
url_queue = PriorityQueue()

# Count for saved articles to not overlap and instead be numerically organized
count = 0

# Set to store visited URLs
visited_urls = set()

# Values to filter out of CSV ranking file later
common_words = set([
    word for word in (set([
        "i", "and", "the", "my", "to", "a", "you", "me", "in", "so", "for", "etc", "by"
    ])) if not word.isdigit()  # Get rid of any digits (usually prices)
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
def get_html(url, retries=1, delay=5):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and url not in visited_urls:
            return response.content
        elif response.status_code in [503, 429]:
            logging.warning(f"Received {response.status_code} status code. Retrying after delay.")
            time.sleep(delay)
            if retries > 0:
                return get_html(url, retries - 1, delay)
            else:
                logging.warning(f"Retry limit exceeded for {url}. Moving on to next URL.")
                return None
        else:
            logging.error(f"Failed to fetch HTML from {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error fetching HTML from {url}: {e}, moving onto next URL.")
        retries -= 1
        return None
    
# Get full HTML text content of the article and save it to a text file
def extract_article_content(url, output_dir):
    global count
    html_content = get_html(url)
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        # Extract text content from article
        text_content = ""
        for tag in soup.find_all(['p', 'span', 'title', 'h1', 'h2', 'h3']):
            text_content += tag.get_text() + "\n"

        # Save text content to a file
        count += 1
        with open(f'{output_dir}/{count}_VOGUEcontent.txt', 'w', encoding='utf-8') as file:
            file.write(text_content)
        logging.info(f"Article content extracted and saved to {output_dir}/{count}_VOGUEcontent.txt")      
    else:
        logging.error(f"Failed to fetch HTML from {url}")

# Function to scrape article content from a page and its subpages
def scrape_page(url, retries=1, delay=5):
        html_content = get_html(url, retries=retries, delay=delay)
        visited_urls.add(url)
        if html_content:
            soup = BeautifulSoup(html_content, "html.parser")
            images = soup.find_all('img')
            # Extract text content from article to split into individual words
            text = " ".join(tag.get_text() for tag in soup.find_all(['p', 'span', 'alt', 'title', 'h1', 'h2', 'h3']))
            # Clean the text
            cleaned_text = re.sub(r'[^\w\s]', '', text.lower())  # Remove punctuation and convert to lowercase
            # Tokenize the text
            words = cleaned_text.split()
            words = [word for word in words if word not in common_words]
            word_counter.update(words)
            # Write article name and link to CSV to store URLS
            with open('articles.csv', 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([url])

            # Extract and save full article text for AI model training
            output_dir = f'articletext'  
            os.makedirs(output_dir, exist_ok=True)  
            extract_article_content(url, output_dir)

            # Extract and save images
            images = soup.find_all('img')
            for idx, img in enumerate(images):
                img_url = img.get('src')
                download_and_resize_image(img_url)

            logging.info(f"Scraped page: {url}")
        
            # Find all links on the page and scrape subpages
            links = [link.get('href') for link in soup.find_all(['a'], {'href': True})]
            for link in links:

                if link.startswith('http://www.condenast.com/'):
                    # Don't go down this rabbit hole
                    return None
                if link.startswith('https://ar.vogue.me/'):
                    # Don't go down this rabbit hole
                    return None
                if link.startswith('http://login'):
                    # Don't go down this rabbit hole
                    return None
                if link.startswith('http://vogue.globo.com/'):
                    # Don't go down this rabbit hole
                    return None

                if not link.startswith('http'):
                    link = urljoin('https://www.vogue.com', link) 
                    

                url_queue.put((1, link))
            logging.info(f"Scraped page: {url}")


        else:
            if retries > 0:
                logging.error(f"Failed to scrape page: {url}. Retrying...")
                scrape_page(url, retries=retries - 1, delay=delay)
            else:
                logging.error(f"Failed to scrape page: {url}. Retry limit exceeded.")
                return None

# Function to scrape article content from a page's subpages
def scrape_subpage(url, retries=1, delay=5):
        html_content = get_html(url, retries=retries, delay=delay)
        if html_content:
            soup = BeautifulSoup(html_content, "html.parser")
            images = soup.find_all('img')
            # Extract text content from article to split into individual words
            text = " ".join(tag.get_text() for tag in soup.find_all(['p', 'span', 'alt', 'title', 'h1', 'h2', 'h3']))
            # Clean the text
            cleaned_text = re.sub(r'[^\w\s]', '', text.lower())  # Remove punctuation and convert to lowercase
            # Tokenize the text
            words = cleaned_text.split()
            words = [word for word in words if word not in common_words]
            word_counter.update(words)
            # Write article name and link to CSV to store URLS
            with open('voguearticles.csv', 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([url])

            # Extract and save full article text for AI model training
            output_dir = f'articletext'  
            os.makedirs(output_dir, exist_ok=True)  
            extract_article_content(url, output_dir)

            # Extract and save images
            images = soup.find_all('img')
            for idx, img in enumerate(images):
                img_url = img.get('src')
                download_and_resize_image(img_url)

            logging.info(f"Scraped page: {url}")

        else:
            if retries > 0:
                logging.error(f"Failed to scrape page: {url}. Retrying...")
                scrape_subpage(url, retries=retries - 1, delay=delay)
            else:
                logging.error(f"Failed to scrape page: {url}. Retry limit exceeded.")
                return None

# Function to download and resize images, accounting for different format types
def download_and_resize_image(img_url):
    global count
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
        if img_url.startswith(':/'):
            return


        response = requests.get(img_url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            if img.mode == 'RGBA':
                img = img.convert('RGB')
                img.save(f'articleimages/{count}.jpg', 'JPEG', quality=100)
            if img.mode == 'P':
                img = img.convert('RGB')
                img.save(f'articleimages/{count}.webp', 'WEBP', quality=100) 
            img = img.resize((256, 256))
            img.save(f'articleimages/{count}.jpg', 'JPEG', quality=95)
        else:
            logging.error(f"Failed to download image from {img_url}. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error downloading or resizing image: {e}")

# Function to print the current contents of the URL queue if needed
def print_queue():
    queue_contents = list(url_queue.queue)
    print("Current URL Queue:")
    for priority, url in queue_contents:
        print(f"Priority: {priority}, URL: {url}")

# Function to process URLs from the queue
def process_queue():
    while True:
        priority, url = url_queue.get()
        time.sleep(90)
        if priority == 0:
            scrape_page(url)
            url_queue.task_done()
        if priority == 1:
            scrape_subpage(url)
            url_queue.task_done()
        if url_queue.empty():
            break
        # Print the current contents of the URL queue every now and then
        if url_queue.qsize() % 10 == 0:
            print_queue()
        

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
            "https://www.vogue.com/fashion/celebrity-style",
            "https://www.vogue.com/fashion/street-style",
            "https://www.vogue.com/fashion/models",
            "https://www.vogue.com/fashion/trends"
        ]

    # Add start URLs to the queue
    for url in start_urls:
        url_queue.put((0, url))
        process_queue()


    # Create worker threads for efficiency
    num_threads = 14
    for _ in range(num_threads):
        thread = threading.Thread(target=process_queue)
        thread.daemon = True
        thread.start()
    
   
    # Wait for all URLs to be scraped
    print("-" * 40)
    logging.info("All URLs have been scraped.")


    # Rank word frequencies and export them to a CSV file
    ranked_words = word_counter.most_common()
    with open('vogue_ranked_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
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
        s3.upload_file('vogue_ranked_data.csv', 'gaineddata', 'vogue_ranked_data.csv')
        
        for filename in os.listdir('/Users/taliak/Documents/GitHub/LooksByData/articletext'):
            file_path = os.path.join('/Users/taliak/Documents/GitHub/LooksByData/articletext', filename)  
            s3.upload_file(file_path, 'gaineddata', filename) 

        for filename in os.listdir('/Users/taliak/Documents/GitHub/LooksByData/articleimages'):
            file_path = os.path.join('/Users/taliak/Documents/GitHub/LooksByData/articleimages', filename)
            s3.upload_file(file_path, 'gaineddata/images/', filename)


        logging.info("Files have been uploaded to S3!")
    except Exception as e:
        logging.error(f"Error occurred while uploading files to S3: {e}")


if __name__ == "__main__":
    main()



# Notes:
# make sure to scrape on a jupyter server and not on a local machine for the AI part of this.
