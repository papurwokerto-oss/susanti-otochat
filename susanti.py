import os
import streamlit as st
from google import genai

# === 1. KONFIGURASI HALAMAN ===
st.set_page_config(
    page_title="SANTI AI", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === 2. API KEY GOOGLE ===
if "GOOGLE_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Kunci API tidak ditemukan!")
    st.stop()

DOC_FILENAME = "sumber.txt"

# === 3. LOAD DATA ===
if not os.path.exists(DOC_FILENAME):
    st.error(f"File {DOC_FILENAME} tidak ditemukan.")
    st.stop()

with open(DOC_FILENAME, "r", encoding="utf-8") as f:
    sumber_teks = f.read()

# === 4. LOGIKA RETRIEVAL & GEMINI ===
def ambil_konteks_relevan(pertanyaan, dokumen, top_n=3):
    paragraf_list = [p.strip() for p in dokumen.split("\n\n") if p.strip()]
    kata_kunci = set(pertanyaan.lower().split())
    skor_paragraf = []
    for paragraf in paragraf_list:
        kata_paragraf = set(paragraf.lower().split())
        kecocokan = len(kata_kunci.intersection(kata_paragraf))
        skor_paragraf.append((kecocokan, paragraf))
    skor_paragraf.sort(key=lambda x: x[0], reverse=True)
    return "\n\n".join([p for skor, p in skor_paragraf[:top_n]])

def jawab_gemini(pertanyaan, konteks, riwayat):
    prompt = f"""
Anda adalah SANTI, Asisten Virtual Pengadilan Agama Purwokerto.
Jawab ramah, lucu, dan berikan pujian singkat. Gunakan HANYA konteks berikut:
<konteks>{konteks}</konteks>
Jika tidak ada jawaban, arahkan pengguna ke kantor.
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt + f"\nUser: {pertanyaan}",
            config={'temperature': 0.5, 'max_output_tokens': 2048}
        )
        return response.text.strip()
    except:
        return "Maaf, koneksi SANTI sedang terganggu. Silakan coba lagi ya!"

# === 5. INISIALISASI STATE ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# === 6. CSS UI ELEGAN ===
st.markdown("""
<style>
    /* Reset & Background */
    header, [data-testid='stHeader'] {display: none !important;}
    .stApp {background-color: #f9fafb !important;}
    
    /* Layout Chat */
    .stMainBlockContainer {max-width: 800px !important; padding-top: 2rem !important; padding-bottom: 150px !important;}
    
    /* Tombol Hapus */
    .stButton > button {
        background-color: #0d4e36 !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 8px 24px !important;
        font-weight: 600 !important;
        margin: 20px auto !important;
        display: block !important;
    }
    .stButton > button:hover {background-color: #063a26 !important;}
    
    /* Chat Bubble Styling */
    div[data-testid='stChatMessage'] {border-radius: 15px !important; padding: 15px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05);}
    
    /* Footer */
    .custom-footer {
        text-align: center;
        padding: 20px;
        font-size: 0.8rem;
        color: #6b7280;
        position: fixed;
        bottom: 0;
        width: 100%;
        background: #f9fafb;
        border-top: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

# === 7. RENDER CHAT ===
if len(st.session_state.chat_history) == 0:
    st.markdown("<h2 style='text-align: center; color: #0d4e36;'>Halo, Saya SANTI!</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Asisten virtual PA Purwokerto siap membantu Anda.</p>", unsafe_allow_html=True)

for role, msg in st.session_state.chat_history:
    avatar = "🤖" if role == "bot" else "👤"
    with st.chat_message(role, avatar=avatar):
        st.write(msg)

# === 8. INPUT & LOGIKA ===
if user_input := st.chat_input("Tulis pertanyaan Anda di sini..."):
    st.session_state.chat_history.append(("user", user_input))
    konteks = ambil_konteks_relevan(user_input, sumber_teks)
    jawaban = jawab_gemini(user_input, konteks, st.session_state.chat_history)
    st.session_state.chat_history.append(("bot", jawaban))
    st.rerun()

# Tombol Hapus & Footer
if st.button("Hapus Riwayat Chat"):
    st.session_state.chat_history = []
    st.rerun()

st.markdown("""
<div class="custom-footer">
    &copy; 2026 - Pengadilan Agama Purwokerto
</div>
""", unsafe_allow_html=True)
