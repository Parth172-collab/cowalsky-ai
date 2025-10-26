import os
import socket
import qrcode
import base64
import io
import requests
from datetime import datetime
import pytz
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from PIL import Image

# --- Load environment and API ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Page Setup ---
st.set_page_config(page_title="🐧 Cowalsky", page_icon="🐧", layout="centered")

# --- Minimal CSS + Scrollable Chat ---
st.markdown("""
<style>
body, .stApp { background-color: #0e1117; color: white; }
.stTextInput > div > div > input { background-color: #1e1e1e; color: white; border: 1px solid #333; }
.stButton > button { background-color: #1e1e1e; color: white; border: 1px solid #333; width:100%; }
.stSidebar { background-color: #111; }
.chat-container { max-height: 400px; overflow-y: auto; border: 1px solid #333; padding: 10px; background-color: #1a1a1a; }
</style>
""", unsafe_allow_html=True)

# --- Utility Functions ---
LOCAL_TIMEZONE = pytz.timezone("Asia/Kolkata")  # Set your local timezone

def get_time():
    return datetime.now(LOCAL_TIMEZONE).strftime("%I:%M:%S %p")

def get_date():
    return datetime.now(LOCAL_TIMEZONE).strftime("%B %d, %Y")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Unavailable"

def get_public_ip():
    try:
        import urllib.request, json
        with urllib.request.urlopen("https://api.ipify.org?format=json", timeout=5) as resp:
            data = json.load(resp)
            return data.get("ip", "Unknown")
    except Exception:
        return "Unavailable"

def make_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="white", back_color="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def free_generate_image(prompt):
    try:
        # Pollinations free text-to-image API
        url = "https://api.pollinations.ai/prompt"
        response = requests.post(url, json={"prompt": prompt})
        if response.status_code == 200:
            img = Image.open(io.BytesIO(response.content))
            return img
        else:
            st.error("Image generation failed. API might be busy or down.")
            return None
    except Exception as e:
        st.error(f"Image generation failed: {e}")
        return None

def analyze_image(image_file, user_prompt):
    try:
        base64_img = base64.b64encode(image_file.read()).decode("utf-8")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Cowalsky, a clever penguin assistant who analyzes images."},
                {"role": "user", "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}}
                ]}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error analyzing image: {e}"

def chat_with_cowalsky(user_input):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Cowalsky, a witty penguin assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {e}"

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

# --- App Layout ---
st.title("🐧 Cowalsky the Penguin Assistant")
st.caption("Minimalistic Penguin AI Helper · Powered by OpenAI")
st.divider()

# --- Sidebar Tools ---
with st.sidebar:
    st.header("🧰 Tools")
    if st.button("🕒 Show Time"): st.success(f"The time is {get_time()}")
    if st.button("📅 Show Date"): st.success(f"Today is {get_date()}")
    if st.button("🏠 Local IP"): st.info(f"Local IP: {get_local_ip()}")
    if st.button("🌐 Public IP"): st.info(f"Public IP: {get_public_ip()}")

    st.divider()
    st.subheader("🧾 Generate QR Code")
    qr_data = st.text_input("Enter text or URL:")
    if st.button("Generate QR"):
        if qr_data.strip():
            qr_img = make_qr(qr_data)
            st.image(qr_img, caption="Generated QR Code", use_column_width=True)
            st.download_button("Download QR", qr_img, "cowalsky_qr.png")
        else:
            st.warning("Please enter some text.")

    st.divider()
    st.subheader("🎨 Generate Image (Free)")
    img_prompt = st.text_input("Enter image prompt:")
    if st.button("Generate Image"):
        if img_prompt.strip():
            img_data = free_generate_image(img_prompt)
            if img_data:
                st.image(img_data, caption="Generated by Cowalsky", use_column_width=True)
                buf = io.BytesIO()
                img_data.save(buf, format="PNG")
                st.download_button("Download Image", buf.getvalue(), "cowalsky_image.png")
            else:
                st.error("Failed to generate image.")
        else:
            st.warning("Please enter a prompt.")

# --- Chat Section ---
st.subheader("💬 Chat with Cowalsky")
chat_col1, chat_col2 = st.columns([4,1])
with chat_col1:
    chat_input_val = st.text_input("You:", value=st.session_state.chat_input, placeholder="Ask Cowalsky anything...")
with chat_col2:
    send_btn = st.button("Send")

if send_btn and chat_input_val.strip() != "":
    with st.spinner("🐧 Thinking..."):
        bot_reply = chat_with_cowalsky(chat_input_val)
    st.session_state.chat_history.append(("You", chat_input_val))
    st.session_state.chat_history.append(("🐧 Cowalsky", bot_reply))
    st.session_state.chat_input = ""  # clear input

# --- Display chat history (scrollable, newest on top) ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for sender, message in reversed(st.session_state.chat_history):
    st.markdown(f"**{sender}:** {message}")
st.markdown('</div>', unsafe_allow_html=True)

# --- Image Analysis Section ---
st.divider()
st.subheader("🖼️ Upload or Take Photo for Analysis")
uploaded_img = st.file_uploader("Upload an image (JPG, PNG)", type=["jpg","jpeg","png"])
camera_img = st.camera_input("Or take a picture with your camera")
image_prompt = st.text_input("Ask Cowalsky about this image:")

image_to_analyze = camera_img if camera_img else uploaded_img

if image_to_analyze and st.button("Analyze Image"):
    if image_prompt.strip() == "":
        st.warning("Please enter a question for Cowalsky about the image.")
    else:
        with st.spinner("Analyzing image..."):
            result = analyze_image(image_to_analyze, image_prompt)
            st.session_state.chat_history.append(("You (image)", image_prompt))
            st.session_state.chat_history.append(("🐧 Cowalsky", result))

st.divider()
st.caption("Made by Parth, Arnav, Aarav")
