# ============================================================
# Cowalsky (Gen-2) - Streamlit app with model selection + fixes
# ============================================================

import os
import io
import base64
import requests
from dotenv import load_dotenv
from PIL import Image
import streamlit as st

# Safe imports for APIs
try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ----------------------------
# Streamlit page setup
# ----------------------------
st.set_page_config(page_title="Cowalsky (Gen-2)", page_icon="🐧", layout="wide")

# ----------------------------
# Sidebar: image + model options
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

# Sigma mode
sigma_mode = st.sidebar.checkbox("Sigma Mode", value=False)

# Model selection
model_choice = st.sidebar.radio(
    "Select AI Engine",
    ["Gemini only", "GPT-4 only", "Both (auto fallback)"],
    index=2
)

st.sidebar.markdown("---")
st.sidebar.caption("Made by Parth, Arnav, Aarav")

# ----------------------------
# Configure API clients safely
# ----------------------------
if genai and GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
        st.sidebar.warning(f"Gemini init error: {e}")
else:
    st.sidebar.warning("Gemini API not configured.")

if OpenAI and OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        st.sidebar.warning(f"OpenAI init error: {e}")
else:
    openai_client = None
    st.sidebar.warning("OpenAI API not configured.")

# ----------------------------
# Constants
# ----------------------------
TEXT_MODEL = "gemini-2.5-flash"
IMAGE_MODEL = "gemini-2.5-flash-image"

# ----------------------------
# Helper Functions
# ----------------------------
def penguin_response_text(raw_text: str, sigma: bool) -> str:
    if sigma:
        return f"🐧 Cowalsky: {raw_text.strip()} (That’s colder than Antarctic wind — try harder.)"
    else:
        return f"🐧 Cowalsky: {raw_text.strip()}"

def generate_text_gemini(prompt: str, sigma: bool):
    try:
        model = genai.GenerativeModel(TEXT_MODEL)
        response = model.generate_content(
            ["You are Cowalsky, a witty penguin scientist.", prompt]
        )
        return penguin_response_text(response.text, sigma)
    except Exception as e:
        raise RuntimeError(f"Gemini text error: {e}")

def generate_text_gpt(prompt: str, sigma: bool):
    try:
        result = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Cowalsky, a witty penguin scientist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        text = result.choices[0].message.content
        return penguin_response_text(text, sigma)
    except Exception as e:
        raise RuntimeError(f"GPT-4 text error: {e}")

def generate_text(prompt: str, sigma: bool, choice: str):
    if choice == "Gemini only":
        return generate_text_gemini(prompt, sigma)
    elif choice == "GPT-4 only":
        return generate_text_gpt(prompt, sigma)
    else:
        try:
            return generate_text_gemini(prompt, sigma)
        except Exception:
            return generate_text_gpt(prompt, sigma)

def generate_image(prompt: str):
    """Try Gemini first, then OpenAI fallback."""
    try:
        model = genai.GenerativeModel(IMAGE_MODEL)
        resp = model.generate_content(prompt)
        b64 = resp.candidates[0].content.parts[0].inline_data.data
        image_bytes = base64.b64decode(b64)
        return Image.open(io.BytesIO(image_bytes))
    except Exception:
        if openai_client:
            try:
                result = openai_client.images.generate(
                    model="gpt-image-1",
                    prompt=prompt,
                    size="1024x1024"
                )
                b64 = result.data[0].b64_json
                return Image.open(io.BytesIO(base64.b64decode(b64)))
            except Exception as e2:
                st.error(f"OpenAI image error: {e2}")
                return None
        else:
            st.error("Image generation failed: no valid API.")
            return None

def analyze_image(uploaded_file):
    """Analyze uploaded image using Gemini."""
    try:
        img = Image.open(uploaded_file).convert("RGB")
        model = genai.GenerativeModel(TEXT_MODEL)
        response = model.generate_content(["Describe this image like a penguin scientist.", img])
        return response.text
    except Exception as e:
        return f"Image analysis error: {e}"

# ----------------------------
# Streamlit UI
# ----------------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []

st.title("Cowalsky (Gen-2)")
st.caption("A witty penguin AI — analysis, generation, and optional Sigma roast in one line.")

# Input area
user_input = st.text_area("Enter your message or prompt:")

# Conversation log (above image tools)
st.subheader("Conversation Log")
if not st.session_state.conversation:
    st.info("No conversation yet — ask Cowalsky something!")
else:
    for entry in st.session_state.conversation:
        if entry["speaker"] == "You":
            st.markdown(f"**🧍 You:** {entry['text']}")
        else:
            st.markdown(f"**{entry['text']}**")

# Button row
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Send"):
        if user_input.strip():
            try:
                reply = generate_text(user_input, sigma_mode, model_choice)
                st.session_state.conversation.append({"speaker": "You", "text": user_input})
                st.session_state.conversation.append({"speaker": "Cowalsky", "text": reply})
                st.experimental_rerun()
            except Exception as e:
                st.error(e)

with col2:
    if st.button("Generate Image"):
        if user_input.strip():
            with st.spinner("Generating image..."):
                img = generate_image(user_input)
            if img:
                st.image(img, caption="Generated Image", use_container_width=True)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button(
                    "Download Image",
                    data=buf.getvalue(),
                    file_name="cowalsky_image.png",
                    mime="image/png",
                )

with col3:
    uploaded = st.file_uploader("Upload image for analysis", type=["png", "jpg", "jpeg"])
    if uploaded and st.button("Analyze Image"):
        with st.spinner("Analyzing image..."):
            result = analyze_image(uploaded)
        st.subheader("Image Analysis")
        st.write(result)

# Footer
st.markdown("---")
st.caption("🐧 Made by Parth, Arnav, Aarav — powered by Gemini & GPT-4.")
