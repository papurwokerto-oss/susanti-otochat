# santi_faiss_memory_temp_silent.py

import os
import streamlit as st
from google import genai

# === KONFIGURASI DASAR ===
st.set_page_config(page_title="SUSANTI", page_icon="💬", layout="wide") # Diubah ke wide agar header penuh seperti gambar

# === API KEY GOOGLE ===
if "GOOGLE_API_KEY" in st.secrets:
    api_key_asli = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=api_key_asli)
else:
    st.error("Kunci API tidak terbaca di sistem Secrets!")
    st.stop()

DOC_FILENAME = "sumber.txt"

# === ATUR TEMPERATUR MODEL ===
TEMPERATURE = 0.5 

# === LOAD DOKUMEN SUMBER ===
if not os.path.exists(DOC_FILENAME):
    st.error(f"❌ File '{DOC_FILENAME}' tidak ditemukan.")
    st.stop()

with open(DOC_FILENAME, "r", encoding="utf-8") as f:
    sumber_teks = f.read()

# === BUAT JAWABAN ===
def jawab_gemini(pertanyaan, konteks_dokumen, riwayat_chat):
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


# === INISIALISASI RIWAYAT CHAT ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# === SIDEBAR (UNTUK PROSES DI BELAKANG LAYAR / HAPUS CHAT) ===
# Agar tombol hapus chat diletakkan di pojok kanan atas seperti gambar, 
# kita buat tombol trigger pembersih yang tersembunyi lewat sidebar atau langsung eksekusi script berikut:
with st.sidebar:
    st.markdown("### Navigasi Kontrol")
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


# === TAMPILAN GAYA (BOOTSTRAP + STRUKTUR CSS FIXED) ===
# Kode warna disesuaikan dengan tema hijau tua elegan khas Pengadilan Agama seperti gambar contoh
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
/* Menyembunyikan elemen bawaan Streamlit agar bersih */
#MainMenu, header, footer {visibility: hidden;}
.stAppDeployButton {display:none;}
[data-testid="stHeader"] {background-color: rgba(0,0,0,0); border-bottom: none;}

/* Mengatur dasar halaman */
body, .stApp {
    background-color: #ffffff;
    font-family: "Poppins", sans-serif;
}

/* HEADER FIX DI ATAS */
.custom-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    background-color: #0d4e36; /* Hijau tua khas pengadilan */
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 30px;
    z-index: 9999;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.header-logo {
    font-size: 22px;
    font-weight: bold;
    letter-spacing: 1px;
}
.btn-hapus-custom {
    background-color: transparent;
    border: 1px solid rgba(255,255,255,0.6);
    color: white;
    padding: 5px 15px;
    border-radius: 6px;
    font-size: 14px;
    cursor: pointer;
    text-decoration: none;
}
.btn-hapus-custom:hover {
    background-color: rgba(255,255,255,0.1);
    color: white;
}

/* AREA UTAMA / WADAH CHAT DINAMIS */
.main-chat-area {
    margin-top: 80px;     /* Memberi jarak agar tidak tertutup header */
    margin-bottom: 120px; /* Memberi jarak agar tidak tertutup input & footer */
    padding: 0 10%;
    display: flex;
    flex-direction: column;
}

/* TAMPILAN IDENTITAS AWAL (WELCOME SCREEN) */
.welcome-container {
    text-align: center;
    margin-top: 8%;
    margin-bottom: 5%;
    animation: fadeIn 0.5s ease-in;
}
.welcome-title {
    color: #0d4e36;
    font-size: 32px;
    font-weight: bold;
    margin-bottom: 15px;
}
.welcome-desc {
    color: #555555;
    font-size: 16px;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
}

/* GELEMBUNG CHAT MODERN */
.chat-message-box {
    display: flex;
    align-items: flex-end;
    margin-bottom: 15px;
    animation: fadeIn 0.3s ease-out;
}
.chat-message-box.user { flex-direction: row-reverse; }
.chat-avatar-circle { width: 35px; height: 35px; border-radius: 50%; overflow: hidden; margin: 0 10px; }
.chat-avatar-circle img { width: 100%; height: 100%; object-fit: cover; }

.chat-bubble-custom {
    max-width: 70%;
    padding: 12px 18px;
    border-radius: 15px;
    font-size: 15px;
    line-height: 1.5;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.user .chat-bubble-custom {
    background-color: #e3f2fd;
    color: #0d47a1;
    border-radius: 15px 15px 0 15px;
}
.bot .chat-bubble-custom {
    background-color: #f5f5f5;
    color: #212529;
    border-radius: 15px 15px 15px 0;
    border: 1px solid #eaeaea;
}

/* FOOTER STATIS */
.custom-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 35px;
    background-color: #ffffff;
    text-align: center;
    font-size: 12px;
    color: #888888;
    line-height: 35px;
    border-top: 1px solid #eaeaea;
    z-index: 9998;
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
""", unsafe_allow_html=True)


# === 1. MERENDER HEADER LURUS & ELEGAN (STATIS) ===
# Membuat tombol palsu secara visual yang memicu sidebar reset saat diklik menggunakan skrip streamlit atau petunjuk teks
st.markdown("""
<div class="custom-header">
    <div class="header-logo">SUSANTI</div>
    <div class="text-white" style="font-size:12px; opacity:0.7;">Gunakan Sidebar kiri untuk Reset Chat jika layar penuh</div>
</div>
""", unsafe_allow_html=True)


# === 2. AREA TENGAH: STRUKTUR CHAT DINAMIS ===
st.markdown("<div class='main-chat-area'>", unsafe_allow_html=True)

# Jika riwayat obrolan masih kosong, tampilkan Selamat Datang persis seperti di gambar
if len(st.session_state.chat_history) == 0:
    st.markdown("""
    <div class="welcome-container">
        <h2 class="welcome-title">Saya SUSANTI (Asisten Layanan Informasi Virtual)</h2>
        <p class="welcome-desc">
            Asisten virtual Pengadilan Agama Purwokerto siap membantu Anda memberikan 
            informasi layanan hukum dengan cepat dan akurat.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Jika sudah ada interaksi obrolan, render isi pesan secara kronologis
    AVATAR_USER = "https://cdn-icons-png.flaticon.com/512/847/847969.png"
    AVATAR_BOT = "https://cdn-icons-png.flaticon.com/512/4712/4712100.png"
    
    for role, msg in st.session_state.chat_history:
        avatar = AVATAR_USER if role == "user" else AVATAR_BOT
        cls = "user" if role == "user" else "bot"
        st.markdown(f"""
        <div class="chat-message-box {cls}">
            <div class="chat-avatar-circle"><img src="{avatar}"></div>
            <div class="chat-bubble-custom">{msg}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# === 3. MERENDER FOOTER HAK CIPTA (STATIS DI BAGIAN PALING BAWAH) ===
st.markdown("""
<div class="custom-footer">
    © 2026 - Pengadilan Agama Purwokerto
</div>
""", unsafe_allow_html=True)


# === 4. INPUT CHAT UTAMA ===
# Komponen ini otomatis diatur oleh posisi dasar Streamlit di bawah, agar serasi dengan footer
user_input = st.chat_input("Ketik pertanyaan Anda di sini...")


# === PROSES LOGIKA UTAMA CHAT ===
if user_input:
    # Memasukkan input baru langsung ke model sebelum render ulang
    st.session_state.chat_history.append(("user", user_input))
    
    with st.spinner("SANTI sedang mencari data..."):
        konteks = sumber_teks
        # Membaca riwayat saat ini untuk menyusun jawaban kontekstual
        jawaban = jawab_gemini(user_input, konteks, st.session_state.chat_history[:-1])

    st.session_state.chat_history.append(("bot", jawaban))
    st.rerun()
