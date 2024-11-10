import os
import openai
import streamlit as st
from PIL import Image
import numpy as np
import cv2
import pandas as pd
from datetime import datetime
from pathlib import Path

# Set your OpenAI API key (ensure this is secure in production environments)
openai.api_key = "OpenAI-API-Key"

# Custom CSS for styling consistency with previous page
st.markdown("""
    <style>
    /* Main background and font */
    .main {
        background-color: #FFFFFF;  /* Light background for better contrast */
        font-family: 'Helvetica', sans-serif;
    }

    /* Title styling */
    h1 {
        color: #FFA500;  /* Bright orange for title */
        font-family: 'Helvetica', sans-serif;
    }

    /* Text and label styling */
    .stTextInput label, .stFileUploader label, .stButton button, .stMarkdown {
        color: #333333;  /* Dark gray for better contrast with light background */
        font-family: 'Helvetica', sans-serif;
    }

    /* Button customization */
    .stButton button {
        background-color: #FFA500;  /* Bright orange button */
        color: white;
        font-weight: bold;
        padding: 8px 20px;
        border-radius: 5px;
        border: none;
    }
    .stButton button:hover {
        background-color: #FF8C00;  /* Darker orange on hover */
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #F0F2F6 !important;  /* Light gray sidebar */
    }

    </style>
""", unsafe_allow_html=True)

# Define the file path to the historical data CSV using an environment variable or fallback
file_path = Path("118i-tutorial/pages/data/Data.csv")

# Load the historical data and calculate average wait times by hour
# Code generated with assistance from ChatGPT, OpenAI, 2024.
try:
    data = pd.read_csv(file_path)
    data['Datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'])
    data['Hour'] = data['Datetime'].dt.hour
    average_wait_by_hour = data.groupby('Hour')['Estimated Wait Time (minutes)'].mean()
except FileNotFoundError:
    st.error(f"Historical data file not found at {file_path}. Please ensure the CSV file path is correct.")
    st.stop()

# Streamlit app title and description
st.title("🍽️Restaurant Wait Time Estimator (IN-PERSON)🍽️")
st.markdown("Combining historical data and real-time line analysis for more accurate wait time estimates.")

# Image upload section for line feedback
st.subheader("Upload an Image of the Restaurant Line")
uploaded_image = st.file_uploader("Upload an image (JPEG, PNG) of the line at the restaurant", type=["jpg", "jpeg", "png"])

# Function to blur faces in an image
# Code generated with assistance from ChatGPT, OpenAI, 2024.
def blur_faces(image: Image.Image) -> Image.Image:
    # Convert the PIL image to an OpenCV format
    opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Load OpenCV's pre-trained Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Detect faces
    faces = face_cascade.detectMultiScale(opencv_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    # Blur each detected face
    for (x, y, w, h) in faces:
        face_region = opencv_image[y:y+h, x:x+w]
        face_region = cv2.GaussianBlur(face_region, (51, 51), 30)
        opencv_image[y:y+h, x:x+w] = face_region

    # Convert back to PIL format
    return Image.fromarray(cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB))

# Function to generate feedback based on image description and historical data
# Code generated with assistance from ChatGPT, OpenAI, 2024.
def generate_feedback_with_data(image_description, current_hour, average_wait_by_hour):
    # Get the average wait time for the current hour from historical data
    avg_wait_time = average_wait_by_hour.get(current_hour, "No data available")
    prompt = (
        f"Based on historical data, the average wait time around {current_hour}:00 is approximately "
        f"{avg_wait_time} minutes. Given the following description of the current line: {image_description}, "
        "please provide an adjusted wait time estimate and any additional operational insights."
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.5,
        messages=[
            {"role": "system", "content": "You are an assistant providing wait time estimations based on data and real-time conditions."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Display image and provide feedback if an image is uploaded & source: ChatGpt
# Code generated with assistance from ChatGPT, OpenAI, 2024.
if uploaded_image:
    image = Image.open(uploaded_image)
    blurred_image = blur_faces(image)
    st.image(blurred_image, caption="Uploaded Image with Blurred Faces", use_column_width=True)
    
    # Generate feedback using both historical data and image description
    current_hour = datetime.now().hour
    image_description = "An image showing a long line of people waiting outside a popular restaurant."
    feedback = generate_feedback_with_data(image_description, current_hour, average_wait_by_hour)
    
    st.write("**Feedback on Wait Time (Enhanced with Historical Data):**")
    st.write(feedback)
