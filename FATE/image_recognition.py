# Purpose of image_recognition.py
# This file contains functions that are used to process image data for the purpose of image recognition.
# The functions are used to predict trends using image data from the articleimages folder in the project directory.

import np
import os
import nltk
import tensorflow as tf
from keras.applications import ResNet50
from keras.applications.resnet50 import preprocess_input, decode_predictions
from keras.preprocessing import image


model = ResNet50(weights='imagenet')

def predict(image_folder):
    image_folder = str(image_folder)
    dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(dir, image_folder)):
        dir = os.path.join(dir, image_folder)
    else:
        raise(Exception(f"The following foler does not exist: {image_folder}"))
    image_paths = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            image_paths.append(os.path.join(root, file))
    predictions = []
    for image_path in image_paths:
        try:
            img = image.load_img(image_path, target_size=(224, 224))
            x = image.img_to_array(img)
            x = preprocess_input(x)
            x = np.expand_dims(x, axis=0)
            preds = model.predict(x)
            predictions.append(decode_predictions(preds, top=3)[0])
        except:
            print(f"0/1 Error processing image: {image_path}")
    return predictions
