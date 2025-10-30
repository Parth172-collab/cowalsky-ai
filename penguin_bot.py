# ============================================================
# Cowalsky (Gen-2) - Streamlit app (fixed genai.configure)
# ============================================================

import os
import io
import base64
import requests
from dotenv import load_dotenv
from PIL import Image
import streamlit as st

# Correct imports for Gemini + OpenAI
import google.generativeai as genai
from openai import OpenAI

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not GOOGLE_API_KEY:
    st.error("Missing GOOGLE_API_KEY in environment.")
if not OPENAI_API_KEY:
    st.warning("Missing OPENAI_API_KEY in environment — OpenAI fallback may not work.")

# ----------------------------
# Configure clients
# ----------------------------
genai.configure(api_key=GOOGLE_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ----------------------------
# Streamlit page config
# ----------------------------
st.set_page_config(page_title="Cowalsky (Gen-2)", page_icon="🐧", layout="wide")

# ----------------------------
# Sidebar: Kowalski image + controls
# ----------------------------
st.sidebar.title("Kowalski Control Panel")

kowalski_url = "https://upload.wikimedia.org/wikipedia/en/0/0c/Kowalski_%28Madagascar%29.png"
try:
    resp = requests.get(kowalski_url, timeout=8)
    if resp.status_code == 200:
        kowalski_img = Image.open(io.BytesIO(resp.content))
        st.sidebar.image(kowalski_img, caption="Kowalski — The Brains Behind the Ice", use_container_width=True)
    else:
        st.sidebar.warning("Could not load Kowalski image (HTTP {}).".format(resp.status_code))
except Exception:
    st.sidebar.warning("Could not load Kowalski image (network error).")

sigma_mode = st.sidebar.checkbox("Sigma Mode", value=False)
st.sidebar.markdown("---")
st.sidebar.caption("Made by Parth, Arnav, Aarav")

# ----------------------------
# Models (use available/compatible model ids)
# ----------------------------
# Use the Flash text model (change if you prefer another available model)
TEXT_MODEL = "gemini-2.5-flash"
# Use Gemini image model name if you want to try Gemini image generation.
# We'll try Gemini for images first, then fallback to OpenAI if it fails.
IMAGE_MODEL = "gemini-2.5-flash-image"

# ----------------------------
# Helpers / Generators
# ----------------------------
def penguin_response_text(raw_text: str, sigma: bool) -> str:
    """Return a single-line Cowalsky reply. If sigma True, include a short roast in the same line."""
    if sigma:
        roast = " (That’s colder than Antarctic wind — try harder.)"
        return f"🐧 Cowalsky: {raw_text.strip()}{roast}"
    else:
        return f"🐧 Cowalsky: {raw_text.strip()}"

def generate_text(prompt: str, sigma: bool) -> str:
    """Generate text via Gemini (with single-line sigma roast if enabled)."""
    try:
        system = (
            "You are Cowalsky, a witty penguin scientist. Answer helpfully and with light penguin humor. "
            "If Sigma Mode is enabled, append a short roast to the same line."
        )
        # Using GenerativeModel interface
        model = genai.GenerativeModel(TEXT_MODEL)
        response = model.generate_content([system, prompt])
        text = response.text if hasattr(response, "text") else str(response)
        return penguin_response_text(text, sigma)
    except Exception as e:
        # fallback: try OpenAI ChatCompletion
        try:
            completion = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are Cowalsky, a witty penguin scientist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            text = completion.choices[0].message.content
            return penguin_response_text(text, sigma)
        except Exception as e2:
            return f"⚠️ Both generators failed: Gemini error: {e}; OpenAI error: {e2}"

def generate_image_gemini(prompt: str):
    """Try to generate an image using Gemini image model. Returns PIL.Image or raises."""
    model = genai.GenerativeModel(IMAGE_MODEL)
    resp = model.generate_content(prompt)
    # extract base64 from response structure
    try:
        b64 = resp.candidates[0].content.parts[0].inline_data.data
        image_bytes = base64.b64decode(b64)
        return Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        raise RuntimeError(f"Gemini image parse error: {e}")

def generate_image_openai(prompt: str):
    """Fallback image generation using OpenAI images API (size 1024x1024)."""
    try:
        result = openai_client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )
        b64 = result.data[0].b64_json
        image_bytes = base64.b64decode(b64)
        return Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        raise RuntimeError(f"OpenAI image error: {e}")

def generate_image(prompt: str):
    """Try Gemini first, then OpenAI fallback. Return PIL.Image or None."""
    try:
        return generate_image_gemini(prompt)
    except Exception:
        try:
            return generate_image_openai(prompt)
        except Exception as e:
            st.error(f"Image generation failed: {e}")
            return None

def analyze_image_with_gemini(uploaded_file):
    """Send an image to Gemini for analysis (no mime_type field)."""
    try:
        img = Image.open(uploaded_file).convert("RGB")
        # Create a model instance and pass image as multimodal part
        model = genai.GenerativeModel(TEXT_MODEL)
        # Many SDKs accept [prompt, image] style; use image directly as second content
        response = model.generate_content(["Describe this image like a penguin scientist.", img])
        return response.text if hasattr(response, "text") else str(response)
    except Exception as e:
        return f"Image analysis error: {e}"

# ----------------------------
# Conversation state & UI
# ----------------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []

st.title("Cowalsky (Gen-2)")
st.caption("A witty penguin AI — analysis, generation, and optional Sigma roast in one line.")

# Input area
user_input = st.text_area("Enter your message or prompt:")

# Top: Conversation log (above image tools)
st.subheader("Conversation Log")
if not st.session_state.conversation:
    st.info("No conversation yet — ask Cowalsky something!")
else:
    for entry in st.session_state.conversation:
        speaker = entry["speaker"]
        text = entry["text"]
        if speaker == "You":
            st.markdown(f"**🧍 You:** {text}")
        else:
            st.markdown(f"**{text}**")

# Controls row
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Send"):
        if user_input.strip():
            reply = generate_text(user_input, sigma_mode)
            st.session_state.conversation.append({"speaker": "You", "text": user_input})
            st.session_state.conversation.append({"speaker": "Cowalsky", "text": reply})
            # refresh to show updated log
            st.experimental_rerun()
with col2:
    if st.button("Generate Image"):
        if user_input.strip():
            with st.spinner("Generating image..."):
                img = generate_image(user_input)
            if img:
                st.image(img, caption="Generated Image", use_container_width=True)
                # Download
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button(
                    label="Download Image",
                    data=buf.getvalue(),
                    file_name="cowalsky_image.png",
                    mime="image/png"
                )
with col3:
    uploaded = st.file_uploader("Upload image for analysis", type=["png", "jpg", "jpeg"])
    if uploaded and st.button("Analyze Image"):
        with st.spinner("Analyzing image..."):
            analysis = analyze_image_with_gemini(uploaded)
        st.subheader("Image Analysis")
        st.write(analysis)

# Footer / credits
st.markdown("---")
st.caption("Made by Parth, Arnav, Aarav.")
