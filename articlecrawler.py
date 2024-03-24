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


# Words to filter out of CSV file later
common_words = set([
    "i", "and", "the", "my", "to", "a", "you", "me", "in", "so", "for", "etc"
])

# Words to find articles
keywords = [
    "dress", "wear", "look", "moments", "style", "celebrity", "celebrity style", "photos", "show", "shows",
    "era", "trend", "wears", "jewelry", "season", "couture", "after-party", "girl", "women", "spring", "summer",
    "fall", "winter", "shoe", "swimwear", "bag", "report", "week", "fashion week", "edit", "she", "lookbook", 
    "Fall", "Summer", "Spring", "Winter", "wardrobe", "outfit", "styles", "outfits", "idea", "cute", "wore", 
    "weather", "best", "fits", "shop", "new", "How to", "cuter", "worth", "need", "needed", "these", "love", "happy", "guide","studio","brand","brands","clothing"
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
    html_content = get_html(url)
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        # Find all links on the page
        links = [link.get('href') for link in soup.find_all('a', href=True)]
        for link in links:
            # Add pagination pages to the queue with lower priority
            if re.match(r'^https?://', link) and 'page=' in link:
                url_queue.put((1, link))
            # Add article URLs to the queue with higher priority
            elif re.match(r'^https?://', link) and 'article' in link:
                url_queue.put((0, link))
        logging.info(f"Crawled page: {url}")

def extract_article_content(url, output_dir):
    # Get HTML content of the article
    html_content = get_html(url)
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        # Extract text content from article
        text_content = ""
        for tag in soup.find_all(['p', 'span']):
            text_content += tag.get_text() + "\n"

        # Extract and save images
        images = soup.find_all('img')
        for idx, img in enumerate(images):
            img_url = img.get('src')
            try:
                response = requests.get(img_url)
                img = Image.open(BytesIO(response.content))
                img.save(f'{output_dir}/image_{idx}.jpg')
            except Exception as e:
                logging.error(f"Error downloading or saving image: {e}")

        # Save text content to a file
        with open(f'{output_dir}/article_content.txt', 'w', encoding='utf-8') as file:
            file.write(text_content)
        logging.info(f"Article content extracted and saved to {output_dir}/article_content.txt")
    else:
        logging.error(f"Failed to fetch HTML from {url}")


# Function to scrape article content from a page
def scrape_page(url):
    html_content = get_html(url)
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        title_tags = soup.find_all(['h1', 'h2', 'h3','a'])
        if title_tags:
            title = title_tags[0].get_text().lower()
            # Check if any keyword is present in the title
            if any(keyword in title for keyword in keywords):
                # Extract text content from article
                text = " ".join(tag.get_text() for tag in soup.find_all(['p', 'span']))
                # Clean the text
                cleaned_text = re.sub(r'[^\w\s]', '', text.lower())  # Remove punctuation and convert to lowercase
                # Tokenize the text
                words = cleaned_text.split()
                words = [word for word in words if word not in common_words]
                word_counter.update(words)
                # Write article name and link to CSV
                article_name = title_tags[0].get_text()
                with open('fashion_data.csv', 'a', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow([article_name, url])

                images = soup.find_all('img')
                for idx, img in enumerate(images):
                    img_url = img.get('src')
                    download_and_resize_image(img_url, f'{idx}_{article_name}')
                
                # Extract and save article content for AI model training
                output_dir = f'training/{article_name}'  
                os.makedirs(output_dir, exist_ok=True)  
                extract_article_content(url, output_dir)


            logging.info(f"Scraped page: {url}")
        else:
            logging.warning(f"No title found for page: {url}")
    else:
        logging.error(f"Failed to scrape page: {url}")

# Function to download and resize images
def download_and_resize_image(img_url, filename):
    try:
        response = requests.get(img_url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((256, 256))  
        img.save(f'articleimages/{filename}.jpg')
        logging.info(f"Downloaded and resized image: {filename}")
    except Exception as e:
        logging.error(f"Error downloading or resizing image: {e}")



# Function to process URLs from the queue
def process_queue():
    while True:
        priority, url = url_queue.get()
        if priority == 0:  # High priority (article URLs)
            scrape_page(url)
        else:  # Low priority (pagination pages)
            crawl_page(url)
        url_queue.task_done()
        time.sleep(random.uniform(1, 3))  








# Run it!
def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Start URLs for crawling
    start_urls = [
        "https://www.vogue.com/fashion/celebrity-style",
        "https://www.vogue.com/fashion/street-style",
        "https://www.vogue.com/fashion/models",
        "https://www.vogue.com/fashion/trends",
        "https://www.asos.com/us/women/fashion-feed/?ctaref=ww|fashionandbeauty",
        "https://www.aritzia.com/us/en/stories",
        "https://www.glamour.com/fashion",
        "https://www.cosmopolitan.com/style-beauty/fashion/",
        "https://www.elle.com/fashion/",
        "https://blog.nastygal.com/style/page/2/",
        "https://www.ssense.com/en-us/editorial/fashion",
        "https://www2.hm.com/en_us/women/seasonal-trending/trending-now.html",
        "https://www.zara.com/us/en/woman-new-in-l1180.html?v1=1180001",
        "https://www.freepeople.com/free-people-blog/",
        "https://www.anthropologie.com/stories-style",
        "https://www.madewell.com/Inspo.html",
        "https://www.farfetch.com/style-guide/",
        "https://www.modaoperandi.com/editorial/what-we-are-wearing",
        "https://www.brownsfashion.com/woman/stories/fashion",
        "https://www.saksfifthavenue.com/?orgin=%2Feditorial",
        "https://www.neimanmarcus.com/editorial",
    ]

    # Add start URLs to the queue
    for url in start_urls:
        url_queue.put((0, url))

    # Create worker threads
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
    with open('fashion_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Word', 'Frequency'])
        csv_writer.writerows(ranked_words)

    logging.info("Data has been successfully exported to 'fashion_data.csv'.")

if __name__ == "__main__":
    main()


# keep track of number of articles scraped
# keep track of number of images
    #fix row labels of CSV