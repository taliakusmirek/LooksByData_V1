import os
from PIL import Image
import numpy as np
import csv
import image_recognition
import nlp
from datetime import date

def create_dataset(txt_folder, image_folder):
    dataset = []

    txt_folder = str(txt_folder)
    dir1 = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(dir1, txt_folder)):
        dir1 = os.path.join(dir1, txt_folder)
    else:
        raise(Exception(f"The following foler does not exist: {txt_folder}"))
    txt_file = [os.path.join(dir1, filename) for filename in os.listdir(dir1)]

    image_folder = str(image_folder)
    dir2 = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(dir2, image_folder)):
        dir2 = os.path.join(dir2, image_folder)
    else:
        raise(Exception(f"The following foler does not exist: {image_folder}"))
    image_file = [os.path.join(dir2, filename) for filename in os.listdir(dir2)]


    # Process text data from all TXT files
    for txt_file in os.listdir(txt_folder):
            txt_file_path = os.path.join(txt_folder, txt_file)
            with open(txt_file_path, 'r', encoding='utf-8', errors='replace') as file:
                text = file.read() #.encode('utf-8', errors='replace').decode('utf-8')
                processed_text = nlp.tokenize_text(text)  
                dataset.append({'text': processed_text, 'image': None})

    # Process image data from all image files
    for image_file in os.listdir(image_folder):
            image_file_path = os.path.join(image_folder, image_file)
            image_data = image_recognition.predict(image_file_path)  
            dataset.append({'text': None, 'image': image_data})

    # Save dataset as CSV
    dataset_name = date.today().strftime("%Y-%m-%d")
    csv_file_path = os.path.join(f'{dataset_name}.csv')
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['text', 'image'])
        writer.writeheader()
        writer.writerows(dataset)


    return dataset