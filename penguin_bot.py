import os
import io
import base64
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from PIL import Image
from google import genai

# ==========================
# Load environment variables
# ==========================
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ==========================
# API Clients
# ==========================
gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ==========================
# Streamlit Page Setup
# ==========================
st.set_page_config(page_title="Cowalsky (Gen-2)", page_icon="🐧", layout="wide")

# ==========================
# Sidebar (Kowalski Image + Mode Toggle)
# ==========================
kowalski_base64 = """
iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAMAAACahl6sAAAAM1BMVEXMzMyWlpb///+hoaGcnJzQ0NCMjIzd3d3v7+/V1dXNzc3R0dGYmJizs7OXl5e/v7+mpqaqqqqJiYk2E1r0AAABxUlEQVR4nO3cyQ3CMAwEUP1J+98cQIJ3lNVi6q2JPDlZb57QpAIAAAAAAAAAAAAAAAAAAAD8L8QyxEj7KZYwT8lJbMW8s9R6jP/5RbK9P+QWyz0b7E8i2v+qU6x7E8y3P/kFss9G+xPItr/qn2U2yPiXPvU3qxzI8xT3X6sYyLMU913rOMi3FfZ/qxrIuxX2f6sSyL8U91+rGMi3FfZ/qxrIuxX2f6sSyL8U91+rGMi3FfZ/qxrIuxX2f6sSyL8U91+rGMi3FfZ/qxrIuxX2f6sSyL8U91+rGMi3FfZ/qxrIuxX2f6sSyL8U91+rGMi3FfZ/qxrIuxX2f6sSyL8U91+rGMi3FfZ/qxrIuxX2f6sSyL8U9y8+7Yo5zUoAAAAASUVORK5CYII=
"""
kowalski_img = Image.open(io.BytesIO(base64.b64decode(kowalski_base64)))
st.sidebar.image(kowalski_img, caption="Kowalski — The Brains Behind the Ice", use_container_width=True)

sigma_mode = st.sidebar.toggle("Sigma Mode")
dark_theme = st.sidebar.toggle("Dark Theme")

if dark_theme:
    st.markdown(
        """
        <style>
        body { background-color: #0E1117; color: white; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ==========================
# Page Title
# ==========================
st.title("Cowalsky (Gen-2)")
st.caption("A witty penguin AI with Sigma intelligence. Analyze, generate, and roast — all in one.")

# ==========================
# Functions
# ==========================
def penguin_personality(reply, sigma=False):
    if sigma:
        return f"🐧 Cowalsky: {reply} (That’s colder than Antarctic wind, try harder next time.)"
    else:
        return f"🐧 Cowalsky: {reply}"

def generate_response(prompt, sigma=False):
    try:
        system_prompt = (
            "You are Cowalsky, a witty penguin scientist from Madagascar. "
            "You answer cleverly and humorously. In Sigma mode, you roast the user subtly within the same line."
        )
        result = gemini_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[system_prompt, prompt]
        )
        response = result.text.strip()
        return penguin_personality(response, sigma)
    except Exception as e:
        return f"⚠️ Text generation error: {e}"

def generate_image(prompt):
    try:
        result = openai_client.images.generate(
            model="gpt-image-1-mini",
            prompt=prompt,
            size="1024x1024"
        )
        image_base64 = result.data[0].b64_json
        image_data = base64.b64decode(image_base64)
        return Image.open(io.BytesIO(image_data))
    except Exception as e:
        st.error(f"Image generation error: {e}")
        return None

def analyze_image(uploaded_file):
    try:
        image_data = uploaded_file.getvalue()
        img_base64 = base64.b64encode(image_data).decode("utf-8")

        result = gemini_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                {"role": "user", "parts": [
                    {"text": "Analyze this image and describe it like a penguin scientist."},
                    {"inline_data": {"mime_type": "image/png", "data": img_base64}}
                ]}
            ]
        )
        return result.text.strip()
    except Exception as e:
        return f"⚠️ Image analysis error: {e}"

# ==========================
# Conversation State
# ==========================
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

user_input = st.text_area("Enter your message or prompt:")

if st.button("Generate Text"):
    if user_input.strip():
        with st.spinner("Thinking... 🧠"):
            reply = generate_response(user_input, sigma_mode)
        st.session_state.chat_log.append(("You", user_input))
        st.session_state.chat_log.append(("Cowalsky", reply))

# ==========================
# Display Conversation Log
# ==========================
if st.session_state.chat_log:
    st.subheader("Conversation Log")
    for speaker, msg in st.session_state.chat_log:
        if speaker == "You":
            st.markdown(f"**🧍 You:** {msg}")
        else:
            st.markdown(f"**{msg}**")

# ==========================
# Image Tools
# ==========================
uploaded_image = st.file_uploader("Upload an image to analyze (optional)", type=["png", "jpg", "jpeg"])

col1, col2 = st.columns(2)
with col1:
    img_btn = st.button("Generate Image")
with col2:
    analyze_btn = st.button("Analyze Image")

if img_btn and user_input.strip():
    with st.spinner("Generating Image..."):
        image = generate_image(user_input)
    if image:
        st.image(image, caption="Generated Image", use_container_width=True)
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        st.download_button("Download Image", buf.getvalue(), "cowalsky_creation.png", "image/png")

if analyze_btn and uploaded_image:
    with st.spinner("Analyzing like a true penguin scientist..."):
        analysis = analyze_image(uploaded_image)
    st.subheader("Image Analysis")
    st.write(analysis)

# ==========================
# Credits
# ==========================
st.markdown("---")
st.caption("Made by Parth, Arnav, Aarav.")
