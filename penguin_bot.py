# ============================================================
# Cowalsky (Gen-2) — Streamlit AI Assistant
# Dual-engine (Gemini 2.5 + GPT-4), Sigma Mode, Dark Mode default
# Newest replies appear first + spaced conversation layout
# ============================================================

import os
import io
import base64
import requests
import streamlit as st
from PIL import Image
from openai import OpenAI
import google.generativeai as genai
import random

# ------------------------- CONFIG ----------------------------
st.set_page_config(page_title="Cowalsky (Gen-2)", page_icon="🐧", layout="centered")

# --- Retrieve API keys ---
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")

# --- Initialize clients ---
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------------- SIDEBAR ----------------------------
with st.sidebar:
    st.title("Cowalsky (Gen-2) Settings")

    # ✅ Working Kowalski image (GitHub CDN)
    kowalski_url = "https://raw.githubusercontent.com/ParthK3107/public-assets/main/kowalski_penguin.png"
    try:
        response = requests.get(kowalski_url, timeout=10)
        if response.status_code == 200:
            kowalski_img = Image.open(io.BytesIO(response.content))
            st.image(kowalski_img, use_container_width=True)
        else:
            st.warning("🐧 Kowalsky is hiding in the shadows... (Image blocked)")
    except Exception:
        st.warning("🐧 Kowalsky couldn’t load — probably on a stealth mission.")

    st.markdown("---")
    ai_choice = st.radio("Choose AI Model:", ["Gemini 2.5", "GPT-4", "Both"])
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
        textarea, .stTextInput>div>div>input {
            background-color: #161b22 !important;
            color: white !important;
        }
        .chat-bubble { margin-bottom: 20px; }
        </style>
        """,
        unsafe_allow_html=True
    )

# ------------------------- FUNCTIONS --------------------------
def cowalsky_roast():
    roasts = [
        "You call that logic? Even my flippers do better.",
        "That thought was colder than Antarctica.",
        "Bold move, soldier — but logic’s on vacation.",
        "I’ve seen smarter fish than that idea.",
    ]
    return random.choice(roasts)

def gemini_reply(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Gemini Error: {e}]"

def gpt4_reply(prompt):
    try:
        res = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Cowalsky, a witty penguin strategist with sharp logic."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"[GPT-4 Error: {e}]"

def generate_image(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-exp")
        result = model.generate_content([{"role": "user", "parts": [f"Generate an image of: {prompt}"]}])
        if result and result.candidates:
            img_data = base64.b64decode(result.candidates[0].content.parts[0].inline_data.data)
            return Image.open(io.BytesIO(img_data))
        return None
    except Exception as e:
        st.error(f"Image generation error: {e}")
        return None

# ✅ Enhanced Image Analyzer — with user question
def analyze_image(uploaded_image, user_question):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        image_bytes = uploaded_image.read()
        response = model.generate_content([
            {"role": "user", "parts": [
                {"text": f"Answer this question about the image: {user_question}"},
                {"inline_data": {"mime_type": "image/png", "data": base64.b64encode(image_bytes).decode("utf-8")}}
            ]}
        ])
        return response.text.strip()
    except Exception as e:
        return f"[Image analysis error: {e}]"

# --------------------- CHAT INTERFACE -------------------------
st.title("Cowalsky (Gen-2)")
st.markdown("Chat with a tactical penguin powered by Gemini 2.5 and GPT-4.")

if "chat" not in st.session_state:
    st.session_state.chat = []

user_input = st.text_input("Enter your message:")
send_button = st.button("Send", use_container_width=True)

if send_button and user_input.strip():
    st.session_state.chat.append(("You", user_input))
    reply = ""
    if ai_choice == "Gemini 2.5":
        reply = gemini_reply(user_input)
    elif ai_choice == "GPT-4":
        reply = gpt4_reply(user_input)
    else:
        reply = f"Gemini: {gemini_reply(user_input)}\n\nGPT-4: {gpt4_reply(user_input)}"

    if sigma_mode:
        reply += "\n\n💀 " + cowalsky_roast()

    st.session_state.chat.append(("Cowalsky", reply))

# --- Display Chat (Newest First + Blank Spacing) ---
if st.session_state.chat:
    st.markdown("### Conversation Log")
    for sender, msg in reversed(st.session_state.chat):  # 👈 newest first
        st.markdown(f"**{'🐧' if sender == 'Cowalsky' else '🧑'} {sender}:** {msg}")
        st.markdown("<br>", unsafe_allow_html=True)  # blank spacing

# --------------------- IMAGE GENERATION -----------------------
st.markdown("---")
st.subheader("Image Generation")
img_prompt = st.text_input("Enter an image prompt:")
if st.button("Generate Image"):
    with st.spinner("Drawing like a tactical penguin..."):
        image = generate_image(img_prompt)
    if image:
        st.image(image, caption="Generated by Cowalsky", use_container_width=True)
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        st.download_button("Download Image", buf.getvalue(), "cowalsky_image.png", "image/png")

# --------------------- IMAGE ANALYZER -------------------------
st.markdown("---")
st.subheader("Image Analyzer")

uploaded_image = st.file_uploader("Upload an image for analysis", type=["png", "jpg", "jpeg"])

if uploaded_image:
    st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
    user_question = st.text_input("Ask something about this image:")
    if st.button("Analyze Image"):
        with st.spinner("Analyzing image like a penguin detective..."):
            answer = analyze_image(uploaded_image, user_question or "Describe this image in detail.")
        st.markdown(f"**🐧 Cowalsky’s Analysis:** {answer}")
