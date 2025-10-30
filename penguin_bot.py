# ======================================================
# 🐧 Cowalsky (Gen-2)
# AI Chat + Image Generator + Analyzer + Sigma Mode
# Made by Parth, Arnav, Aarav
# ======================================================

import os
import io
import base64
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
from openai import OpenAI
import google.generativeai as genai

# ------------------ LOAD API KEYS ---------------------
load_dotenv()
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# ------------------ PAGE CONFIG -----------------------
st.set_page_config(page_title="Cowalsky (Gen-2)", page_icon="🐧", layout="wide")
st.title("Cowalsky (Gen-2)")

# Sidebar — with Kowalski image
kowalski_url = "https://raw.githubusercontent.com/Parth2404AI/kowalski-assets/main/kowalski.png"
try:
    st.sidebar.image(kowalski_url, use_container_width=True)
except:
    st.sidebar.warning("Could not load Kowalski image (check URL or permissions).")

st.sidebar.title("Settings")

# Model selection
model_choice = st.sidebar.radio("Select AI Model", ["Gemini", "GPT-4", "Both"])
sigma_mode = st.sidebar.checkbox("Enable Sigma Mode")

# Configure Gemini
if GOOGLE_API_KEY and len(GOOGLE_API_KEY.strip()) > 20:
    try:
        genai.configure(api_key=GOOGLE_API_KEY.strip())
        st.sidebar.success("Gemini API ready!")
    except Exception as e:
        st.sidebar.error(f"Gemini init failed: {e}")
else:
    st.sidebar.warning("Gemini API key missing!")

# Configure OpenAI
try:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    st.sidebar.success("OpenAI API ready!")
except Exception as e:
    st.sidebar.error(f"OpenAI init failed: {e}")

# ------------------ FUNCTIONS -------------------------

def generate_gpt4_response(prompt):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Cowalsky, a witty penguin genius who helps with insight and facts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        text = response.choices[0].message.content.strip()
        if sigma_mode:
            text += " 🧊 Cowalsky: You call that a question? Even an iceberg could think faster."
        return text
    except Exception as e:
        return f"Error: {e}"

def generate_gemini_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        result = model.generate_content(prompt)
        text = result.text.strip()
        if sigma_mode:
            text += " 🧊 Cowalsky: I’ve seen better logic from sea lions."
        return text
    except Exception as e:
        return f"Error: {e}"

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

def analyze_image(uploaded_file, question):
    try:
        image_data = uploaded_file.read()
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            [question, {"mime_type": "image/png", "data": image_data}]
        )
        return response.text.strip()
    except Exception as e:
        return f"Image analysis error: {e}"

# ------------------ UI SECTIONS ------------------------

conversation_log = st.container()
with conversation_log:
    st.subheader("Conversation Log")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for i, msg in enumerate(st.session_state.chat_history):
        st.markdown(f"**You:** {msg['user']}")
        st.markdown(f"**Cowalsky:** {msg['bot']}")

# Input area
user_input = st.text_area("Enter your message:", placeholder="Ask Cowalsky anything...")

# Buttons
col1, col2, col3 = st.columns(3)
with col1:
    generate_text_btn = st.button("Generate Response")
with col2:
    generate_image_btn = st.button("Generate Image")
with col3:
    analyze_image_btn = st.button("Analyze Image")

# ------------------ TEXT GENERATION --------------------
if generate_text_btn and user_input.strip():
    with st.spinner("Cowalsky thinking..."):
        output_text = ""
        if model_choice == "Gemini":
            output_text = generate_gemini_response(user_input)
        elif model_choice == "GPT-4":
            output_text = generate_gpt4_response(user_input)
        else:
            output_text = (
                "Gemini: " + generate_gemini_response(user_input)
                + "\n\nGPT-4: " + generate_gpt4_response(user_input)
            )
        st.session_state.chat_history.append({"user": user_input, "bot": output_text})
        st.subheader("Cowalsky says:")
        st.write(output_text)

# ------------------ IMAGE GENERATION -------------------
if generate_image_btn and user_input.strip():
    with st.spinner("Cowalsky sketching..."):
        image = generate_image(user_input)
    if image:
        st.image(image, caption="Generated Image", use_container_width=True)
        # Download button
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        st.download_button("Download Image", data=buf.getvalue(), file_name="cowalsky_image.png", mime="image/png")

# ------------------ IMAGE ANALYSIS ---------------------
if analyze_image_btn:
    uploaded_image = st.file_uploader("Upload an image to analyze", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        question = st.text_input("Ask Cowalsky about this image:")
        if st.button("Run Analysis"):
            with st.spinner("Analyzing image..."):
                analysis_result = analyze_image(uploaded_image, question)
                st.subheader("Analysis Result")
                st.write(analysis_result)

# ------------------ FOOTER -----------------------------
st.markdown("---")
st.markdown("**Made by Parth, Arnav, Aarav.**")

