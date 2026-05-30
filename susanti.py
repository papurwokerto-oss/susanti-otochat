# susanti.py
# Versi siap-tempel untuk Streamlit + Google GenAI (SANTI)
# Pastikan: streamlit, google-genai terpasang dan SECRET "GOOGLE_API_KEY" sudah diset di Streamlit Cloud/Secrets

import os
import streamlit as st
from google import genai
import datetime
from typing import List, Tuple

# -------------------------
# KONFIGURASI HALAMAN & API
# -------------------------
st.set_page_config(page_title="SUSANTI", page_icon="💬", layout="centered")

# Ambil API key dari secrets
if "GOOGLE_API_KEY" in st.secrets:
    api_key_asli = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=api_key_asli)
else:
    st.error("Kunci API tidak terbaca di sistem Secrets! Silakan set GOOGLE_API_KEY di Secrets.")
    st.stop()

# Nama file dokumen sumber
DOC_FILENAME = "sumber.txt"

# Pengaturan model
MODEL_NAME = "gemini-2.5-flash"
TEMPERATURE = 0.5
MAX_OUTPUT_TOKENS = 1024

# Batas-batas untuk chunking dan prompt
MAX_CHUNK_CHARS = 2500
MAX_PROMPT_CHARS = 15000
MAX_HISTORY_TO_SEND = 5
TOP_K_CHUNKS = 2

# -------------------------
# UTIL: load dokumen & chunk
# -------------------------
@st.cache_data(show_spinner=False)
def load_sumber(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def chunk_document(doc: str, max_chars: int = MAX_CHUNK_CHARS) -> List[str]:
    # Potong berdasarkan paragraf, gabungkan sampai batas max_chars
    paras = [p.strip() for p in doc.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current = ""
    for p in paras:
        if not current:
            current = p
        elif len(current) + len(p) + 2 <= max_chars:
            current += "\n\n" + p
        else:
            chunks.append(current)
            current = p
    if current:
        chunks.append(current)
    return chunks

def find_relevant_chunks(question: str, chunks: List[str], top_k: int = TOP_K_CHUNKS) -> List[str]:
    # Pencocokan kata sederhana; cukup untuk dokumen lokal kecil
    q_words = set(w.lower() for w in question.split() if len(w) > 2)
    scored = []
    for c in chunks:
        c_words = set(w.lower() for w in c.split())
        score = len(q_words & c_words)
        scored.append((score, c))
    scored.sort(reverse=True, key=lambda x: x[0])
    selected = [c for s, c in scored[:top_k] if s > 0]
    if not selected and chunks:
        # fallback: ambil chunk pertama sebagai ringkasan
        selected = [chunks[0]]
    return selected

def promptwrap(text: str, max_chars: int = MAX_PROMPT_CHARS) -> str:
    return text if len(text) <= max_chars else text[:max_chars]

# -------------------------
# BUILD PROMPT
# -------------------------
def build_prompt(question: str, doc_chunks: List[str], chat_history: List[Tuple[str, str]]) -> str:
    # Siapkan riwayat (maks MAX_HISTORY_TO_SEND)
    history_lines = []
    for role, msg in chat_history[-MAX_HISTORY_TO_SEND:]:
        who = "User" if role == "user" else "SANTI"
        history_lines.append(f"{who}: {msg}")
    history_text = "\n".join(history_lines)

    doc_text = "\n\n---\n\n".join(doc_chunks)

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
{history_text}

=== DOKUMEN SUMBER (HANYA BAGIAN RELEVAN) ===
{doc_text}

=== PERTANYAAN BARU ===
{question}

Jawablah sopan, ringkas, dan mudah dimengerti.
Tambahkan tawaran bantuan di akhir jawaban.
"""
    return promptwrap(prompt)

# -------------------------
# FUNGSI UTAMA: panggil model
# -------------------------
def jawab_gemini(question: str, doc_chunks: List[str], chat_history: List[Tuple[str, str]]) -> str:
    prompt = build_prompt(question, doc_chunks, chat_history)
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "temperature": TEMPERATURE,
                "max_output_tokens": MAX_OUTPUT_TOKENS
            }
        )
        # Beberapa SDK mengembalikan .text atau .output[0].content; gunakan .text jika tersedia
        text = getattr(response, "text", None)
        if text:
            return text.strip()
        # fallback: coba ambil dari struktur lain
        try:
            return response.output[0].content[0].text.strip()
        except Exception:
            return str(response).strip()
    except Exception as e:
        # Tangani error API dengan pesan ramah
        return f"⚠️ Terjadi kesalahan saat memanggil model: {e}"

# -------------------------
# TAMPILAN (CSS + THEME)
# -------------------------
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

# -------------------------
# INISIALISASI RIWAYAT CHAT
# -------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history: List[Tuple[str, str]] = []

# Muat dokumen sumber
sumber_teks = load_sumber(DOC_FILENAME)
if sumber_teks is None:
    st.error(f"❌ File '{DOC_FILENAME}' tidak ditemukan. Silakan unggah atau letakkan file tersebut di folder aplikasi.")
    st.stop()

# Buat chunks (cached)
if "doc_chunks" not in st.session_state:
    st.session_state.doc_chunks = chunk_document(sumber_teks, max_chars=MAX_CHUNK_CHARS)

# -------------------------
# RENDER RIWAYAT CHAT (menggunakan st.chat_message bila tersedia)
# -------------------------
st.markdown("<div class='chat-body'>", unsafe_allow_html=True)
AVATAR_USER = "https://cdn-icons-png.flaticon.com/512/847/847969.png"
AVATAR_BOT = "https://cdn-icons-png.flaticon.com/512/4712/4712100.png"

# Tampilkan riwayat yang tersimpan
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

# -------------------------
# INPUT CHAT
# -------------------------
user_input = st.chat_input("Tanyakan informasi pengadilan di sini...")

# -------------------------
# LOGIKA PANGGILAN
# -------------------------
if user_input:
    # 1) Tampilkan pesan user segera (UX)
    st.session_state.chat_history.append(("user", user_input))
    # Render pesan user secara langsung agar terlihat
    st.experimental_rerun() if False else None  # no-op; hanya memastikan tidak auto-rerun

    # 2) Cari chunk relevan
    chunks = st.session_state.doc_chunks
    relevant = find_relevant_chunks(user_input, chunks, top_k=TOP_K_CHUNKS)

    # 3) Panggil model dengan spinner
    with st.spinner("🤖 SANTI sedang menganalisis dokumen..."):
        jawaban = jawab_gemini(user_input, relevant, st.session_state.chat_history)

    # 4) Simpan jawaban ke riwayat dan tampilkan
    st.session_state.chat_history.append(("bot", jawaban))

    # Tampilkan jawaban baru (agar langsung muncul tanpa reload)
    st.experimental_rerun() if False else None  # no-op

# -------------------------
# CATATAN PENTING
# -------------------------
st.markdown(
    """
    <div style="margin-top:12px; font-size:13px; color:gray;">
    Tips: Aplikasi ini hanya menjawab berdasarkan isi file <b>sumber.txt</b>. 
    Jika ingin memperbarui informasi, edit file <b>sumber.txt</b> lalu refresh aplikasi.
    </div>
    """,
    unsafe_allow_html=True,
)
