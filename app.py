import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS
from translate import Translator
import random
import time
import urllib.parse

# --- 1. AYARLAR ---
GOOGLE_API_KEY = "AIzaSyBpfia2i-dayH5UE_4DvGBAHvDyTLTtru0"
genai.configure(api_key=GOOGLE_API_KEY)
translator = Translator(to_lang="zh")

st.set_page_config(page_title="Zırhlı Trend Avcısı", page_icon="🛡️", layout="wide")

# --- 2. TASARIM (HATASIZ GÖRÜNÜM) ---
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #fff; }
    
    /* Ürün Kartı */
    .trend-card {
        background-color: #111;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        text-align: center;
    }
    .trend-card img {
        border-radius: 8px;
        max-height: 200px;
        object-fit: cover;
    }
    
    /* B Planı Kartı (Resim Yüklenemezse Çıkar) */
    .backup-card {
        background: linear-gradient(135deg, #1e1e1e, #2a2a2a);
        border: 2px dashed #555;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .tag { background-color: #E60023; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    
    /* Butonlar */
    .big-btn { width: 100%; padding: 18px; font-size: 22px; background: linear-gradient(90deg, #FF512F, #DD2476); color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold; }
    .link-btn { display:inline-block; background-color:#00e5ff; color:black; padding:8px 15px; border-radius:6px; text-decoration:none; font-weight:bold; margin-top:10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. RULET KAVANOZU (SINIRSIZ YENİ FİKİR) ---
KONSEPTLER = [
    "Labubu Vinyl Face Plush", "Crybaby Powerpuff Girls Popmart", "Skullpanda Image Of Reality",
    "Dimoo Dating Series", "Hirono Reshape Series", "Azura Animal Fighting Match",
    "Nyota Fluffy Life Series", "Zsiga Walking Into The Forest", "Molly Imaginary Wandering",
    "Sweet Bean Supermarket", "Pucky Elf Forest", "Hacipupu The Kindergarten",
    "Pino Jelly How Are You", "Satyr Rory Cuddly Toy", "Bunny Winter Series",
    "Harry Potter Mystery Minis", "Sanrio Characters Latte Baby", "Kuromi Poker Kingdom",
    "Crayon Shin-chan Daily Life", "Doraemon Future Department Store"
]

# --- 4. GÜVENLİ ARAMA MOTORU ---

def trend_avla():
    # 1. Rastgele Konu Seç
    konu = random.choice(KONSEPTLER)
    
    # 2. Link Hazırla (Resim gelmese bile bu link çalışır)
    google_link = f"https://www.google.com/search?q={urllib.parse.quote(konu + ' blind box viral')}&tbm=isch"
    
    # 3. Resim Çekmeye Çalış (Riskli Kısım)
    bulunan_resimler = []
    hata_var = False
    
    try:
        with DDGS() as ddgs:
            # Sadece 3 saniye dene, olmazsa zorlama
            sorgu = f"{konu} blind box viral unboxing"
            sonuclar = list(ddgs.images(sorgu, max_results=3))
            if sonuclar:
                bulunan_resimler = sonuclar
            else:
                hata_var = True
    except:
        hata_var = True # Hata alırsa B Planına geç
        
    return {
        "konu": konu,
        "resimler": bulunan_resimler,
        "hata": hata_var,
        "link": google_link
    }

# --- 5. ARAYÜZ ---

st.title("🛡️ ZIRHLI TREND AVCISI")
st.caption("Engel tanımayan mod devrede.")

if st.button("ŞANSINI DENE VE ARA 🎲", type="primary"):
    
    with st.spinner("İstihbarat uydusuna bağlanılıyor..."):
        time.sleep(1) # Ban yememek için nazik bekleme
        
        veri = trend_avla()
        konu = veri['konu']
        
        st.success(f"🎯 Hedef Kilitlendi: **{konu}**")
        
        # EĞER RESİM BULUNDUYSA (A Planı)
        if not veri['hata'] and veri['resimler']:
            cols = st.columns(3)
            for i, resim in enumerate(veri['resimler']):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="trend-card">
                        <img src="{resim['image']}" width="100%">
                        <h4 style="margin-top:10px; font-size:14px;">{resim['title'][:30]}...</h4>
                        <a href="{resim['image']}" target="_blank" class="link-btn">Resmi Büyüt 🔍</a>
                    </div>
                    """, unsafe_allow_html=True)
                    
        # EĞER RESİM BULUNAMADIYSA / ENGELLENDİYSE (B Planı - Asla Boş Dönmez)
        else:
            st.warning("⚠️ Uydu Görüntüsü Alınamadı (İnternet Engeli), Ama Koordinatlar Geldi!")
            st.markdown(f"""
            <div class="backup-card">
                <h3>🚫 Görsel Yüklenemedi</h3>
                <p>DuckDuckGo şu an yoğun ama trendi bulduk.</p>
                <h2 style="color:#00e5ff;">{konu}</h2>
                <br>
                <a href="{veri['link']}" target="_blank" class="big-btn" style="text-decoration:none; font-size:18px;">
                    🚀 Tıkla ve Google'da Gör
                </a>
                <p style="margin-top:10px; font-size:12px; color:#888;">Bu buton seni direkt bu ürünün görsellerine götürür.</p>
            </div>
            """, unsafe_allow_html=True)