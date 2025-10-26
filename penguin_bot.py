import os
import socket
import qrcode
import base64
import urllib.request
import json
import io
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import streamlit as st

--- Load environment variables ---

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

--- Streamlit Page Setup ---

st.set_page_config(page_title="🐧 Cowalsky", page_icon="🐧", layout="centered")

--- Custom minimal dark style ---

st.markdown("""
<style>
body, [data-testid="stAppViewContainer"] {
background-color: #0b0b0b;
color: white;
}
.stButton>button {
background-color: #1a1a1a;
color: white;
border: 1px solid #333;
border-radius: 6px;
padding: 0.4em 1em;
}
.stTextInput>div>div>input, textarea, .stTextArea>div>div>textarea {
background-color: #111 !important;
color: white !important;
border: 1px solid #333 !important;
}
.stMarkdown, .stText, .stCaption {
color: white;
}
</style>
""", unsafe_allow_html=True)

--- Utility functions ---

def get_time():
return datetime.now().strftime("%I:%M:%S %p")

def get_date():
return datetime.now().strftime("%B %d, %Y")

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
with urllib.request.urlopen("https://api.ipify.org?format=json
", timeout=5) as resp:
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

def chat_with_cowalsky(user_input, image_bytes=None):
messages = [
{"role": "system", "content": "You are Cowalsky, a witty, intelligent penguin assistant who answers clearly and kindly."},
{"role": "user", "content": user_input}
]

if image_bytes:
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": user_input},
            {"type": "image_url", "image_url": f"data:image/png;base64,{image_base64}"}
        ]
    })

try:
    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message.content
except Exception as e:
    return f"⚠️ Error: {e}"

--- Header ---

st.title("🐧 Cowalsky the Penguin")
st.caption("Simple. Smart. Minimal.")

--- Sidebar ---

with st.sidebar:
st.header("Quick Tools")

col1, col2 = st.columns(2)
with col1:
    if st.button("🕒 Time"):
        st.success(get_time())
with col2:
    if st.button("📅 Date"):
        st.success(get_date())

if st.button("🏠 Local IP"):
    st.info(get_local_ip())
if st.button("🌐 Public IP"):
    st.info(get_public_ip())

st.divider()
st.subheader("QR Code Generator")
qr_data = st.text_input("Enter text or URL:")
if st.button("Generate QR"):
    if qr_data.strip():
        qr_img = make_qr(qr_data)
        st.image(qr_img, caption="Generated QR Code", use_column_width=True)
        st.download_button("Download QR", qr_img, file_name="cowalsky_qr.png")
    else:
        st.warning("Please enter text or URL first.")

--- Chat Section ---

st.divider()
st.subheader("💬 Chat with Cowalsky")

uploaded_image = st.file_uploader("Optional: Upload an image (PNG/JPG)", type=["png", "jpg", "jpeg"])
user_message = st.text_area("You:", placeholder="Ask Cowalsky something...")

if st.button("Send"):
if not user_message.strip():
st.warning("Please type a message.")
else:
with st.spinner("🐧 Thinking..."):
img_bytes = uploaded_image.read() if uploaded_image else None
reply = chat_with_cowalsky(user_message, img_bytes)
st.markdown(f"🐧 Cowalsky: {reply}")

st.markdown("---")
st.caption("🐧 Powered by OpenAI · Built by Parth & Cowalsky")
