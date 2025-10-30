# ============================================================
# Cowalsky (Gen-2) — Streamlit AI Assistant
# Dual-engine (Gemini + GPT-4), Sigma Mode, Dark/Light Themes
# Made by Parth, Arnav, Aarav.
# ============================================================

import os
import io
import base64
import requests
import streamlit as st
from PIL import Image
from openai import OpenAI
import google.generativeai as genai

# ------------------------- CONFIG ----------------------------
st.set_page_config(page_title="Cowalsky (Gen-2)", page_icon="🐧", layout="centered")

# --- Retrieve API keys (flat structure in secrets.toml) ---
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")

# --- Initialize clients ---
genai.configure(api_key=GOOGLE_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------------- SIDEBAR ----------------------------
with st.sidebar:
    st.title("Cowalsky (Gen-2) Settings")

    # Load Kowalski image safely
    kowalski_url = "https://upload.wikimedia.org/wikipedia/en/0/0c/Kowalski_%28Madagascar%29.png"
    try:
        resp = requests.get(kowalski_url, timeout=5)
        if resp.status_code == 200:
            st.image(Image.open(io.BytesIO(resp.content)), use_container_width=True)
        else:
            st.warning("Couldn't load Kowalski image.")
    except Exception:
        st.warning("Network error loading Kowalski image.")

    st.markdown("---")
    ai_choice = st.radio("Choose AI Model:", ["Gemini", "GPT-4", "Both"])
    sigma_mode = st.checkbox("Sigma Mode (Savage Replies)")
    dark_theme = st.checkbox("Dark Theme", value=True)
    st.markdown("---")
    st.caption("Made by Parth, Arnav, Aarav.")

# --------------------- THEME HANDLING -------------------------
if dark_theme:
    st.markdown(
        """
        <style>
        body, .stApp { background-color: #0d1117; color: white; }
        textarea, .stTextInput>div>div>input { background-color: #161b22 !important; color: white !important; }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        body, .stApp { background-color: white; color: black; }
        </style>
        """,
        unsafe_allow_html=True
    )

# ------------------------- FUNCTIONS --------------------------

def cowalsky_roast(user_text):
    """Return a short savage Sigma-style roast."""
    roasts = [
        "You call that a thought? Even my flippers type better.",
        "That was colder than Antarctica itself.",
        "Bold of you to assume I needed to hear that, rookie.",
        "Try again, commander — logic not found.",
    ]
    import random
    return random.choice(roasts)

def gemini_reply(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Gemini Error: {e}]"

def gpt4_reply(prompt):
    try:
        res = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Cowalsky, a brilliant penguin strategist with wit and logic."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"[GPT-4 Error: {e}]"

def generate_image(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        result = model.generate_content([
            {"role": "user", "parts": [f"Generate an image of: {prompt}"]}
        ], generation_config={"response_mime_type": "image/png"})
        if result and result.candidates:
            img_data = base64.b64decode(result.candidates[0].content.parts[0].inline_data.data)
            return Image.open(io.BytesIO(img_data))
        return None
    except Exception as e:
        st.error(f"Image generation error: {e}")
        return None

def analyze_image(uploaded_image):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        img = Image.open(uploaded_image)
        result = model.generate_content(["Describe this image briefly:", img])
        return result.text.strip()
    except Exception as e:
        return f"[Image analysis error: {e}]"

# --------------------- CHAT INTERFACE -------------------------
st.title("Cowalsky (Gen-2)")
st.markdown("Chat with a tactical penguin powered by Gemini and GPT-4.")

# Initialize chat history
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# Display previous chat messages
for msg in st.session_state.chat_log:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Cowalsky:** {msg['content']}")

# Input field
user_input = st.text_area("Enter your message:", placeholder="Type something cool...")

# Send button
if st.button("Send") and user_input.strip():
    user_text = user_input.strip()
    st.session_state.chat_log.append({"role": "user", "content": user_text})

    # Generate AI response(s)
    responses = []
    if ai_choice in ["Gemini", "Both"]:
        responses.append(gemini_reply(user_text))
    if ai_choice in ["GPT-4", "Both"]:
        responses.append(gpt4_reply(user_text))

    reply = "\n\n---\n\n".join(responses)
    if sigma_mode:
        reply = cowalsky_roast(user_text) + " " + reply

    st.session_state.chat_log.append({"role": "assistant", "content": reply})
    st.rerun()

# --------------------- IMAGE TOOLS ---------------------------
st.markdown("## Image Tools")

col1, col2 = st.columns(2)
with col1:
    img_prompt = st.text_input("Image generation prompt:")
    if st.button("Generate Image") and img_prompt:
        with st.spinner("Drawing..."):
            image = generate_image(img_prompt)
        if image:
            st.image(image, caption="Generated Image", use_container_width=True)
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            st.download_button("Download Image", data=buf.getvalue(),
                               file_name="cowalsky_image.png", mime="image/png")

with col2:
    upload = st.file_uploader("Upload image to analyze:", type=["png", "jpg", "jpeg"])
    if upload and st.button("Analyze Image"):
        with st.spinner("Analyzing..."):
            analysis = analyze_image(upload)
        st.success(analysis)

