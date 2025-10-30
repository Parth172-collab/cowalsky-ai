# ============================================================
# Cowalsky (Gen-2) — Streamlit AI Assistant
# Dual-engine (Gemini 2.5 + GPT-4), Sigma Mode, Dark/Light Themes
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

    # ✅ Fixed Kowalski image (reliable hosted link)
    kowalski_url = "https://lh3.googleusercontent.com/pw/AP1GczMWKowalskiFixedImage=w800-h800"
    try:
        response = requests.get(kowalski_url, timeout=10)
        if response.status_code == 200:
            kowalski_img = Image.open(io.BytesIO(response.content))
            st.image(kowalski_img, use_container_width=True)
        else:
            st.warning("🐧 Kowalsky is hiding in the shadows...")
    except Exception:
        st.warning("Network error loading Kowalsky image.")

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

def analyze_image(uploaded_image):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        img = Image.open(uploaded_image)
        result = model.generate_content(["Describe this image briefly:", img])
        return result.text.strip()
    except Exception as e:
        return f"[Image analysis error: {e}]"

# --------------------- CHAT INTERFACE -------------------------
st.title("Cowalsky (Gen-2)")
st.markdown("Chat with a tactical penguin powered by Gemini 2.5 and GPT-4.")

# Initialize chat history
if "chat" not in st.session_state:
    st.session_state.chat = []

# Chat input and button
user_input = st.text_input("Enter your message:")
send_button = st.button("Send", use_container_width=True)

# Handle input
if send_button and user_input.strip():
    st.session_state.chat.append(("You", user_input))

    reply = ""
    if ai_choice == "Gemini 2.5":
        reply = gemini_reply(user_input)
    elif ai_choice == "GPT-4":
        reply = gpt4_reply(user_input)
    else:
        g1, g2 = gemini_reply(user_input), gpt4_reply(user_input)
        reply = f"**Gemini:** {g1}\n\n**GPT-4:** {g2}"

    if sigma_mode:
        reply = cowalsky_roast() + " " + reply

    st.session_state.chat.append(("Cowalsky", reply))

# Display chat log above tools
st.subheader("💬 Conversation Log")
for sender, msg in st.session_state.chat:
    if sender == "You":
        st.markdown(f"**🧍‍♂️ {sender}:** {msg}")
    else:
        st.markdown(f"**🐧 {sender}:** {msg}")

# ------------------- IMAGE TOOLS -------------------
st.markdown("---")
st.subheader("🎨 Generate Image")
img_prompt = st.text_input("Describe an image to generate:")
if st.button("Generate Image", use_container_width=True):
    img = generate_image(img_prompt)
    if img:
        st.image(img, caption="Generated by Cowalsky", use_container_width=True)
        st.download_button("Download Image", data=io.BytesIO(img.tobytes()), file_name="cowalsky_image.png")

st.markdown("---")
st.subheader("🔍 Image Analyzer")
uploaded = st.file_uploader("Upload an image for analysis", type=["png", "jpg", "jpeg"])
if uploaded:
    st.image(uploaded, caption="Uploaded Image", use_container_width=True)
    if st.button("Analyze Image", use_container_width=True):
        analysis = analyze_image(uploaded)
        st.success(f"**Analysis:** {analysis}")
