import os
import streamlit as st
import base64
from google import genai

# === 1. FUNGSI PEMBANTU (Helper) ===
def get_image_as_base64(file_path):
    """Membaca gambar dan mengubahnya ke base64 agar pasti tampil di Streamlit"""
    try:
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except:
        return None

# Konversi gambar ke base64
santi_img_base64 = get_image_as_base64("santi.png")
santi_data_url = f"data:image/png;base64,{santi_img_base64}" if santi_img_base64 else None

# === 7. SUNTIKAN CSS PREMIUM ===
style_html = (
    "<style>"
    "header, footer, [data-testid='stHeader'] {display: none !important;}"
    ".custom-header {position: fixed; top: 0; left: 0; right: 0; height: 60px; background-color: #0a5d3f; display: flex; align-items: center; justify-content: center; z-index: 99999; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3); border-bottom: 2px solid #e6a119; gap: 12px;}"
    ".custom-header-img {height: 40px; width: 40px; border-radius: 50%; border: 2px solid #ffffff; object-fit: cover; background-color: #ffffff;}"
    ".custom-header-title {color: #ffffff !important; font-size: 1.5rem !important; font-weight: 800 !important; font-family: 'Inter', sans-serif !important; letter-spacing: 1px !important;}"
    ".stMainBlockContainer {padding-top: 80px !important;}"
    "</style>"
)
st.markdown(style_html, unsafe_allow_html=True)

# === 8. KONTROL HEADER ===
# Memastikan gambar benar-benar dirender dengan tag img yang bersih
if santi_data_url:
    st.markdown(f"""
    <div class="custom-header">
        <img src="{santi_data_url}" class="custom-header-img" alt="SANTI">
        <div class="custom-header-title">SANTI</div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Fallback jika gambar tidak terbaca
    st.markdown("""
    <div class="custom-header">
        <div class="custom-header-title">SANTI</div>
    </div>
    """, unsafe_allow_html=True)

# === 9. RENDER CHAT ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for role, msg in st.session_state.chat_history:
    avatar_bot = santi_data_url if role == "bot" else None
    with st.chat_message(role, avatar=avatar_bot):
        st.write(msg)
