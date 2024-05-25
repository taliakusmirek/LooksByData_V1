import pandas as pd
from sklearn.model_selection import train_test_split
from statsmodels.tsa.arima.model import ARIMA
from datetime import date, timedelta
import time
import nltk
nltk.download('wordnet')

# Import all files for the FATE pipeline
import image_recognition
import make_datasets
import trend_prediction
import articlecrawler
import voguecrawler


# Save the output of each step to a text file for emailing to the user in Step 5
def save_output_to_csv(output, filename):
    if isinstance(output, list):
        output = pd.DataFrame(output)
    if isinstance(output, tuple):
        output = pd.DataFrame(output)
    output.to_csv(filename, index=False)


# Goal: Run each step specified and save its output to a text file to be emailed to the user
def main():

    # Step 1: Run the crawlers: if completed manually make sure to comment this out. 
    # Note: This should be done starting every Wednesday to ensure the most recent data is used.
    #voguecrawler_output = voguecrawler.main()
    #save_output_to_txt(voguecrawler_output, 'voguecrawler_output.txt')
    #articlecrawler_output = articlecrawler.main()
    #save_output_to_txt(articlecrawler_output, 'articlecrawler_output.txt')
    print("Crawlers have been run and their data is saved!")

    # Step 2: Run the image recognition
    #image_recognition_output = image_recognition.predict("articleimages")
    #save_output_to_csv(image_recognition_output, 'image_recognition_output.txt')
    print("Image recognition is now complete!")

    # Step 3: Make datasets with the data
    #make_datasets.create_dataset("articletext", "articleimages")
    print("Dataset has now been created!")

    # Step 4: Make trend predictions with the datasets, update ARIMA model for future predictions, and generate outfit recommendations
    trend_prediction_output = trend_prediction.main()
    save_output_to_csv(trend_prediction_output, 'trend_prediction_output.txt')

    # Step 5: Email the user the results of the FATE pipeline: IN PROGRESS!
    #email.main(voguecrawler_output, articlecrawler_output, image_recognition_output, trend_prediction_output)

    # Output to the user that the FATE pipeline has been completed
    print("FATE pipeline has been completed!")


if __name__ == "__main__":
    main()