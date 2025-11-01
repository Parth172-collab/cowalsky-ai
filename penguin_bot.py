# ============================================================
# Cowalsky (Gen-2) — Streamlit AI Assistant (Updated)
# - Chat (Gemini + GPT-4)
# - Image generation & analysis
# - IP Geolocation lookup (manual IP)
# - NEW: IP extraction from images & Wi-Fi logs (user-supplied)
# - NEW: EXIF GPS extraction from images -> lat/lon + small map
# ============================================================

import os
import io
import base64
import requests
import streamlit as st
from PIL import Image, ExifTags
from openai import OpenAI
import google.generativeai as genai
import random
import re
import pandas as pd

# Optional OCR (pytesseract)
try:
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

# ------------------------- CONFIG ----------------------------
st.set_page_config(page_title="Cowalsky (Gen-2)", page_icon="🐧", layout="centered")

# --- Retrieve API keys (optional) ---
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")

# --- Initialize clients (if keys provided) ---
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------------- SIDEBAR ----------------------------
with st.sidebar:
    st.title("Cowalsky (Gen-2) Settings")

    kowalski_url = "https://raw.githubusercontent.com/ParthK3107/public-assets/main/kowalski_penguin.png"
    try:
        response = requests.get(kowalski_url, timeout=10)
        if response.status_code == 200:
            kowalski_img = Image.open(io.BytesIO(response.content))
            st.image(kowalski_img, use_container_width=True)
        else:
            st.warning("🐧 Kowalsky is hiding in the shadows...")
    except Exception:
        st.warning("🐧 Kowalsky couldn’t load — probably on a stealth mission.")

    st.markdown("---")
    ai_choice = st.radio("Choose AI Model:", ["Gemini 2.5", "GPT-4", "Both"])
    sigma_mode = st.checkbox("Sigma Mode (Savage Replies)")
    dark_theme = st.checkbox("Dark Theme", value=True)
    st.markdown("---")
    st.caption("Made by Parth, Arnav, Aarav.")

# --------------------- THEME HANDLING -------------------------
if dark_theme:
    st.markdown(
        """
        <style>
        body, .stApp { background-color: #0d1117; color: white; }
        textarea, .stTextInput>div>div>input {
            background-color: #161b22 !important;
            color: white !important;
        }
        .chat-bubble { margin-bottom: 20px; }
        </style>
        """,
        unsafe_allow_html=True
    )

# ------------------------- HELPERS ---------------------------
IPV4_RE = re.compile(
    r'\b(?:25[0-5]|2[0-4]\d|1?\d{1,2})(?:\.(?:25[0-5]|2[0-4]\d|1?\d{1,2})){3}\b'
)
IPV6_RE = re.compile(
    r'('
    r'(?:(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4})|'
    r'(?:(?:[0-9a-fA-F]{1,4}:){1,7}:)|'
    r'(?:(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4})|'
    r'(?:(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2})|'
    r'(?:(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3})|'
    r'(?:(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4})|'
    r'(?:(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5})|'
    r'(?:(?:[0-9a-fA-F]{1,4}:){1}(?::[0-9a-fA-F]{1,4}){1,6})|'
    r'(?::(?::[0-9a-fA-F]{1,4}){1,7})'
    r')'
)

def extract_ips_from_text(text: str):
    """Return deduplicated list of ipv4 and ipv6 addresses found in text."""
    if not text:
        return []
    ipv4s = IPV4_RE.findall(text)
    ipv6s = IPV6_RE.findall(text)
    ipv6s = [m for m in ipv6s if m]
    seen = set()
    results = []
    for ip in ipv4s + ipv6s:
        if ip not in seen:
            seen.add(ip)
            results.append(ip)
    return results

def ocr_text_from_image_bytes(image_bytes: bytes):
    """Run OCR on an image bytes object and return extracted text (if pytesseract available)."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        return "", f"Unable to open image: {e}"
    if OCR_AVAILABLE:
        try:
            text = pytesseract.image_to_string(img)
            return text, None
        except Exception as e:
            return "", f"OCR error: {e}"
    else:
        return "", "OCR not available (install pytesseract and tesseract binary)"

def get_exif_gps_from_image_bytes(image_bytes: bytes):
    """Extract GPS lat/lon from image EXIF data. Returns (lat, lon) or (None, None)."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        exif = img._getexif()
        if not exif:
            return None, None, None  # no exif
        # Build tag -> value map with human-readable keys
        exif_data = {}
        for k, v in exif.items():
            tag = ExifTags.TAGS.get(k, k)
            exif_data[tag] = v
        gps_info = exif_data.get("GPSInfo")
        if not gps_info:
            return None, None, None
        # convert rational tuples to float
        def _convert_ratio(r):
            # r might be (num, den) or a float
            try:
                if isinstance(r, tuple) and len(r) == 2:
                    num, den = r
                    if den == 0:
                        return 0
                    return float(num) / float(den)
                return float(r)
            except Exception:
                return 0.0
        # Extract lat/lon parts
        lat_tuple = gps_info.get(2)  # degrees, minutes, seconds
        lat_ref = gps_info.get(1)    # 'N' or 'S'
        lon_tuple = gps_info.get(4)
        lon_ref = gps_info.get(3)
        if not lat_tuple or not lon_tuple:
            return None, None, None
        lat_d = _convert_ratio(lat_tuple[0])
        lat_m = _convert_ratio(lat_tuple[1])
        lat_s = _convert_ratio(lat_tuple[2])
        lon_d = _convert_ratio(lon_tuple[0])
        lon_m = _convert_ratio(lon_tuple[1])
        lon_s = _convert_ratio(lon_tuple[2])
        lat = lat_d + (lat_m / 60.0) + (lat_s / 3600.0)
        lon = lon_d + (lon_m / 60.0) + (lon_s / 3600.0)
        if lat_ref and lat_ref.upper() == "S":
            lat = -lat
        if lon_ref and lon_ref.upper() == "W":
            lon = -lon
        # return also a human-readable excerpt of EXIF GPS data
        gps_summary = {
            "LatRef": lat_ref,
            "LonRef": lon_ref,
            "RawLat": lat_tuple,
            "RawLon": lon_tuple
        }
        return lat, lon, gps_summary
    except Exception as e:
        return None, None, f"EXIF parse error: {e}"

# ------------------------- FUNCTIONS --------------------------
def cowalsky_roast():
    roasts = [
        "You call that logic? Even my flippers do better.",
        "That thought was colder than Antarctica.",
        "Bold move, soldier — but logic’s on vacation.",
        "I’ve seen smarter fish than that idea.",
    ]
    return random.choice(roasts)

def gemini_reply(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Gemini Error: {e}]"

def gpt4_reply(prompt):
    try:
        res = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Cowalsky, a witty penguin strategist with sharp logic."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"[GPT-4 Error: {e}]"

def generate_image(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-exp")
        result = model.generate_content([{"role": "user", "parts": [f"Generate an image of: {prompt}"]}])
        if result and result.candidates:
            img_data = base64.b64decode(result.candidates[0].content.parts[0].inline_data.data)
            return Image.open(io.BytesIO(img_data))
        return None
    except Exception as e:
        st.error(f"Image generation error: {e}")
        return None

def analyze_image(uploaded_image, user_question):
    """Keep previous analyze_image behavior (GenAI image question)."""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        image_bytes = uploaded_image.read()
        encoded_data = base64.b64encode(image_bytes).decode("utf-8")
        response = model.generate_content([
            {"role": "user", "parts": [
                {"text": f"Answer this question about the image: {user_question}"},
                {"inline_data": {"data": encoded_data}}
            ]}
        ])
        return response.text.strip()
    except Exception as e:
        return f"[Image analysis error: {e}]"

# --------------------- CHAT INTERFACE -------------------------
st.title("Cowalsky (Gen-2)")
st.markdown("Chat with a tactical penguin powered by Gemini 2.5 and GPT-4.")

if "chat" not in st.session_state:
    st.session_state.chat = []

# Enter key submits + button (keeps behavior consistent)
user_input = st.text_input("Enter your message:", key="chat_input",
                           on_change=lambda: st.session_state.update(send_clicked=True))
send_button = st.button("Send", use_container_width=True)
send_triggered = send_button or st.session_state.get("send_clicked", False)

if send_triggered and user_input.strip():
    st.session_state.chat.append(("You", user_input))
    reply = ""
    if ai_choice == "Gemini 2.5":
        reply = gemini_reply(user_input)
    elif ai_choice == "GPT-4":
        reply = gpt4_reply(user_input)
    else:
        reply = f"Gemini: {gemini_reply(user_input)}\n\nGPT-4: {gpt4_reply(user_input)}"

    if sigma_mode:
        reply += "\n\n💀 " + cowalsky_roast()

    st.session_state.chat.append(("Cowalsky", reply))
    st.session_state.chat_input = ""
    st.session_state.send_clicked = False

# Display Chat (Newest First + blank spacing)
if st.session_state.chat:
    st.markdown("### Conversation Log")
    for sender, msg in reversed(st.session_state.chat):
        st.markdown(f"**{'🐧' if sender == 'Cowalsky' else '🧑'} {sender}:** {msg}")
        st.markdown("<br>", unsafe_allow_html=True)

# --------------------- IMAGE GENERATION -----------------------
st.markdown("---")
st.subheader("🖼️ Image Generation")
img_prompt = st.text_input("Enter an image prompt:", key="img_prompt")
if st.button("Generate Image"):
    with st.spinner("Drawing like a tactical penguin..."):
        image = generate_image(img_prompt)
    if image:
        st.image(image, caption="Generated by Cowalsky", use_container_width=True)
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        st.download_button("Download Image", buf.getvalue(), "cowalsky_image.png", "image/png")

# --------------------- IMAGE ANALYZER -------------------------
st.markdown("---")
st.subheader("🔍 Image Analyzer (Question about uploaded image)")
uploaded_image = st.file_uploader("Upload an image for analysis", type=["png", "jpg", "jpeg"], key="analyzer_image")

if uploaded_image:
    st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
    user_question = st.text_input("Ask something about this image:", key="analyzer_question")
    if st.button("Analyze Image"):
        with st.spinner("Analyzing image like a penguin detective..."):
            answer = analyze_image(uploaded_image, user_question or "Describe this image in detail.")
        st.markdown(f"**🐧 Cowalsky’s Analysis:** {answer}")

# --------------------- IP & GPS EXTRACTOR -------------------------
st.markdown("---")
st.subheader("🔎 IP & GPS Extractor (from images & Wi-Fi / network logs)")

st.markdown(
    """
    Upload an image (screenshot/photo) or paste/upload Wi-Fi or network scan output (text).
    The tool will:
      - Try to extract **IP addresses** from image OCR/text and from logs.
      - Try to read **EXIF GPS** coordinates (latitude / longitude) from the image if present.
    **Important:** This app does not perform active Wi-Fi scanning. Provide scan output yourself.
    """
)

col1, col2 = st.columns(2)

with col1:
    extractor_image = st.file_uploader("Upload image to extract IPs & GPS (EXIF)", type=["png","jpg","jpeg","tiff"], key="extractor_img")
    if extractor_image:
        raw = extractor_image.read()
        st.info("Processing image for EXIF and OCR...")
        # EXIF GPS
        lat, lon, gps_summary = get_exif_gps_from_image_bytes(raw)
        if lat and lon:
            st.success("✅ EXIF GPS coordinates found")
            st.markdown(f"**Latitude:** {lat}\n\n**Longitude:** {lon}")
            # show small map pin using st.map (expects dataframe with lat & lon)
            try:
                df = pd.DataFrame([{"lat": lat, "lon": lon}])
                st.map(df)
            except Exception:
                # fallback: show coordinates only
                pass
            st.write("EXIF GPS summary:")
            st.text(str(gps_summary))
        else:
            if gps_summary:
                # gps_summary contains error message
                st.warning(f"EXIF parse note: {gps_summary}")
            else:
                st.info("No EXIF GPS data found in this image.")

        # OCR -> extract IPs
        ocr_text, ocr_error = ocr_text_from_image_bytes(raw)
        if ocr_error:
            st.warning(ocr_error)
        if ocr_text:
            st.markdown("**OCR text (excerpt):**")
            st.text(ocr_text[:2000])
        # Also check filename for ip-like patterns
        filename_ips = extract_ips_from_text(extractor_image.name or "")
        found_ips = extract_ips_from_text(ocr_text) + filename_ips
        found_ips = list(dict.fromkeys(found_ips))  # deduplicate preserving order
        if found_ips:
            st.success(f"Found {len(found_ips)} IP(s) in image (OCR/filename):")
            for ip in found_ips:
                st.code(ip)
        else:
            st.info("No IP addresses found in the image via OCR or filename.")

with col2:
    st.markdown("### Wi-Fi / Network log analysis")
    st.markdown(
        "Paste Wi-Fi / network scan output (e.g., `iwlist scan`, `nmcli device wifi list`, "
        "`netsh wlan show networks mode=bssid`, router logs), or upload a text/log file."
    )
    pasted_scan = st.text_area("Paste scan / log output here", key="scan_text")
    uploaded_log = st.file_uploader("Or upload log file", type=["txt","log","json"], key="scan_file")
    if st.button("Extract IPs from logs"):
        text = (pasted_scan or "").strip()
        if uploaded_log and not text:
            try:
                text = uploaded_log.read().decode(errors="ignore")
            except Exception as e:
                st.error(f"Could not read uploaded log file: {e}")
                text = ""
        if not text:
            st.warning("No text/log provided. Paste the scan output or upload a file.")
        else:
            ips = extract_ips_from_text(text)
            if ips:
                st.success(f"Found {len(ips)} IP(s) in provided text/log:")
                for ip in ips:
                    st.code(ip)
            else:
                st.info("No IP addresses found in the provided text/log.")

st.markdown("---")
st.markdown(
    "**Notes & limitations**\n\n"
    "- This extractor looks for textual IP patterns (IPv4/IPv6) inside images via OCR and inside text logs you provide. "
    "It **does not** actively scan nearby Wi-Fi networks — you must paste or upload the scan output.  \n"
    "- EXIF GPS coordinates are only available if the original camera/device saved them in the image. Many social apps and websites strip EXIF.  \n"
    "- For OCR you need `pytesseract` + the Tesseract binary installed on the host. If OCR is not installed, the tool will still check EXIF and filenames.  \n"
    "- Use responsibly — do not upload private or sensitive logs/images you are not allowed to share."
)

# --------------------- LOCATION FINDER (IP lookup) -------------------------
st.markdown("---")
st.subheader("🌍 Location Finder (IP Lookup)")

ip_input = st.text_input("Enter an IP address (e.g., 8.8.8.8):", key="ip_lookup_input")

if st.button("Find Location"):
    if not ip_input.strip():
        st.warning("Please enter a valid IP address.")
    else:
        with st.spinner("Tracking down that penguin’s coordinates..."):
            try:
                response = requests.get(f"https://ipapi.co/{ip_input}/json/", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ IP Lookup Successful")
                    st.markdown(f"""
                        **IP Address:** {data.get('ip', 'N/A')}  
                        **City:** {data.get('city', 'N/A')}  
                        **Region:** {data.get('region', 'N/A')}  
                        **Country:** {data.get('country_name', 'N/A')}  
                        **Postal Code:** {data.get('postal', 'N/A')}  
                        **Latitude:** {data.get('latitude', 'N/A')}  
                        **Longitude:** {data.get('longitude', 'N/A')}  
                        **ISP:** {data.get('org', 'N/A')}  
                        **Timezone:** {data.get('timezone', 'N/A')}  
                    """)
                else:
                    st.error("Could not fetch location data. Try again later.")
            except Exception as e:
                st.error(f"Error: {e}")
