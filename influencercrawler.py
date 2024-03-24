import instaloader
from collections import Counter
import csv
import time
import random
import re
import requests
from PIL import Image

L = instaloader.Instaloader()

# Pre-define the Instagram account to use for scraping in the variable below
scrapeuser = "taliadouceur"
#PW: Elizabeth2006@



# Log into scrapeuser account each time crawler is used: this is for security purposes
L.interactive_login(scrapeuser) 

# Words to filter out of results
common_words = ["i", "the", "my", "to", "a", "and", "you", "in", "so", "for", "me", "of", "is", "it", "this", "with", "that", "be", "are", "its", "was", "on", "at", "from", "like", "all", "have", "if", "get", "we", "because", "dont", "as", "things", "people", "good", "best", "just", "one", "about", "an", "beautiful", "day", "thank", "last", "when", "new", "your", "what", "by"]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
]

# Fetch posts from a specific user 
def fetch_user_posts(username):
    user_profile = instaloader.Profile.from_username(L.context, username)
    posts = user_profile.get_posts()
    return posts

# Function to fetch and resize images of posts
def fetch_and_resize_images(posts, output_folder, target_size=(256, 256)):
    for post in posts:
        image_url = post.url
        image_filename = f"{output_folder}/{post.mediaid}.jpg"  # Unique filename based on media ID
        try:
            response = requests.get(image_url)
            with open(image_filename, 'wb') as f:
                f.write(response.content)
            image = Image.open(image_filename)
            image = image.resize(target_size)
            image.save(image_filename)
            print(f"Image saved: {image_filename}")
        except Exception as e:
            print(f"Error fetching or resizing image: {e}")


# Extract fashion-related data from captions and hashtags
def extract_fashion_data(posts):
    fashion_data = Counter()
    for post in posts:
        captions = post.caption
        if captions:
            # Extract text from captions
            caption_text = re.sub(r'[^\w\s#]', '', captions.lower())
            # Tokenize the text
            words = caption_text.split()
            words = [word for word in words if word not in common_words]
            fashion_data.update(words)
        # Extract hashtags
        hashtags = post.caption_hashtags
        if hashtags:
            hashtags = [hashtag for hashtag in hashtags if hashtag.lower() not in common_words]
            fashion_data.update(hashtags)
        L.context.user_agent = random.choice(USER_AGENTS)
    return fashion_data

# Add data to CSV, making sure to remove redundant common words and providing a column for influencers
def append_to_csv(data, filename, influencer):
    with open(filename, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        for word, frequency in data:
            csv_writer.writerow([word, frequency, influencer])

# Find the most overlapping words from each influencer's data
def find_most_overlapping_words(input_filename, output_filename):
    influencer_word_counts = {}
    
    # Read the CSV file and load the data into memory
    with open(input_filename, 'r', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        header = next(csv_reader)
        
        # Find the index of the columns based on their position
        word_index = 0  # Assuming the first column contains words
        frequency_index = 1  # Assuming the second column contains frequencies
        influencer_index = 2  # Assuming the third column contains influencer names
        
        # Initialize influencer_word_counts
        influencer_word_counts['all'] = Counter()
        
        # Iterate over the rows of the CSV file
        for row in csv_reader:
            word = row[word_index]
            influencer = row[influencer_index]
            frequency = int(row[frequency_index]) if row[frequency_index] else 0
            influencer_word_counts.setdefault(influencer, Counter())
            influencer_word_counts[influencer][word] += frequency
            # Update the overall word counts
            influencer_word_counts['all'][word] += frequency
    
    most_common_words = influencer_word_counts['all'].most_common()
    
    with open(output_filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Word', 'Frequency'])
        for word, frequency in most_common_words:
            csv_writer.writerow([word, frequency])







# Run it!
def main():
    usernames = ["jihoon", "matildadjerf", "ninaheatherlea", "christinaelezaj", "lydsbutler", "prettylittlething", "daisyherriott"]
    input_filename = 'influencer_data.csv'
    output_filename = 'influencer_finalcomparisons.csv'
    output_folder = 'images'

    for username in usernames:
        print("-" * 40)
        print(f"Fetching data for user: {username}")
        user_posts = fetch_user_posts(username)

        print("Extracting influencer-related data...")
        fashion_data = extract_fashion_data(user_posts)

        ranked_instagram = fashion_data.most_common()

        print("Appending data to CSV...")
        append_to_csv(ranked_instagram, input_filename, username)


        print("Fetching and resizing images...")
        fetch_and_resize_images(user_posts, output_folder)


        print("Data has been successfully extracted!")
        print("-" * 40)
        time.sleep(15)
    
    print("Finding most overlapping words...")
    find_most_overlapping_words(input_filename, output_filename)
    print("Most overlapping words saved to 'influencer_finalcomparisons.csv'")
    print("Images saved to 'images' folder.")

if __name__ == "__main__":
    main()





#matplotlib?
    # alter to look at accounts with fashion in it and not limit to certain users? 
    # base scrap ad crawl on HASHTAGS
    # fix row labels of csv