import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import os
from PIL import Image
from io import BytesIO

# Set OpenAI API key
openai.api_key = "api-key-here"

st.title("Restaurant Line Planner 🍽️")
st.markdown("Plan your restaurant visit with real-time data and content summaries.")

# Section: Input Restaurant Details
st.subheader("Enter Your Restaurant Details")
restaurant_name = st.text_input("Restaurant Name", placeholder="e.g., Panda Express, Chipotle, Taco Bell, Subway")
location = st.text_input("Location", placeholder="e.g., Sunnyvale, Santa Clara, Palo Alto, Fremont")
visit_time = st.text_input("Planned Visit Time", placeholder="e.g., Breakfast = 9:00 AM - 11:30 AM, Lunch = 12:30 - 2:30, Dinner = 5:30 PM - 8:00 PM")

# URL input for restaurant website
url = st.text_input("Restaurant Website URL", placeholder="https://example.com")

# Function to fetch and parse content from the provided URL
def get_web_content(url):
    time_related_content = ""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract time-related content
        paragraphs = soup.find_all(['p', 'div', 'span'])
        for p in paragraphs:
            text = p.get_text().strip()
            # Filter for keywords like "hours," "open," "close," etc.
            if any(keyword in text.lower() for keyword in ["hours", "open", "close", "time", "am", "pm"]):
                time_related_content += text + '\n'

        return time_related_content if time_related_content else "No time-related information found."
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the content: {e}")
        return None

# Function to generate a recommendation based on fetched hours and visit time
def generate_recommendation(time_related_content, visit_time):
    prompt = f"""Based on the restaurant's operating hours:\n\n{time_related_content}\n\n
    and the user's planned visit time: {visit_time}, provide a recommendation on whether this is a suitable time to visit the restaurant."""
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a helpful assistant providing visit recommendations based on restaurant hours."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Single button to fetch content, summarize, and provide recommendation
if st.button("Provide Recommendation"):
    # Fetch time-related content from the URL
    display_content = get_web_content(url)
    
    if display_content:
        # Generate recommendation based on visit time and restaurant hours
        recommendation = generate_recommendation(display_content, visit_time)
        st.write("**Visit Recommendation:**")
        st.write(recommendation)
    else:
        st.write("No time-related information could be extracted from the website.")

# Image upload section for line feedback
st.subheader("Upload an Image of the Restaurant Line")
uploaded_image = st.file_uploader("Upload an image (JPEG, PNG) of the line at the restaurant", type=["jpg", "jpeg", "png"])

# Function to generate feedback based on image description
def generate_image_feedback(image_description):
    prompt = f"Provide feedback on the likely wait time based on the following image description: {image_description}."
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.5,
        messages=[
            {"role": "system", "content": "You are an assistant providing feedback on restaurant wait times based on image descriptions."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Display image and provide feedback if an image is uploaded
if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image of the Restaurant Line", use_column_width=True)
    
    # Example description based on the uploaded image
    # You may customize this or provide input based on the type of image content you want to describe
    image_description = "An image showing a long line of people waiting outside a popular restaurant."
    
    # Generate and display feedback based on the image
    feedback = generate_image_feedback(image_description)
    st.write("**Feedback on Wait Time:**")
    st.write(feedback)

# Additional navigation options and features for UI
st.markdown("For more Streamlit features, visit the [documentation](https://docs.streamlit.io/develop).")
