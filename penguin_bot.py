import os
import socket
import urllib.request
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import streamlit as st
import io
import requests

# --- Load environment and API ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Streamlit setup ---
st.set_page_config(page_title="🐧 Cowalsky", page_icon="🐧", layout="centered")

st.markdown("""
<style>
body { background-color: #0e1117; color: white; }
h1, h2, h3, h4, h5, h6 { color: white; }
.stTextInput>div>div>input { background-color: #1c1f26; color: white; }
.stButton>button { background-color: #222; color: white; border-radius: 10px; }
.stTextArea textarea { background-color: #1c1f26; color: white; }
</style>
""", unsafe_allow_html=True)

# --- Utilities ---
def get_time():
    return datetime.now().strftime("%I:%M %p")

def get_date():
    return datetime.now().strftime("%B %d, %Y")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unable to determine local IP"

def get_public_ip():
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json", timeout=5) as resp:
            data = json.load(resp)
            return data.get("ip", "Unknown")
    except:
        return "Unable to fetch public IP"

# --- Chat with Cowalsky ---
def chat_with_cowalsky(user_input):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Cowalsky, a cute, clever, minimalistic penguin assistant who responds helpfully and humorously."},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {e}"

# --- NanoBanana Text-to-Image ---
def generate_image_nanobanana(prompt):
    try:
        # Pollinations (NanoBanana) endpoint
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception as e:
        st.error(f"⚠️ Image generation failed: {e}")
        return None

# --- Image Analysis with GPT-4o ---
def analyze_image(uploaded_file, question):
    try:
        img_bytes = uploaded_file.getvalue()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Cowalsky, a penguin that can analyze images."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(img_bytes).decode()}}
                    ],
                }
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error analyzing image: {e}"

# --- Initialize chat memory ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Header ---
st.title("🐧 Cowalsky - Your Penguin Assistant")
st.caption("Minimal, Fast, and Cool ❄️")

# --- Chat Section ---
st.subheader("💬 Chat with Cowalsky")

user_input = st.text_input("Type your message:", key="chat_input")
send_btn = st.button("Send")

if send_btn and user_input.strip():
    bot_reply = chat_with_cowalsky(user_input)
    st.session_state.chat_history.insert(0, ("You", user_input))
    st.session_state.chat_history.insert(0, ("🐧 Cowalsky", bot_reply))
    st.session_state.chat_input = ""  # clear input

# Display chat (newest first)
for sender, msg in st.session_state.chat_history:
    st.markdown(f"**{sender}:** {msg}")

st.divider()

# --- Image Analyzer ---
st.subheader("🖼️ Image Analyzer")
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
question = st.text_input("Ask Cowalsky about the image (e.g., 'What do you see here?')")

if st.button("Analyze Image"):
    if uploaded_file and question:
        with st.spinner("Analyzing image... 🧊"):
            result = analyze_image(uploaded_file, question)
            st.success(result)
    else:
        st.warning("Please upload an image and enter a question first.")

st.divider()

# --- NanoBanana Image Generation ---
st.subheader("🎨 Generate Image with NanoBanana (Free)")
img_prompt = st.text_input("Enter a prompt to generate an image:")

if st.button("Generate Image"):
    with st.spinner("Generating your image... 🍌"):
        img_data = generate_image_nanobanana(img_prompt)
        if img_data:
            st.image(img_data, caption="Generated by NanoBanana 🍌", use_column_width=True)
            st.download_button("Download Image", img_data, file_name="nanobanana_image.png")
        else:
            st.error("Failed to generate image. Try again!")

# --- Footer ---
st.markdown("---")
st.caption("🐧 Made by Parth, Arnav, Aarav")
