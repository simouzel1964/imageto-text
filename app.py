from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import sqlite3

# --- Step 1: Environment Variables and Model Setup ---
load_dotenv()
api_key = os.getenv("GOOGLE_GENERATIVEAI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro-vision')  # Replace with your desired model

# --- Step 2: Database Setup ---
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()
cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        email TEXT
    )
''')
conn.commit()

# --- Step 3: Helper Functions ---
def is_valid_email(email):
    return '@' in email and '.' in email

def get_user_info():
    print("Inside get_user_info")  
    full_name = st.text_input("Enter your full name:", key="full_name")
    email = st.text_input("Enter your email address:", key="email")

    if full_name and email:
        if is_valid_email(email):
            save_user_info(full_name, email)
            st.success("User information saved!")
            return full_name, email
        else:
            st.error("Please enter a valid email address.")
    else:
        st.error("Please enter both your full name and email address.")

    return None, None  # Default if nothing is entered

def save_user_info(full_name, email):
    with conn:
        cursor.execute("INSERT INTO users (full_name, email) VALUES (?, ?)", (full_name, email))
        conn.commit()

def get_gemini_response(input, image, full_name, email):
  if input!="":
      response=model.generate_content([input, image, full_name, email])
  else:
      response=model.generate_content(image)
  return response.text


# --- Step 4: Streamlit App Structure ---
st.set_page_config(page_title="Image Demo")
st.header("Image Teller")

# Get user information (call only once)
print("Before calling get_user_info") 
full_name, email = get_user_info()
print("After calling get_user_info") 

if full_name and email:  
    input = st.text_input("Input:", key="image_input") 
    uploaded_file = st.file_uploader("Choose an image ...", type=["jpg", "jpeg", "png", "webp", "video/mp4"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("Tell me about the Image"):
            with st.spinner("Generating description..."): 
                response = get_gemini_response(input, image, full_name, email)
                st.subheader("The Response is")
                st.write(response) 
else:
    st.warning("User information not provided. App functionality limited.") 