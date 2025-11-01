import streamlit as st
import requests
import re
import easyocr
import numpy as np
from PIL import Image

st.set_page_config(page_title="🐧 Penguin Bot", layout="wide")

# -------------------- INIT --------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------- SIDEBAR TOOLS --------------------
st.sidebar.title("🧰 Penguin Tools")

# ======================================================
# 🖼️ IMAGE ANALYZER
# ======================================================
st.sidebar.subheader("🖼️ Image Analyzer")
uploaded_image = st.sidebar.file_uploader("Upload an image (e.g., screenshot)", type=["png", "jpg", "jpeg"])

if uploaded_image:
    image = Image.open(uploaded_image)
    st.sidebar.image(image, caption="Uploaded Image", use_container_width=True)

    with st.sidebar.spinner("Analyzing image..."):
        reader = easyocr.Reader(['en'])
        result = reader.readtext(np.array(image))
        text = " ".join([r[1] for r in result])

    st.sidebar.text_area("Extracted Text", text, height=120)

    ips = re.findall(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', text)
    if ips:
        st.sidebar.success(f"Detected IPs: {', '.join(ips)}")
    else:
        st.sidebar.warning("No IPs detected in image.")

# ======================================================
# 📶 WI-FI / NETWORK ANALYZER
# ======================================================
st.sidebar.subheader("📶 Wi-Fi / Network Analyzer")
network_text = st.sidebar.text_area("Paste Wi-Fi or network scan output")

if network_text:
    ips = re.findall(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', network_text)
    if ips:
        st.sidebar.success(f"Detected IPs: {', '.join(ips)}")
    else:
        st.sidebar.warning("No IP addresses found.")

# ======================================================
# 🌐 IP GEOLOCATOR TOOL
# ======================================================
st.sidebar.subheader("🌐 IP Locator Tool")

ip_input = st.sidebar.text_input("Enter IP address manually")
geo_image = st.sidebar.file_uploader("Or upload image with IPs", type=["png", "jpg", "jpeg"])

ip_candidates = []

if geo_image:
    img = Image.open(geo_image)
    reader = easyocr.Reader(['en'])
    result = reader.readtext(np.array(img))
    detected_text = " ".join([r[1] for r in result])
    ip_candidates = re.findall(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', detected_text)
    if ip_candidates:
        st.sidebar.info(f"IPs found in image: {', '.join(ip_candidates)}")

if st.sidebar.button("Find Location"):
    ip_to_search = ip_input.strip() or (ip_candidates[0] if ip_candidates else None)
    if ip_to_search:
        try:
            res = requests.get(f"https://ipapi.co/{ip_to_search}/json/").json()
            if "latitude" in res and "longitude" in res:
                st.sidebar.success(f"""
📍 **Location Found**
- IP: {ip_to_search}
- City: {res.get('city', 'Unknown')}
- Region: {res.get('region', 'Unknown')}
- Country: {res.get('country_name', 'Unknown')}
- Latitude: {res.get('latitude')}
- Longitude: {res.get('longitude')}
                """)
            else:
                st.sidebar.error("Could not retrieve coordinates.")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
    else:
        st.sidebar.warning("Enter or upload an IP first.")

# ======================================================
# 💬 MAIN CHAT INTERFACE
# ======================================================
st.title("🐧 Penguin Bot")
st.write("Chat with Penguin — your tactical AI assistant.")

def render_chat():
    for msg in st.session_state.messages[::-1]:  # newest first
        st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")
        st.markdown("<br>", unsafe_allow_html=True)

render_chat()

col1, col2 = st.columns([6, 1])
with col1:
    user_input = st.text_input("Type your message...", key="chat_input", placeholder="Ask me anything...")
with col2:
    send_clicked = st.button("Send")

def handle_message():
    user_text = st.session_state.chat_input.strip()
    if user_text:
        st.session_state.messages.append({"role": "user", "content": user_text})
        reply = f"Penguin 🐧 says: '{user_text}' sounds interesting!"
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

if send_clicked:
    handle_message()
