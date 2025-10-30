# === Cowalsky (Gen-2) Streamlit App ===
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
st.set_page_config(page_title="Cowalsky (Gen-2)", page_icon="🐧", layout="wide")

# --- Sidebar ---
st.sidebar.image(
    "https://static.wikia.nocookie.net/madagascar/images/0/02/Kowalski.png/revision/latest?cb=20220318225149",
    caption="Kowalski — The Brains Behind the Ice 🧊",
    use_container_width=True
)
st.sidebar.title("Kowalski Control Panel")

theme = st.sidebar.radio("Theme:", ["Light", "Dark"], index=0)
penguin_mode = st.sidebar.checkbox("🐧 Penguin Talk Mode", value=True)
sigma_mode = st.sidebar.checkbox("😈 Sigma Mode (Roast Enabled)", value=False)
st.sidebar.markdown("---")
st.sidebar.info("Made by Parth, Arnav, Aarav.")

# --- Chat Memory ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Penguinify Response ---
def penguinify(text):
    if not text:
        return "Hmm... looks like my flippers slipped!"
    if not penguin_mode:
        return text
    endings = ["brrr!", "flap-flap!", "slide safe!", "cool as ice!", "stay frosty!"]
    return f"{text}\n\n– said the penguin, {endings[len(text) % len(endings)]}"

# --- Sigma Roast Mode ---
def sigma_roast(prompt, reply):
    roast_lines = [
        "Bro, even my fish have better questions.",
        "That take was so cold even Antarctica blushed.",
        "You’re trying… I’ll give you that. Barely.",
        "I ran your question through my logic circuits — still nonsense.",
        "Kowalski, analysis: user might be running low on IQ points.",
        "You’re like a penguin trying to fly — admirable, yet hopeless."
    ]
    roast = roast_lines[len(prompt) % len(roast_lines)]
    return f"{reply}\n\n😈 Sigma Mode: {roast}"

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
        st.warning(f"Gemini image hiccup: {e}\nSwitching to OpenAI fallback...")
        try:
            result = openai_client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1024"
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
        image_part = types.Part.from_bytes(data=image_bytes)  # ✅ Removed mime_type
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[image_part, "Describe this image like a penguin detective."]
        )
        return penguinify(response.text)
    except Exception as e:
        st.error(f"🐧 Oops, slipped analyzing that image: {e}")
        return None

# --- Chatbot Response ---
def chat_with_penguin(prompt):
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        reply = penguinify(response.text)
    except Exception as e:
        st.warning(f"Gemini took a dive: {e}\nSwitching to OpenAI fallback...")
        try:
            reply = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            ).choices[0].message.content
            reply = penguinify(reply)
        except Exception as e2:
            st.error(f"❌ Both models failed: {e2}")
            return "Eek! My ice broke, can’t think right now."
    
    if sigma_mode:
        reply = sigma_roast(prompt, reply)
    return reply

# --- UI Layout ---
st.title("Cowalsky (Gen-2)")
st.caption("AI Intelligence with Ice-Cold Precision ❄️")

user_input = st.text_area("💬 Ask Cowalsky:", placeholder="Ask something smart... or don’t 😏")

col1, col2 = st.columns(2)
with col1:
    if st.button("Send"):
        if user_input.strip():
            st.session_state.history.append(("You", user_input))
            penguin_reply = chat_with_penguin(user_input)
            st.session_state.history.append(("Cowalsky", penguin_reply))
        else:
            st.warning("Say something, even penguins need words!")

with col2:
    prompt_img = st.text_input("🎨 Generate image prompt:")
    if st.button("Generate Image"):
        if prompt_img.strip():
            image = generate_image(prompt_img)
            if image:
                if isinstance(image, str):
                    st.image(image, caption="Generated by Cowalsky")
                else:
                    st.image(image, caption="Generated by Cowalsky")
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    st.download_button(
                        "⬇️ Download Image",
                        data=buffered.getvalue(),
                        file_name="cowalsky_creation.png",
                        mime="image/png"
                    )

uploaded = st.file_uploader("📸 Upload an image for analysis")
if uploaded:
    st.image(uploaded, caption="Your Uploaded Image", use_container_width=True)
    analysis = analyze_image(uploaded)
    if analysis:
        st.info(analysis)

# --- Chat History ---
if st.session_state.history:
    st.markdown("### 🗨️ Conversation Log")
    for sender, msg in st.session_state.history:
        if sender == "You":
            st.markdown(f"**🧍 You:** {msg}")
        else:
            st.markdown(f"**🐧 {sender}:** {msg}")

st.markdown("---")
st.caption("🐧 Powered by Gemini + GPT | Made by Parth, Arnav, Aarav.")
