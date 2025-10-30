import os
import io
import base64
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import streamlit as st

--- Load environment and API key ---

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

--- Page Setup ---

st.set_page_config(page_title="Cowalsky AI", page_icon="❄️", layout="centered")
st.title("Cowalsky AI")
st.caption("Chat, analyze images, and create visuals — powered by Google Gemini Free Models")

--- Function: Generate text or image analysis ---

def generate_text_or_analysis(prompt, image=None):
try:
model = genai.GenerativeModel("gemini-2.5-flash")
if image:
response = model.generate_content([prompt, image])
else:
response = model.generate_content(prompt)
return response.text
except Exception as e:
return f"Error: {e}"

--- Function: Generate image ---

def generate_image(prompt):
try:
model = genai.GenerativeModel("gemini-2.5-flash-image")
result = model.generate_content(prompt)
# Extract the image bytes (Gemini returns a blob)
image_data = result.candidates[0].content.parts[0].blob
image = Image.open(io.BytesIO(image_data))
return image
except Exception as e:
st.error(f"Image generation error: {e}")
return None

--- Helper: Convert image to downloadable format ---

def get_image_download_link(img, filename="cowalsky_image.png"):
buf = io.BytesIO()
img.save(buf, format="PNG")
byte_im = buf.getvalue()
b64 = base64.b64encode(byte_im).decode()
href = f'<a href="data:image/png;base64,{b64}" download="{filename}">Download Image</a>'
return href

--- User input ---

user_input = st.text_area("Enter your message or prompt:", placeholder="Type something...")

uploaded_file = st.file_uploader("Upload an image (optional for analysis):", type=["jpg", "jpeg", "png"])

--- Buttons ---

col1, col2 = st.columns(2)
with col1:
text_btn = st.button("Generate Text / Analyze")
with col2:
img_btn = st.button("Generate Image")

--- Text or Analysis Output ---

if text_btn and user_input.strip():
with st.spinner("Processing..."):
image = None
if uploaded_file is not None:
image = Image.open(uploaded_file)
output = generate_text_or_analysis(user_input, image)
st.subheader("Result:")
st.write(output)

--- Image Generation Output ---

if img_btn and user_input.strip():
with st.spinner("Creating image..."):
image = generate_image(user_input)
if image:
st.image(image, caption="Generated Image", use_container_width=True)
st.markdown(get_image_download_link(image), unsafe_allow_html=True)

--- Credits ---

st.markdown("---")
st.markdown("Made by Parth, Arnav, Aarav.")
