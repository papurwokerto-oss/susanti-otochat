# santi_faiss_memory_temp_silent.py

import os
import numpy as np
import faiss
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
INDEX_FILENAME = "santi_index.faiss"

# === ATUR TEMPERATUR MODEL ===
TEMPERATURE = 0.9  # 0.0 = faktual, 1.0 = kreatif

# === LOAD DOKUMEN SUMBER (PERBAIKAN) ===
if not os.path.exists(DOC_FILENAME):
    st.error(f"❌ File '{DOC_FILENAME}' tidak ditemukan.")
    st.stop()

with open(DOC_FILENAME, "r", encoding="utf-8") as f:
    sumber_teks = f.read()

# Perbaikan pemotongan teks: Membersihkan karakter \r (Windows) dan memotong dengan aman
sumber_teks = sumber_teks.replace("\r\n", "\n")
# Memotong berdasarkan double enter ATAU single enter jika barisnya cukup panjang
raw_paragraphs = sumber_teks.split("\n\n") if "\n\n" in sumber_teks else sumber_teks.split("\n")
paragraphs = [p.strip() for p in raw_paragraphs if len(p.strip()) > 5]

# === BUAT & SIMPAN EMBEDDING (SUDAH DIPERBAIKI) ===
@st.cache_resource(show_spinner=False)
def buat_faiss_index(paragraphs):
    model_name = "text-embedding-005" 
    
    # LAKUKAN INI PERTAMA: Cek apakah file indeks lama sudah ada di server
    if os.path.exists(INDEX_FILENAME):
        try:
            index = faiss.read_index(INDEX_FILENAME)
            return index, paragraphs
        except Exception as e:
            st.warning(f"Gagal membaca indeks lokal, membuat ulang... Error: {e}")
            if os.path.exists(INDEX_FILENAME):
                os.remove(INDEX_FILENAME)

    # LAKUKAN INI KEDUA: Siapkan wadah kosong SEBELUM proses looping dimulai
    embeddings = []
    
    status_box = st.empty()
    status_box.info(f"🔄 Sedang memproses {len(paragraphs)} paragraf dari dokumen...")

    # LAKUKAN INI KETIGA: Lakukan looping untuk mengambil embedding dari API Google
    for i, para in enumerate(paragraphs):
        try:
            res = client.models.embed_content(
                model=model_name,
                contents=para
            )
            embeddings.append(res.embeddings[0].values)
        except Exception as e:
            # Sekarang blok 'try' sudah memiliki pasangan 'except' yang valid
            status_box.empty()
            st.error(f"❌ Gagal membuat embedding pada paragraf ke-{i+1}.")
            st.error(f"Detail Pesan Eror: {e}")
            st.stop()

    status_box.empty()

    if len(embeddings) == 0:
        st.error("❌ Dokumen kosong atau tidak ada teks yang berhasil diproses.")
        st.stop()

    # LAKUKAN INI KEEMPAT: Ubah menjadi array dan masukkan ke FAISS
    embeddings = np.array(embeddings, dtype=np.float32)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    # LAKUKAN INI KELIMA: Simpan indeks ke file lokal agar tidak memotong kuota lagi nanti
    try:
        faiss.write_index(index, INDEX_FILENAME)
        st.success(f"✅ Berhasil membuat database! File '{INDEX_FILENAME}' telah tersimpan.")
    except Exception as e:
        st.error(f"Gagal menyimpan file indeks ke server: {e}")
        
    return index, paragraphs

# Inisialisasi ulang
index, paragraphs = buat_faiss_index(paragraphs)

# === SEMANTIC SEARCH ===
def cari_konteks_semantik(query, index, paragraphs, top_k=3):
    try:
        res = client.models.embed_content(
            model="text-embedding-005", # Samakan dengan yang di atas
            contents=query
        )
        query_emb = np.array([res.embeddings[0].values], dtype=np.float32)

        D, I = index.search(query_emb, top_k)
        hasil = "\n\n".join([paragraphs[i] for i in I[0] if i != -1])
        return hasil
    except Exception as e:
        print(f"Error embedding query: {e}")
        return ""

# === BUAT JAWABAN (DENGAN MEMORY + TEMPERATUR) ===
def jawab_gemini(pertanyaan, konteks, riwayat_chat):
    # Gabungkan riwayat chat (5 pesan terakhir)
    chat_history = "\n".join(
        [f"{'User' if r=='user' else 'SANTI'}: {m}" for r, m in riwayat_chat[-5:]]
    )

    # Prompt utama
    prompt = f"""
Anda berperan sebagai asisten virtual yang cerdas. 
Nama lengkap Anda "SUSANTI, biasa dipanggil SANTI - Asisten Layanan Informasi Pengadilan Agama Purwokerto".
Sifat Anda: Ramah, lucu, menarik, dan selalu memberikan pujian singkat sebelum menjawab.

TUGAS ANDA:
1. Jawablah pertanyaan pengguna HANYA berdasarkan konteks dokumen di bawah ini:
2. Jika jawaban ada di konteks, jelaskan dengan bahasa yang mudah dipahami.
3. Jika jawaban TIDAK ADA di konteks, cukup katakan: "Hmm, kayaknya untuk hal itu kamu langsung datang aja deh ke Pengadilan Agama Purwokerto agar lebih jelas." dan jangan berikan informasi tambahan lain.
4. Jangan pernah merusak karakter Anda sebagai SANTI.

=== RIWAYAT CHAT ===
{chat_history}

=== DOKUMEN SUMBER ===
{konteks}

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


# === BOOTSTRAP + AVATAR + ANIMASI + DARK MODE + ENTER SEND ===
import datetime

# Deteksi waktu lokal (gelap setelah jam 18.00)
hour = datetime.datetime.now().hour
is_dark = hour >= 18 or hour <= 5

bg_color = "#121212" if is_dark else "#f8f9fa"
header_color = "#0d6efd" if not is_dark else "#1f6feb"
text_color = "#f1f1f1" if is_dark else "#212529"
bubble_user_bg = "#3aafa9" if is_dark else "#d1e7dd"
bubble_bot_bg = "#2e2e2e" if is_dark else "#e9ecef"
bubble_user_color = "#ffffff" if is_dark else "#0f5132"
bubble_bot_color = "#f1f1f1" if is_dark else "#212529"

# Menggunakan st.markdown untuk CSS dan JS
st.markdown(f"""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body {{
    background-color: {bg_color};
    font-family: "Poppins", sans-serif;
    color: {text_color};
}}
.chat-body {{
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
}}
.chat-message {{
    display: flex;
    align-items: flex-end;
    margin-bottom: 12px;
    animation: fadeIn 0.4s ease-in;
}}
.chat-message.user {{
    flex-direction: row-reverse;
}}
.chat-avatar {{
    width: 38px;
    height: 38px;
    border-radius: 50%;
    overflow: hidden;
    margin: 0 8px;
}}
.chat-avatar img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
}}
.chat-bubble {{
    max-width: 70%;
    padding: 10px 15px;
    border-radius: 18px;
    font-size: 15px;
    line-height: 1.4;
}}
.user .chat-bubble {{
    background-color: {bubble_user_bg};
    color: {bubble_user_color};
    border-radius: 18px 18px 0 18px;
}}
.bot .chat-bubble {{
    background-color: {bubble_bot_bg};
    color: {bubble_bot_color};
    border-radius: 18px 18px 18px 0;
}}
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
</style>

<script>
const chatBody = window.parent.document.querySelector('.chat-body');
if (chatBody) {{
    chatBody.scrollTop = chatBody.scrollHeight;
}}
</script>
""", unsafe_allow_html=True)

# === CHAT STRUCTURE ===
st.markdown("<div class='chat-body'>", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

AVATAR_USER = "https://cdn-icons-png.flaticon.com/512/847/847969.png"
AVATAR_BOT = "https://cdn-icons-png.flaticon.com/512/4712/4712100.png"

for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user">
            <div class="chat-avatar"><img src="{AVATAR_USER}"></div>
            <div class="chat-bubble">{msg}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot">
            <div class="chat-avatar"><img src="{AVATAR_BOT}"></div>
            <div class="chat-bubble">{msg}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# === INPUT TANPA PLACEHOLDER, ENTER UNTUK KIRIM ===
user_input = st.chat_input("", key="chat_input_field")

# JavaScript untuk hapus placeholder dan kirim pakai Enter
html_code = """
<script>
const t = window.parent.document.querySelector('textarea');
if (t) {
    t.placeholder = '';
    t.style.minHeight = '38px';
    t.style.fontSize = '15px';
    t.style.borderRadius = '10px';
    t.style.padding = '8px 10px';
    t.style.width = '95%';
    t.style.margin = '10px auto';
    t.style.display = 'block';
    t.style.backgroundColor = 'white';
    t.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const btn = window.parent.document.querySelector('button[kind="secondaryFormSubmit"]');
            if (btn) btn.click();
        }
    });
}
</script>
"""
st.markdown(html_code, unsafe_allow_html=True)


# === PROSES CHAT (VERSI PERBAIKAN) ===
if user_input:
    with st.spinner("🤖 SANTI sedang berpikir..."):
        # 1. Cari konteks dari dokumen menggunakan input user SAJA sebelum dimasukkan ke riwayat
        konteks = cari_konteks_semantik(user_input, index, paragraphs)
        
        # 2. Ambil jawaban dari Gemini (masukkan riwayat yang belum ditambah pertanyaan baru)
        jawaban = jawab_gemini(user_input, konteks, st.session_state.chat_history)

    # 3. Setelah jawaban didapat, baru masukkan pertanyaan dan jawaban sekaligus ke riwayat aplikasi
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("bot", jawaban))

    if "chat_input_field" in st.session_state:
        del st.session_state["chat_input_field"]

    st.rerun()
