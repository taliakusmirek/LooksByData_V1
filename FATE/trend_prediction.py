import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from statsmodels.tsa.arima.model import ARIMA
from datetime import date
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import random

# Predefined outfit mapping here!
outfit_map = {
    'color': {
        'top': 'shirt/blouse',
        'bottom': 'pants/skirt',
        'dress': 'dress',
        'jacket': 'jacket/blazer',
        'shoes': 'shoes',
        'accessory': 'accessory'
    },
    'style': {
        'top': 'casual/formal',
        'bottom': 'casual/formal',
        'dress': 'casual/formal',
        'jacket': 'casual/formal',
        'shoes': 'casual/formal',
        'accessory': 'casual/formal'
    },
    'pattern': {
        'top': 'plain/patterned',
        'bottom': 'plain/patterned',
        'dress': 'plain/patterned',
        'jacket': 'plain/patterned',
        'shoes': 'plain/patterned',
        'accessory': 'plain/patterned'
    },
    'fabric': {
        'top': 'cotton/silk/wool',
        'bottom': 'denim/linen/leather',
        'dress': 'satin/chiffon/velvet',
        'jacket': 'tweed/cashmere/fur',
        'shoes': 'canvas/leather/suede',
        'accessory': 'metal/leather/fabric'
    },
    'occasion': {
        'top': 'casual/formal/party',
        'bottom': 'casual/formal/party',
        'dress': 'casual/formal/party',
        'jacket': 'casual/formal/party',
        'shoes': 'casual/formal/party',
        'accessory': 'casual/formal/party'
    },
    'weather': {
        'top': 'hot/mild/cold',
        'bottom': 'hot/mild/cold',
        'dress': 'hot/mild/cold',
        'jacket': 'hot/mild/cold',
        'shoes': 'hot/mild/cold',
        'accessory': 'hot/mild/cold'
    },
    'season': {
        'top': 'spring/summer/fall/winter',
        'bottom': 'spring/summer/fall/winter',
        'dress': 'spring/summer/fall/winter',
        'jacket': 'spring/summer/fall/winter',
        'shoes': 'spring/summer/fall/winter',
        'accessory': 'spring/summer/fall/winter'
    }
}

def preprocess_forecast_data(predicted_value, outfit_map):
  # Define probability distribution for choosing outfit categories (optional)
  category_weights = {'color': 0.25, 'style': 0.25, 'pattern': 0.25, 'fabric': 0.15, 'occasion': 0.1}
  
  # Randomly choose an outfit category based on weights
  chosen_category = np.random.choice(list(category_weights.keys()), p=list(category_weights.values()))
  
  # Randomly select a specific item within the chosen category
  random_index = random.randint(0, len(outfit_map[chosen_category]) - 1)
  predicted_item = list(outfit_map[chosen_category].values())[random_index]
  
  confidence_score = predicted_value

  return confidence_score, chosen_category, predicted_item







def convert_numeric_to_text(numeric_data, outfit_map):
  text_predictions = []
  for forecast in numeric_data:  # Loop through numeric data (confidence score + item info)
    if isinstance(forecast, tuple) and len(forecast) == 4:  # Check if it's a tuple with 3 elements
        confidence_score, score2, chosen_category, predicted_item = forecast
        outfit_prediction = {}
        for attribute, values in outfit_map.items():
          attribute_prediction = {}
          for item, options in values.items():
            supporting_data = get_supporting_data(numeric_data, chosen_category, predicted_item)
            # Confidence score is retrieved from the forecast data
            prediction_text = f"Consider a {predicted_item} {item} based on {confidence_score:.2f} confidence. Supported by the following terms from dataset: {supporting_data}"
            if confidence_score > 0.7:
                prediction_text = f"I recommend a {predicted_item} {item} based on high confidence."
            attribute_prediction[item] = {
                "predicted_option": prediction_text,
                "confidence_score": confidence_score,
                "predicted_category": chosen_category  # Add predicted category information
            }
          outfit_prediction[attribute] = attribute_prediction
        text_predictions.append(outfit_prediction)
    else:
        # Handle cases where forecast is not a valid tuple
        print(f"Warning: Unexpected data structure in forecast: {forecast}")
        text_predictions.append(forecast)
    
  return text_predictions

# Function to gain data from csv dataset that relates to each prediction in 'convert_numeric_to_text'
def get_supporting_data(train_data, chosen_category, predicted_item):
  if True:  
      keywords = [f"{predicted_item} {word}" for word in ["dress", "shirt", "pants", "shoes"]]  # Example keywords
      filtered_data = filtered_data[filtered_data['text'].str.contains("|".join(keywords))]  # Filter by keywords
      
      if not filtered_data.empty:
          top_term = filtered_data['text'].iloc[0]  # Assuming the first row provides the strongest support
          supporting_data = f"Examples include: {top_term}"
      else:
          supporting_data = "No specific examples found in the data."
  else:
      raise NotImplementedError("No summarization technique chosen!")

  return supporting_data


# Function to update ARIMA model with new data
def update_arima_model(topic_predictions):
    # Split data into training and testing sets
    train_data = topic_predictions[:, 0]
    train_data, test_data = train_test_split(train_data, test_size=0.2, shuffle=False)
    
    # Train ARIMA model
    arima_model = ARIMA(train_data, order=(5,1,0))
    arima_fit = arima_model.fit()
    
    # Generate forecasts for future time steps
    future_forecast = arima_fit.forecast(steps=len(test_data))
    
    # Preprocess forecast data (confidence score) and return a tuple
    preprocessed_forecast = [(score, *preprocess_forecast_data(score, outfit_map)) for score in future_forecast]  # Unpack preprocessed data
    
    text_predictions = convert_numeric_to_text(preprocessed_forecast, outfit_map)
    return text_predictions


# Function to perform topic modeling
def perform_topic_modeling(text_data):
    # Drop rows with NaN values
    text_data.dropna(inplace=True)
    
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(text_data)
    
    lda_model = LatentDirichletAllocation(n_components=5, random_state=42)
    lda_model.fit(X)
    
    return lda_model

# Create outfit recommendations based on trend predictions
def generate_outfit_recommendations(topic_predictions, outfit_map):
    outfit_recommendations = {}

    for topic, prediction in enumerate(topic_predictions):
        # Map topic to trend based on your criteria
        trend = f'trend_{topic}'
        if trend in outfit_map:
            # Get outfit items for the current trend category
            outfit_items = outfit_map[trend]
            # Add outfit items to recommendation
            for item_type, item_description in outfit_items.items():
                outfit_recommendations[item_type] = f"Consider {item_description} in {prediction}."

    return outfit_recommendations

def main():

    # Load data
    train_data = pd.read_csv(f'{date.today().strftime("%Y-%m-%d")}.csv')

    # Drop rows with NaN values in the 'text' column
    train_data.dropna(subset=['text'], inplace=True)

    if not train_data.empty:
        # Perform topic modeling on text data
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(train_data['text'])  # Fit the vectorizer on the text data
        lda_model = perform_topic_modeling(train_data['text'])

        # Get topic predictions for the training data
        topic_predictions = lda_model.transform(X)  # Transform using the fitted vectorizer

        # Generate outfit recommendations based on topic predictions
        outfit_recommendations = generate_outfit_recommendations(topic_predictions, outfit_map)

        # Update ARIMA model with the training data
        trend_predictions = update_arima_model(topic_predictions)

        return trend_predictions, outfit_recommendations
    else:
        print("No valid text data found in the dataset.")
        return None, None

if __name__ == "__main__":
    main()
