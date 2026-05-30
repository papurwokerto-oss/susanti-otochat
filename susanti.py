# santi_faiss_memory_temp_silent.py

import os
import streamlit as st
from google import genai

# === KONFIGURASI DASAR ===
st.set_page_config(page_title="SUSANTI", page_icon="💬", layout="centered")

# === API KEY GOOGLE ===
if "GOOGLE_API_KEY" in st.secrets:
    api_key_asli = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=api_key_asli)
else:
    st.error("Kunci API tidak terbaca di sistem Secrets!")
    st.stop()

DOC_FILENAME = "sumber.txt"

# === ATUR TEMPERATUR MODEL ===
TEMPERATURE = 0.5  # 0.5 membuat SANTI konsisten dan patuh pada dokumen

# === LOAD DOKUMEN SUMBER ===
if not os.path.exists(DOC_FILENAME):
    st.error(f"❌ File '{DOC_FILENAME}' tidak ditemukan.")
    st.stop()

with open(DOC_FILENAME, "r", encoding="utf-8") as f:
    sumber_teks = f.read()

# === BUAT JAWABAN (LANGSUNG MEMBACA DOKUMEN UTUH) ===
def jawab_gemini(pertanyaan, konteks_dokumen, riwayat_chat):
    # Gabungkan riwayat chat (5 pesan terakhir)
    chat_history = "\n".join(
        [f"{'User' if r=='user' else 'SANTI'}: {m}" for r, m in riwayat_chat[-5:]]
    )

    # Prompt utama dengan memasukkan seluruh isi dokumen sumber
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


# === TAMPILAN (BOOTSTRAP + CSS) ===
import datetime
hour = datetime.datetime.now().hour
is_dark = hour >= 18 or hour <= 5

bg_color = "#121212" if is_dark else "#f8f9fa"
text_color = "#f1f1f1" if is_dark else "#212529"
bubble_user_bg = "#3aafa9" if is_dark else "#d1e7dd"
bubble_bot_bg = "#2e2e2e" if is_dark else "#e9ecef"
bubble_user_color = "#ffffff" if is_dark else "#0f5132"
bubble_bot_color = "#f1f1f1" if is_dark else "#212529"

st.markdown(f"""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body {{ background-color: {bg_color}; font-family: "Poppins", sans-serif; color: {text_color}; }}
.chat-body {{ display: flex; flex-direction: column; padding: 10px; }}
.chat-message {{ display: flex; align-items: flex-end; margin-bottom: 12px; animation: fadeIn 0.3s ease-in; }}
.chat-message.user {{ flex-direction: row-reverse; }}
.chat-avatar {{ width: 38px; height: 38px; border-radius: 50%; overflow: hidden; margin: 0 8px; }}
.chat-avatar img {{ width: 100%; height: 100%; object-fit: cover; }}
.chat-bubble {{ max-width: 70%; padding: 10px 15px; border-radius: 18px; font-size: 15px; line-height: 1.4; }}
.user .chat-bubble {{ background-color: {bubble_user_bg}; color: {bubble_user_color}; border-radius: 18px 18px 0 18px; }}
.bot .chat-bubble {{ background-color: {bubble_bot_bg}; color: {bubble_bot_color}; border-radius: 18px 18px 18px 0; }}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
</style>
""", unsafe_allow_html=True)

# === MERENDER RIWAYAT CHAT ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown("<div class='chat-body'>", unsafe_allow_html=True)
AVATAR_USER = "https://cdn-icons-png.flaticon.com/512/847/847969.png"
AVATAR_BOT = "https://cdn-icons-png.flaticon.com/512/4712/4712100.png"

for role, msg in st.session_state.chat_history:
    avatar = AVATAR_USER if role == "user" else AVATAR_BOT
    cls = "user" if role == "user" else "bot"
    st.markdown(f"""
    <div class="chat-message {cls}">
        <div class="chat-avatar"><img src="{avatar}"></div>
        <div class="chat-bubble">{msg}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# === INPUT CHAT ===
user_input = st.chat_input("Tanyakan informasi pengadilan di sini...")

# === PROSES LOGIKA CHAT ===
if user_input:
    with st.spinner("🤖 SANTI sedang menganalisis dokumen..."):
        # Langsung kirim seluruh isi dokumen sumber ke fungsi jawab_gemini
        jawaban = jawab_gemini(user_input, sumber_teks, st.session_state.chat_history)

    # Masukkan interaksi ke riwayat setelah proses selesai
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("bot", jawaban))

    st.rerun()# santi_faiss_memory_temp_silent.py

import os
import streamlit as st
from google import genai

# === KONFIGURASI DASAR ===
st.set_page_config(page_title="SUSANTI", page_icon="💬", layout="centered")

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


# === TAMPILAN & DETEKSI TEMA (BOOTSTRAP + CSS) ===
import datetime
hour = datetime.datetime.now().hour
is_dark = hour >= 18 or hour <= 5

bg_color = "#121212" if is_dark else "#f8f9fa"
text_color = "#f1f1f1" if is_dark else "#212529"
card_bg = "#1e1e1e" if is_dark else "#ffffff"
bubble_user_bg = "#3aafa9" if is_dark else "#d1e7dd"
bubble_bot_bg = "#2e2e2e" if is_dark else "#e9ecef"
bubble_user_color = "#ffffff" if is_dark else "#0f5132"
bubble_bot_color = "#f1f1f1" if is_dark else "#212529"

st.markdown(f"""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body {{ background-color: {bg_color}; font-family: "Poppins", sans-serif; color: {text_color}; }}

/* HEADER STATIS DI ATAS */
.santi-header {{
    background-color: {card_bg};
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    border: 1px solid rgba(0,0,0,0.05);
}}
.header-avatar {{
    width: 70px;
    height: 70px;
    border-radius: 50%;
    margin-right: 15px;
    object-fit: cover;
    border: 2px solid #0d6efd;
}}
.header-title {{ margin: 0; font-size: 18px; font-weight: bold; color: {text_color}; }}
.header-desc {{ margin: 3px 0 0 0; font-size: 13px; color: gray; line-height: 1.3; }}

/* AREA CHAT DINAMIS (BISA SCROLL) */
.chat-container {{
    max-height: 400px; /* Batas tinggi area chat */
    overflow-y: auto;  /* Mengaktifkan scroll vertikal */
    padding: 10px;
    display: flex;
    flex-direction: column;
    border-radius: 10px;
    background-color: rgba(0,0,0,0.02);
}}
.chat-message {{ display: flex; align-items: flex-end; margin-bottom: 12px; animation: fadeIn 0.3s ease-in; }}
.chat-message.user {{ flex-direction: row-reverse; }}
.chat-avatar {{ width: 35px; height: 35px; border-radius: 50%; overflow: hidden; margin: 0 8px; }}
.chat-avatar img {{ width: 100%; height: 100%; object-fit: cover; }}
.chat-bubble {{ max-width: 75%; padding: 10px 15px; border-radius: 18px; font-size: 14px; line-height: 1.4; }}
.user .chat-bubble {{ background-color: {bubble_user_bg}; color: {bubble_user_color}; border-radius: 18px 18px 0 18px; }}
.bot .chat-bubble {{ background-color: {bubble_bot_bg}; color: {bubble_bot_color}; border-radius: 18px 18px 18px 0; }}

@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
</style>
""", unsafe_allow_html=True)


# === LINK GAMBAR AVATAR ===
AVATAR_USER = "https://cdn-icons-png.flaticon.com/512/847/847969.png"
AVATAR_BOT = "https://cdn-icons-png.flaticon.com/512/4712/4712100.png" # Ini juga dipakai untuk avatar besar di atas


# === 1. BAGIAN ATAS: HEADER PROFIL SANTI (STATIS) ===
st.markdown(f"""
<div class="santi-header">
    <img src="{AVATAR_BOT}" class="header-avatar" alt="Avatar SUSANTI">
    <div>
        <h1 class="header-title">SUSANTI (SANTI)</h1>
        <p class="header-desc">
            <strong>Asisten Layanan Informasi Virtual</strong><br>
            Pengadilan Agama Purwokerto Kelas IA.<br>
            <em>Siap melayani Anda dengan ramah, ceria, dan akurat!</em>
        </p>
    </div>
</div>
""", unsafe_allow_html=True)


# === MENU SAMPING (SIDEBAR) ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.markdown("### Pengaturan Chat")
    if st.button("🗑️ Hapus Riwayat Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


# === 2. BAGIAN TENGAH: AREA MERENDER CHAT (DINAMIS & SCROLLABLE) ===
# Membuka pembungkus container chat agar bisa di-scroll
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for role, msg in st.session_state.chat_history:
    avatar = AVATAR_USER if role == "user" else AVATAR_BOT
    cls = "user" if role == "user" else "bot"
    st.markdown(f"""
    <div class="chat-message {cls}">
        <div class="chat-avatar"><img src="{avatar}"></div>
        <div class="chat-bubble">{msg}</div>
    </div>
    """, unsafe_allow_html=True)

# Menutup pembungkus container chat
st.markdown("</div>", unsafe_allow_html=True)


# === 3. BAGIAN BAWAH: INPUT CHAT ===
user_input = st.chat_input("Tanyakan informasi pengadilan di sini...")


# === PROSES LOGIKA CHAT ===
if user_input:
    with st.spinner("🤖 SANTI sedang menganalisis dokumen..."):
        konteks = sumber_teks
        jawaban = jawab_gemini(user_input, konteks, st.session_state.chat_history)

    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("bot", jawaban))
    st.rerun()
