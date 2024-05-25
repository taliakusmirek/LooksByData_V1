# Purpose of nlp.py
# This file contains functions that are used to process text data for the purpose of natural language processing.
# The functions are used to tokenize text data, remove punctuation, remove stop words, and lemmatize words.
# The functions are used to process text data from the articletext folder in the project directory.


import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('stopwords')

def tokenize_text(text):
    # tokenize text
    tokens = word_tokenize(text)
    # convert to lowercase
    tokens = [w.lower() for w in tokens]
    # remove punctuation from each word
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens]
    # remove remaining tokens that are not alphabetic
    words = [word for word in stripped if word.isalpha()]
    # filter out stop words
    stop_words = set(stopwords.words('english'))
    words = [w for w in words if not w in stop_words]
    # lemmatize words
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(w) for w in words]
    return words

