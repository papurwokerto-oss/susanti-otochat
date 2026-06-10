import os
import streamlit as st
import base64
from google import genai

# === 1. KONFIGURASI HALAMAN UTAMA ===
st.set_page_config(
    page_title="SUSANTI AI", 
    page_icon="💬", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === 2. FUNGSI KONVERSI GAMBAR KE BASE64 ===
def get_image_base64(path):
    try:
        with open(path, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    except:
        return None

# Konversi gambar
santi_header_url = get_image_base64("santi.png")
santi_avatar_url = get_image_base64("Susanti.png")

# === 3. API KEY GOOGLE ===
if "GOOGLE_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Kunci API tidak terbaca!")
    st.stop()

DOC_FILENAME = "sumber.txt"
TEMPERATURE = 0.5 

# === 4. LOAD DOKUMEN & RETRIEVAL CERDAS ===
with open(DOC_FILENAME, "r", encoding="utf-8") as f:
    sumber_teks = f.read()

def ambil_konteks_relevan(pertanyaan, dokumen, top_n=3):
    paragraf_list = [p.strip() for p in dokumen.split("\n\n") if p.strip()]
    
    # Skor paragraf berdasarkan kecocokan kata kunci
    kata_kunci = set(pertanyaan.lower().split())
    skor_paragraf = []
    
    for p in paragraf_list:
        p_lower = p.lower()
        skor = sum(1 for kata in kata_kunci if kata in p_lower)
        skor_paragraf.append((skor, p))
    
    # Ambil paragraf dengan skor tertinggi
    skor_paragraf.sort(key=lambda x: x[0], reverse=True)
    paragraf_terpilih = [p for skor, p in skor_paragraf[:top_n] if skor > 0]
    
    # Jika tidak ada yang cocok sama sekali, ambil 2 paragraf pertama sebagai fallback
    if not paragraf_terpilih:
        return "\n\n".join(paragraf_list[:2])
    return "\n\n".join(paragraf_terpilih)

def jawab_gemini(pertanyaan, konteks_terpilih, riwayat_chat):
    # Mengambil 3 pesan terakhir agar lebih ringan
    chat_history_slice = "\n".join(
        [f"{'User' if r=='user' else 'SANTI'}: {m}" for r, m in riwayat_chat[-3:]]
    )

    prompt = f"""
Nama Anda SANTI, Asisten PA Purwokerto.
Jawab berdasarkan konteks: {konteks_terpilih}
Jika tidak ada jawaban di konteks, katakan: "Mohon maaf yaa, untuk hal itu sebaiknya kamu langsung datang aja deh ke Pengadilan Agama Purwokerto agar lebih jelas."
Riwayat: {chat_history_slice}
Pertanyaan: {pertanyaan}
Jawablah dengan ramah, sopan, dan ringkas.
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'temperature': 0.5,
                'max_output_tokens': 300 
            }
        )
        return response.text.strip()
    except Exception as e:
        # INI AKAN MENAMPILKAN ERROR ASLINYA DI CHAT
        return f"SANTI mengalami error teknis: {str(e)}"
# === 5. CSS PREMIUM (DIPERBAIKI UNTUK MOBILE) ===
st.markdown("""
<style>
    header, footer, [data-testid='stHeader'] {display: none !important;}
    
    /* Header Responsive */
    .custom-header {
        position: fixed; top: 0; left: 0; right: 0; min-height: 80px; 
        background-color: #0a5d3f; display: flex; align-items: center; 
        padding: 10px 15px; z-index: 99999; border-bottom: 2px solid #e6a119;
        gap: 15px;
    }
    .custom-header-img {width: 50px; height: 50px; border-radius: 50%; border: 2px solid #ffffff; object-fit: cover;}
    .custom-header-text {display: flex; flex-direction: column; justify-content: center;}
    .custom-header-title {color: #ffffff !important; font-size: 1.1rem !important; font-weight: 800 !important; margin: 0 !important; line-height: 1.2;}
    .custom-header-subtitle {color: #e2e8f0 !important; font-size: 0.75rem !important; margin: 0 !important; line-height: 1.2;}

    @media (max-width: 600px) {
        .custom-header {min-height: 70px; gap: 10px; padding: 8px 10px;}
        .custom-header-img {width: 40px; height: 40px;}
        .custom-header-title {font-size: 0.95rem !important;}
        .custom-header-subtitle {font-size: 0.65rem !important;}
    }

    .stMainBlockContainer {padding-top: 100px !important; padding-bottom: 150px !important;}
    .welcome-screen {text-align: center; margin-top: 20px; color: #94a3b8;}
    .custom-footer {position: fixed; bottom: 0; left: 0; right: 0; height: 35px; background-color: #052217; text-align: center; border-top: 1px solid #0a5d3f; z-index: 99998; color: #94a3b8; font-size: 0.7rem; line-height: 35px;}
    .btn-container {text-align: center; margin-top: 20px;}
</style>
""", unsafe_allow_html=True)

# === 6. HEADER (DIPERBAIKI) ===
st.markdown(f"""
<div class="custom-header">
    <img src="{santi_header_url}" class="custom-header-img">
    <div class="custom-header-text">
        <div class="custom-header-title">SUSANTI</div>
        <div class="custom-header-subtitle">Sistem Unggulan Setara Aparatur Navigatif, Tanggap dan Informatif</div>
    </div>
</div>
""", unsafe_allow_html=True)

# === 7. CHAT LOGIC ===
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# Tombol Hapus (Ditempatkan di area chat)
st.markdown('<div class="btn-container">', unsafe_allow_html=True)
if st.button("Hapus Riwayat Chat"):
    st.session_state.chat_history = []
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Tampilan Welcome Screen dengan animasi fade-in
if len(st.session_state.chat_history) == 0:
    st.markdown(f"""
    <style>
    .welcome-screen {{
        text-align: center;
        margin-top: 50px;
        color: #94a3b8;
    }}
    .welcome-screen img {{
        height: 120px;
        width: 120px;
        border-radius: 50%;
        border: 3px solid #0a5d3f;
        margin-bottom: 20px;
        opacity: 0;
        animation: fadeIn 2s forwards;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: scale(0.9); }}
        to {{ opacity: 1; transform: scale(1); }}
    }}
    </style>

    <div class="welcome-screen">
        <img src="{santi_header_url}" alt="Santi Logo"/>
        <h2>Assalamu'alaikum! Saya SUSANTI</h2>
        <p>Saya adalah Sistem Unggulan yang Setara dengan Aparatur, bersifat Navigatif, Tanggap dan Informatif</p>
        <p>Sebagai pegawai virtual Pengadilan Agama Purwokerto, saya siap membantu Anda.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for role, msg in st.session_state.chat_history:
        avatar = santi_avatar_url if role == "bot" else "👤"
        with st.chat_message(role, avatar=avatar):
            st.write(msg)


user_input = st.chat_input("Ketik pertanyaan Anda di sini...")

# === BAGIAN LOGIKA CHAT YANG DIPERBAIKI ===
if user_input:
    # 1. Simpan dan tampilkan pesan user
    st.session_state.chat_history.append(("user", user_input))
    with st.chat_message("user", avatar="👤"): 
        st.write(user_input)
    
    # 2. Proses jawaban bot dengan spinner
    with st.chat_message("bot", avatar=santi_avatar_url):
        with st.spinner("Sabar ya Lur, inyong tak mikir disit..."):
            # Ambil konteks
            konteks_terpilih = ambil_konteks_relevan(user_input, sumber_teks, top_n=3)
            
            # Panggil fungsi jawab_gemini
            jawaban = jawab_gemini(
                user_input, 
                konteks_terpilih, 
                st.session_state.chat_history[:-1]
            )
            
            # Tampilkan jawaban
            st.write(jawaban)
            
    # 3. Simpan pesan bot ke riwayat
    st.session_state.chat_history.append(("bot", jawaban))
    st.rerun()

# === 8. FOOTER ===
st.markdown("""
<div class="custom-footer">&copy; 2026 - Pengadilan Agama Purwokerto</div>
""", unsafe_allow_html=True)

# === 9. AUTO-SCROLL FIX ===
import streamlit.components.v1 as components

# Kode JavaScript untuk scroll ke bawah secara otomatis
components.html(
    """
    <script>
        const scrollBottom = () => {
            window.parent.document.querySelector('section.main').scrollTo(0, 1000000);
        };
        setTimeout(scrollBottom, 100); // Memberi jeda sedikit agar konten selesai di-render
    </script>
    """,
    height=0,
)
