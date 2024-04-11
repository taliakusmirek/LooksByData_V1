# Technically you shouldn't be using this. Technically. But if you want to, you can....at your own risk.




import instaloader
from collections import Counter
import csv
import time
import random
import re
import requests
from PIL import Image
import time

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

L = instaloader.Instaloader()

# Pre-define the Instagram account to use for scraping and crawling in the variable below
scrapeuser = ""
#PW: 



# Log into scrapeuser account each time crawler is used: this is for security purposes
L.interactive_login(scrapeuser) 

# Words to filter out of results
common_words = ["i", "the", "my", "to", "a", "and", "you", "in", "so", "for", "me", "of", "is", "it", "this", "with", "that", "be", "are", "its", "was", "on", "at", "from", "like", "all", "have", "if", "get", "we", "because", "dont", "as", "things", "people", "good", "best", "just", "one", "about", "an", "beautiful", "day", "thank", "last", "when", "new", "your", "what", "by"]

# PRE-ESTABLISHED: words to scrape for, and users to scrape from
luxury_brands = ["gucci", "chanel", "louisvuitton", "hermes", "prada", "dior", "versace", "fendi", "balenciaga", "valentino"]
fashion_words = ["fashion", "style", "outfit", "trend", "clothing", "apparel", "designer", "luxury", "model", "runway", "vogue", "glamour", "trendy", "chic", "stylish", "couture", "accessories", "shopping", "wardrobe", "fashionista", "fashionable", "trendsetter", "fashionblogger", "fashionweek", "fashiondesigner", "fashionstyle", "fashionphotography", "fashionmodel", "fashioninspo", "fashiondaily", "fashionaddict", "fashionlover", "fashiongram", "fashionpost", "fashionforward", "fashiondiaries", "fashiongirl", "fashiontrends", "fashionlovers", "fashiondesign", "fashionphotographer", "fashionphotograph", "fashionphotographers", "fashionphotographs", "fashionphotographyappreciation", "fashionphotographyofficial", "fashionphotographyoftheday", "fashionphotographyworkshop", "fashionphotographyacademy", "fashionphotographyblog", "fashionphotographyeditorial", "fashionphotographyevents", "fashionphotographyinstitute", "fashionphotographyinspiration", "fashionphotographyinternational", "fashionphotographyislife", "fashionphotographylove", "fashionphotographyofinstagram", "fashionphotographyproject", "fashionphotographytips", "fashionphotographyworkshops", "fashionphotographyworld", "fashionphotographyworkshop", "fashionphotographyworkshops", "fashionphotographyacademy", "fashionphotographyblog", "fashionphotographyeditorial", "fashionphotographyevents", "fashionphotographyinstitute", "fashionphotographyinspiration", "fashionphotographyinternational", "fashionphotographyislife", "fashionphotographylove", "fashionphotographyofinstagram", "fashionphotographyproject", "fashionphotographytips", "fashionphotographyworkshops", "fashionphotographyworld", "fashionphotographyworkshop", "fashionphotographyworkshops", "fashionphotographyacademy", "fashionphotographyblog", "fashionphotographyeditorial", "fashionphotographyevents", "fashionphotographyislife", "fashionphotographylove", "fashionphotographyofinstagram", "fashionphotographyproject", "fashionphotographytips", "fashionphotographyworkshops", "fashionphotographyworld", "fashionphotographyworkshop", "fashionphotographyworkshops", "fashionphotographyacademy", "fashionphotographyblog", "fashionphotographyeditorial", "fashionphotographyevents", "fashionphotographyinstitute", "fashionphotographyinspiration", "fashionphotographyinternational", "fashionphotographyislife", "fashionphotographylove", "fashionphotographyofinstagram", "fashionphotographyproject", "fashionphotographytips", "fashionphotographyworkshops", "fashionphotographyworld", "fashionphotographyworkshop", "fashionphotographyworkshops", "fashionphotographyacademy", "fashionphotographyblog", "fashionphotographyeditorial", "fashionphotographyevents"]
username = ["loewe", "aritzia", "jihoon", "matildadjerf", "ninaheatherlea", "christinaelezaj", "lydsbutler", "prettylittlething", "daisyherriott"]


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

# Function to fetch posts containing specified keywords
def fetch_posts_by_hashtags(hashtags, count=100):
    posts = []
    for hashtag in hashtags:
        print(f"Fetching posts for hashtag: {hashtag}...")
        for post in L.get_hashtag_posts(hashtag):
            posts.append(post)
            if len(posts) >= count:
                break
        if len(posts) >= count:
            break
    return posts


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
            # Filter posts that mention luxury brands or fashion-related words
            if any(brand in caption_text for brand in luxury_brands) or any(word in caption_text for word in fashion_words):
                fashion_data.update(words)
        # Extract hashtags
        hashtags = post.caption_hashtags
        if hashtags:
            hashtags = [hashtag for hashtag in hashtags if hashtag.lower() not in common_words]
            # Filter posts that mention luxury brands or fashion-related words
            if any(brand in hashtags for brand in luxury_brands) or any(word in hashtags for word in fashion_words):
                fashion_data.update(hashtags)
        L.context.user_agent = random.choice(USER_AGENTS)
    return fashion_data


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
    input_filename = 'instagram_data.csv'
    output_filename = 'influencer_comparisons.csv'
    output_folder = 'instagram_images'

    hashtags_to_search = luxury_brands + fashion_words
    posts = fetch_posts_by_hashtags(hashtags_to_search)

    # Fetch posts with specified keywords and brands
    for user in username:
        print(f"Fetching posts from {user}...")
        posts = fetch_user_posts(user)

        print("Extracting fashion-related data...")
        fashion_data = extract_fashion_data(posts)

        ranked_instagram = fashion_data.most_common()

        print("Appending data to CSV...")
        with open(input_filename, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            for word, frequency in ranked_instagram:
                csv_writer.writerow([word, frequency])
        
        print("Fetching and resizing images...")
        fetch_and_resize_images(posts, output_folder)

        print("Data has been successfully extracted!")
        print("-" * 40)

        # Add a random delay before fetching data from the next user
        delay = random.randint(15, 135) 
        print(f"Waiting for {delay} seconds...please stand by!")
        time.sleep(delay)

    print("Finding most overlapping words...")
    find_most_overlapping_words(input_filename, output_filename)
    print("Ranked words saved to 'instagram_ranked_words.csv'")
    print("All images saved to 'instagram_images' folder.")

if __name__ == "__main__":
    main()





