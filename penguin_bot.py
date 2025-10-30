# ============================================================
# 🐧 Cowalsky PenguinBot - Streamlit + Gemini + OpenAI Fallback
# ============================================================

# ---------- Imports ----------
import os
import io
import base64
from dotenv import load_dotenv
from PIL import Image
import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import random

# ---------- Environment Setup ----------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- Streamlit Page Setup ----------
st.set_page_config(page_title="Cowalsky AI", page_icon="🐧", layout="centered")

# ---------- Sidebar ----------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/0/0f/Penguin_icon.svg", width=120)
    st.title("Cowalsky AI")
    st.markdown("### ❄️ Penguin-powered AI companion")
    st.toggle("🌙 Dark Mode (via Streamlit theme settings)")
    st.markdown("---")
    st.caption("Made by Parth, Arnav, Aarav.\nSupports Gemini + OpenAI fallback for reliability!")

# ---------- Session State ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- Helper Function: Penguin-style Replies ----------
def penguin_reply(text: str) -> str:
    phrases = [
        "🐧 *flaps wings* That’s quite something!",
        "❄️ Cool as ice, here’s what I found:",
        "Brrr... logic this crisp can only come from the poles!",
        "Sliding into knowledge like it’s fresh snow:"
    ]
    preface = random.choice(phrases)
    return f"{preface}\n\n{text}"

# ---------- Gemini + OpenAI Fallback ----------
def generate_text_or_image(prompt, image=None):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        if image:
            response = model.generate_content([prompt, image])
        else:
            response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Fallback to OpenAI if Gemini quota or failure
        try:
            completion = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are Cowalsky, a friendly and witty penguin assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            return completion.choices[0].message.content
        except Exception as e2:
            return f"⚠️ Error: {e2}"

# ---------- Image Generation ----------
def generate_image(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        result = model.generate_content(prompt, generation_config={"mime_type": "image/png"})
        image_data = result._result.response.candidates[0].content.parts[0].inline_data.data
        image_bytes = base64.b64decode(image_data)
        return Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        st.error(f"Image generation error: {e}")
        return None

# ---------- Input Section ----------
st.markdown("### Enter your message or image prompt below:")
user_input = st.text_area("", placeholder="Ask Cowalsky anything...")

col1, col2 = st.columns(2)
with col1:
    text_btn = st.button("Generate Text")
with col2:
    img_btn = st.button("Generate Image")

# ---------- Text Output ----------
if text_btn and user_input.strip():
    with st.spinner("Thinking like a penguin..."):
        response = generate_text_or_image(user_input)
    st.subheader("Cowalsky says:")
    st.write(penguin_reply(response))
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("Cowalsky", response))

# ---------- Image Output ----------
if img_btn and user_input.strip():
    with st.spinner("Drawing ice art..."):
        image = generate_image(user_input)
    if image:
        st.image(image, caption="Nano Banana Creation", use_container_width=True)
        # Download button
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.download_button(
            label="Download Image",
            data=byte_im,
            file_name="cowalsky_art.png",
            mime="image/png",
        )

# ---------- Chat History ----------
if st.session_state.chat_history:
    st.markdown("### Chat History")
    for sender, msg in st.session_state.chat_history:
        st.markdown(f"**{sender}:** {msg}")

# ---------- Footer ----------
st.markdown("---")
st.caption("Made by Parth, Arnav, Aarav. ❄️ Powered by Gemini & OpenAI.")
