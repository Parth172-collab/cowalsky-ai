# === PenguinBot 🐧 Streamlit App ===
# --- Imports ---
import os
import base64
import streamlit as st
from openai import OpenAI
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

# --- Initialize Clients ---
gemini_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Streamlit Page Config ---
st.set_page_config(page_title="🐧 PenguinBot", page_icon="🐧", layout="wide")

# --- Sidebar ---
st.sidebar.image("https://i.imgur.com/2yaf2wb.png", use_container_width=True)
st.sidebar.title("🐧 PenguinBot Settings")
theme = st.sidebar.radio("Choose Theme:", ["Light", "Dark"], index=0)
penguin_mode = st.sidebar.checkbox("🧊 Penguin Talk Mode", value=True)
st.sidebar.markdown("---")
st.sidebar.info("Made with ❤️ + 🧊 by PenguinBot")

# --- Chat Memory ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Penguin Response Style ---
def penguinify(text):
    if not text:
        return "Hmm... looks like my flippers slipped! 🐧"
    if not penguin_mode:
        return text
    endings = ["brrr!", "flap-flap!", "slide safe!", "cool as ice!", "stay frosty!"]
    return f"{text}\n\n– said the penguin, {endings[len(text) % len(endings)]}"

# --- Image Generator ---
def generate_image(prompt):
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt],
        )
        image_data = response.candidates[0].content.parts[0].inline_data.data
        img_bytes = base64.b64decode(image_data)
        return Image.open(BytesIO(img_bytes))
    except Exception as e:
        st.warning(f"🐧 Gemini hiccup: {e}\nSwitching to OpenAI fallback...")
        try:
            result = openai_client.images.generate(
                model="gpt-image-1-mini",
                prompt=prompt,
                size="512x512"
            )
            img_url = result.data[0].url
            return img_url
        except Exception as e2:
            st.error(f"❌ Both image generators failed: {e2}")
            return None

# --- Image Analyzer ---
def analyze_image(uploaded_image):
    try:
        image_bytes = uploaded_image.getvalue()
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=uploaded_image.type)
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[image_part, "Describe this image in detail like a penguin reviewer."]
        )
        return penguinify(response.text)
    except Exception as e:
        st.error(f"🐧 Oops, I slipped analyzing that image: {e}")
        return None

# --- Chatbot Response ---
def chat_with_penguin(prompt):
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return penguinify(response.text)
    except Exception as e:
        st.warning(f"Gemini took a dive: {e}\nSwitching to OpenAI fallback...")
        try:
            reply = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return penguinify(reply.choices[0].message.content)
        except Exception as e2:
            st.error(f"❌ Both models failed: {e2}")
            return "Eek! My ice broke, can’t think right now."

# --- UI Layout ---
st.title("🐧 PenguinBot")
st.caption("A chill AI assistant that slides between Gemini & GPT for you!")

user_input = st.text_area("💬 Ask PenguinBot something...", placeholder="Type your question here...")

col1, col2 = st.columns(2)
with col1:
    if st.button("Send 🐧"):
        if user_input.strip():
            st.session_state.history.append(("You", user_input))
            penguin_reply = chat_with_penguin(user_input)
            st.session_state.history.append(("PenguinBot", penguin_reply))
        else:
            st.warning("Please say something, even penguins need input!")

with col2:
    prompt_img = st.text_input("🎨 Generate image prompt:")
    if st.button("Generate Image 🧊"):
        if prompt_img.strip():
            image = generate_image(prompt_img)
            if image:
                if isinstance(image, str):
                    st.image(image, caption="Penguin Creation")
                else:
                    st.image(image, caption="Penguin Creation")
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    st.download_button(
                        "⬇️ Download Image",
                        data=buffered.getvalue(),
                        file_name="penguin_creation.png",
                        mime="image/png"
                    )

uploaded = st.file_uploader("📸 Upload an image for Penguin analysis")
if uploaded:
    st.image(uploaded, caption="Your Uploaded Image", use_container_width=True)
    analysis = analyze_image(uploaded)
    if analysis:
        st.info(analysis)

# --- Chat History Display ---
if st.session_state.history:
    st.markdown("### 🗨️ Chat History")
    for sender, msg in st.session_state.history:
        if sender == "You":
            st.markdown(f"**🧍 You:** {msg}")
        else:
            st.markdown(f"**🐧 PenguinBot:** {msg}")

st.markdown("---")
st.caption("🐧 Powered by Gemini & GPT — where AI meets ice-cool charm.")
