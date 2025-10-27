import os
import io
import base64
import qrcode
import urllib.request
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from PIL import Image

# --- Load environment variables ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Streamlit Page Setup ---
st.set_page_config(
    page_title="🐧 Cowalsky - Penguin Assistant",
    page_icon="🐧",
    layout="centered"
)

# --- Minimal dark theme styling ---
st.markdown("""
    <style>
    body { background-color: #0f1116; color: #ffffff; }
    .stTextInput > div > div > input, textarea {
        background-color: #1b1e24; color: white; border-radius: 8px; border: 1px solid #333;
    }
    .stButton > button {
        background-color: #20242c; color: white; border-radius: 8px; border: 1px solid #444;
    }
    </style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def get_time():
    return datetime.now().strftime("%I:%M:%S %p")

def get_date():
    return datetime.now().strftime("%B %d, %Y")

def get_local_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unavailable"

def get_public_ip():
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json", timeout=5) as resp:
            data = json.load(resp)
            return data.get("ip", "Unknown")
    except:
        return "Unavailable"

def make_qr(data):
    qr = qrcode.QRCode(version=1, box_size=8, border=3)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="white", back_color="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def chat_with_cowalsky(user_input):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Cowalsky, a witty penguin assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error: {e}"

def analyze_image_with_prompt(uploaded_image, user_prompt):
    try:
        bytes_data = uploaded_image.read()
        encoded_image = base64.b64encode(bytes_data).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI that analyzes uploaded images."},
                {"role": "user", "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
                ]}
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error analyzing image: {e}"

def generate_image(prompt):
    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="512x512"
        )
        image_base64 = response.data[0].b64_json
        return base64.b64decode(image_base64)
    except:
        return None

# --- Title ---
st.title("🐧 Cowalsky - Your Minimal Penguin Assistant")

# --- Auto Generate Nano Banana Image ---
st.subheader("🍌 Auto Generated Nano Banana Image")
with st.spinner("Generating Nano Banana..."):
    img_data = generate_image("A futuristic nano banana glowing under neon lights in a lab, digital art style.")
    if img_data:
        st.image(img_data, caption="Nano Banana by Cowalsky", use_column_width=True)
    else:
        st.error("⚠️ Failed to generate Nano Banana image.")

# --- Chat Section ---
st.divider()
st.subheader("💬 Chat with Cowalsky")

user_input = st.text_input("You:", placeholder="Ask Cowalsky something...")
if st.button("Send"):
    if user_input.strip():
        with st.spinner("🐧 Thinking..."):
            reply = chat_with_cowalsky(user_input)
            st.markdown(f"**🐧 Cowalsky:** {reply}")
    else:
        st.warning("Please enter a message!")

# --- Image Analyzer Section ---
st.divider()
st.subheader("🖼️ Image Analyzer")

uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
image_prompt = st.text_input("What do you want me to analyze in the image?")

if st.button("Analyze Image"):
    if uploaded_image and image_prompt.strip():
        with st.spinner("Analyzing image..."):
            result = analyze_image_with_prompt(uploaded_image, image_prompt)
            st.success(result)
    else:
        st.warning("Please upload an image and enter your prompt first.")

# --- Tools Section ---
st.divider()
st.subheader("🧰 Quick Tools")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🕒 Time"):
        st.info(get_time())
with col2:
    if st.button("📅 Date"):
        st.info(get_date())
with col3:
    if st.button("🏠 Local IP"):
        st.info(get_local_ip())
with col4:
    if st.button("🌐 Public IP"):
        st.info(get_public_ip())

st.subheader("📱 Generate QR Code")
qr_text = st.text_input("Enter text or link:")
if st.button("Generate QR"):
    if qr_text.strip():
        qr_img = make_qr(qr_text)
        st.image(qr_img, caption="Your QR Code", use_column_width=True)
        st.download_button("Download QR", qr_img, file_name="cowalsky_qr.png")
    else:
        st.warning("Please enter text or a URL.")

# --- Footer ---
st.markdown("---")
st.caption("🐧 Made by Parth, Arnav, and Aarav · Powered by OpenAI")
