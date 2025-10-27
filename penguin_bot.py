import os
import io
import base64
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import streamlit as st

# --- Load environment and API key ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Page Setup ---
st.set_page_config(page_title="🐧 Cowalsky AI", page_icon="🐧", layout="centered")

# --- Title and description ---
st.title("🐧 Cowalsky AI")
st.caption("Chat with PenguinBot — powered by GPT and Nano Banana 🍌 image generator.")

# --- Function: Generate text response ---
def generate_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Cowalsky, a friendly and smart penguin assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error: {e}"

# --- Function: Generate Image (Nano Banana AI) ---
def generate_image(prompt):
    try:
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="512x512"
        )
        image_base64 = result.data[0].b64_json
        image_data = base64.b64decode(image_base64)
        return Image.open(io.BytesIO(image_data))
    except Exception as e:
        st.error(f"Image generation error: {e}")
        return None

# --- Input area ---
user_input = st.text_area("💬 Enter your message or prompt:", placeholder="Type something...")

# --- Buttons ---
col1, col2 = st.columns(2)
with col1:
    text_btn = st.button("✨ Generate Text")
with col2:
    img_btn = st.button("🖼️ Generate Image")

# --- Text Generation Output ---
if text_btn and user_input.strip():
    with st.spinner("Thinking like a penguin... 🐧"):
        output = generate_response(user_input)
    st.subheader("🐧 Cowalsky says:")
    st.write(output)

# --- Image Generation Output ---
if img_btn and user_input.strip():
    with st.spinner("Drawing with Nano Banana 🍌..."):
        image = generate_image(user_input)
    if image:
        st.image(image, caption="🖼️ Nano Banana Creation", use_container_width=True)
