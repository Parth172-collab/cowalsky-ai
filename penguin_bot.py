import os
import io
import base64
import tempfile
from dotenv import load_dotenv
from PIL import Image
import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS

# --- Load environment and Gemini API key ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- Page Setup ---
st.set_page_config(page_title="Cowalsky AI", layout="centered")

# --- Title and description ---
st.title("Cowalsky AI")
st.caption("Chat with PenguinBot — powered by Gemini API and Nano Banana image generator.")

# --- Function: Generate text response ---
def generate_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# --- Function: Generate Image ---
def generate_image(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([
            prompt,
            "Create a detailed image based on this description."
        ])
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.mime_type == "image/png":
                    image_data = base64.b64decode(part.data)
                    return Image.open(io.BytesIO(image_data))
        return None
    except Exception as e:
        st.error(f"Image generation error: {e}")
        return None

# --- Function: Analyze Uploaded Image ---
def analyze_image(uploaded_file, prompt):
    try:
        image = Image.open(uploaded_file)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt, image], stream=False)
        return response.text
    except Exception as e:
        return f"Image analysis error: {e}"

# --- Function: Convert Text to Speech ---
def text_to_speech(text):
    try:
        tts = gTTS(text)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        st.error(f"Voice generation error: {e}")
        return None

# --- Function: Convert Speech to Text ---
def speech_to_text(audio_file):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    except Exception as e:
        return f"Speech recognition error: {e}"

# --- Input area ---
st.write("Enter your message or record your voice below.")
user_input = st.text_area("Prompt:", placeholder="Type or record something...")

# --- Voice recording upload ---
uploaded_audio = st.file_uploader("Upload a voice recording (optional, WAV format recommended):", type=["wav", "mp3"])

# --- Image upload for analysis ---
uploaded_file = st.file_uploader("Upload an image for analysis (optional):", type=["png", "jpg", "jpeg"])

# --- Buttons ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    text_btn = st.button("Generate Text")
with col2:
    img_btn = st.button("Generate Image")
with col3:
    analyze_btn = st.button("Analyze Image")
with col4:
    voice_btn = st.button("Analyze Voice")

# --- Voice Input ---
if voice_btn and uploaded_audio:
    with st.spinner("Processing voice input..."):
        recognized_text = speech_to_text(uploaded_audio)
        st.write("Recognized Text:")
        st.write(recognized_text)
        output = generate_response(recognized_text)
        st.subheader("Cowalsky says:")
        st.write(output)
        voice_file = text_to_speech(output)
        if voice_file:
            st.audio(voice_file, format="audio/mp3")

# --- Text Generation Output ---
if text_btn and user_input.strip():
    with st.spinner("Generating response..."):
        output = generate_response(user_input)
    st.subheader("Cowalsky says:")
    st.write(output)
    voice_file = text_to_speech(output)
    if voice_file:
        st.audio(voice_file, format="audio/mp3")

# --- Image Generation Output ---
if img_btn and user_input.strip():
    with st.spinner("Generating image..."):
        image = generate_image(user_input)
    if image:
        st.image(image, caption="Nano Banana Creation", use_container_width=True)

# --- Image Analysis Output ---
if analyze_btn and uploaded_file and user_input.strip():
    with st.spinner("Analyzing image..."):
        analysis = analyze_image(uploaded_file, user_input)
    st.subheader("Analysis Result:")
    st.write(analysis)
    voice_file = text_to_speech(analysis)
    if voice_file:
        st.audio(voice_file, format="audio/mp3")

# --- Footer ---
st.markdown("---")
st.markdown("Made by Parth, Arnav, Aarav.")
