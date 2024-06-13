import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load the trained model
model_path = "model_fine_tuned_full.h5"
model = load_model(model_path)

# Define the labels for prediction
labels = ['NORMAL', 'PNEUMONIA']

def preprocess_image(image):
    # Preprocess the image
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)  # Convert to BGR
    img = cv2.resize(img, (128, 128))  # Adjust size as per your model's requirement
    img = img / 255.0  # Normalize pixel values
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    return img

def classify_image(image):
    # Preprocess the image
    img = preprocess_image(image)

    # Make prediction
    pred = model.predict(img)
    class_idx = np.argmax(pred)
    class_label = labels[class_idx]
    confidence = pred[0][class_idx]

    return class_label, confidence
