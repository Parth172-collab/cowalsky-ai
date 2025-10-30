# ============================================================
# Cowalsky (Gen-2) - A Streamlit App with Gemini AI
# ============================================================

import os
import io
import base64
import requests
from dotenv import load_dotenv
from google import genai
from PIL import Image
import streamlit as st

# --- Load environment and API key ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Page Setup ---
st.set_page_config(page_title="Cowalsky (Gen-2)", layout="centered")

# --- Sidebar with Kowalski Image ---
kowalski_url = "https://upload.wikimedia.org/wikipedia/en/0/0c/Kowalski_%28Madagascar%29.png"
try:
    response = requests.get(kowalski_url)
    if response.status_code == 200:
        kowalski_img = Image.open(io.BytesIO(response.content))
        st.sidebar.image(kowalski_img, use_container_width=True)
    else:
        st.sidebar.warning("Couldn't load Kowalski image.")
except Exception as e:
    st.sidebar.error(f"Image load error: {e}")

st.sidebar.title("Settings")
sigma_mode = st.sidebar.checkbox("Sigma Mode 😎", value=False)

# --- Model Setup ---
model_text = genai.GenerativeModel("gemini-1.5-flash")
model_image = genai.GenerativeModel("gemini-2.0-flash")

# --- Conversation Log Setup ---
st.title("Cowalsky (Gen-2)")
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# --- User Input ---
user_input = st.text_area("Enter your message:", placeholder="Ask Cowalsky something...")

# --- Functions ---
def generate_text_response(prompt):
    """Generate Cowalsky's text reply."""
    try:
        if sigma_mode:
            prompt = f"You are Cowalsky, a savage sigma penguin from Madagascar. Roast the user humorously in one line: {prompt}"
        else:
            prompt = f"You are Cowalsky, the smart penguin from Madagascar. Reply cleverly and politely: {prompt}"
        response = model_text.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

def generate_image(prompt):
    """Generate an image using Gemini."""
    try:
        response = model_image.generate_content([prompt])
        img_data = response.candidates[0].content.parts[0].inline_data.data
        image = Image.open(io.BytesIO(base64.b64decode(img_data)))
        return image
    except Exception as e:
        st.error(f"Image generation error: {e}")
        return None

def analyze_image(uploaded_file):
    """Analyze an uploaded image."""
    try:
        image = Image.open(uploaded_file)
        response = model_text.generate_content(["Analyze this image and describe it briefly.", image])
        return response.text.strip()
    except Exception as e:
        return f"Error analyzing image: {e}"

# --- Conversation Log Display ---
st.subheader("Conversation Log")
for entry in st.session_state.conversation:
    st.markdown(f"**You:** {entry['user']}")
    st.markdown(f"**Cowalsky:** {entry['bot']}")

# --- Buttons Section ---
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Send"):
        if user_input.strip():
            reply = generate_text_response(user_input)
            st.session_state.conversation.append({"user": user_input, "bot": reply})
            st.rerun()

with col2:
    if st.button("Generate Image"):
        if user_input.strip():
            image = generate_image(user_input)
            if image:
                st.image(image, caption="Generated Image", use_container_width=True)
                # Create a downloadable image link
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                b64 = base64.b64encode(buffered.getvalue()).decode()
                href = f'<a href="data:file/png;base64,{b64}" download="cowalsky_image.png">Download Image</a>'
                st.markdown(href, unsafe_allow_html=True)

with col3:
    uploaded_file = st.file_uploader("Upload Image for Analysis", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        analysis = analyze_image(uploaded_file)
        st.subheader("Image Analysis")
        st.write(analysis)

# --- Credits ---
st.markdown("---")
st.caption("Made by Parth, Arnav, Aarav.")
