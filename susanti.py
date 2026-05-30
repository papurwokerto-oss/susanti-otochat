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


# === 6. SUNTIKAN CSS GLOBAL (KUSTOMISASI ANTARMUKA) ===
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
/* Sembunyikan elemen standar Streamlit agar lebih bersih */
#MainMenu, header, footer { visibility: hidden; }
.stAppDeployButton { display: none; }
[data-testid="stHeader"] { background-color: rgba(0,0,0,0); border-bottom: none; }

/* Mengatur latar belakang aplikasi */
body, .stApp {
    background-color: #ffffff !important;
    font-family: "Poppins", sans-serif;
}

/* HEADER BESAR STATIS DI ATAS */
.custom-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 64px;
    background-color: #0d4e36; /* Warna Hijau Tua Elegan */
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 40px;
    z-index: 9999;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.header-logo {
    font-size: 24px;
    font-weight: 700;
    letter-spacing: 1px;
}

/* Memposisikan Tombol Hapus Chat Asli Streamlit ke Header Atas */
div[data-testid="stMarkdownContainer"] + div.element-container:has(button[key="btn_hapus_chat"]) {
    position: fixed;
    top: 13px;
    right: 40px;
    z-index: 10000;
    width: auto !important;
}

/* Mengatur Gaya Tombol Hapus Chat Streamlit agar Menyatu dengan Header */
button[key="btn_hapus_chat"] {
    background-color: transparent !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.4) !important;
    border-radius: 8px !important;
    padding: 6px 16px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease;
}
button[key="btn_hapus_chat"]:hover {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border-color: white !important;
}

/* AREA BUNGKUS CHAT UTAMA (MENGALIR & BISA SCROLL) */
.main-chat-container {
    margin-top: 90px;     /* Jarak aman agar tidak tertimpa header */
    margin-bottom: 110px; /* Jarak aman agar tidak tertimpa input bottom */
    padding: 0 15%;
    display: flex;
    flex-direction: column;
}

@media (max-width: 768px) {
    .main-chat-container {
        padding: 0 5%;
    }
}

/* TAMPILAN SELAMAT DATANG (WELCOME SCREEN) */
.welcome-box {
    text-align: center;
    margin-top: 10vh;
    margin-bottom: 5vh;
    animation: fadeIn 0.6s ease-out;
}
.welcome-title {
    color: #0d4e36;
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 18px;
}
.welcome-desc {
    color: #666666;
    font-size: 16px;
    max-width: 650px;
    margin: 0 auto;
    line-height: 1.6;
}

/* DESAIN GELEMBUNG PESAN */
.chat-row {
    display: flex;
    align-items: flex-end;
    margin-bottom: 18px;
    animation: fadeIn 0.3s ease-out;
}
.chat-row.user {
    flex-direction: row-reverse;
}
.chat-icon-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    overflow: hidden;
    margin: 0 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.chat-icon-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.chat-bubble-box {
    max-width: 70%;
    padding: 12px 18px;
    border-radius: 16px;
    font-size: 15px;
    line-height: 1.5;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.user .chat-bubble-box {
    background-color: #d1e7dd; /* Hijau Soft khas User */
    color: #0f5132;
    border-radius: 16px 16px 0 16px;
}
.bot .chat-bubble-box {
    background-color: #f8f9fa; /* Abu-abu terang khas Bot */
    color: #212529;
    border-radius: 16px 16px 16px 0;
    border: 1px solid #e9ecef;
}

/* COPYRIGHT BAR DI BAGIAN PALING BAWAH */
.custom-footer-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 32px;
    background-color: #ffffff;
    text-align: center;
    font-size: 11px;
    color: #999999;
    line-height: 32px;
    border-top: 1px solid #f1f3f5;
    z-index: 9998;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)


# === 7. KONTROL HEADER DAN TOMBOL HAPUS (DI-RENDER ULANG SECARA PROSES) ===
# Header Visual HTML
st.markdown("""
<div class="custom-header">
    <div class="header-logo">SUSANTI</div>
</div>
""", unsafe_allow_html=True)

# Tombol Streamlit Asli yang diletakkan persis di posisi tombol header via CSS target
if st.button("Hapus Chat", key="btn_hapus_chat"):
    st.session_state.chat_history = []
    st.rerun()


# === 8. AREA RENDER CHAT DINAMIS ===
st.markdown("<div class='main-chat-container'>", unsafe_allow_html=True)

# Jika riwayat chat kosong, tampilkan Welcome Screen cantik
if len(st.session_state.chat_history) == 0:
    st.markdown("""
    <div class="welcome-box">
        <h1 class="welcome-title">Saya SUSANTI (Asisten Layanan Informasi Virtual)</h1>
        <p class="welcome-desc">
            Asisten virtual Pengadilan Agama Purwokerto siap membantu Anda memberikan
            informasi layanan hukum dengan cepat dan akurat.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Render pesan-pesan dari riwayat chat
    AVATAR_USER = "https://cdn-icons-png.flaticon.com/512/847/847969.png"
    AVATAR_BOT = "https://cdn-icons-png.flaticon.com/512/4712/4712100.png"
    
    for role, msg in st.session_state.chat_history:
        avatar = AVATAR_USER if role == "user" else AVATAR_BOT
        cls = "user" if role == "user" else "bot"
        
        st.markdown(f"""
        <div class="chat-row {cls}">
            <div class="chat-icon-avatar"><img src="{avatar}"></div>
            <div class="chat-bubble-box">{msg}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# === 9. FOOTER HAK CIPTA STATIS ===
st.markdown("""
<div class="custom-footer-bar">
    © 2026 - Pengadilan Agama Purwokerto
</div>
""", unsafe_allow_html=True)


# === 10. INPUT CHAT UTAMA ===
# Streamlit secara otomatis akan mengunci letak widget ini di bagian bawah layar
user_input = st.chat_input("Ketik pertanyaan Anda di sini...")


# === 11. PROSES JAWABAN ===
if user_input:
    # Simpan input user terlebih dahulu
    st.session_state.chat_history.append(("user", user_input))
    
    with st.spinner("SANTI sedang membaca dokumen..."):
        # Panggil API Gemini dengan menyertakan memori chat
        jawaban = jawab_gemini(user_input, sumber_teks, st.session_state.chat_history[:-1])

    # Simpan respon SANTI
    st.session_state.chat_history.append(("bot", jawaban))
    st.rerun()
