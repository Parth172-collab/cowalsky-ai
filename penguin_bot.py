import streamlit as st
import requests
import re
import easyocr
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="🐧 Penguin Bot", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar Tools ---
st.sidebar.title("🧰 Penguin Tools")

# ========== Image Analyzer ==========
st.sidebar.subheader("🖼️ Image Analyzer")
uploaded_image = st.sidebar.file_uploader("Upload an image (e.g., network screenshot)", type=["png", "jpg", "jpeg"])

if uploaded_image:
    image = Image.open(uploaded_image)
    st.sidebar.image(image, caption="Uploaded Image", use_container_width=True)

    with st.sidebar.spinner("Analyzing image..."):
        reader = easyocr.Reader(['en'])
        result = reader.readtext(np.array(image))
        text = " ".join([r[1] for r in result])

    st.sidebar.text_area("Extracted Text", text, height=120)

    # Find IP addresses
    ips = re.findall(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', text)
    if ips:
        st.sidebar.success(f"Detected IPs: {', '.join(ips)}")
    else:
        st.sidebar.warning("No IPs detected in image.")

# ========== Wi-Fi / Network Scan Analyzer ==========
st.sidebar.subheader("📶 Wi-Fi / Network Analyzer")
network_text = st.sidebar.text_area("Paste Wi-Fi or network scan output")

if network_text:
    ips = re.findall(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', network_text)
    if ips:
        st.sidebar.success(f"Detected IPs: {', '.join(ips)}")
    else:
        st.sidebar.warning("No IP addresses found.")

# ========== IP Geolocation ==========
st.sidebar.subheader("🌐 IP Geolocation")
ip_input = st.sidebar.text_input("Enter IP address (e.g., 8.8.8.8)")

if st.sidebar.button("Find Location"):
    if ip_input:
        try:
            response = requests.get(f"https://ipapi.co/{ip_input}/json/").json()
            if "latitude" in response and "longitude" in response:
                st.sidebar.success(f"""
📍 **Location Found:**
- City: {response.get('city', 'Unknown')}
- Region: {response.get('region', 'Unknown')}
- Country: {response.get('country_name', 'Unknown')}
- Latitude: {response.get('latitude')}
- Longitude: {response.get('longitude')}
                """)
            else:
                st.sidebar.error("Could not retrieve coordinates.")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
    else:
        st.sidebar.warning("Please enter an IP address.")

# --- Main Chat Area ---
st.title("🐧 Penguin Bot")

def render_chat():
    for msg in reversed(st.session_state.messages):
        st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")
        st.markdown("---")

render_chat()

# --- Input and Send ---
col1, col2 = st.columns([6, 1])
with col1:
    user_input = st.text_input("Type your message...", key="chat_input", placeholder="Ask me anything...")
with col2:
    send_clicked = st.button("Send")

# --- Handle Input ---
def handle_message():
    user_text = st.session_state.chat_input.strip()
    if user_text:
        st.session_state.messages.append({"role": "user", "content": user_text})
        # Simple bot reply (you can replace this with AI logic)
        reply = f"Penguin 🐧 says: '{user_text}' sounds interesting!"
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.chat_input = ""  # Clear input
        st.rerun()

# Trigger on Enter or Send
if user_input and not send_clicked:
    handle_message()
elif send_clicked:
    handle_message()
