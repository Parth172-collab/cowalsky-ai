import os
import io
import base64
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import streamlit as st

# === Load environment and API key ===
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# === Streamlit Page Setup ===
st.set_page_config(page_title="Cowalsky AI", page_icon="❄️", layout="centered")

# === Sidebar ===
st.sidebar.title("Settings")
theme = st.sidebar.radio("Theme", ["Light", "Dark"])
model_choice = st.sidebar.selectbox(
    "Select Gemini Model",
    ["gemini-2.5-flash", "gemini-2.5-pro"],
    index=0
)
st.sidebar.markdown("---")
st.sidebar.info("Created by Parth, Arnav, Aarav")

# === Theme Customization ===
if theme == "Dark":
    st.markdown(
        """
        <style>
        body { background-color: #0e1117; color: #fafafa; }
        .stTextInput, .stTextArea { background-color: #262730; color: white; }
        </style>
        """,
        unsafe_allow_html=True
    )

# === Title and Intro ===
st.title("Cowalsky AI")
st.caption("Chat, analyze images, or generate visuals — powered by Google Gemini.")

# === Core Functions ===
def generate_text_or_analysis(prompt, image=None, model_name="gemini-2.5-flash"):
    """Generates text or analyzes an image using Gemini."""
    try:
        model = genai.GenerativeModel(model_name)
        if image:
            response = model.generate_content([prompt, image])
        else:
            response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

def generate_image(prompt):
    """Generates an image from a text prompt."""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-image")
        result = model.generate_content(prompt)
        image_data = result.candidates[0].content.parts[0].blob
        image = Image.open(io.BytesIO(image_data))
        return image
    except Exception as e:
        st.error(f"Image generation error: {e}")
        return None

def get_image_download_link(img, filename="cowalsky_image.png"):
    """Creates a download link for generated image."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    b64 = base64.b64encode(byte_im).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}">Download Image</a>'
    return href

# === Main Input Section ===
user_input = st.text_area("Enter your message or prompt:", placeholder="Type something...")

uploaded_file = st.file_uploader("Upload an image (optional for analysis):", type=["jpg", "jpeg", "png"])

# === Buttons ===
col1, col2 = st.columns(2)
with col1:
    text_btn = st.button("Generate Text / Analyze")
with col2:
    img_btn = st.button("Generate Image")

# === Outputs ===
if text_btn and user_input.strip():
    with st.spinner("Processing your request..."):
        image = None
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
        output = generate_text_or_analysis(user_input, image, model_choice)
    st.subheader("Result:")
    st.write(output)

if img_btn and user_input.strip():
    with st.spinner("Creating your image..."):
        image = generate_image(user_input)
    if image:
        st.image(image, caption="Generated Image", use_container_width=True)
        st.markdown(get_image_download_link(image), unsafe_allow_html=True)

# === Footer ===
st.markdown("---")
st.markdown("**Made by Parth, Arnav, Aarav.**")
