# susanti.py

import os
import streamlit as st
from google import genai

# === 1. KONFIGURASI HALAMAN UTAMA ===
st.set_page_config(
    page_title="SUSANTI - Pengadilan Agama Purwokerto", 
    page_icon="💬", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === 2. API KEY GOOGLE ===
if "GOOGLE_API_KEY" in st.secrets:
    api_key_asli = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=api_key_asli)
else:
    st.error("Kunci API tidak terbaca di sistem Secrets!")
    st.stop()

DOC_FILENAME = "sumber.txt"
TEMPERATURE = 0.5 

# === 3. LOAD DOKUMEN SUMBER ===
if not os.path.exists(DOC_FILENAME):
    st.error(f"❌ File '{DOC_FILENAME}' tidak ditemukan.")
    st.stop()

with open(DOC_FILENAME, "r", encoding="utf-8") as f:
    sumber_teks = f.read()

# === 4. FUNGSI JAWABAN GEMINI ===
def jawab_gemini(pertanyaan, konteks_dokumen, riwayat_chat):
    # Format riwayat chat (5 pesan terakhir saja untuk memori ringkas)
    chat_history = "\n".join(
        [f"{'User' if r=='user' else 'SANTI'}: {m}" for r, m in riwayat_chat[-5:]]
    )

    prompt = f"""
Anda berperan sebagai asisten virtual yang cerdas. 
Nama lengkap Anda "SUSANTI, biasa dipanggil SANTI - Asisten Layanan Informasi Pengadilan Agama Purwokerto".
Sifat Anda: Ramah, lucu, menarik, dan selalu memberikan pujian singkat sebelum menjawab.

TUGAS ANDA:
1. Jawablah pertanyaan pengguna HANYA berdasarkan dokumen sumber di bawah ini:
2. Jika jawaban ada di dokumen, jelaskan dengan bahasa yang mudah dipahami.
3. Jika jawaban TIDAK ADA di dokumen, cukup katakan: "Hmm, kayaknya untuk hal itu kamu langsung datang aja deh ke Pengadilan Agama Purwokerto agar lebih jelas." dan jangan berikan informasi tambahan lain.
4. Jangan pernah merusak karakter Anda sebagai SANTI.

=== RIWAYAT CHAT ===
{chat_history}

=== DOKUMEN SUMBER ===
{konteks_dokumen}

=== PERTANYAAN BARU ===
{pertanyaan}

Jawablah sopan, ringkas, dan mudah dimengerti. 
Tambahkan tawaran bantuan di akhir jawaban.
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'temperature': TEMPERATURE,
                'max_output_tokens': 2048
            }
        )
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Terjadi kesalahan: {e}"


# === 5. INISIALISASI STATE ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# === 6. SUNTIKAN CSS GLOBAL (KUSTOMISASI ANTARMUKA SECARA AMAN TANPA BARIS KOSONG) ===
st.markdown("""<style>
header, footer, [data-testid="stHeader"] {display: none !important;}
.stApp {background-color: #ffffff !important;}
.custom-header {position: fixed; top: 0; left: 0; right: 0; height: 60px; background-color: #0d4e36; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 99999; box-shadow: 0 2px 5px rgba(0,0,0,0.15);}
.custom-header-title {color: #ffffff; font-size: 22px; font-weight: 700; font-family: 'Poppins', sans-serif; letter-spacing: 0.5px;}
button[key="btn_hapus_chat"] {position: fixed !important; top: 12px !important; right: 40px !important; z-index: 100000 !important; background-color: transparent !important; color: #ffffff !important; border: 1px solid rgba(255, 255, 255, 0.5) !important; border-radius: 6px !important; padding: 4px 14px !important; font-size: 14px !important; font-weight: 500 !important; transition: all 0.2s ease;}
button[key="btn_hapus_chat"]:hover {background-color: rgba(255,255,255,0.1) !important; border-color: #ffffff !important;}
.stMainBlockContainer {padding-top: 85px !important; padding-bottom: 120px !important; max-width: 900px !important; margin: 0 auto !important;}
.welcome-box {text-align: center; margin-top: 15vh; margin-bottom: 5vh; font-family: 'Poppins', sans-serif;}
.welcome-title {color: #0d4e36; font-size: 34px; font-weight: 700; margin-bottom: 15px;}
.welcome-desc {color: #555555; font-size: 16px; max-width: 650px; margin: 0 auto; line-height: 1.6;}
.custom-footer {position: fixed; bottom: 0; left: 0; right: 0; height: 35px; background-color: #ffffff; text-align: center; font-size: 11px; color: #888888; line-height: 35px; border-top: 1px solid #f1f3f5; z-index: 99998;}
div[data-testid="stChatMessage"] {background-color: #f8f9fa !important; border: 1px solid #e9ecef !important; border-radius: 12px !important; padding: 12px 16px !important; margin-bottom: 12px !important;}
div[data-testid="stChatMessage"]:has(span[data-testid="stChatMessageAvatar"] img[alt="user"]), div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatar"] [data-testid="UserIcon"]) {background-color: #e2f0d9 !important; border-color: #c5e1a5 !important; color: #1e4620 !important;}
div[data-testid="stChatInput"] {bottom: 35px !important; background-color: #ffffff !important; border-top: none !important; padding: 10px 0 !important;}
div[data-testid="stChatInput"] textarea {border-radius: 12px !important; border: 1px solid #ced4da !important; font-size: 14.5px !important;}
div[data-testid="stChatInput"] button {background-color: #0d4e36 !important; color: #ffffff !important; border-radius: 8px !important;}
</style>""", unsafe_allow_html=True)


# === 7. KONTROL HEADER DAN TOMBOL HAPUS ===
st.markdown("""
<div class="custom-header">
    <div class="custom-header-title">SANTI</div>
</div>
""", unsafe_allow_html=True)

# Tombol Streamlit Asli diposisikan ke Header via CSS kustom di atas
if st.button("Hapus Chat", key="btn_hapus_chat"):
    st.session_state.chat_history = []
    st.rerun()


# === 8. AREA RENDER CHAT DINAMIS ===
if len(st.session_state.chat_history) == 0:
    st.markdown("""
    <div class="welcome-box">
        <h1 class="welcome-title">Saya SANTI (Asisten Layanan Informasi Virtual)</h1>
        <p class="welcome-desc">
            Asisten virtual Pengadilan Agama Purwokerto siap membantu Anda memberikan
            informasi layanan hukum dengan cepat dan akurat.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    for role, msg in st.session_state.chat_history:
        avatar = "👤" if role == "user" else "🤖"
        with st.chat_message(role, avatar=avatar):
            st.write(msg)


# === 9. FOOTER HAK CIPTA STATIS ===
st.markdown("""
<div class="custom-footer">
    © 2026 - Pengadilan Agama Purwokerto
</div>
""", unsafe_allow_html=True)


# === 10. INPUT CHAT UTAMA ===
user_input = st.chat_input("Ketik pertanyaan Anda di sini...")


# === 11. PROSES JAWABAN ===
if user_input:
    st.session_state.chat_history.append(("user", user_input))
    
    with st.spinner("SANTI sedang membaca dokumen..."):
        # Ambil seluruh isi dokumen teks dan kumpulkan riwayat sebelumnya untuk Gemini
        jawaban = jawab_gemini(user_input, sumber_teks, st.session_state.chat_history[:-1])

    st.session_state.chat_history.append(("bot", jawaban))
    st.rerun()
