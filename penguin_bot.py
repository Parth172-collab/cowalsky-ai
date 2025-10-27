import streamlit as st
from datetime import datetime
from PIL import Image
import requests
from io import BytesIO

# --- Page Setup ---
st.set_page_config(page_title="🐧 Cowalsky", page_icon="🐧", layout="centered")

# --- Title ---
st.title("🐧 Cowalsky - Your Smart Penguin Friend")
st.caption("Chat, analyze images, and generate fun placeholder art!")

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

# --- Placeholder Image Generator (Free & No API Key Needed) ---
def generate_placeholder_image(prompt):
    try:
        # Use a random placeholder image based on current timestamp
        response = requests.get(f"https://picsum.photos/seed/{datetime.now().timestamp()}/512")
        return Image.open(BytesIO(response.content))
    except Exception:
        return None

# --- Image Analyzer ---
def analyze_image(uploaded_file):
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        st.info("🧠 Analyzing image... (pretend AI magic here)")
        return "This image looks very interesting, possibly something amazing!"
    return None

# --- Chat Section ---
st.subheader("💬 Chat with Cowalsky")

# Show chat messages (newest on top)
for chat in reversed(st.session_state.messages):
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# Input + Send button
st.divider()
user_message = st.text_input("Type your message...", key="user_input")
send_btn = st.button("Send 🐧")

if send_btn and user_message.strip():
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_message})

    # Simple bot response
    reply = f"🐧 Cowalsky: Hmm, '{user_message}' sounds cool!"
    st.session_state.messages.append({"role": "assistant", "content": reply})

    # Clear only the input field
    st.session_state.user_input = ""

    # Trigger safe refresh
    st.experimental_set_query_params(refresh=str(datetime.now().timestamp()))
    st.rerun()

# --- Image Analyzer Section ---
st.divider()
st.subheader("🖼️ Image Analyzer")
uploaded_file = st.file_uploader("Upload an image to analyze", type=["jpg", "jpeg", "png"])
if uploaded_file:
    result = analyze_image(uploaded_file)
    if result:
        st.success(result)

# --- Fun Placeholder Image Generator ---
st.divider()
st.subheader("🎨 Fun Image Generator")
prompt = st.text_input("Enter any fun idea (e.g., 'penguin on a skateboard'):")
if st.button("Generate Image"):
    with st.spinner("Generating image..."):
        img = generate_placeholder_image(prompt)
        if img:
            st.image(img, caption="Generated Placeholder 🐧", use_column_width=True)
        else:
            st.error("Could not generate image. Try again!")

# --- Footer ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;'>Made by <b>Parth</b>, <b>Arnav</b>, and <b>Aarav</b> 🐧</p>",
    unsafe_allow_html=True
)
