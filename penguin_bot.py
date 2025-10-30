import os
import io
import base64
from PIL import Image
import streamlit as st
from dotenv import load_dotenv
from google import genai
from openai import OpenAI

# ============================================================
# Load environment variables
# ============================================================
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not GOOGLE_API_KEY:
    st.error("Missing GOOGLE_API_KEY in environment.")
if not OPENAI_API_KEY:
    st.warning("Missing OPENAI_API_KEY — image fallback may not work.")

# ============================================================
# Initialize clients
# ============================================================
gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ============================================================
# Page setup
# ============================================================
st.set_page_config(page_title="Cowalsky AI", layout="wide")
st.sidebar.image("https://i.imgur.com/WlGvO6T.png", use_container_width=True)
st.sidebar.title("Cowalsky AI")
st.sidebar.caption("Chat, create, and analyze — powered by Gemini + OpenAI")
st.sidebar.write("Made by Parth, Arnav, Aarav")

# ============================================================
# Functions
# ============================================================

# --- Generate Text Response ---
def generate_text(prompt):
    try:
        response = gemini_client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"text": f"You are Cowalsky, a witty and intelligent penguin. Reply warmly, with penguin humor.\n\n{prompt}"}
                    ]
                }
            ],
        )
        return response.text.strip()
    except Exception as e:
        return f"Error generating text: {e}"

# --- Generate Image ---
def generate_image(prompt):
    try:
        response = gemini_client.models.generate_content(
            model="models/gemini-2.5-flash-image",
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
        )
        image_base64 = response.parts[0].inline_data.data
        image_bytes = base64.b64decode(image_base64)
        return Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        st.warning("Gemini image generation failed, trying OpenAI fallback.")
        try:
            result = openai_client.images.generate(
                model="gpt-image-1-mini", prompt=prompt, size="512x512"
            )
            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
            return Image.open(io.BytesIO(image_bytes))
        except Exception as e2:
            st.error(f"Both generators failed: {e2}")
            return None

# --- Analyze Image ---
def analyze_image(image, prompt):
    try:
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        response = gemini_client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"text": f"Analyze this image like a witty penguin scientist.\n\nTask: {prompt}"},
                        {"inline_data": {"mime_type": "image/png", "data": base64.b64encode(img_bytes.read()).decode("utf-8")}},
                    ],
                }
            ],
        )
        return response.text.strip()
    except Exception as e:
        return f"Error analyzing image: {e}"

# ============================================================
# UI Layout
# ============================================================
st.title("Cowalsky AI")
st.caption("Your friendly penguin assistant — powered by Gemini and OpenAI")

tab1, tab2, tab3 = st.tabs(["Chat", "Generate Image", "Image Analyzer"])

# --- Tab 1: Chat ---
with tab1:
    prompt = st.text_area("Ask Cowalsky something:", placeholder="Type here...")
    if st.button("Generate Response"):
        if prompt.strip():
            with st.spinner("Cowalsky is thinking..."):
                reply = generate_text(prompt)
            st.subheader("Cowalsky says:")
            st.write(reply)
        else:
            st.warning("Please enter a prompt.")

# --- Tab 2: Image Generator ---
with tab2:
    img_prompt = st.text_area("Describe your image idea:", placeholder="Example: a penguin surfing in Hawaii")
    if st.button("Generate Image"):
        if img_prompt.strip():
            with st.spinner("Drawing your masterpiece..."):
                image = generate_image(img_prompt)
            if image:
                st.image(image, caption="Generated Image", use_container_width=True)
                img_buffer = io.BytesIO()
                image.save(img_buffer, format="PNG")
                st.download_button(
                    "Download Image",
                    data=img_buffer.getvalue(),
                    file_name="penguin_art.png",
                    mime="image/png",
                )
        else:
            st.warning("Please enter a description.")

# --- Tab 3: Image Analyzer ---
with tab3:
    uploaded = st.file_uploader("Upload an image to analyze:", type=["png", "jpg", "jpeg"])
    analyze_prompt = st.text_input("What should Cowalsky analyze?", "Describe what’s happening in this image")
    if uploaded and st.button("Analyze Image"):
        image = Image.open(uploaded)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        with st.spinner("Cowalsky is observing carefully..."):
            result = analyze_image(image, analyze_prompt)
        st.subheader("Analysis Result:")
        st.write(result)

# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.markdown("Made by **Parth, Arnav, Aarav**.")
